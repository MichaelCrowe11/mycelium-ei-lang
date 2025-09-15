#!/usr/bin/env python3
"""
Mycelium Network Framework
Basic implementation of mycelium network communication
"""

import time
import uuid
import math
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    GROWTH = "growth"
    NUTRIENT = "nutrient"
    STRESS = "stress"
    ALERT = "alert"
    DATA = "data"

@dataclass
class Signal:
    signal_type: SignalType
    source_node: str
    payload: Dict[str, Any]
    strength: float = 1.0
    ttl: int = 3

class MyceliumNode:
    def __init__(self, node_id: str = None):
        self.node_id = node_id or str(uuid.uuid4())
        self.connections = {}
        self.environment_params = {}
        self.position = (random.uniform(0, 100), random.uniform(0, 100))
        self.network = None
        
    def connect_to(self, other_node):
        self.connections[other_node.node_id] = other_node
        other_node.connections[self.node_id] = self
        print(f"Connected {self.node_id[:8]} <-> {other_node.node_id[:8]}")
    
    def send_signal(self, signal: Signal):
        if self.network:
            self.network.propagate_signal(signal, self)
        
    def receive_signal(self, signal: Signal):
        print(f"Node {self.node_id[:8]}: Received {signal.signal_type.value} signal")
        
        if signal.signal_type == SignalType.GROWTH:
            rate = signal.payload.get('rate', 0.0)
            print(f"  Growth rate: {rate:.3f}")
            
        elif signal.signal_type == SignalType.STRESS:
            level = signal.payload.get('level', 0.0)
            print(f"  Stress level: {level:.2f}")
            
        elif signal.signal_type == SignalType.ALERT:
            message = signal.payload.get('message', '')
            print(f"  Alert: {message}")

class MyceliumNetwork:
    def __init__(self, name: str = "MyceliumNetwork"):
        self.name = name
        self.nodes = {}
        self.global_environment = {
            'temperature': 24.0,
            'humidity': 85.0,
            'ph_level': 6.8
        }
    
    def add_node(self, node: MyceliumNode = None):
        if node is None:
            node = MyceliumNode()
        node.network = self
        self.nodes[node.node_id] = node
        print(f"Added node {node.node_id[:8]} to network")
        return node
    
    def create_simple_topology(self, num_nodes: int = 5):
        nodes = []
        
        # Create nodes
        for i in range(num_nodes):
            node = self.add_node()
            nodes.append(node)
        
        # Connect adjacent nodes in a ring
        for i in range(num_nodes):
            nodes[i].connect_to(nodes[(i + 1) % num_nodes])
            
        print(f"Created ring topology with {num_nodes} nodes")
        return nodes
    
    def broadcast_signal(self, signal_type: SignalType, payload: Dict[str, Any]):
        if not self.nodes:
            return
            
        source_node = list(self.nodes.values())[0]
        signal = Signal(signal_type, source_node.node_id, payload)
        
        print(f"Broadcasting {signal_type.value} signal")
        self.propagate_signal(signal, source_node)
    
    def propagate_signal(self, signal: Signal, from_node: MyceliumNode):
        if signal.ttl <= 0:
            return
            
        # Send to all connected nodes
        for node_id, node in from_node.connections.items():
            if node_id != signal.source_node:  # Avoid sending back to source
                node.receive_signal(signal)
                
                # Continue propagation with reduced TTL
                new_signal = Signal(
                    signal.signal_type,
                    signal.source_node, 
                    signal.payload,
                    signal.strength * 0.9,
                    signal.ttl - 1
                )
                if new_signal.ttl > 0:
                    self.propagate_signal(new_signal, node)
    
    def update_environment(self, parameter: str, value: float):
        old_value = self.global_environment.get(parameter, 0.0)
        self.global_environment[parameter] = value
        
        print(f"Environment update: {parameter} = {value} (change: {value - old_value:+.2f})")
        
        # Broadcast environment change
        self.broadcast_signal(SignalType.DATA, {
            'type': 'environment_change',
            'parameter': parameter,
            'value': value,
            'change': value - old_value
        })
    
    def get_stats(self):
        return {
            'name': self.name,
            'nodes': len(self.nodes),
            'connections': sum(len(node.connections) for node in self.nodes.values()) // 2,
            'environment': self.global_environment
        }

def demo():
    print("Creating Mycelium Network Demo...")
    
    # Create network
    network = MyceliumNetwork("Demo Network")
    
    # Create topology
    nodes = network.create_simple_topology(4)
    
    print("\nSimulating environmental changes and signals...")
    
    # Growth signal
    network.broadcast_signal(SignalType.GROWTH, {
        'rate': 0.75,
        'factor': 1.1
    })
    
    time.sleep(0.2)
    
    # Environment change
    network.update_environment('temperature', 26.0)
    
    time.sleep(0.2)
    
    # Stress signal due to temperature
    network.broadcast_signal(SignalType.STRESS, {
        'type': 'temperature',
        'level': 0.6
    })
    
    time.sleep(0.2)
    
    # Alert signal
    network.broadcast_signal(SignalType.ALERT, {
        'message': 'Nutrient levels low',
        'priority': 'medium'
    })
    
    print("\nNetwork Statistics:")
    stats = network.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    demo()