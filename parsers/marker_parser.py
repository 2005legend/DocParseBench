import os
import tempfile
import subprocess
from .base import BaseParser

class MarkerParser(BaseParser):
    def parse(self, file_path: str) -> str:
        # Since marker-pdf often recommends the CLI for simple usage and 
        # API can change, we'll invoke the CLI. 
        # Alternatively, use the internal API if preferred.
        # Here we use the CLI to avoid model loading state issues.
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = [
                "marker_single", 
                file_path, 
                "--output_dir", temp_dir,
                "--batch_multiplier", "1"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Find the generated markdown file
            # Marker usually creates a folder with the pdf name
            pdf_name = os.path.splitext(os.path.basename(file_path))[0]
            out_folder = os.path.join(temp_dir, pdf_name)
            md_file = os.path.join(out_folder, f"{pdf_name}.md")
            
            if os.path.exists(md_file):
                with open(md_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return f"Error: Markdown file not found in {out_folder}"
