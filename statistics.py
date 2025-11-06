# File: statistics.py
import matplotlib.pyplot as plt

class StatisticsCollector:
    """Collects and plots simulation data."""
    def __init__(self):
        self.video_latencies = []

    def log_video_latency(self, arrival_time, finish_time):
        latency_sec = finish_time - arrival_time
        latency_ms = latency_sec * 1000
        self.video_latencies.append((arrival_time, latency_ms))
        
    def get_average_video_latency(self):
        if not self.video_latencies:
            return 0.0
        total_latency = sum(latency for time, latency in self.video_latencies)
        return total_latency / len(self.video_latencies)

# --- UPDATED THIS FUNCTION ---
def plot_results(stats_list, congestion_period):
    """
    Uses Matplotlib to plot the final results.
    'stats_list' is a list of tuples: [('Label', stats_collector), ...]
    """
    
    plt.figure(figsize=(12, 7))
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    
    print(f"\n--- Results ---")
    
    # Track the highest Y-value for a clean plot
    max_y_seen = 0.0
    
    for i, (label, stats) in enumerate(stats_list):
        
        # Unzip the data for plotting
        x_data = [d[0] for d in stats.video_latencies]
        y_data = [d[1] for d in stats.video_latencies]
        
        avg_latency = stats.get_average_video_latency()
        color = colors[i % len(colors)]
        
        print(f"{label} Average Video Latency: {avg_latency:.2f} ms")
        
        plt.scatter(x_data, y_data, 
                    label=f"{label} - Avg: {avg_latency:.2f} ms", 
                    color=color, s=5, alpha=0.7)
        
        if y_data:
            max_y_seen = max(max_y_seen, max(y_data))

    # Highlight the congestion period
    start, end = congestion_period
    plt.axvspan(start, end, color='gray', alpha=0.2, label='Network Congestion (Download Active)')
    
    plt.title('Dynamic QoS Management for Home Media')
    plt.xlabel('Simulation Time (seconds)')
    plt.ylabel('Video Packet Latency (milliseconds)')
    plt.legend()
    plt.grid(True)
    
    # Set Y-limit based on the highest *non-FIFO* spike
    # This keeps the plot readable.
    max_y = 200 # Default
    if len(stats_list) > 1:
        # Find max of all *except* the first one (FIFO)
        non_fifo_max = 0
        for label, stats in stats_list[1:]:
            if stats.video_latencies:
                non_fifo_max = max(non_fifo_max, max(d[1] for d in stats.video_latencies))
        max_y = max(non_fifo_max * 4, 200) # Show 4x the max QoS latency
    
    plt.ylim(0, max_y)
    
    print("\nPlot window is opening...")
    plt.show()