import os
from .base import BaseParser

class LiteparseParser(BaseParser):
    def parse(self, file_path: str) -> str:
        import liteparse
        parser = liteparse.Parser()
        doc = parser.parse_file(file_path)
        text = ""
        for page in doc.pages:
            for block in page.blocks:
                for line in block.lines:
                    text += line.text + "\n"
        return text
