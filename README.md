# DocParseBench / PDFParserArena

A comprehensive benchmarking repository to evaluate popular PDF parsing and extraction tools for RAG (Retrieval-Augmented Generation) pipelines. 

## Included Parsers
*   **Docling** - State-of-the-art vision models for document understanding.
*   **LiteParse** - High-speed, native PDF text stream extraction.
*   **PyMuPDF / PyMuPDF4LLM** - Fast, layout-aware extraction.
*   **LlamaParse** - Cloud-based API for complex document extraction.
*   **Marker** - (Note: Requires C++ Build Tools for local compilation on some OS/Python combos).

## The Benchmark Leaderboard

We test these parsers based on **Speed**, **RAM Usage**, and qualitative metrics like **Table Extraction** and **OCR Quality**.

*To see the latest hardware execution times, check `leaderboard.md`.*

| Metric | Docling | LiteParse | PyMuPDF | LlamaParse | Marker |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Speed** | Slow (~3s/page) | Very Fast | Fast | Varies (API) | Slow |
| **Peak RAM** | High (GBs) | Low (MBs) | Low (MBs) | Low (API) | High (GBs) |
| **Tables** | Excellent | Poor | Medium | Excellent | Excellent |
| **OCR** | Excellent | None | None | Excellent | Excellent |
| **RAG Quality**| High | Low/Medium | Medium | High | High |

---

## 🚀 The Docling Memory Guide

Are you experiencing `std::bad_alloc` or `CUDA Out of Memory` crashes when running **Docling** on large PDFs (50+ pages)? 

Check out our definitive guide on how to architect a chunking pipeline to run Docling on any PDF size with just 16GB of RAM or an RTX 3050. 
👉 [**Read the Docling Memory Optimization Guide here**](./docling_optimization_guide.md)

---

## How to Run the Benchmark Locally

**1. Install dependencies**
```bash
pip install -r requirements.txt
```
*(Note: To test Marker on Windows, you must install the Microsoft C++ Build Tools first).*

**2. Add your LlamaParse API Key**
Update the key in `parsers/llamaparse/runner.py`.

**3. Execute the Orchestrator**
```bash
python benchmarks/run_all.py
```
Outputs will be saved in the `results/` folder, and hardware execution metrics will be updated in `leaderboard.md`.
