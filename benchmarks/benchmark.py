import time
import os
import psutil
import threading
import gc

PDF_PATH = "sample_5_pages.pdf"
OUTPUT_DIR = "benchmark_outputs"

# --- Parsers ---
def run_liteparse():
    import liteparse
    parser = liteparse.Parser()
    doc = parser.parse_file(PDF_PATH)
    text = ""
    for page in doc.pages:
        for block in page.blocks:
            for line in block.lines:
                text += line.text + "\n"
    return text

def run_docling():
    from docling.document_converter import DocumentConverter
    converter = DocumentConverter()
    result = converter.convert(PDF_PATH)
    return result.document.export_to_markdown()

def run_pymupdf():
    import pymupdf4llm
    return pymupdf4llm.to_markdown(PDF_PATH)

def run_marker():
    from marker.convert import convert_single_pdf
    from marker.models import load_all_models
    
    model_lst = load_all_models()
    full_text, _, _ = convert_single_pdf(PDF_PATH, model_lst)
    return full_text

def run_llamaparse():
    os.environ["LLAMA_CLOUD_API_KEY"] = "llx-DFfnyUVEHlXUH3e9Ye0yIt0vphhqQDpa2dugJTJuSC1Ml4mB"
    from llama_parse import LlamaParse
    parser = LlamaParse(result_type="markdown")
    documents = parser.load_data(PDF_PATH)
    return "\n\n".join([doc.text for doc in documents])

# --- Monitoring ---
class PeakMemoryMonitor:
    def __init__(self):
        self.keep_measuring = True
        self.peak_memory = 0
        
    def measure_memory(self):
        process = psutil.Process(os.getpid())
        while self.keep_measuring:
            mem = process.memory_info().rss / (1024 * 1024) # MB
            if mem > self.peak_memory:
                self.peak_memory = mem
            time.sleep(0.05)

def benchmark_parser(name, func):
    print(f"\n--- Benchmarking {name} ---")
    
    # Force Garbage Collection before test
    gc.collect()
    
    # Start memory monitoring thread
    monitor = PeakMemoryMonitor()
    t = threading.Thread(target=monitor.measure_memory)
    t.start()
    
    start_time = time.time()
    try:
        output_text = func()
        status = "Success"
    except Exception as e:
        output_text = f"Error: {e}"
        status = "Failed"
    end_time = time.time()
    
    # Stop monitoring
    monitor.keep_measuring = False
    t.join()
    
    duration = end_time - start_time
    peak_mb = monitor.peak_memory
    
    print(f"Status: {status}")
    print(f"Time Taken: {duration:.2f} seconds")
    print(f"Peak RAM: {peak_mb:.2f} MB")
    
    # Save output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, f"{name.lower()}_output.md"), "w", encoding="utf-8") as f:
        f.write(output_text)
        
    return {"name": name, "time": duration, "peak_ram_mb": peak_mb, "status": status}

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print(f"Error: Could not find {PDF_PATH}")
        exit(1)
        
    results = []
    
    # Run benchmarks
    results.append(benchmark_parser("LiteParse", run_liteparse))
    results.append(benchmark_parser("PyMuPDF", run_pymupdf))
    results.append(benchmark_parser("Docling", run_docling))
    results.append(benchmark_parser("LlamaParse", run_llamaparse))
    
    # Run Marker last as it loads heavy models into RAM globally 
    results.append(benchmark_parser("Marker", run_marker))
    
    # Print Markdown Table
    print("\n\n### Benchmark Results")
    print("| Parser | Status | Time (5 pages) | Peak RAM (MB) |")
    print("|--------|--------|----------------|---------------|")
    for r in results:
        print(f"| {r['name']} | {r['status']} | {r['time']:.2f}s | {r['peak_ram_mb']:.2f} MB |")
