import os
import sys
import gc

# Add parent directory to path so we can import from parsers and metrics
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metrics.speed import SpeedMonitor
from metrics.memory import PeakMemoryMonitor
from metrics.diff_tool import calculate_diff_and_similarity

# Import the runners
import parsers.docling.runner as docling_runner
import parsers.liteparse.runner as liteparse_runner
import parsers.pymupdf.runner as pymupdf_runner
import parsers.llamaparse.runner as llamaparse_runner

PDF_PATH = os.path.join("datasets", "sample_5_pages.pdf")
OUTPUT_DIR = "results"

def execute_benchmark(name, runner_func):
    print(f"\n[Benchmarking: {name}]")
    gc.collect() # Force GC to clear memory
    
    with PeakMemoryMonitor() as mem_monitor:
        with SpeedMonitor() as speed_monitor:
            try:
                output_md = runner_func(PDF_PATH)
                status = "Success"
            except Exception as e:
                output_md = f"Error: {e}"
                status = "Failed"
                
    time_taken = speed_monitor.duration()
    peak_ram = mem_monitor.get_peak_mb()
    
    print(f"Status: {status}")
    print(f"Speed: {time_taken:.2f}s")
    print(f"Peak RAM: {peak_ram:.2f} MB")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, f"{name.lower()}_output.md"), "w", encoding="utf-8") as f:
        f.write(output_md)
        
    return {
        "name": name,
        "status": status,
        "time": time_taken,
        "ram": peak_ram
    }

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print(f"Error: {PDF_PATH} not found.")
        sys.exit(1)
        
    results = []
    
    # Execute Docling first to serve as the baseline
    results.append(execute_benchmark("Docling", docling_runner.parse))
    
    # Execute others
    results.append(execute_benchmark("LiteParse", liteparse_runner.parse))
    results.append(execute_benchmark("PyMuPDF", pymupdf_runner.parse))
    results.append(execute_benchmark("LlamaParse", llamaparse_runner.parse))
    
    # Calculate Diffs
    docling_output = os.path.join(OUTPUT_DIR, "docling_output.md")
    for r in results:
        if r['name'] == "Docling":
            r['similarity'] = "100.00% (Baseline)"
            continue
        
        target_output = os.path.join(OUTPUT_DIR, f"{r['name'].lower()}_output.md")
        diff_file = os.path.join(OUTPUT_DIR, f"{r['name'].lower()}_vs_docling_diff.txt")
        r['similarity'] = calculate_diff_and_similarity(docling_output, target_output, diff_file)
        
    # Save the leaderboard
    with open("leaderboard.md", "w", encoding="utf-8") as f:
        f.write("# DocParseBench Leaderboard\n\n")
        f.write("Target: `sample_5_pages.pdf`\n\n")
        f.write("| Parser | Status | Speed | Peak RAM | Similarity to Docling |\n")
        f.write("|--------|--------|-------|----------|-----------------------|\n")
        for r in results:
            f.write(f"| {r['name']} | {r['status']} | {r['time']:.2f}s | {r['ram']:.2f} MB | {r.get('similarity', 'N/A')} |\n")
            
    print("\nBenchmark complete! Results saved to leaderboard.md and outputs in results/")
