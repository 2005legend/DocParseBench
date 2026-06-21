from .base import BaseParser

class DoclingParser(BaseParser):
    def parse(self, file_path: str) -> str:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document.export_to_markdown()
