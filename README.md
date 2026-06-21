<div align="center">
  <h1>📄 DocParseBench</h1>
  <p><b>A Comprehensive Benchmarking Arena for Modern PDF Parsing & Extraction Frameworks</b></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
  [![CI](https://github.com/placeholder/DocParseBench/actions/workflows/benchmark.yml/badge.svg)](https://github.com/placeholder/DocParseBench/actions)
</div>

<br/>

**DocParseBench** (or *PDFParserArena*) is a rigorous evaluation suite designed specifically for **Retrieval-Augmented Generation (RAG)** pipelines. 

Unlike traditional OCR benchmarks that only measure extraction quality, DocParseBench emphasizes **Operational and Deployment Characteristics**. When building production systems, you need to know not just how accurate a parser is, but how much RAM it will consume, how fast it runs, and at what scale it fails.

---

## 🏆 Current Leaderboard Snapshot

*Note: Below is an estimation snapshot. Run the orchestrator locally on your hardware to generate your specific performance bounds.*

| Parser | Pages/Sec | Peak RAM (MB) | WER | Table Fidelity | Heading Score | Reading Order |
|---|---|---|---|---|---|---|
| liteparse | 0.00 | 0.00 | N/A | N/A | N/A | N/A |
| pymupdf | 2.71 | 402.02 | 0.155 | 79.63% | 1.65% | 35.99% |
| llamaparse | 6.93 | 150.07 | 0.000 | 100.00% | 100.00% | 100.00% |
| docling | 0.20 | 2276.68 | 0.190 | 100.00% | 0.00% | 40.39% |

---

## 🏗️ Architecture & Metrics Engine

We built the runner using **Isolated Subprocesses** and a background **`psutil` Profiler** thread. This prevents massive memory leaks (common in vision models) from bleeding across documents and destroying the orchestrator.

### ⚙️ Evaluated Metrics
1. **Performance**: Pages per Second, Peak RAM (RSS) tracking, CPU Utilization, Output File Size.
2. **Advanced Quality**:
    - **Word Error Rate (WER)**: Native dynamic programming evaluation of insertions, deletions, substitutions against Ground Truth.
    - **Table Extraction Fidelity**: Extraction of all Markdown tables to verify row recovery rates and table counts.
    - **Heading Hierarchy Preservation**: Longest Common Subsequence of `H1, H2, H3` to ensure semantic structure remains intact.
    - **Reading Order Preservation**: Proxy hash sequencing to catch errant column reading.

### 📂 Supported Document Categories
The benchmark is structured to test against a diverse set of real-world layouts:
1. Financial Reports (10-Ks, 10-Qs)
2. Scientific Papers (ArXiv)
3. Scanned Documents
4. Presentation Slides
5. Legal Contracts
6. Forms & Invoices

---

## 🚀 Quickstart

**1. Clone and Install**
```bash
git clone https://github.com/yourusername/DocParseBench.git
cd DocParseBench
pip install -r requirements.txt
```
*(Note: To test Marker on Windows, you must install the Microsoft C++ Build Tools first).*

**2. Configure API Keys**
Create a `.env` file at the root of the project to authenticate cloud parsers:
```bash
LLAMA_CLOUD_API_KEY="your_llamaparse_key_here"
```

**3. Generate Ground Truth (Optional Bootstrapping)**
If you are adding new PDFs to `datasets/pdfs/` and don't have human-annotated Ground Truth, you can auto-generate a baseline using LlamaParse:
```bash
python scripts/generate_ground_truth.py
```

**4. Execute the Benchmark Arena**
```bash
python benchmarks/runner.py --output-dir results
```
This spawns isolated processes for each parser and safely captures resource usage.

**5. Generate the Final Report**
```bash
python benchmarks/report_builder.py
```
Outputs a pristine Markdown table summarizing WER, Table Fidelity, Speed, and RAM usage into `reports/report.md`.

---

## 📚 Guides
- 👉 [**The Docling Memory Optimization Guide**](./docling_optimization_guide.md): How to architect a chunking pipeline to run Docling on any PDF size without crashing.
