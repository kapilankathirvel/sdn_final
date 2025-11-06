# File: flow.py
import random
from packet import Packet

class Flow:
    """Base class (template) for all traffic generators."""
    def __init__(self, flow_id):
        self.flow_id = flow_id

    def generate_packets(self, simulation_time_sec):
        """Must be implemented by subclasses."""
        raise NotImplementedError

class VideoStream(Flow):
    """Generates a Constant Bit Rate (CBR) stream of packets."""
    def __init__(self, flow_id, bitrate_mbps, packet_size_bytes):
        super().__init__(flow_id)
        self.bitrate_bps = (bitrate_mbps * 1_000_000) / 8
        self.packet_size_bytes = packet_size_bytes
        self.packet_interval_sec = self.packet_size_bytes / self.bitrate_bps

    def generate_packets(self, simulation_time_sec):
        packets = []
        current_time = 0.0
        packet_count = 0
        while current_time < simulation_time_sec:
            packets.append(Packet(
                id=f"{self.flow_id}_{packet_count}",
                flow_type='VIDEO',
                size_bytes=self.packet_size_bytes,
                arrival_time_sec=current_time
            ))
            current_time += self.packet_interval_sec
            packet_count += 1
        return packets

class FileDownload(Flow):
    """Generates a "greedy" burst of traffic."""
    def __init__(self, flow_id, start_time, end_time, packet_size_bytes, interval_sec):
        super().__init__(flow_id)
        self.start_time = start_time
        self.end_time = end_time
        self.packet_size_bytes = packet_size_bytes
        self.interval_sec = interval_sec

    def generate_packets(self, simulation_time_sec):
        packets = []
        current_time = self.start_time
        packet_count = 0
        while current_time < self.end_time and current_time < simulation_time_sec:
            packets.append(Packet(
                id=f"{self.flow_id}_{packet_count}",
                flow_type='DOWNLOAD',
                size_bytes=self.packet_size_bytes,
                arrival_time_sec=current_time
            ))
            # Add a little randomness (jitter)
            current_time += self.interval_sec + (random.random() * 0.0005)
            packet_count += 1
        return packets