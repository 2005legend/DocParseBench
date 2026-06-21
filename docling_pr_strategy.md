# Docling GitHub Issue / PR Strategy

## Background
Currently, when processing large PDFs (e.g., 50+ pages), Docling loads the entire document into memory to render bitmaps and pass them through its underlying models (LayoutLM, TableFormer, RapidOCR). On machines with standard RAM (16GB) or low VRAM (4GB), this causes an unavoidable `std::bad_alloc` crash before any text is extracted.

While developers can manually bypass this by chunking the PDF into smaller temporary files using `pypdf`, a native batching solution would significantly improve Docling's out-of-the-box developer experience.

## Proposed GitHub Issue Draft

**Title:** `Feature Request: Native Sequential Batch Processing to Prevent OOM on Large PDFs`

**Description:**
Hi team! Docling is incredible for RAG pipelines, but it currently struggles with memory scaling on large PDFs (>50 pages) when running on consumer hardware (16GB RAM / 4GB VRAM GPU), consistently resulting in `std::bad_alloc` crashes.

I've benchmarked the parser and found that wrapping the document in a `pypdf` chunker (feeding it 5 pages at a time sequentially and calling `gc.collect()`) completely eliminates the OOM issue, making memory usage approximately constant regardless of PDF length. 

However, this requires developers to manually split the PDF and stitch the Markdown back together. 

**Proposal:**
Would you be open to a PR that implements a native `max_pages_per_batch` or `sequential_processing` flag within the `DocumentConverter`? 

**Expected Behavior:**
```python
converter = DocumentConverter()
result = converter.convert("massive_1000_page_document.pdf", max_pages_per_batch=5)
```
*Under the hood, the converter would iteratively load and process X pages at a time, clear the intermediate tensors from memory, and append the results to the final Document object.*

**Why this is valuable:**
1. Allows Docling to run indefinitely on large documents without RAM/VRAM exhaustion.
2. Prevents users from abandoning Docling when they see an immediate crash on their first large 10-K test.
3. Cheaper cloud deployment (avoids needing 64GB instances for large documents).

Please let me know if this aligns with the roadmap, and I'd be happy to submit a PR implementing this pattern!

---

## Action Plan
1. Check the official Docling repository issues to ensure this hasn't been requested in the last month.
2. Post the above Issue Draft.
3. If maintainers approve, fork the repository, integrate our `pypdf` chunking logic directly into the `DocumentConverter` preprocessing pipeline, and submit the PR.
