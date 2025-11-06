# File: router.py
from collections import deque

class Router:
    """Base class (template) for a router."""
    def __init__(self):
        pass
    def add_packet(self, packet):
        raise NotImplementedError
    def get_next_packet(self):
        raise NotImplementedError
    def has_packets(self):
        raise NotImplementedError

class FIFORouter(Router):
    """A simple First-In, First-Out router."""
    def __init__(self):
        super().__init__()
        self.queue = deque()
    def add_packet(self, packet):
        self.queue.append(packet)
    def get_next_packet(self):
        if not self.queue:
            return None
        return self.queue.popleft()
    def has_packets(self):
        return len(self.queue) > 0

# --- RENAMED THIS CLASS ---
class PQRouter(Router):
    """
    A router with two priority queues (PQ).
    This was our original 'QoSRouter'.
    """
    def __init__(self):
        super().__init__()
        self.high_priority_queue = deque()
        self.low_priority_queue = deque()
    def add_packet(self, packet):
        if packet.flow_type == 'VIDEO':
            self.high_priority_queue.append(packet)
        else:
            self.low_priority_queue.append(packet)
    def get_next_packet(self):
        if self.high_priority_queue:
            return self.high_priority_queue.popleft()
        if self.low_priority_queue:
            return self.low_priority_queue.popleft()
        return None
    def has_packets(self):
        return len(self.high_priority_queue) > 0 or len(self.low_priority_queue) > 0

# --- NEW CLASS FOR WFQ ---
class WFQRouter(Router):
    """
    A router that implements Weighted Fair Queuing (WFQ)
    using a simple Weighted Round Robin (WRR) packet scheduler.
    """
    def __init__(self, video_weight=7, download_weight=3):
        super().__init__()
        self.high_priority_queue = deque()
        self.low_priority_queue = deque()
        
        # Store the "master" weights
        self.video_weight = video_weight
        self.download_weight = download_weight
        
        # Store the "current" counters for this round
        self.video_counter = self.video_weight
        self.download_counter = self.download_weight

    def add_packet(self, packet):
        # Same logic as PQ: separate traffic into queues
        if packet.flow_type == 'VIDEO':
            self.high_priority_queue.append(packet)
        else:
            self.low_priority_queue.append(packet)
            
    def get_next_packet(self):
        # This logic is now much smarter
        
        # Check if both queues have packets and both counters are zero
        if self.high_priority_queue and self.low_priority_queue and \
           self.video_counter == 0 and self.download_counter == 0:
            # Reset the counters for a new "round"
            self.video_counter = self.video_weight
            self.download_counter = self.download_weight

        # Try to send a video packet if it has "credit"
        if self.high_priority_queue and self.video_counter > 0:
            self.video_counter -= 1
            return self.high_priority_queue.popleft()

        # Try to send a download packet if it has "credit"
        if self.low_priority_queue and self.download_counter > 0:
            self.download_counter -= 1
            return self.low_priority_queue.popleft()

        # --- Handle cases where one queue is empty (use spare bandwidth) ---
        
        if self.high_priority_queue:
            # Low queue is empty OR has no credit, send high
            return self.high_priority_queue.popleft()
            
        if self.low_priority_queue:
            # High queue is empty OR has no credit, send low
            return self.low_priority_queue.popleft()
            
        return None # Both queues are empty

    def has_packets(self):
        return len(self.high_priority_queue) > 0 or len(self.low_priority_queue) > 0