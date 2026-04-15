#!/usr/bin/env python3
"""
Unpaired between-subject analysis of Exp 2 (threat faces).

Shows the full (unpaired) distribution of individual D-values for each
face identity (ID015 low-threat, ID017 high-threat), styled after
within_subject_exp2.png.

Panels:
  A. Bar chart (mean D ± SE) for each face — all participants (unpaired)
  B. Strip / jitter plot of individual D distributions per face
  C. Direct between-group comparison (Welch's t-test on D_ID017 vs D_ID015)

Run:  python between_subject_exp2.py
Output: symposium/between_subject_exp2.png
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Calibri', 'Arial', 'DejaVu Sans']
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from schema_analysis.tube import load
from schema_analysis.tube.treatments import resolve as resolve_treatment

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(ROOT, 'symposium', 'between_subject_exp2.png')

# ── Load & clean (identical pipeline to within_subject_exp2.py) ───────────────

ANGLE_LO, ANGLE_HI = 3, 40
BOT_CLEAN = True

s = load(clean=False)
s = s.exclude_face('ID030')
if BOT_CLEAN:
    s = s.remove_bad_sessions()
s = s.validate_trials(min=ANGLE_LO, max=ANGLE_HI)
s = s.balance()
s = s.select_trials('valid == True').select(exp_num=2)

trial_frames = []
for sess in s:
    t = sess.trials[['face_id', 'towards_away', 'angle']].copy()
    t['subject_id'] = sess.session_id
    trial_frames.append(t)
valid = pd.concat(trial_frames, ignore_index=True)

TARGET_FACES = ['ID015', 'ID017']
valid = valid[valid['face_id'].isin(TARGET_FACES)].copy()
faces = [f for f in TARGET_FACES if f in valid['face_id'].unique()]
LOW_FACE, HIGH_FACE = 'ID015', 'ID017'

# ── Compute per-participant D for each face (unpaired — all participants) ────

rows = []
for uid, udata in valid.groupby('subject_id'):
    for fid in faces:
        sub = udata[udata['face_id'] == fid]
        tw = sub[sub['towards_away'] == 'towards']['angle']
        aw = sub[sub['towards_away'] == 'away']['angle']
        if len(tw) > 0 and len(aw) > 0:
            rows.append({'subject_id': uid, 'face_id': fid,
                         'D': float(tw.mean() - aw.mean())})

indiv = pd.DataFrame(rows)

# ── Per-group statistics (unpaired one-sample t vs 0) ────────────────────────

group_stats = {}
for fid in faces:
    d_vals = indiv.loc[indiv['face_id'] == fid, 'D'].values
    t, p = stats.ttest_1samp(d_vals, 0)
    group_stats[fid] = dict(D=d_vals.mean(), SE=d_vals.std() / np.sqrt(len(d_vals)),
                             t=t, p=p, N=len(d_vals), raw=d_vals)

# ── Between-group Welch's t-test (D_high vs D_low) ──────────────────────────

d_low  = group_stats[LOW_FACE]['raw']
d_high = group_stats[HIGH_FACE]['raw']
t_welch, p_welch = stats.ttest_ind(d_high, d_low, equal_var=False)
mean_diff = d_high.mean() - d_low.mean()
se_diff   = np.sqrt(d_high.std()**2 / len(d_high) + d_low.std()**2 / len(d_low))
df_welch  = (
    (d_high.std()**2 / len(d_high) + d_low.std()**2 / len(d_low))**2
    / (
        (d_high.std()**2 / len(d_high))**2 / (len(d_high) - 1)
      + (d_low.std()**2  / len(d_low))**2  / (len(d_low)  - 1)
    )
)

between = dict(D=mean_diff, SE=se_diff, t=t_welch, p=p_welch,
               df=int(df_welch), N_low=len(d_low), N_high=len(d_high))

# ── Console summary ──────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("BETWEEN-SUBJECT ANALYSIS - Exp 2 (ID015 vs ID017, unpaired)")
print("=" * 70)
print(f"\nAngle cutoffs: {ANGLE_LO}° < angle < {ANGLE_HI}°")
print("\n-- One-sample t-tests (D vs 0, unpaired) --")
for fid in faces:
    r = group_stats[fid]
    info = resolve_treatment(fid, False)
    sig = '*' if r['p'] < .05 else ''
    print(f"  {info['label']:25s}  N={r['N']:3d}  D={r['D']:+.4f}°  "
          f"SE={r['SE']:.4f}  t({r['N']-1})={r['t']:+.3f}  p={r['p']:.4f} {sig}")

print(f"\n-- Welch's independent-samples t-test (D_high - D_low) --")
print(f"  Mean diff = {between['D']:+.4f}°  SE = {between['SE']:.4f}")
print(f"  t({between['df']}) = {between['t']:+.3f}  p = {between['p']:.4f}")
print(f"  N_low = {between['N_low']}  N_high = {between['N_high']}")

# ── Plot helpers ─────────────────────────────────────────────────────────────

IMG_DIR = os.path.join(ROOT, 'data', 'tube', 'images')

def add_face_image(ax, fid, x_pos, y_axes=0.88):
    info = resolve_treatment(fid, False)
    img_path = info.get('image_path')
    if img_path and os.path.exists(img_path):
        img = plt.imread(img_path)
        h = img.shape[0]
        zoom = 0.16 * (500 / h)
        oi = OffsetImage(img, zoom=zoom)
        ab = AnnotationBbox(oi, (x_pos, y_axes),
                            xycoords=('data', 'axes fraction'),
                            box_alignment=(0.5, 0.5),
                            frameon=False, annotation_clip=False)
        ax.add_artist(ab)

rng = np.random.default_rng(42)

def jitter(n, width=0.18):
    return rng.uniform(-width, width, size=n)

# ── Figure layout ─────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(24, 13))
gs = gridspec.GridSpec(1, 3, width_ratios=[1.1, 1.2, 1.0],
                       left=0.08, right=0.94, top=0.75, bottom=0.25,
                       wspace=0.52)

# Simplified, human-reader title (black, bold, large)
fig.suptitle(
    "Social Threat Test: Does threat level change the gaze-push?",
    fontsize=34, fontweight='bold', color='black', y=0.97)

# Red caption (smaller, below title)
fig.text(0.5, 0.90,
         f'Unpaired Analysis of {resolve_treatment(LOW_FACE, False)["label"]} vs. '
         f'{resolve_treatment(HIGH_FACE, False)["label"]} | Angle cutoff {ANGLE_LO}° - {ANGLE_HI}° | * p < 0.05',
         ha='center', va='top', fontsize=26, color='#E84A30')

COLORS = {fid: resolve_treatment(fid, False)['color'] for fid in faces}

# ── Panel A: Bar chart (mean D ± SE per face, all participants) ───────────────

ax_bar = fig.add_subplot(gs[0])
ylim_vals = []

for i, fid in enumerate(faces):
    r = group_stats[fid]
    c = COLORS[fid]
    ax_bar.bar(i, r['D'], 0.55, color=c, edgecolor='black',
               linewidth=0.8, alpha=0.85)
    ax_bar.errorbar(i, r['D'], yerr=r['SE'], capsize=6,
                    color='black', linewidth=1.5)
    if r['p'] < .05:
        ax_bar.text(i, r['D'] + r['SE'] + 0.03, '*', ha='center', va='bottom', fontsize=48, fontweight='bold')
    ax_bar.text(i, -0.15,
                f"p = {r['p']:.3f}\nN = {r['N']}",
                ha='center', va='top', fontsize=30, color='black',
                transform=ax_bar.get_xaxis_transform(), clip_on=False)
    ylim_vals.append(abs(r['D']) + r['SE'])
    add_face_image(ax_bar, fid, i)

ylim = max(ylim_vals) + 0.07   # tight zoom — just enough for bars + SE + headroom
ax_bar.set_ylim(-ylim, ylim)
ax_bar.axhline(0, color='black', linewidth=0.8)
ax_bar.set_xticks(range(len(faces)))
ax_bar.set_xticklabels([resolve_treatment(f, False)['label'].replace('\n', ' ')
                         for f in faces], fontsize=28)
ax_bar.set_ylabel('D (degrees)', fontsize=28)
ax_bar.set_title('A. Mean D per Face\n(between-subject, unpaired)', fontsize=32, fontweight='bold', pad=16)
ax_bar.tick_params(labelsize=26)
ax_bar.spines['top'].set_visible(False)
ax_bar.spines['right'].set_visible(False)

# ── Panel B: Strip / jitter plot of individual D distributions ────────────────

ax_strip = fig.add_subplot(gs[1])

for i, fid in enumerate(faces):
    r = group_stats[fid]
    c = COLORS[fid]
    d_vals = r['raw']
    x_jit = i + jitter(len(d_vals), width=0.20)

    ax_strip.scatter(x_jit, d_vals, s=12, color=c, alpha=0.35,
                     linewidths=0, zorder=2)

    # Median line
    ax_strip.plot([i - 0.22, i + 0.22], [np.median(d_vals)] * 2,
                  color='black', linewidth=2.0, zorder=4)
    # Mean ± SE diamond
    ax_strip.plot(i, r['D'], 'D', color=c, markeredgecolor='black',
                  markersize=11, zorder=5)
    ax_strip.plot([i, i], [r['D'] - r['SE'], r['D'] + r['SE']],
                  color='black', linewidth=2.2, zorder=4)

    # Annotation box
    ax_strip.text(i, -0.15,
                  f"p = {r['p']:.3f}\nN = {r['N']}",
                  ha='center', va='top', fontsize=30, color='black',
                  transform=ax_strip.get_xaxis_transform(), clip_on=False)
    add_face_image(ax_strip, fid, i)

ax_strip.axhline(0, color='black', linewidth=0.8)
ax_strip.set_ylim(-5, 5)  # Zoom to ±5° to show the dense cluster near zero
ax_strip.set_xticks(range(len(faces)))
ax_strip.set_xticklabels([resolve_treatment(f, False)['label'].replace('\n', ' ')
                            for f in faces], fontsize=28)
ax_strip.set_ylabel('D per participant (degrees)', fontsize=28)
ax_strip.set_title('B. Individual D distributions\n(Diamond = mean ± SE, — = median)', fontsize=32, fontweight='bold', pad=16)
ax_strip.tick_params(labelsize=26)
ax_strip.spines['top'].set_visible(False)
ax_strip.spines['right'].set_visible(False)

# ── Panel C: Between-group difference histogram (Welch) ───────────────────────

ax_diff = fig.add_subplot(gs[2])

# Bootstrap the difference distribution for illustration
n_boot = 5000
boot_diffs = np.array([
    rng.choice(d_high, len(d_high), replace=True).mean()
    - rng.choice(d_low,  len(d_low),  replace=True).mean()
    for _ in range(n_boot)
])

ax_diff.hist(boot_diffs, bins=50, orientation='horizontal',
             color='#C06040', alpha=0.30, edgecolor='white',
             linewidth=0.4, density=True, label='Bootstrap dist.')

ax_diff.axhline(0, color='black', linewidth=0.8)
ax_diff.axhline(mean_diff, color='#C06040', linewidth=1.4,
                linestyle='--', alpha=0.7)

x_c = ax_diff.get_xlim()[1] * 0.55
ax_diff.plot(x_c, mean_diff, 'D', color='#C06040',
             markeredgecolor='black', markersize=14, zorder=5)
ax_diff.plot([x_c, x_c], [mean_diff - se_diff, mean_diff + se_diff],
             color='black', linewidth=2.5, zorder=4)
ax_diff.plot([x_c - 0.008, x_c + 0.008],
             [mean_diff - se_diff, mean_diff - se_diff],
             color='black', linewidth=2.5, zorder=4)
ax_diff.plot([x_c - 0.008, x_c + 0.008],
             [mean_diff + se_diff, mean_diff + se_diff],
             color='black', linewidth=2.5, zorder=4)


# Format txt to be shorter vertically
txt = (f"Diff = {mean_diff:+.3f}° | p = {between['p']:.3f}\n"
       f"t({between['df']}) = {between['t']:+.2f} | N = {between['N_low']}")
ax_diff.text(0.5, -0.14, txt, ha='center', va='top', fontsize=30, color='black',
             transform=ax_diff.transAxes, clip_on=False)

d_span = max(abs(boot_diffs.min()), abs(boot_diffs.max())) * 1.15
d_span = max(d_span, abs(mean_diff) + se_diff + 0.4)
ax_diff.set_ylim(-d_span, d_span)
ax_diff.set_ylabel(f'D difference: {HIGH_FACE} − {LOW_FACE} (°)', fontsize=28)
ax_diff.set_xlabel('Bootstrap density', fontsize=28)
ax_diff.set_title(f'C. Group difference\n(Welch\'s independent t-test)', fontsize=32, fontweight='bold')
ax_diff.tick_params(labelsize=26)
ax_diff.spines['top'].set_visible(False)
ax_diff.spines['right'].set_visible(False)

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=200, bbox_inches='tight', facecolor='white')
print(f"\nSaved -> {OUT_PATH}")
plt.close()
