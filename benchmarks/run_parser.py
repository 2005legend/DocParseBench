import argparse
import sys
import os
import time

# Ensure we can import from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_parser(name):
    if name == 'liteparse':
        from parsers.liteparse_parser import LiteparseParser
        return LiteparseParser()
    elif name == 'docling':
        from parsers.docling_parser import DoclingParser
        return DoclingParser()
    elif name == 'pymupdf':
        from parsers.pymupdf_parser import PyMuPDFParser
        return PyMuPDFParser()
    elif name == 'llamaparse':
        from parsers.llamaparse_parser import LlamaParseParser
        return LlamaParseParser()
    elif name == 'marker':
        from parsers.marker_parser import MarkerParser
        return MarkerParser()
    else:
        raise ValueError(f"Unknown parser: {name}")

def main():
    parser = argparse.ArgumentParser(description="Run a specific parser on a PDF")
    parser.add_argument('--parser', type=str, required=True, help="Name of the parser")
    parser.add_argument('--input', type=str, required=True, help="Path to input PDF")
    parser.add_argument('--output', type=str, required=True, help="Path to output file")
    
    args = parser.parse_args()
    
    p = get_parser(args.parser)
    
    start_time = time.time()
    result = p.parse(args.input)
    end_time = time.time()
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(result)
        
    print(f"DONE|{end_time - start_time:.4f}")

if __name__ == '__main__':
    main()
