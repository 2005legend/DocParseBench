import json
import os

manifest_path = r'c:\Users\USER\Downloads\ocr comparison\DocParseBench\datasets\manifest.json'
subset_path = r'c:\Users\USER\Downloads\ocr comparison\DocParseBench\datasets\manifest_subset.json'

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

# Pick two representative documents that already have ground truth generated
subset_ids = ['1706.03762v7', 'NASDAQ_AAPL_2024']

subset_datasets = [d for d in manifest['datasets'] if d['id'] in subset_ids]

with open(subset_path, 'w') as f:
    json.dump({'datasets': subset_datasets}, f, indent=2)

print(f"Created subset manifest with {len(subset_datasets)} datasets.")
