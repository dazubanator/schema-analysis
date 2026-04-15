import os
import pandas as pd
import numpy as np
from scipy import stats
from schema_analysis.tube import load

def check_global_effect():
    # Load all valid trials
    s = load(clean=True).validate_trials(min=3, max=40).balance().select_trials('valid == True')
    
    # Select all "Eyes Open" / "Gaze Present" cases
    # Exp 1 Open + Exp 2 Faces
    e1_open = s.select(exp_num=1).select_trials('eyes_covered == False')
    e2 = s.select(exp_num=2)
    
    all_gaze_sessions = list(e1_open) + list(e2)
    
    d_vals = []
    for sess in all_gaze_sessions:
        tw = sess.trials[sess.trials['towards_away'] == 'towards']['angle']
        aw = sess.trials[sess.trials['towards_away'] == 'away']['angle']
        if len(tw) > 0 and len(aw) > 0:
            d_vals.append(tw.mean() - aw.mean())
            
    d_vals = np.array(d_vals)
    t, p = stats.ttest_1samp(d_vals, 0)
    
    print(f"GLOBAL GAZE EFFECT (All Open-Eye Sessions)")
    print(f"Total N : {len(d_vals)}")
    print(f"Mean D  : {d_vals.mean():+.4f}°")
    print(f"SD      : {d_vals.std():.4f}")
    print(f"SE      : {d_vals.std()/np.sqrt(len(d_vals)):.4f}")
    print(f"t-stat  : {t:.4f}")
    print(f"p-value : {p:.10f}")

if __name__ == "__main__":
    check_global_effect()
