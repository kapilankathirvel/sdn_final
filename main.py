# File: main.py
from flow import VideoStream, FileDownload
from router import FIFORouter, QoSRouter
from statistics import StatisticsCollector, plot_results

# --- 1. Simulation Constants ---

SIMULATION_TIME_SEC = 30
LINK_BANDWIDTH_MBPS = 10  # CONGESTED link
LINK_BANDWIDTH_BPS = (LINK_BANDWIDTH_MBPS * 1_000_000) / 8

# Traffic definitions
CONGESTION_START = 5
CONGESTION_END = 25
VIDEO_BITRATE_MBPS = 5
DOWNLOAD_PACKET_INTERVAL = 0.001 # 12 Mbps download

# --- 2. The Simulation Function ---

def run_simulation(router, stats_collector, all_packets, link_bps):
    """
    Runs a single simulation with a given router and stats collector.
    This is the core discrete-event loop.
    """
    link_free_at_time = 0.0
    packet_index = 0
    total_packets = len(all_packets)

    # This loop is the "simulation time"
    while packet_index < total_packets or router.has_packets():
        
        # Step A: Fill the router's queues with all packets that have "arrived"
        # by the time the link is free.
        while packet_index < total_packets:
            packet = all_packets[packet_index]
            if packet.arrival_time_sec <= link_free_at_time:
                router.add_packet(packet)
                packet_index += 1
            else:
                # This packet arrives in the future, stop filling
                break
        
        # Step B: Get the next packet from the router's logic
        packet_to_send = router.get_next_packet()

        if packet_to_send:
            # We have a packet, process it
            arrival_time = packet_to_send.arrival_time_sec
            
            # When does it *start* transmitting?
            start_time = max(arrival_time, link_free_at_time)
            
            transmit_duration = packet_to_send.size_bytes / link_bps
            finish_time = start_time + transmit_duration
            
            # The link is now busy until this packet finishes
            link_free_at_time = finish_time
            
            # Log stats if it's a video packet
            if packet_to_send.flow_type == 'VIDEO':
                stats_collector.log_video_latency(arrival_time, finish_time)
        
        elif packet_index < total_packets:
            # Queues are empty, but more packets are coming.
            # "Jump" time forward to the next packet's arrival
            # to avoid an infinite loop.
            link_free_at_time = all_packets[packet_index].arrival_time_sec
        
        else:
            # No packets to send, and no more to arrive. We are done.
            break

# --- 3. Main Execution ---

if __name__ == "__main__":
    
    print("Starting simulation setup...")
    
    # Step 1: Create the traffic flows
    video_flow = VideoStream(
        flow_id="video_1",
        bitrate_mbps=VIDEO_BITRATE_MBPS,
        packet_size_bytes=1200
    )
    download_flow = FileDownload(
        flow_id="download_1",
        start_time=CONGESTION_START,
        end_time=CONGESTION_END,
        packet_size_bytes=1500,
        interval_sec=DOWNLOAD_PACKET_INTERVAL
    )
    
    # Step 2: Generate all packets for the *entire* simulation
    all_packets = video_flow.generate_packets(SIMULATION_TIME_SEC) + \
                  download_flow.generate_packets(SIMULATION_TIME_SEC)
                  
    # Sort them by arrival time to create the master event list
    all_packets.sort(key=lambda p: p.arrival_time_sec)
    
    print(f"Generated {len(all_packets)} total packets.")
    
    # --- Run Baseline (FIFO) Simulation ---
    print("Running Baseline (FIFO) simulation...")
    fifo_router = FIFORouter()
    fifo_stats = StatisticsCollector()
    run_simulation(fifo_router, fifo_stats, list(all_packets), LINK_BANDWIDTH_BPS)

    # --- Run Solution (QoS) Simulation ---
    print("Running Solution (QoS) simulation...")
    qos_router = QoSRouter()
    qos_stats = StatisticsCollector()
    run_simulation(qos_router, qos_stats, list(all_packets), LINK_BANDWIDTH_BPS)
    
    # --- Plot Results ---
    print("Generating plot...")
    plot_results(fifo_stats, qos_stats, (CONGESTION_START, CONGESTION_END))
    
    print("Simulation complete.")