import json

class PerformanceEvaluator:
    def __init__(self, results_path: str):
        self.results_path = results_path
        
    def evaluate(self):
        with open(self.results_path, 'r') as f:
            data = json.load(f)
            
        summary = {}
        
        for dataset_id, dataset_info in data.items():
            pages = dataset_info['pages']
            runs = dataset_info['runs']
            
            for parser, metrics in runs.items():
                if parser not in summary:
                    summary[parser] = {
                        'total_time': 0,
                        'total_pages': 0,
                        'peak_ram_max': 0,
                        'avg_cpu_avg': [],
                        'success_count': 0,
                        'fail_count': 0
                    }
                    
                if metrics['status'] == 'success':
                    summary[parser]['success_count'] += 1
                    summary[parser]['total_time'] += metrics['execution_time_seconds']
                    summary[parser]['total_pages'] += pages
                    
                    if metrics['peak_ram_mb'] > summary[parser]['peak_ram_max']:
                        summary[parser]['peak_ram_max'] = metrics['peak_ram_mb']
                        
                    summary[parser]['avg_cpu_avg'].append(metrics['avg_cpu_percent'])
                else:
                    summary[parser]['fail_count'] += 1
                    
        # Compute final aggregates
        for parser, stats in summary.items():
            stats['overall_pages_per_sec'] = stats['total_pages'] / stats['total_time'] if stats['total_time'] > 0 else 0
            stats['overall_avg_cpu'] = sum(stats['avg_cpu_avg']) / len(stats['avg_cpu_avg']) if stats['avg_cpu_avg'] else 0
            
        return summary
