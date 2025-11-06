# File: router.py
from collections import deque

class Router:
    """
    Base class (template) for a router.
    It defines the *interface* (the methods) that a Router must have.
    """
    def __init__(self):
        pass

    def add_packet(self, packet):
        """Add a packet to the router's queue(s)."""
        raise NotImplementedError

    def get_next_packet(self):
        """Get the next packet to send, based on the queuing logic."""
        raise NotImplementedError

    def has_packets(self):
        """Check if any queues have packets."""
        raise NotImplementedError

class FIFORouter(Router):
    """A simple First-In, First-Out router."""
    def __init__(self):
        super().__init__()
        self.queue = deque() # A 'deque' is a list optimized for popping from the left

    def add_packet(self, packet):
        self.queue.append(packet)

    def get_next_packet(self):
        if not self.queue:
            return None
        return self.queue.popleft() # First-in, first-out

    def has_packets(self):
        return len(self.queue) > 0

class QoSRouter(Router):
    """
    A router with two priority queues:
    - High: For 'VIDEO' traffic
    - Low: For 'DOWNLOAD' traffic
    """
    def __init__(self):
        super().__init__()
        self.high_priority_queue = deque()
        self.low_priority_queue = deque()

    def add_packet(self, packet):
        # This is the "controller logic"
        if packet.flow_type == 'VIDEO':
            self.high_priority_queue.append(packet)
        else:
            self.low_priority_queue.append(packet)

    def get_next_packet(self):
        # Always check the high-priority queue first
        if self.high_priority_queue:
            return self.high_priority_queue.popleft()
        
        # Only check the low-priority queue if the high one is empty
        if self.low_priority_queue:
            return self.low_priority_queue.popleft()
            
        return None # No packets to send

    def has_packets(self):
        return len(self.high_priority_queue) > 0 or len(self.low_priority_queue) > 0