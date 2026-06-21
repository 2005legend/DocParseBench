import difflib
import os
import json
import re

class QualityEvaluator:
    def __init__(self, manifest_path: str, results_dir: str):
        self.manifest_path = manifest_path
        self.results_dir = results_dir
        
    def _calculate_wer(self, ref: str, hyp: str) -> float:
        """Calculate an approximate Word Error Rate using difflib to prevent hanging on massive documents."""
        ref_words = ref.split()
        hyp_words = hyp.split()
        
        if len(ref_words) == 0:
            return float('inf') if len(hyp_words) > 0 else 0.0
            
        sm = difflib.SequenceMatcher(None, ref_words, hyp_words)
        # SequenceMatcher gives ratio = 2 * M / (T)
        # Error can be roughly approximated as 1 - ratio
        return 1.0 - sm.ratio()

    def _extract_tables(self, md_text: str):
        """Extract markdown tables. Returns a list of tables, where each table is a list of rows."""
        lines = md_text.split('\n')
        tables = []
        current_table = []
        
        for line in lines:
            if line.strip().startswith('|') and line.strip().endswith('|'):
                current_table.append(line.strip())
            else:
                if current_table:
                    # Filter out separator row (e.g. |---|---|)
                    clean_table = [row for row in current_table if not re.match(r'^\|[\s\-\|]+\|$', row)]
                    if len(clean_table) > 0:
                        tables.append(clean_table)
                    current_table = []
        if current_table:
            clean_table = [row for row in current_table if not re.match(r'^\|[\s\-\|]+\|$', row)]
            if len(clean_table) > 0:
                tables.append(clean_table)
                
        return tables
        
    def _evaluate_table_fidelity(self, ref_text: str, hyp_text: str) -> dict:
        ref_tables = self._extract_tables(ref_text)
        hyp_tables = self._extract_tables(hyp_text)
        
        if not ref_tables and not hyp_tables:
            return {"score": 1.0, "ref_count": 0, "hyp_count": 0}
        elif not ref_tables:
            return {"score": 0.0, "ref_count": 0, "hyp_count": len(hyp_tables)}
            
        # Very simplistic: ratio of table counts + ratio of total rows.
        ref_rows = sum(len(t) for t in ref_tables)
        hyp_rows = sum(len(t) for t in hyp_tables)
        
        count_score = min(len(hyp_tables) / len(ref_tables), 1.0)
        row_score = min(hyp_rows / ref_rows, 1.0) if ref_rows > 0 else 0.0
        
        return {
            "score": (count_score + row_score) / 2.0,
            "ref_count": len(ref_tables),
            "hyp_count": len(hyp_tables)
        }

    def _extract_headings(self, md_text: str):
        """Extract all markdown headings in order."""
        headings = []
        for line in md_text.split('\n'):
            match = re.match(r'^(#+)\s+(.*)', line.strip())
            if match:
                headings.append((len(match.group(1)), match.group(2).strip()))
        return headings

    def _evaluate_heading_hierarchy(self, ref_text: str, hyp_text: str) -> float:
        ref_headings = [h[0] for h in self._extract_headings(ref_text)]
        hyp_headings = [h[0] for h in self._extract_headings(hyp_text)]
        
        if not ref_headings and not hyp_headings:
            return 1.0
        if not ref_headings:
            return 0.0
            
        # LCS of heading levels
        sm = difflib.SequenceMatcher(None, ref_headings, hyp_headings)
        return sm.ratio()

    def _evaluate_reading_order(self, ref_text: str, hyp_text: str) -> float:
        """Proxy reading order by comparing sequences of paragraphs."""
        ref_paras = [p.strip() for p in ref_text.split('\n\n') if p.strip()]
        hyp_paras = [p.strip() for p in hyp_text.split('\n\n') if p.strip()]
        
        # We use a trick: take the first 20 characters of each paragraph to represent it
        # This allows fast sequence matching to see if paragraphs are out of order
        ref_hashes = [p[:20] for p in ref_paras]
        hyp_hashes = [p[:20] for p in hyp_paras]
        
        sm = difflib.SequenceMatcher(None, ref_hashes, hyp_hashes)
        return sm.ratio()

    def evaluate(self):
        with open(self.manifest_path, 'r') as f:
            manifest = json.load(f)
            
        quality_scores = {}
        
        for dataset in manifest.get('datasets', []):
            dataset_id = dataset['id']
            # Ground truth paths are relative to the manifest directory (e.g. 'ground_truth/filename.md')
            ground_truth_path = os.path.join(os.path.dirname(self.manifest_path), dataset.get('ground_truth_path', ''))
            
            if not os.path.exists(ground_truth_path):
                continue
                
            with open(ground_truth_path, 'r', encoding='utf-8') as f:
                gt_text = f.read()
                
            for filename in os.listdir(self.results_dir):
                if filename.startswith(dataset_id + "_") and filename.endswith(".md"):
                    parser_name = filename.replace(dataset_id + "_", "").replace(".md", "")
                    
                    if parser_name not in quality_scores:
                        quality_scores[parser_name] = []
                        
                    output_path = os.path.join(self.results_dir, filename)
                    with open(output_path, 'r', encoding='utf-8') as f:
                        output_text = f.read()
                        
                    wer = self._calculate_wer(gt_text, output_text)
                    table_metrics = self._evaluate_table_fidelity(gt_text, output_text)
                    heading_score = self._evaluate_heading_hierarchy(gt_text, output_text)
                    reading_order_score = self._evaluate_reading_order(gt_text, output_text)
                    
                    quality_scores[parser_name].append({
                        'dataset_id': dataset_id,
                        'wer': wer,
                        'table_fidelity': table_metrics['score'],
                        'heading_hierarchy': heading_score,
                        'reading_order': reading_order_score
                    })
                    
        # Aggregate scores
        summary = {}
        for parser, scores in quality_scores.items():
            if not scores:
                continue
            summary[parser] = {
                'avg_wer': sum(s['wer'] for s in scores) / len(scores),
                'avg_table_fidelity': sum(s['table_fidelity'] for s in scores) / len(scores),
                'avg_heading_hierarchy': sum(s['heading_hierarchy'] for s in scores) / len(scores),
                'avg_reading_order': sum(s['reading_order'] for s in scores) / len(scores)
            }
            
        return summary
