import json
import os
import sys

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.performance import PerformanceEvaluator
from metrics.quality import QualityEvaluator

class ReportBuilder:
    def __init__(self, results_path: str, manifest_path: str, output_dir: str):
        self.results_path = results_path
        self.manifest_path = manifest_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_markdown(self):
        perf_evaluator = PerformanceEvaluator(self.results_path)
        perf_summary = perf_evaluator.evaluate()
        
        qual_evaluator = QualityEvaluator(self.manifest_path, os.path.dirname(self.results_path))
        qual_summary = qual_evaluator.evaluate()
        
        md_content = "# DocParseBench Results\n\n"
        
        md_content += "## Overall Summary\n\n"
        md_content += "| Parser | Pages/Sec | Peak RAM (MB) | WER | Table Fidelity | Heading Score | Reading Order |\n"
        md_content += "|---|---|---|---|---|---|---|\n"
        
        # Combine metrics
        all_parsers = set(list(perf_summary.keys()) + list(qual_summary.keys()))
        
        for parser in all_parsers:
            p_stats = perf_summary.get(parser, {})
            q_stats = qual_summary.get(parser, {})
            
            pages_sec = p_stats.get('overall_pages_per_sec', 0)
            peak_ram = p_stats.get('peak_ram_max', 0)
            
            wer = f"{q_stats.get('avg_wer', 0):.3f}" if 'avg_wer' in q_stats else "N/A"
            tab_fid = f"{q_stats.get('avg_table_fidelity', 0):.2%}" if 'avg_table_fidelity' in q_stats else "N/A"
            head_scr = f"{q_stats.get('avg_heading_hierarchy', 0):.2%}" if 'avg_heading_hierarchy' in q_stats else "N/A"
            read_ord = f"{q_stats.get('avg_reading_order', 0):.2%}" if 'avg_reading_order' in q_stats else "N/A"
            
            md_content += f"| {parser} | {pages_sec:.2f} | {peak_ram:.2f} | {wer} | {tab_fid} | {head_scr} | {read_ord} |\n"
            
        md_path = os.path.join(self.output_dir, 'report.md')
        with open(md_path, 'w') as f:
            f.write(md_content)
            
        return md_path

if __name__ == '__main__':
    builder = ReportBuilder(
        results_path='results/benchmark_results.json',
        manifest_path='datasets/manifest.json',
        output_dir='reports'
    )
    if os.path.exists('results/benchmark_results.json'):
        md_file = builder.generate_markdown()
        print(f"Report generated: {md_file}")
    else:
        print("No results file found. Run benchmarks/runner.py first.")
