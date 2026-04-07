import os
import glob
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.stats import linregress

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data', 'arm_angle')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
RESULTS_DIR = os.path.join(ROOT, 'results', 'arm_angle')
READOUT_ARM_COLOR = '#FD8164'
MANIPULATED_ARM_COLOR = '#1996FC'

def save_plot_png_and_svg(path_png, dpi=200):
    plt.savefig(path_png, dpi=dpi)
    path_svg = os.path.splitext(path_png)[0] + '.svg'
    plt.savefig(path_svg)

def load_events(events_file):
    events = []
    with open(events_file, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                marker = parts[0].strip()
                time_s = float(parts[1].strip())
                events.append((marker, time_s))
    return events

def get_voltage_at_time(data, sample_rate, time_s, window_s=0.2):
    idx_center = int(time_s * sample_rate)
    window_samples = int(window_s * sample_rate / 2)
    start_idx = max(0, idx_center - window_samples)
    end_idx = min(len(data), idx_center + window_samples)
    
    snippet = data[start_idx:end_idx]
    if len(snippet.shape) == 1:
        return np.median(snippet), np.median(snippet)
    else:
        return np.median(snippet[:, 0]), np.median(snippet[:, 1])

def process_subject(subject, wav_file, events_file, calib_angles):
    print(f"Processing {subject}...")
    sample_rate, data = wavfile.read(wav_file)
    events = load_events(events_file)
    
    calib_events = {}
    for marker, t in events:
        if marker in ['1', '2', '3', '4', '5']:
            if marker not in calib_events:
                calib_events[marker] = t
        if marker == '8':
            break

    ch0_volts = []
    ch1_volts = []
    angles = []
    
    for marker in ['1', '2', '3', '4', '5']:
        if marker in calib_events and calib_angles[int(marker)-1] is not None and not np.isnan(calib_angles[int(marker)-1]):
            t = calib_events[marker]
            v0, v1 = get_voltage_at_time(data, sample_rate, t)
            ch0_volts.append(v0)
            ch1_volts.append(v1)
            angles.append(calib_angles[int(marker)-1])
            
    if len(angles) < 2:
        print(f"  Not enough calibration points for {subject}.")
        return
        
    slope0, intercept0, r0, p0, std_err0 = linregress(ch0_volts, angles)
    slope1, intercept1, r1, p1, std_err1 = linregress(ch1_volts, angles)
    
    if len(data.shape) > 1:
        ch0_data = data[:, 0]
        ch1_data = data[:, 1]
    else:
        ch0_data = data
        ch1_data = data

    times = np.arange(len(ch0_data)) / sample_rate
    ch0_angles = slope0 * ch0_data + intercept0
    ch1_angles = slope1 * ch1_data + intercept1
    
    t_vib_start, t_vib_end = None, None
    t_follow_start, t_follow_end = None, None
    vib_markers = [t for m, t in events if m == '9']
    follow_markers = [t for m, t in events if m == '8']
    
    if len(vib_markers) >= 2:
        t_vib_start = vib_markers[0]
        t_vib_end = vib_markers[1]
    
    if len(follow_markers) >= 2:
        t_follow_start = follow_markers[0]
        t_follow_end = follow_markers[1]
        
    os.makedirs(os.path.join(RESULTS_DIR, subject), exist_ok=True)
    
    def plot_phase(title, t_start=None, t_end=None, filename="plot.png"):
        plt.figure(figsize=(12, 6))
        
        if t_start is not None and t_end is not None:
            mask = (times >= max(0, t_start - 5)) & (times <= min(times[-1], t_end + 5))
            plot_times = times[mask]
            plot_ch0 = ch0_angles[mask]
            plot_ch1 = ch1_angles[mask]
        else:
            plot_times = times
            plot_ch0 = ch0_angles
            plot_ch1 = ch1_angles
            
        plt.plot(plot_times, plot_ch0, label='Manipulated Arm', color=MANIPULATED_ARM_COLOR)
        plt.plot(plot_times, plot_ch1, label='Subject Matching Arm', color=READOUT_ARM_COLOR)
        
        if t_start is not None and t_end is not None:
            plt.axvline(x=t_start, color='black', linestyle='--', alpha=0.35)
            plt.axvline(x=t_end, color='black', linestyle='--', alpha=0.35)
                
        plt.title(title)
        plt.xlabel("Time (s)")
        plt.ylabel("Angle (Degrees)")
        plt.legend(loc='upper right', frameon=False)
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        save_plot_png_and_svg(os.path.join(RESULTS_DIR, subject, filename), dpi=200)
        plt.close()

    plot_phase(f"Overall Experiment - {subject}", filename="1_overall.png")
    
    if t_follow_start and t_follow_end:
        plot_phase(f"Follow Me Phase - {subject}", t_start=t_follow_start, t_end=t_follow_end, filename="2_follow_me.png")
    
    if t_vib_start and t_vib_end:
        plot_phase(f"Vibration Phase - {subject}", t_start=t_vib_start, t_end=t_vib_end, filename="3_vibration.png")
        
    print(f"  Saved graphs for {subject}")

def run_analysis():
    print("Starting Arm Angle Analysis...")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    json_path = os.path.join(DATA_DIR, 'metadata.json')
    if not os.path.exists(json_path):
        print("Metadata JSON not found.")
        return
        
    with open(json_path, 'r') as f:
        metadata = json.load(f)
    
    wav_files = glob.glob(os.path.join(RAW_DIR, "*.wav"))
    
    for wav_file in wav_files:
        basename = os.path.basename(wav_file).replace('.wav', '')
        parts = basename.split('_')
        if len(parts) >= 4:
            subject = parts[-1]
            events_file = os.path.join(RAW_DIR, f"{basename}-events.txt")
            
            if os.path.exists(events_file):
                if subject in metadata:
                    info = metadata[subject]
                    if info.get('exclude'):
                        print(f"Skipping {subject} (Excluded in metadata)")
                    else:
                        calib_angles = [float(a) if a is not None else np.nan for a in info.get('angles', [])]
                        process_subject(subject, wav_file, events_file, calib_angles)
                else:
                    print(f"Subject {subject} not found in metadata.")
            else:
                print(f"Events file not found for {basename}")

if __name__ == '__main__':
    run_analysis()
