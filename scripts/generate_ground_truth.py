import os
import json
import sys
from dotenv import load_dotenv

# Ensure we can import from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parsers.llamaparse_parser import LlamaParseParser

def generate_ground_truth(manifest_path: str):
    load_dotenv()
    
    if not os.getenv("LLAMA_CLOUD_API_KEY"):
        print("Error: LLAMA_CLOUD_API_KEY not found in environment.")
        return
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    base_dir = os.path.dirname(manifest_path)
    parser = LlamaParseParser()
    
    for dataset in manifest.get('datasets', []):
        gt_rel_path = dataset.get('ground_truth_path')
        if not gt_rel_path:
            continue
            
        gt_path = os.path.join(base_dir, gt_rel_path)
        
        if os.path.exists(gt_path):
            print(f"Skipping {dataset['id']} - ground truth already exists.")
            continue
            
        pdf_path = os.path.join(base_dir, dataset['file_path'])
        if not os.path.exists(pdf_path):
            print(f"Error: PDF for {dataset['id']} not found at {pdf_path}")
            continue
            
        print(f"Generating Ground Truth for {dataset['id']} using LlamaParse...")
        try:
            markdown_content = parser.parse(pdf_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(gt_path), exist_ok=True)
            
            with open(gt_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            print(f"  -> Saved to {gt_path}")
        except Exception as e:
            print(f"  -> Failed: {e}")

if __name__ == "__main__":
    manifest_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasets', 'manifest.json'))
    generate_ground_truth(manifest_loc)
