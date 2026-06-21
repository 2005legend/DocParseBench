from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time

class BaseParser(ABC):
    """Abstract base class for all PDF parsers."""

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """
        Extract text/markdown from a PDF file.
        
        Args:
            file_path: Path to the input PDF file.
            
        Returns:
            The extracted text or markdown content.
        """
        pass
