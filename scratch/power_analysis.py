from scipy import stats
import numpy as np

def power_analysis(d, sd, alpha=0.05, target_power=0.80):
    """How many subjects are needed to reach target power?"""
    # Standard effect size (Cohen's d)
    cohens_d = d / sd
    
    # Simple power calculation for one-sample t-test
    # This is a rough estimate
    n_needed = ((stats.norm.ppf(1 - alpha/2) + stats.norm.ppf(target_power)) / cohens_d)**2
    return int(np.ceil(n_needed))

# ID008 Open (Already significant)
d_lady = 0.237
sd_lady = 2.749
n_lady = 577

# ID017 (High threat)
d_man = 0.157
sd_man = 3.266
n_man = 254

print(f"ID008 (Lady) Cohen's d: {d_lady/sd_lady:.4f}")
print(f"ID017 (Man)  Cohen's d: {d_man/sd_man:.4f}")
print("-" * 30)
print(f"To reach p < 0.05 with 80% power:")
print(f"Lady (ID008) would need N = {power_analysis(d_lady, sd_lady)}")
print(f"Man  (ID017) would need N = {power_analysis(d_man, sd_man)}")
