import difflib
import os

def calculate_diff_and_similarity(baseline_file, target_file, output_diff_file):
    if not os.path.exists(baseline_file) or not os.path.exists(target_file):
        return "N/A (Missing File)"
        
    with open(baseline_file, 'r', encoding='utf-8') as f:
        baseline_text = f.readlines()
        
    with open(target_file, 'r', encoding='utf-8') as f:
        target_text = f.readlines()
        
    # Calculate similarity ratio
    matcher = difflib.SequenceMatcher(None, "".join(baseline_text), "".join(target_text))
    similarity = matcher.ratio() * 100
    
    # Generate unified diff
    diff = difflib.unified_diff(
        baseline_text, 
        target_text, 
        fromfile='Baseline (Docling)', 
        tofile='Target', 
        n=1
    )
    
    with open(output_diff_file, 'w', encoding='utf-8') as f:
        f.writelines(diff)
        
    return f"{similarity:.2f}%"
