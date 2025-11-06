# File: statistics.py
import matplotlib.pyplot as plt

class StatisticsCollector:
    """Collects and plots simulation data."""
    def __init__(self):
        # We will store (arrival_time, latency_ms) tuples
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

def plot_results(fifo_stats, qos_stats, congestion_period):
    """
    Uses Matplotlib to plot the final results.
    'fifo_stats' and 'qos_stats' are StatisticsCollector objects.
    """
    
    # Unzip the data for plotting
    fifo_x = [d[0] for d in fifo_stats.video_latencies]
    fifo_y = [d[1] for d in fifo_stats.video_latencies]
    
    qos_x = [d[0] for d in qos_stats.video_latencies]
    qos_y = [d[1] for d in qos_stats.video_latencies]
    
    avg_fifo = fifo_stats.get_average_video_latency()
    avg_qos = qos_stats.get_average_video_latency()
    
    print(f"\n--- Results ---")
    print(f"Baseline (FIFO) Average Video Latency: {avg_fifo:.2f} ms")
    print(f"Solution (QoS) Average Video Latency:  {avg_qos:.2f} ms")
    
    plt.figure(figsize=(12, 7))
    
    plt.scatter(fifo_x, fifo_y, label=f"Baseline (FIFO) - Avg: {avg_fifo:.2f} ms", color='red', s=5, alpha=0.7)
    plt.scatter(qos_x, qos_y, label=f"Solution (QoS) - Avg: {avg_qos:.2f} ms", color='blue', s=5, alpha=0.7)
    
    # Highlight the congestion period
    start, end = congestion_period
    plt.axvspan(start, end, color='gray', alpha=0.2, label='Network Congestion (Download Active)')
    
    plt.title('Dynamic QoS Management for Home Media')
    plt.xlabel('Simulation Time (seconds)')
    plt.ylabel('Video Packet Latency (milliseconds)')
    plt.legend()
    plt.grid(True)
    
    max_y = max(qos_y) * 4 if qos_y else 200
    plt.ylim(0, max(max_y, 200))
    
    print("\nPlot window is opening...")
    plt.show()