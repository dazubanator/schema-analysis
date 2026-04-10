# 📊 Symposium Poster: Gaze-as-Force & Threat Analysis

This document centralizes all visual findings and methodological details for the symposium poster. All figures are located in the same directory as this file for easy use.

---

## 🔬 Methodology & Task Setup

People appear to treat others' gaze as if it imparts a physical "pressure" on world objects. We used a **tube-tipping task** to measure this implicit bias.

### Task Diagram
**Asset:** `task_diagram.png`
![Methodology Diagram](task_diagram.png)
> **Caption:** Participants judge the tipping point of a paper tube. "D" is calculated as the mean tilt magnitude when tipping toward the face minus the mean tilt magnitude when tipping away.

### Face Stimuli
We manipulated gaze (Sighted vs. Blindfolded) in Experiment 1 and social threat (Low vs. High Threat identity) in Experiment 2.

| Condition | Identity | Image | Threat Rating |
| :--- | :--- | :--- | :--- |
| **Exp 1 (Sighted)** | ID008 | ![ID008](images/ID008.png)<br><small>`images/ID008.png`</small> | 1.75 / 5 |
| **Exp 1 (Blindfold)** | ID008 | ![ID008_blindfold](images/ID008_blindfold.png)<br><small>`images/ID008_blindfold.png`</small> | 1.75 / 5 |
| **Exp 2 (Low Threat)** | ID015 | ![ID015](images/ID015.png)<br><small>`images/ID015.png`</small> | 1.78 / 5 |
| **Exp 2 (High Threat)** | ID017 | ![ID017](images/ID017.png)<br><small>`images/ID017.png`</small> | 4.43 / 5 |
| **Exp 2 (Alt High)** | ID030 | ![ID030](images/ID030.png)<br><small>`images/ID030.png`</small> | 4.50 / 5 |

---

## 📈 Key Findings & Results

### Main Results (Exp 1 & 2)
**Asset:** `figure_d_bars.png`
![Main Results](figure_d_bars.png)

> [!TIP]
> **Replication Success (Exp 1):** We successfully replicated the core gaze-as-force effect. Visible faces (ID008) produced a small but reliable bias ($D = +0.237^\circ, p = 0.039$), while the blindfolded control showed no bias ($p = 0.921$).
>
> **Threat Manipulation (Exp 2):** Swapping between a low-threat and high-threat identity (ID015 vs. ID017) did not produce a statistically significant change in $D$. These results temper the hypothesis that social threat simply "scales" the physical intuition of gaze influence.

---

## 🧪 Technical & Sensitivity Analysis

For a more rigorous presentation, use these detailed analyses to show the robustness of your findings.

### Within-Subject Re-Analysis (Exp 2)
**Asset:** `within_subject_exp2.png`
![Within Subject](within_subject_exp2.png)
*This panel shows the distribution of individual differences and the paired t-test results ($N=249$), confirming no reliable modulation by threat.*

### Between-Subject Distribution (Exp 2)
**Asset:** `between_subject_exp2.png`
![Between Subject](between_subject_exp2.png)
*This panel shows the full unpaired distribution of D-values for each face, including the N=332 and N=208 samples.*

### Sensitivity Sweeps
These heatmaps show that the findings are robust across a wide range of tilt angle filters ($3^\circ$ to $40^\circ$).

````carousel
**Asset:** `sensitivity_exp1.png`
![Sensitivity Exp 1](sensitivity_exp1.png)
<!-- slide -->
**Asset:** `sensitivity_exp2.png`
![Sensitivity Exp 2](sensitivity_exp2.png)
````

---

## 📝 Poster Copy (Draft Text)

**Abstract:**
> People treat others' gaze as if it exerts a small physical influence on nearby objects. Prior work found a directional bias in a tube-tipping task. We replicated this (Exp 1) and asked if perceived social threat amplifies this bias (Exp 2).

**Key Takeaways:**
- **Robustness:** The core gaze-as-force effect is robust to visual information (sighted vs. blindfold).
- **Threat Neutrality:** Swapping identity from low-threat (ID015) to high-threat (ID017) did not significantly increase the tilt bias in this paradigm ($p = 0.580$).
- **Implications:** Physical intuitions about gaze may be "triggered" by the presence of a social agent but not necessarily scaled by social/emotional traits like threat.
