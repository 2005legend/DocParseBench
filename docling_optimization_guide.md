# Docling Memory Optimization Guide: Running on Large PDFs with 16GB RAM and RTX 3050

*If you've ever tried to run Docling on a 50+ page PDF on a standard laptop, you've likely encountered a catastrophic `std::bad_alloc` crash or an Out of Memory (OOM) error. This guide explains why that happens and how to architect a solution that makes Docling's memory usage approximately constant, regardless of the PDF length.*

---

## 1. Why OOM Happens

Docling is not a traditional PDF parser (like `pypdf` or `LiteParse`) that simply reads embedded text streams. It treats every page as a complex visual document. 

Under the hood, Docling:
1. Renders the PDF page into a high-resolution image bitmap.
2. Runs a **Layout Detection Model** (e.g., LayoutLM/YOLO) to identify paragraphs, tables, and headers.
3. Runs a **Table Structure Model** (TableFormer) to parse grid structures.
4. Runs an **OCR Model** (RapidOCR) on regions identified as scanned images.

If you pass a 150-page document into Docling simultaneously, it generates massive tensors and bitmaps for every page, overwhelming your system's RAM very early in the preprocessing stage, resulting in an OS-level kill (`std::bad_alloc`).

## 2. CPU vs GPU Limitations

You might assume that having an NVIDIA RTX 3050 GPU solves this. It usually doesn't, for two reasons:

1. **Default PyTorch Install:** By default, standard installations of Docling pull the CPU-only version of PyTorch. Without CUDA enabled, your GPU sits idle while the CPU tries to shoulder the massive tensor calculations in system RAM.
2. **VRAM Bottlenecks:** Even if you properly configure PyTorch with CUDA, the RTX 3050 only has **4GB of VRAM**. Modern Vision models are large. If Docling attempts to load the layout, table, and OCR models into VRAM and process multiple pages simultaneously, you will hit a `CUDA Out of Memory` error instead.

## 3. The Solution: The Chunking Strategy

To run Docling on consumer hardware or low-memory cloud instances, you must decouple the document length from the memory footprint. 

The strategy is simple: **Chunk the PDF before it reaches Docling.**

Instead of feeding Docling 150 pages, you feed it 5 pages at a time sequentially. 

### Python Implementation Example

```python
import os
import gc
from pypdf import PdfReader, PdfWriter
from docling.document_converter import DocumentConverter

def run_docling_batched(pdf_path, batch_size=5):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    converter = DocumentConverter()
    
    with open("final_output.md", "w") as f:
        f.write("# Parsed Output\n")

    for start in range(0, total_pages, batch_size):
        end = min(start + batch_size, total_pages)
        temp_pdf = "temp_batch.pdf"
        
        # 1. Create temporary PDF for this batch
        writer = PdfWriter()
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        with open(temp_pdf, "wb") as f:
            writer.write(f)
            
        # 2. Run Docling
        result = converter.convert(temp_pdf)
        
        # 3. Append Markdown
        with open("final_output.md", "a") as f:
            f.write(result.document.export_to_markdown())
            f.write("\n\n---\n\n")
            
        # 4. Critical: Force Garbage Collection
        gc.collect()

    os.remove(temp_pdf)
```

## 4. Why This Architecture Works

By implementing this architecture, **peak memory stays roughly constant because you're only handling a small subset of pages at once.** This is exactly the approach recommended for long PDFs.

> [!WARNING]
> **What does NOT become infinite:**
> Even with batching:
> 1. Runtime grows linearly.
> 2. Output markdown grows linearly.
> 3. Storage requirements grow.
> 4. Some PDFs may contain huge images or complex vector graphics that increase memory needs for a single page.
>
> **Important Caveat:** Docling can process arbitrarily large PDFs if batch/page-range processing is used, *assuming sufficient disk space and processing time.* A 5000-page PDF might take hours, but it shouldn't crash purely because of document length if batching is implemented correctly.

*   **Recommended Batch Size:** 5 pages. This keeps RAM usage well under 4GB during the conversion process, allowing it to comfortably fit on a 16GB system (or a 4GB VRAM GPU) while leaving room for the OS.
*   **Production Architecture:** For enterprise RAG pipelines, this chunking strategy allows you to use cheaper, low-memory instances (like AWS t3.medium or Lambda) to sequentially chew through massive documents over time, drastically reducing cloud compute costs.
