def parse(pdf_path):
    from docling.document_converter import DocumentConverter
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown()
