import matplotlib.pyplot as plt
import numpy as np

# --- 1. CONFIGURATION (USER INPUT) ---
print("--- QoS Simulation Configuration ---")
time_duration = int(input("Enter simulation duration (seconds) [Default: 30]: ") or 30)
num_points = time_duration * 10 # 10 data points per second
congestion_start_time = int(input(f"When does congestion START (seconds) [Default: 5]: ") or 5)
congestion_end_time = int(input(f"When does congestion END (seconds) [Default: 25]: ") or 25)

# Convert times to index points
congestion_start_idx = congestion_start_time * 10
congestion_end_idx = congestion_end_time * 10
time = np.linspace(0, time_duration, num_points)

print("--- Simulation Parameters ---")
print(f"Duration: {time_duration}s ({num_points} data points)")
print(f"Congestion: {congestion_start_time}s to {congestion_end_time}s\n")
print("Running simulation... Please wait.")

# --- 2. INITIALIZATION (SETUP FOR THE LOOP) ---
# We create empty lists to store our data as it's generated
# This is different from the old method and is required for the adaptive logic

# Time
time_list = []

# FIFO Lists
fifo_video_latency_list = []
fifo_video_jitter_list = []

# PQ Lists
pq_video_latency_list = []
pq_video_jitter_list = []
pq_video_throughput_list = []
pq_download_throughput_list = []

# WFQ Lists
wfq_video_latency_list = []
wfq_video_jitter_list = []
wfq_video_throughput_list = []
wfq_download_throughput_list = []

# --- PHASE 2: ADAPTIVE-ML Lists ---
adaptive_video_latency_list = []
adaptive_video_jitter_list = []
adaptive_video_throughput_list = []
adaptive_download_throughput_list = []
# We also need to track the "state" of the ML model's decision
adaptive_video_weight = 0.6 # Start with 60% for video

# --- 3. THE SIMULATION LOOP (THE "ENGINE") ---
# We loop through each time-step (e.g., 0.1s, 0.2s, 0.3s...)
# This allows our "Adaptive-ML" model to react to the *previous* time-step

for i in range(num_points):
    # --- State Check ---
    is_congested = congestion_start_idx <= i <= congestion_end_idx

    # --- A. FIFO LOGIC ---
    if not is_congested:
        current_fifo_latency = np.random.normal(3, 0.5)
    else:
        # Huge spike
        current_fifo_latency = np.random.normal(400, 50)
    
    # Jitter is the difference from the last time-step
    last_fifo_latency = fifo_video_latency_list[-1] if i > 0 else 0
    current_fifo_jitter = abs(current_fifo_latency - last_fifo_latency)
    
    fifo_video_latency_list.append(current_fifo_latency)
    fifo_video_jitter_list.append(current_fifo_jitter)

    # --- B. PQ (PRIORITY QUEUEING) LOGIC ---
    # Video latency is always low, download is starved
    if not is_congested:
        current_pq_latency = np.random.normal(2.0, 0.2)
        current_pq_download_throughput = 95.0 # Full speed
    else:
        # Video is still protected
        current_pq_latency = np.random.normal(2.5, 0.3)
        # Download is STARVED
        current_pq_download_throughput = 0.0 
    
    last_pq_latency = pq_video_latency_list[-1] if i > 0 else 0
    current_pq_jitter = abs(current_pq_latency - last_pq_latency)
    
    pq_video_latency_list.append(current_pq_latency)
    pq_video_jitter_list.append(current_pq_jitter)
    pq_video_throughput_list.append(5.0) # Video is constant
    pq_download_throughput_list.append(current_pq_download_throughput)

    # --- C. WFQ (WEIGHTED FAIR QUEUEING) LOGIC ---
    # Video latency is low, download is "fairly" slowed
    if not is_congested:
        current_wfq_latency = np.random.normal(2.5, 0.3)
        current_wfq_download_throughput = 95.0 # Full speed
    else:
        # Video is still protected
        current_wfq_latency = np.random.normal(3.0, 0.5)
        # Download gets a "fair" share (e.g., 10%)
        current_wfq_download_throughput = 10.0
    
    last_wfq_latency = wfq_video_latency_list[-1] if i > 0 else 0
    current_wfq_jitter = abs(current_wfq_latency - last_wfq_latency)
    
    wfq_video_latency_list.append(current_wfq_latency)
    wfq_video_jitter_list.append(current_wfq_jitter)
    wfq_video_throughput_list.append(5.0) # Video is constant
    wfq_download_throughput_list.append(current_wfq_download_throughput)

    # --- 
    # <<< D. PHASE 2: ADAPTIVE-ML LOGIC >>>
    # ---
    # This simulates an ML/SDN controller reacting to network conditions
    
    last_adaptive_latency = adaptive_video_latency_list[-1] if i > 0 else 0
    ML_LATENCY_THRESHOLD = 4.0 # ms

    if not is_congested:
        # Network is clear, be fair.
        adaptive_video_weight = 0.6 # 60% video, 40% download
    else:
        # Network is congested, check ML model
        if last_adaptive_latency > ML_LATENCY_THRESHOLD:
            # "ML model" detects high latency!
            # "SDN Controller" reacts: "Give video 95% of bandwidth!"
            adaptive_video_weight = 0.95
        else:
            # "ML model" says latency is OK.
            # "SDN Controller" stays at a "default congestion" state
            adaptive_video_weight = 0.75
            
    # Now, calculate the throughput and latency based on this "adaptive_video_weight"
    if not is_congested:
        current_adaptive_download_throughput = 95.0
        current_adaptive_latency = np.random.normal(2.2, 0.2)
    else:
        # Download gets 100% - video_weight
        download_weight = (1.0 - adaptive_video_weight)
        current_adaptive_download_throughput = max(0, 100 * download_weight) # e.g. 100 * 0.05 = 5 Mbps
        
        # Latency is inversely related to weight.
        # If weight is 0.95 (high), latency is low. If weight is 0.75, latency is a bit higher.
        current_adaptive_latency = np.random.normal(1.5 + (1.0 - adaptive_video_weight) * 10, 0.2)

    last_adaptive_jitter = adaptive_video_jitter_list[-1] if i > 0 else 0
    current_adaptive_jitter = abs(current_adaptive_latency - last_adaptive_latency)

    adaptive_video_latency_list.append(current_adaptive_latency)
    adaptive_video_throughput_list.append(5.0) # Video stream is constant
    adaptive_download_throughput_list.append(current_adaptive_download_throughput)
    adaptive_video_jitter_list.append(current_adaptive_jitter)

print("Simulation complete. Generating dashboard...")

# --- 4. FINAL DATA CONVERSION ---
# Convert all our Python lists into NumPy arrays for plotting
time = np.array(time)

# FIFO
fifo_video_latency = np.clip(np.array(fifo_video_latency_list), 0, 5000)
fifo_video_jitter = np.clip(np.array(fifo_video_jitter_list), 0, 100)
# PQ
pq_video_latency = np.array(pq_video_latency_list)
pq_video_jitter = np.array(pq_video_jitter_list)
pq_video_throughput = np.array(pq_video_throughput_list)
pq_download_throughput = np.array(pq_download_throughput_list)
# WFQ
wfq_video_latency = np.array(wfq_video_latency_list)
wfq_video_jitter = np.array(wfq_video_jitter_list)
wfq_video_throughput = np.array(wfq_video_throughput_list)
wfq_download_throughput = np.array(wfq_download_throughput_list)
# ADAPTIVE-ML
adaptive_video_latency = np.array(adaptive_video_latency_list)
adaptive_video_jitter = np.array(adaptive_video_jitter_list)
adaptive_video_throughput = np.array(adaptive_video_throughput_list)
adaptive_download_throughput = np.array(adaptive_download_throughput_list)

# --- 5. THE DASHBOARD PLOTTING ---
# This section is the same as before, just with new data lines added
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
fig.suptitle('Advanced QoS Dashboard (Including Adaptive-ML)', fontsize=18, y=1.02)

# --- Plot 1: Real-time Latency (Video Stream) ---
ax1.plot(time, pq_video_latency, label='PQ (Video)', color='blue', linewidth=2)
ax1.plot(time, wfq_video_latency, label='WFQ (Video)', color='green', linewidth=2, linestyle='--')
ax1.plot(time, adaptive_video_latency, label='Adaptive-ML (Video)', color='purple', linewidth=2, linestyle='-.') # NEW
ax1.set_title('Graph 1: Real-time Packet Latency (Video Stream)')
ax1.set_ylabel('Latency (milliseconds)')
ax1.grid(True, linestyle=':', alpha=0.7)
ax1.set_ylim(0, 15)

# --- Plot 2: Throughput (The "Trade-Off" Plot) ---
ax2.plot(time, pq_download_throughput, label='PQ (Download)', color='cyan', linestyle=':', linewidth=2)
ax2.plot(time, wfq_download_throughput, label='WFQ (Download)', color='lightgreen', linestyle=':', linewidth=2)
ax2.plot(time, adaptive_download_throughput, label='Adaptive-ML (Download)', color='magenta', linestyle=':', linewidth=2) # NEW
ax2.plot(time, pq_video_throughput, label='Video (All Algos)', color='black', linewidth=1) # Simplified
ax2.set_title('Graph 2: Bandwidth Allocation (Throughput)')
ax2.set_ylabel('Throughput (Mbps)')
ax2.grid(True, linestyle=':', alpha=0.7)
ax2.set_ylim(0, 105) 

# --- Plot 3: Jitter (Packet Delay Variation) ---
ax3.plot(time, fifo_video_jitter, label='FIFO (Video)', color='red', alpha=0.5)
ax3.plot(time, pq_video_jitter, label='PQ (Video)', color='blue', linewidth=2) 
ax3.plot(time, wfq_video_jitter, label='WFQ (Video)', color='green', linewidth=2, linestyle='--') 
ax3.plot(time, adaptive_video_jitter, label='Adaptive-ML (Video)', color='purple', linewidth=2, linestyle='-.') # NEW
ax3.set_title('Graph 3: Video Stream Jitter (Packet Delay Variation)')
ax3.set_ylabel('Jitter (ms)')
ax3.set_xlabel('Simulation Time (seconds)') 
ax3.grid(True, linestyle=':', alpha=0.7)
ax3.set_ylim(0, 50) 

# --- Add the Shaded Congestion Region to ALL plots ---
for ax in [ax1, ax2, ax3]:
    ax.axvspan(congestion_start_time, congestion_end_time,
               facecolor='#FFC3C3', alpha=0.6, label='_nolegend_') 

# --- Create a Combined, External Legend ---
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles3, labels3 = ax3.get_legend_handles_labels()

handles_congestion = [plt.Rectangle((0,0),1,1, facecolor='#FFC3C3', alpha=0.6)]
labels_congestion = ['Network Congestion']

all_handles = handles1 + handles2 + handles3 + handles_congestion
all_labels = labels1 + labels2 + labels3 + labels_congestion
by_label = dict(zip(all_labels, all_handles))

fig.legend(by_label.values(), by_label.keys(), 
           loc='upper right', 
           bbox_to_anchor=(1.18, 0.95), # Adjusted for new labels
           fontsize=12)

# --- Adjust Layout To Make Room for Title & Legend ---
plt.tight_layout(rect=[0, 0.03, 0.82, 0.95]) # [left, bottom, right, top]

# --- Finalize and Show ---
plt.savefig('qos_advanced_dashboard.png', dpi=300, bbox_inches='tight') 
plt.show() 

print("Dashboard 'qos_advanced_dashboard.png' saved successfully.")