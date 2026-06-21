import json
import os
import subprocess
from benchmarks.profiler import Profiler

manifest_path = r'c:\Users\USER\Downloads\ocr comparison\DocParseBench\datasets\manifest_subset.json'
results_path = r'c:\Users\USER\Downloads\ocr comparison\DocParseBench\results\benchmark_results.json'

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

with open(results_path, 'r') as f:
    results = json.load(f)

parser = 'liteparse'
output_dir = r'c:\Users\USER\Downloads\ocr comparison\DocParseBench\results'
script_path = r'c:\Users\USER\Downloads\ocr comparison\DocParseBench\benchmarks\run_parser.py'

for dataset in manifest['datasets']:
    dataset_id = dataset['id']
    file_path = os.path.join(os.path.dirname(manifest_path), dataset['file_path'])
    output_file = os.path.join(output_dir, f"{dataset_id}_{parser}.md")
    
    print(f"Running {parser} on {dataset_id}...")
    cmd = ['python', script_path, '--parser', parser, '--input', file_path, '--output', output_file]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    profiler = Profiler(pid=process.pid, interval=0.1)
    profiler.start()
    stdout, stderr = process.communicate()
    metrics = profiler.stop()
    
    exec_time = 0.0
    for line in stdout.split('\n'):
        if line.startswith("DONE|"):
            exec_time = float(line.split('|')[1])
            
    status = "failed" if process.returncode != 0 else "success"
    out_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
    
    if dataset_id not in results:
        results[dataset_id] = {'pages': dataset['pages'], 'category': dataset['category'], 'runs': {}}
        
    results[dataset_id]['runs'][parser] = {
        'status': status,
        'execution_time_seconds': exec_time,
        'pages_per_second': dataset['pages'] / exec_time if exec_time > 0 else 0,
        'peak_ram_mb': metrics['peak_ram_mb'],
        'avg_cpu_percent': metrics['avg_cpu_percent'],
        'output_size_bytes': out_size,
        'error_log': stderr if status == 'failed' else None
    }
    print(f"Completed {dataset_id} in {exec_time:.2f}s, RAM: {metrics['peak_ram_mb']:.2f}MB, error={stderr}")

with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)

print("Liteparse update complete!")
