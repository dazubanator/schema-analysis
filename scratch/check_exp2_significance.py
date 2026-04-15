import os
import pandas as pd
import numpy as np
from schema_analysis.tube import load
from schema_analysis.tube.compute import compute_d

def analyze_variances():
    # Load data with standard cleanup
    s = load(clean=True).validate_trials(min=3, max=40).balance().select_trials('valid == True')
    
    print(" face_id | exp_num |   N |    D    |    SD   |    SE   |    p")
    print("-" * 65)
    
    # Analyze ID008 (Exp 1)
    e1 = s.select(exp_num=1)
    for ec in [False, True]:
        label = "ID008-Open" if not ec else "ID008-Closed"
        res = compute_d(e1, 'eyes_covered', ec)
        raw = res['raw']
        sd = np.std(raw)
        print(f"{label:12} | 1 | {res['N']:3d} | {res['D']:+.3f} | {sd:.3f} | {res['SE']:.3f} | {res['p']:.4f}")

    # Analyze ID015 and ID017 (Exp 2)
    e2 = s.select(exp_num=2)
    for fid in ['ID015', 'ID017']:
        res = compute_d(e2, 'face_id', fid)
        raw = res['raw']
        sd = np.std(raw)
        print(f"{fid:12} | 2 | {res['N']:3d} | {res['D']:+.3f} | {sd:.3f} | {res['SE']:.3f} | {res['p']:.4f}")

if __name__ == "__main__":
    analyze_variances()
