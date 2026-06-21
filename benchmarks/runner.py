import json
import os
import subprocess
import time
import argparse
from profiler import Profiler

def load_manifest(manifest_path):
    with open(manifest_path, 'r') as f:
        return json.load(f)

def run_benchmark(manifest_path, parsers, output_dir):
    manifest = load_manifest(manifest_path)
    datasets = manifest.get('datasets', [])
    
    results = {}
    
    os.makedirs(output_dir, exist_ok=True)
    
    for dataset in datasets:
        dataset_id = dataset['id']
        file_path = os.path.join(os.path.dirname(manifest_path), '..', dataset['file_path'])
        file_path = os.path.abspath(file_path)
        
        results[dataset_id] = {'pages': dataset['pages'], 'category': dataset['category'], 'runs': {}}
        
        for parser in parsers:
            print(f"Running {parser} on {dataset_id}...")
            
            output_file = os.path.join(output_dir, f"{dataset_id}_{parser}.md")
            
            # Start the parser script
            script_path = os.path.join(os.path.dirname(__file__), 'run_parser.py')
            cmd = ['python', script_path, '--parser', parser, '--input', file_path, '--output', output_file]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Start profiling
            profiler = Profiler(pid=process.pid, interval=0.1)
            profiler.start()
            
            # Wait for completion
            stdout, stderr = process.communicate()
            
            # Stop profiling
            metrics = profiler.stop()
            
            # Extract execution time from stdout
            exec_time = 0.0
            for line in stdout.split('\n'):
                if line.startswith("DONE|"):
                    exec_time = float(line.split('|')[1])
                    
            if process.returncode != 0:
                print(f"  Error running {parser}: {stderr}")
                status = "failed"
            else:
                status = "success"
                
            # File size
            out_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
            
            run_result = {
                'status': status,
                'execution_time_seconds': exec_time,
                'pages_per_second': dataset['pages'] / exec_time if exec_time > 0 else 0,
                'peak_ram_mb': metrics['peak_ram_mb'],
                'avg_cpu_percent': metrics['avg_cpu_percent'],
                'output_size_bytes': out_size,
                'error_log': stderr if status == 'failed' else None
            }
            
            results[dataset_id]['runs'][parser] = run_result
            print(f"  Completed in {exec_time:.2f}s, Peak RAM: {metrics['peak_ram_mb']:.2f}MB")
            
    # Save results
    results_file = os.path.join(output_dir, 'benchmark_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Benchmark complete. Results saved to {results_file}")
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=str, default='datasets/manifest.json')
    parser.add_argument('--output-dir', type=str, default='results')
    parser.add_argument('--parsers', nargs='+', default=['liteparse', 'docling', 'pymupdf', 'llamaparse'])
    args = parser.parse_args()
    
    # Ensure manifest path is absolute or relative to root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    manifest_full = os.path.join(base_dir, args.manifest)
    out_full = os.path.join(base_dir, args.output_dir)
    
    run_benchmark(manifest_full, args.parsers, out_full)
