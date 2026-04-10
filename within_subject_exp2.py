#!/usr/bin/env python3
"""
Within-subject re-analysis of Exp 2 (threat faces).

Old approach:  Treat each face as a separate group → between-subject t-test of D vs 0.
New approach:  Each participant contributes D_per_face for EVERY face they saw.
               (1) One-sample t-test of each face's D vs 0 (same test, fuller data)
               (2) Paired t-test of D_high − D_low → direct threat modulation test,
                   eliminates between-subject noise.

Run:  python within_subject_exp2.py
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

# ── Load & clean ──────────────────────────────────────────────────────────────

ANGLE_LO, ANGLE_HI = 3, 40
BOT_CLEAN = True

# Match tube_analysis.py pipeline so subject pool is comparable to D-bar figure.
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
    # Stable participant key: session_id from loader/CSV-JSON merge path.
    t['subject_id'] = sess.session_id
    trial_frames.append(t)
valid = pd.concat(trial_frames, ignore_index=True)

# Restrict analysis to canonical Exp2 pair only.
TARGET_FACES = ['ID015', 'ID017']
valid = valid[valid['face_id'].isin(TARGET_FACES)].copy()
faces = [f for f in TARGET_FACES if f in set(valid['face_id'].unique())]
LOW_FACE = 'ID015'
HIGH_FACE = 'ID017'

# ── Compute per-participant D for each face ──────────────────────────────────

rows = []
for uid, udata in valid.groupby('subject_id'):
    row = {'subject_id': uid}
    for fid in faces:
        sub = udata[udata['face_id'] == fid]
        tw = sub[sub['towards_away'] == 'towards']['angle']
        aw = sub[sub['towards_away'] == 'away']['angle']
        if len(tw) > 0 and len(aw) > 0:
            row[f'D_{fid}'] = tw.mean() - aw.mean()
        else:
            row[f'D_{fid}'] = np.nan
    rows.append(row)

ws = pd.DataFrame(rows)

# ── OLD (between-subject): includes anyone with at least one face ────────────

old_results = {}
for fid in faces:
    col = f'D_{fid}'
    d_vals = ws[col].dropna().values
    if len(d_vals) > 1:
        t, p = stats.ttest_1samp(d_vals, 0)
        old_results[fid] = dict(
            D=d_vals.mean(), SE=d_vals.std() / np.sqrt(len(d_vals)),
            t=t, p=p, N=len(d_vals),
        )

# ── NEW (within-subject): only participants with ALL faces ───────────────────

ws_complete = ws.dropna()
N_paired = len(ws_complete)

new_results = {}
for fid in faces:
    col = f'D_{fid}'
    d_vals = ws_complete[col].values
    t, p = stats.ttest_1samp(d_vals, 0)
    new_results[fid] = dict(
        D=d_vals.mean(), SE=d_vals.std() / np.sqrt(len(d_vals)),
        t=t, p=p, N=len(d_vals),
    )

# Paired difference: high − low
d_high = ws_complete[f'D_{HIGH_FACE}'].values
d_low = ws_complete[f'D_{LOW_FACE}'].values
d_diff = d_high - d_low
t_paired, p_paired = stats.ttest_rel(d_high, d_low)
paired = dict(
    D=d_diff.mean(), SE=d_diff.std() / np.sqrt(len(d_diff)),
    SD=d_diff.std(), t=t_paired, p=p_paired, N=N_paired,
)

# ── Console summary ──────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("WITHIN-SUBJECT RE-ANALYSIS - Exp 2 (ID015 vs ID017)")
print("=" * 70)

print(f"\nAngle cutoffs: {ANGLE_LO}° < angle < {ANGLE_HI}°")
print(f"Participants with both faces: {N_paired}")

print("\n-- One-sample t-tests (D vs 0) --")
for fid in faces:
    r = new_results[fid]
    t_info = resolve_treatment(fid, False)
    sig = '*' if r['p'] < .05 else ''
    print(f"  {t_info['label']:25s}  N={r['N']:3d}  D={r['D']:+.4f}°  SE={r['SE']:.4f}  "
          f"t({r['N']-1})={r['t']:+.3f}  p={r['p']:.4f} {sig}")

print("\n-- Paired t-test (threat modulation) --")
print(f"  D_{HIGH_FACE} - D_{LOW_FACE} = {paired['D']:+.4f}°  SE={paired['SE']:.4f}")
print(f"  Within-subject SD = {paired['SD']:.4f}")
print(f"  t({paired['N']-1}) = {paired['t']:+.3f}  p = {paired['p']:.4f}")

print("\n-- Comparison: old between-subject SEs --")
for fid in faces:
    o = old_results.get(fid, {})
    n = new_results[fid]
    if o:
        reduction = (1 - n['SE'] / o['SE']) * 100
        print(f"  {fid}:  SE_old={o['SE']:.4f} (N={o['N']})  ->  SE_new={n['SE']:.4f} (N={n['N']})  "
              f"({reduction:+.1f}%)")

# ── Plot ─────────────────────────────────────────────────────────────────────

IMG_DIR = os.path.join(ROOT, 'data', 'tube', 'images')

fig = plt.figure(figsize=(24, 11))
gs_top = gridspec.GridSpec(1, 3, width_ratios=[1.1, 1.1, 1.0],
                            left=0.08, right=0.94, top=0.82, bottom=0.25,
                            wspace=0.50)


def add_face_images(ax, face_ids, y_axes=0.86):
    """Place treatment face thumbnails above bars (D-bar style)."""
    for i, fid in enumerate(face_ids):
        t_info = resolve_treatment(fid, False)
        img_path = t_info.get('image_path')
        if img_path and os.path.exists(img_path):
            img = plt.imread(img_path)
            h, _ = img.shape[:2]
            target_zoom = 0.16 * (500 / h)
            oi = OffsetImage(img, zoom=target_zoom)
            ab = AnnotationBbox(
                oi,
                (i, y_axes),
                xycoords=('data', 'axes fraction'),
                box_alignment=(0.5, 0.5),
                frameon=False,
                annotation_clip=False,
            )
            ax.add_artist(ab)

# ── Panel A: Between-subject (old) ──────────────────────────────────────────
ax_old = fig.add_subplot(gs_top[0])
for i, fid in enumerate(faces):
    r = old_results[fid]
    t_info = resolve_treatment(fid, False)
    ax_old.bar(i, r['D'], 0.55, color=t_info['color'], edgecolor='black', linewidth=0.8, alpha=0.5)
    ax_old.errorbar(i, r['D'], yerr=r['SE'], capsize=6, color='black', linewidth=1.5)
    if r['p'] < .05:
        ax_old.text(i, r['D'] + r['SE'] + 0.02, '*', ha='center', va='bottom', fontsize=48, fontweight='bold')
    ax_old.text(i, -0.15, f"p={r['p']:.3f}\nN={r['N']}", ha='center', va='top', fontsize=30, color='black',
                transform=ax_old.get_xaxis_transform(), clip_on=False)

ax_old.axhline(0, color='black', linewidth=0.8)
ax_old.set_xticks(range(len(faces)))
ax_old.set_xticklabels([resolve_treatment(f, False)['label'].replace('\n', ' ') for f in faces], fontsize=28)
ax_old.set_ylabel('D (degrees)', fontsize=28)
ax_old.set_title('A. Between-subject\n(old analysis)', fontsize=32, fontweight='bold', pad=16)
ax_old.tick_params(labelsize=26)
ax_old.spines['top'].set_visible(False)
ax_old.spines['right'].set_visible(False)
add_face_images(ax_old, faces)

# ── Panel B: Within-subject (new) ───────────────────────────────────────────
ax_new = fig.add_subplot(gs_top[1])
for i, fid in enumerate(faces):
    r = new_results[fid]
    t_info = resolve_treatment(fid, False)
    ax_new.bar(i, r['D'], 0.55, color=t_info['color'], edgecolor='black', linewidth=0.8)
    ax_new.errorbar(i, r['D'], yerr=r['SE'], capsize=6, color='black', linewidth=1.5)
    if r['p'] < .05:
        ax_new.text(i, r['D'] + r['SE'] + 0.02, '*', ha='center', va='bottom', fontsize=48, fontweight='bold')
    ax_new.text(i, -0.15, f"p={r['p']:.3f}\nN={r['N']}", ha='center', va='top', fontsize=30, color='black',
                transform=ax_new.get_xaxis_transform(), clip_on=False)
 
ax_new.axhline(0, color='black', linewidth=0.8)
ax_new.set_xticks(range(len(faces)))
ax_new.set_xticklabels([resolve_treatment(f, False)['label'].replace('\n', ' ') for f in faces], fontsize=28)
ax_new.set_title('B. Within-subject\n(full sample cleanup)', fontsize=32, fontweight='bold', pad=16)
ax_new.tick_params(labelsize=26)
ax_new.spines['top'].set_visible(False)
ax_new.spines['right'].set_visible(False)
add_face_images(ax_new, faces)

# Match y-axes
all_d = [old_results[f]['D'] for f in faces] + [new_results[f]['D'] for f in faces]
all_se = [old_results[f]['SE'] for f in faces] + [new_results[f]['SE'] for f in faces]
ylim = max(abs(d) + se for d, se in zip(all_d, all_se)) + 0.15
ylim = max(ylim, abs(paired['D']) + paired['SE'] + 0.15)
for ax in [ax_old, ax_new]:
    ax.set_ylim(-ylim, ylim)

# ── Panel C: Paired difference + distribution ────────────────────────────────
ax_paired = fig.add_subplot(gs_top[2])

# Histogram of individual paired differences.
ax_paired.hist(
    d_diff,
    bins='fd',  # data-adaptive bin width (Freedman-Diaconis)
    orientation='horizontal',
    color='#C06040',
    alpha=0.3,
    edgecolor='white',
    linewidth=0.5,
    density=True,
)
# Mean + SE bar
ax_paired.axhline(0, color='black', linewidth=0.8)
x_center = ax_paired.get_xlim()[1] * 0.5
ax_paired.plot(x_center, paired['D'], 'D', color='#C06040', markersize=14, zorder=5)
ax_paired.plot([x_center, x_center],
               [paired['D'] - paired['SE'], paired['D'] + paired['SE']],
               color='black', linewidth=2.5, zorder=4)
ax_paired.plot([x_center - 0.01, x_center + 0.01],
               [paired['D'] - paired['SE'], paired['D'] - paired['SE']],
               color='black', linewidth=2.5, zorder=4)
ax_paired.plot([x_center - 0.01, x_center + 0.01],
               [paired['D'] + paired['SE'], paired['D'] + paired['SE']],
               color='black', linewidth=2.5, zorder=4)

ax_paired.set_title(f'C. Paired difference\n($D_{{{HIGH_FACE}}}$ − $D_{{{LOW_FACE}}}$)', fontsize=32, fontweight='bold')
ax_paired.set_ylabel(f'D difference (degrees)', fontsize=28)
ax_paired.set_xlabel('Density', fontsize=28)
# Use distribution-driven y-limits so the histogram is not visually collapsed.
d_span = max(abs(np.nanmin(d_diff)), abs(np.nanmax(d_diff)))
paired_ylim = max(d_span * 1.10, abs(paired['D']) + paired['SE'] + 0.5)
ax_paired.set_ylim(-paired_ylim, paired_ylim)

# Annotate
txt = (f"Diff = {paired['D']:+.3f}° | p = {paired['p']:.3f}\n"
       f"t({paired['N']-1}) = {paired['t']:+.2f} | N = {paired['N']}")
ax_paired.text(0.5, -0.14, txt, ha='center', va='top', fontsize=30, color='black',
               transform=ax_paired.transAxes, clip_on=False)

ax_paired.tick_params(labelsize=26)
ax_paired.spines['top'].set_visible(False)
ax_paired.spines['right'].set_visible(False)

# ── Suptitle ─────────────────────────────────────────────────────────────────
fig.suptitle(
    f'Paired Analysis of {LOW_FACE} (low) vs. {HIGH_FACE} (high) | Angle cutoff {ANGLE_LO}° - {ANGLE_HI}° | * p < 0.05',
    fontsize=45, y=0.98, color='#E84A30'
)

out = os.path.join(ROOT, 'symposium', 'within_subject_exp2.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')

print(f"\nSaved {out}")
plt.close()
