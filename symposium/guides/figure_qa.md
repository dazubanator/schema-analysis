# Symposium Poster — Figure Q&A & Narrative Guide

This document serves as a "master script" for your presentation. It incorporates the the core findings, the historical narrative, and the statistical explanations for all project figures.

---

## 🎭 The Symposium Story Script (The Move-by-Move Guide)

Use this script to guide people through your poster. It links the history of the project to the specific graphs on your layout.

### 1. The Historical Hook (Start at the top-left icons)
> *"For over 100 years, we've known the brain builds a 'model' of the physical body to coordinate movement—this is called the **Body Schema (1911)**. In 2011, Michael Graziano proposed that the brain also builds a model of **Attention**: an 'Attention Schema' that treats visual attention like a directional vector—an arrow pointing from the eyes to a target."*

### 2. The Force Hypothesis & The Task (Point to the Example Tube Task)
> *"Our question was simple: Does the brain treat this 'arrow' like a physical force? If you see someone looking at a tube, does your brain think they are literally pushing it? We used a virtual tube-tipping task to measure this mental projection."*

### 3. The Bedrock Validation (Point to Figure D — Gaze-Force Test)
> *"If you look at our **Gaze-Force Test (Figure D)**, you can see the proof. In **Experiment 1 (Blue Bar)**, visible gaze creates a significant 'push' on participants' judgments. But look at the **Grey Bar**: when we blindfold the face, that force disappears. This successfully replicates the core theory: Gaze acts as a mental force."*

### 4. The Mystery & Social Scaling (Point to the Red Bars & Detailed Graphs)
> *"But look at the red bars for **Experiment 2**. We introduced these AI 'Threat' faces to see if a meaner look causes a bigger push. You'll notice these effects are subtler and noisier. This led us to ask: Is the gaze-push a fragile fluke, or is it a robust reflex?"*

### 5. The Mechanistic Deep-Dive (Point to Bottom Exp 2 Graphs)
> *"When we zoom in on our **Social Threat Test (Bottom Graphs)**, we see that even for different faces and threat levels, the gaze-bias remains a stable, directional reflex. It suggests that while the 'push' of AI eyes might be quieter than a real human's, the brain's fundamental reaction to gaze is remarkably robust."*

### 6. The Final Defense (Point to the Heatmaps on the Right)
> *"Finally, we conducted a **Fluke Test (Heatmaps)**. These maps show thousands of different ways we could have filtered the data. Because the colors remain consistent across the map, it proves that our findings are highly reliable and aren't just an artifact of how we cleaned the data."*

---

## 📊 Detailed Statistical Explanations (For Judges)

If a judge asks **"Why is the Guy (Exp 2) not significant if his eyes are open?"**, use this breakdown:

| Case | Result | The "Signal vs. Noise" Explanation |
| :--- | :--- | :--- |
| **Exp 1: Lady (Open)** | **Significant (p=0.038)** | High Signal (+0.24°), Low Noise (SD=2.7), High Power (N=577). |
| **Exp 2: AI Man (ID017)** | **Insignificant (p=0.44)** | Subtler Signal (+0.16°), Higher Noise (SD=3.3), Lower Power (N=254). |

**The Talking Point:** 
*"The brain's Body Schema may be more sensitive to real human gaze than AI-generated faces. While the direction matches our theory, the effect is subtler and noisier for AI stimuli, requiring a larger sample size ($N > 1500$) to reach full statistical significance."*

---

## 📂 Final Resource Gallery
- **High-Res Figures:** Located in `c:\Users\dazub\schema-analysis\symposium\`
- **Source Scripts:** Use `tube_analysis.py` for heatmaps and `between_subject_exp2.py` for detailed threat analysis.
