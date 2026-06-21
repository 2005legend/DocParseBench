import os
from .base import BaseParser

class LiteparseParser(BaseParser):
    def parse(self, file_path: str) -> str:
        from liteparse import LiteParse
        parser = LiteParse(output_format="markdown")
        result = parser.parse(file_path)
        return result.text
