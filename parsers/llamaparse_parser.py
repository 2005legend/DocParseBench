import os
from dotenv import load_dotenv
from .base import BaseParser

class LlamaParseParser(BaseParser):
    def __init__(self):
        super().__init__()
        load_dotenv()
        
    def parse(self, file_path: str) -> str:
        from llama_parse import LlamaParse
        
        # Load API key from env
        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not api_key:
            raise ValueError("LLAMA_CLOUD_API_KEY is not set in the environment.")
            
        parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",
            verbose=False,
            language="en"
        )
        
        # LlamaParse returns a list of Document objects
        documents = parser.load_data(file_path)
        
        # Join the text from all parsed document parts
        return "\n\n".join([doc.text for doc in documents])
