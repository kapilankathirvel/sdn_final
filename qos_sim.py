import matplotlib.pyplot as plt
import random

# --- 1. Simulation Constants ---

LINK_BANDWIDTH_MBPS = 10      # A modest 20 Mbps home connection
LINK_BANDWIDTH_BPS = (LINK_BANDWIDTH_MBPS * 1_000_000) / 8 # Bytes per second
SIMULATION_TIME_SEC = 30      # Run for 30 seconds

# Video traffic: 5 Mbps Constant Bit Rate
VIDEO_BITRATE_MBPS = 5
VIDEO_BITRATE_BPS = (VIDEO_BITRATE_MBPS * 1_000_000) / 8
VIDEO_PACKET_SIZE_BYTES = 1200  # Typical video/UDP packet size
VIDEO_PACKET_INTERVAL_SEC = VIDEO_PACKET_SIZE_BYTES / VIDEO_BITRATE_BPS

# Download traffic: "Bursty" large download
DOWNLOAD_START_TIME_SEC = 5   # Download starts at 5 seconds
DOWNLOAD_END_TIME_SEC = 25    # Download ends at 25 seconds
DOWNLOAD_PACKET_SIZE_BYTES = 1500 # Typical TCP packet size
# Simulate a "greedy" download: Send a packet every ~1ms in the burst
DOWNLOAD_PACKET_INTERVAL_SEC = 0.001 

# --- 2. Traffic Generation (Phase 1) ---

def generate_traffic():
    """Generates a single, sorted list of all packets for the simulation."""
    packets = []
    
    # Generate Video Traffic (Constant)
    current_time = 0.0
    while current_time < SIMULATION_TIME_SEC:
        packets.append({
            'id': f'vid_{int(current_time*1000)}',
            'time': current_time,
            'size': VIDEO_PACKET_SIZE_BYTES,
            'type': 'VIDEO'
        })
        current_time += VIDEO_PACKET_INTERVAL_SEC

    # Generate Download Traffic (Burst)
    current_time = DOWNLOAD_START_TIME_SEC
    while current_time < DOWNLOAD_END_TIME_SEC:
        packets.append({
            'id': f'dl_{int(current_time*1000)}',
            'time': current_time,
            'size': DOWNLOAD_PACKET_SIZE_BYTES,
            'type': 'DOWNLOAD'
        })
        # Add a little randomness (jitter) to the download
        current_time += DOWNLOAD_PACKET_INTERVAL_SEC + (random.random() * 0.0005)
        
    # Sort all packets by their arrival time
    all_packets = sorted(packets, key=lambda p: p['time'])
    print(f"Generated {len(all_packets)} total packets.")
    print(f"  {len([p for p in all_packets if p['type'] == 'VIDEO'])} VIDEO packets.")
    print(f"  {len([p for p in all_packets if p['type'] == 'DOWNLOAD'])} DOWNLOAD packets.")
    return all_packets

# --- 3. Simulation Logic ---

def simulate_fifo(packet_list, link_bps):
    """Baseline: Simulates a simple FIFO (First-In, First-Out) router."""
    video_latencies = []
    link_free_at_time = 0.0
    
    # A simple FIFO queue is just processing packets in order
    for packet in packet_list:
        arrival_time = packet['time']
        
        # When does this packet *start* transmitting?
        # It's the later of: when it arrives, OR when the link is free.
        start_time = max(arrival_time, link_free_at_time)
        
        transmit_duration = packet['size'] / link_bps
        finish_time = start_time + transmit_duration
        
        # The link is now busy until this packet finishes
        link_free_at_time = finish_time
        
        if packet['type'] == 'VIDEO':
            latency_ms = (finish_time - arrival_time) * 1000  # Latency in milliseconds
            video_latencies.append((arrival_time, latency_ms))
            
    return video_latencies

def simulate_qos(packet_list, link_bps):
    """Solution: Simulates a Priority Queue (our 'SDN' logic)."""
    video_latencies = []
    link_free_at_time = 0.0
    
    high_priority_queue = [] # For VIDEO
    low_priority_queue = []  # For DOWNLOAD
    
    packet_index = 0
    total_packets = len(packet_list)
    
    # We must process packets *as they arrive* and *as the link becomes free*
    # This is a discrete-event simulation
    
    # We need to process packets in order of time.
    # The 'current_time' advances to the next 'event'
    # An 'event' is either a packet arrival or a packet departure.
    
    # A simpler way: Process *all* arrivals first, then process departures
    # This is less accurate for a real-time sim, but much simpler to code.
    
    # Let's stick to the event-based loop, it's more correct.
    
    current_time = 0.0
    
    # We need a list of 'events'. An event is (time, type, data)
    # Let's use a simpler loop that just checks the queues.
    
    processed_packets = 0
    
    # This loop simulates processing the queues, one *departure* at a time
    while packet_index < total_packets or high_priority_queue or low_priority_queue:
        
        # ---
        # Step A: Find the next packet to *send*
        # ---
        
        # First, check if the queues are empty.
        # If so, we must "jump time" forward to the next packet arrival
        if not high_priority_queue and not low_priority_queue:
            if packet_index < total_packets:
                next_packet = packet_list[packet_index]
                # Jump simulation time to this packet's arrival
                current_time = next_packet['time']
                link_free_at_time = max(link_free_at_time, current_time)
            else:
                break # No more packets to arrive, and queues are empty. We're done.
        
        # ---
        # Step B: "Fill the queues"
        # Add all packets that have arrived *by the time the link is free*
        # ---
        while packet_index < total_packets:
            packet = packet_list[packet_index]
            if packet['time'] <= link_free_at_time:
                # This packet arrived while the last one was sending, or just now
                if packet['type'] == 'VIDEO':
                    high_priority_queue.append(packet)
                else:
                    low_priority_queue.append(packet)
                packet_index += 1
            else:
                # This packet arrives in the future, stop filling
                break
        
        # ---
        # Step C: Select which packet to send (The QoS Logic!)
        # ---
        packet_to_send = None
        if high_priority_queue:
            packet_to_send = high_priority_queue.pop(0) # Always send video first
        elif low_priority_queue:
            packet_to_send = low_priority_queue.pop(0) # Only send download if no video
        else:
            # Queues were empty, but we jumped time.
            # The next loop iteration (Step B) will fill them.
            continue 

        # ---
        # Step D: Process the selected packet and log latency
        # ---
        arrival_time = packet_to_send['time']
        
        # When does it *start* transmitting?
        # It must have arrived, AND the link must be free.
        start_time = max(arrival_time, link_free_at_time)
        
        transmit_duration = packet_to_send['size'] / link_bps
        finish_time = start_time + transmit_duration
        
        # The link is now busy until this packet finishes
        link_free_at_time = finish_time
        
        if packet_to_send['type'] == 'VIDEO':
            latency_ms = (finish_time - arrival_time) * 1000
            video_latencies.append((arrival_time, latency_ms))
            
    return video_latencies

# --- 4. Plotting (Phase 3) ---

def plot_results(fifo_data, qos_data):
    """Uses Matplotlib to plot the final results."""
    
    # Unzip the data for plotting
    fifo_x = [d[0] for d in fifo_data]
    fifo_y = [d[1] for d in fifo_data]
    
    qos_x = [d[0] for d in qos_data]
    qos_y = [d[1] for d in qos_data]
    
    # Filter out potential empty lists if no video packets were processed (edge case)
    avg_fifo = sum(fifo_y) / len(fifo_y) if fifo_y else 0
    avg_qos = sum(qos_y) / len(qos_y) if qos_y else 0
    
    print(f"\n--- Results ---")
    print(f"Baseline (FIFO) Average Video Latency: {avg_fifo:.2f} ms")
    print(f"Solution (QoS) Average Video Latency:  {avg_qos:.2f} ms")
    
    plt.figure(figsize=(12, 7))
    
    # Use scatter for clarity, 's=5' makes the dots small
    plt.scatter(fifo_x, fifo_y, label=f"Baseline (FIFO) - Avg: {avg_fifo:.2f} ms", color='red', s=5, alpha=0.7)
    plt.scatter(qos_x, qos_y, label=f"Solution (QoS) - Avg: {avg_qos:.2f} ms", color='blue', s=5, alpha=0.7)
    
    # Highlight the congestion period
    plt.axvspan(DOWNLOAD_START_TIME_SEC, DOWNLOAD_END_TIME_SEC, color='gray', alpha=0.2, label='Network Congestion (Download Active)')
    
    plt.title('Dynamic QoS Management for Home Media')
    plt.xlabel('Simulation Time (seconds)')
    plt.ylabel('Video Packet Latency (milliseconds)')
    plt.legend()
    plt.grid(True)
    
    # Set a Y-limit to make the graph readable, cutting off extreme FIFO spikes
    # You may need to adjust this value based on your results
    max_y = max(qos_y) * 4 if qos_y else 200 # Set a reasonable max Y
    plt.ylim(0, max(max_y, 200)) # Ensure ylim is at least 200ms
    
    print("\nPlot window is opening...")
    plt.show()

# --- 5. Main Execution ---

if __name__ == "__main__":
    print("Starting simulation...")
    # Generate the traffic *once*
    all_packets = generate_traffic()
    
    print("Running Baseline (FIFO) simulation...")
    # Pass a copy in case the function modifies it (good practice)
    fifo_results = simulate_fifo(list(all_packets), LINK_BANDWIDTH_BPS)
    
    print("Running Solution (QoS) simulation...")
    # Pass a fresh copy
    qos_results = simulate_qos(list(all_packets), LINK_BANDWIDTH_BPS) 
    
    print("Generating plot...")
    plot_results(fifo_results, qos_results)
    
    print("Simulation complete.")