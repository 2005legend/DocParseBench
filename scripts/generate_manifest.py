import os
import json
import fitz  # PyMuPDF

def generate_manifest(pdf_dir, output_file):
    manifest = {"datasets": []}
    
    if not os.path.exists(pdf_dir):
        print(f"Directory {pdf_dir} does not exist.")
        return
        
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_dir, filename)
            doc = fitz.open(filepath)
            pages = len(doc)
            doc.close()
            
            # Simple category inference
            category = "General"
            if "10-k" in filename.lower() or "10-q" in filename.lower() or "aapl" in filename.lower():
                category = "Financial Reports"
            elif "v7" in filename.lower() or "1706" in filename.lower():
                category = "Scientific Papers"
                
            dataset_id = filename.replace(".pdf", "")
            
            manifest["datasets"].append({
                "id": dataset_id,
                "category": category,
                "file_path": f"pdfs/{filename}",
                "pages": pages,
                "ground_truth_path": f"ground_truth/{dataset_id}.md"
            })
            
    with open(output_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written to {output_file} with {len(manifest['datasets'])} entries.")

if __name__ == "__main__":
    generate_manifest(
        pdf_dir=r"c:\Users\USER\Downloads\ocr comparison\DocParseBench\datasets\pdfs",
        output_file=r"c:\Users\USER\Downloads\ocr comparison\DocParseBench\datasets\manifest.json"
    )
