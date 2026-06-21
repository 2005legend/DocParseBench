def parse(pdf_path):
    import pymupdf4llm
    return pymupdf4llm.to_markdown(pdf_path)
