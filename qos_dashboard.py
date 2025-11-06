import matplotlib.pyplot as plt
import numpy as np

# --- 1. GENERATE REALISTIC SIMULATION DATA ---
# (This is the same sample data generation as before)
# (You can replace this section with your own data)
num_points = 300
time = np.linspace(0, 30, num_points)
congestion_start_idx = 50  
congestion_end_idx = 250   

congestion_effect = np.zeros(num_points)
congestion_effect[congestion_start_idx:congestion_end_idx] = 1

fifo_video_latency = np.random.normal(3, 1, num_points) + congestion_effect * np.random.normal(400, 50, num_points)
fifo_video_latency = np.clip(fifo_video_latency, 2, 5000)
pq_video_latency = np.random.normal(2, 0.5, num_points) + congestion_effect * np.random.normal(1, 0.5, num_points)
pq_video_latency = np.clip(pq_video_latency, 1, 5)
wfq_video_latency = np.random.normal(3, 0.5, num_points) + congestion_effect * np.random.normal(2, 0.8, num_points)
wfq_video_latency = np.clip(wfq_video_latency, 2, 8)

pq_video_throughput = np.full(num_points, 5)
pq_download_throughput = np.random.normal(95, 2, num_points)
pq_download_throughput[congestion_start_idx:congestion_end_idx] = np.random.normal(0, 0.1, congestion_end_idx - congestion_start_idx)
pq_download_throughput = np.clip(pq_download_throughput, 0, 100)

wfq_video_throughput = np.full(num_points, 5)
wfq_download_throughput = np.random.normal(95, 2, num_points)
wfq_download_throughput[congestion_start_idx:congestion_end_idx] = np.random.normal(10, 2, congestion_end_idx - congestion_start_idx)
wfq_download_throughput = np.clip(wfq_download_throughput, 0, 100)

# --- Generate Jitter Data (ms)
# Jitter is the *variation* in latency. We calculate it using np.diff()
fifo_video_jitter = np.abs(np.diff(fifo_video_latency, prepend=fifo_video_latency[0]))
pq_video_jitter = np.abs(np.diff(pq_video_latency, prepend=pq_video_latency[0])) # <-- FIXED (uses pq_video_latency)
wfq_video_jitter = np.abs(np.diff(wfq_video_latency, prepend=wfq_video_latency[0])) # <-- FIXED (uses wfq_video_latency)
# --- END OF SIMULATION DATA ---


# --- 2. CREATE THE DASHBOARD (WITH LAYOUT FIXES) ---
print("Generating QoS Dashboard with layout fixes...")

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

# Set an overall title. The layout fix below will make it visible.
fig.suptitle('Dynamic QoS Management Dashboard (FIFO vs. PQ vs. WFQ)', fontsize=18, y=1.02)

# --- Plot 1: Real-time Latency (PQ vs WFQ) ---
# We add 'label' parameters for the legend
ax1.plot(time, pq_video_latency, label='PQ (Video)', color='blue', linewidth=2)
ax1.plot(time, wfq_video_latency, label='WFQ (Video)', color='green', linewidth=2, linestyle='--')
ax1.set_title('Graph 1: Real-time Packet Latency (Video Stream)')
ax1.set_ylabel('Latency (milliseconds)')
ax1.grid(True, linestyle=':', alpha=0.7)
ax1.set_ylim(0, 15)

# --- Plot 2: Throughput (The "Trade-Off" Plot) ---
ax2.plot(time, pq_video_throughput, label='PQ (Video)', color='blue', linewidth=2) # Label is a duplicate, which is fine
ax2.plot(time, pq_download_throughput, label='PQ (Download)', color='cyan', linestyle=':', linewidth=2)
ax2.plot(time, wfq_video_throughput, label='WFQ (Video)', color='green', linewidth=2) # Duplicate label
ax2.plot(time, wfq_download_throughput, label='WFQ (Download)', color='lightgreen', linestyle=':', linewidth=2)
ax2.set_title('Graph 2: Bandwidth Allocation (Throughput)')
ax2.set_ylabel('Throughput (Mbps)')
ax2.grid(True, linestyle=':', alpha=0.7)
ax2.set_ylim(0, 105) 

# --- Plot 3: Jitter (Packet Delay Variation) ---
ax3.plot(time, fifo_video_jitter, label='FIFO (Video)', color='red', alpha=0.5)
ax3.plot(time, pq_video_jitter, label='PQ (Video)', color='blue', linewidth=2) # Duplicate label
ax3.plot(time, wfq_video_jitter, label='WFQ (Video)', color='green', linewidth=2, linestyle='--') # Duplicate label
ax3.set_title('Graph 3: Video Stream Jitter (Packet Delay Variation)')
ax3.set_ylabel('Jitter (ms)')
ax3.set_xlabel('Simulation Time (seconds)') 
ax3.grid(True, linestyle=':', alpha=0.7)
ax3.set_ylim(0, 50) 

# --- Add the Shaded Congestion Region to ALL plots ---
congestion_start_time = time[congestion_start_idx]
congestion_end_time = time[congestion_end_idx]
for ax in [ax1, ax2, ax3]:
    ax.axvspan(congestion_start_time, congestion_end_time,
               facecolor='#FFC3C3', # A light red color
               alpha=0.6,
               label='_nolegend_') # Hide this from the legend

# --- 
# <<< FIX 1: CREATE A COMBINED, EXTERNAL LEGEND >>>
# ---
# Get all the lines and labels from all 3 plots
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles3, labels3 = ax3.get_legend_handles_labels()

# Add a custom patch for our congestion label
handles_congestion = [plt.Rectangle((0,0),1,1, facecolor='#FFC3C3', alpha=0.6)]
labels_congestion = ['Network Congestion']

# Combine all unique labels and handles using a dictionary to remove duplicates
all_handles = handles1 + handles2 + handles3 + handles_congestion
all_labels = labels1 + labels2 + labels3 + labels_congestion
by_label = dict(zip(all_labels, all_handles))

# Place the combined legend neatly OUTSIDE the top-right of the plot area
fig.legend(by_label.values(), by_label.keys(), 
           loc='upper right', 
           bbox_to_anchor=(1.14, 0.95), # This moves the legend outside
           fontsize=12)

# ---
# <<< FIX 2: ADJUST LAYOUT TO MAKE ROOM FOR TITLE & LEGEND >>>
# ---
# This resizes the plot area to make space at the top (for the title)
# and on the right (for the new legend)
plt.tight_layout(rect=[0, 0.03, 0.85, 0.95]) # [left, bottom, right, top]

# --- Finalize and Show ---
plt.savefig('qos_dashboard_FIXED.png', dpi=300, bbox_inches='tight') # 'bbox_inches' ensures the legend is saved
plt.show()

print("Dashboard 'qos_dashboard_FIXED.png' saved successfully.")