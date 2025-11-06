# File: packet.py
from dataclasses import dataclass

@dataclass
class Packet:
    """
    A simple data class to represent a network packet.
    
    Using @dataclass automatically creates __init__, __repr__, etc.
    """
    id: str         # A unique ID for the packet
    flow_type: str  # 'VIDEO' or 'DOWNLOAD'
    size_bytes: int
    arrival_time_sec: float