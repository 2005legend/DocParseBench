from .base import BaseParser

class PyMuPDFParser(BaseParser):
    def parse(self, file_path: str) -> str:
        import pymupdf4llm
        md_text = pymupdf4llm.to_markdown(file_path)
        return md_text
