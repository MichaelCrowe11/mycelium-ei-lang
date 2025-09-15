#!/usr/bin/env python3
"""
Bio-Inspired Machine Learning Integration for Mycelium-EI-Lang
Combines neural networks with biological growth patterns and environmental adaptation
"""

import numpy as np
import random
import time
import math
from typing import List, Dict, Any, Callable, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Neural Network with Bio-Inspired Features
class BiologicalNeuron:
    """A neuron that mimics biological adaptation and growth"""
    
    def __init__(self, neuron_id: str, activation_threshold: float = 0.5):
        self.neuron_id = neuron_id
        self.activation_threshold = activation_threshold
        self.connections = {}  # target_neuron_id -> weight
        self.dendrite_strength = 1.0
        self.growth_factor = 1.0
        self.adaptation_rate = 0.01
        self.metabolic_energy = 1.0
        self.age = 0
        self.last_activation = 0.0
        
    def add_connection(self, target_neuron_id: str, initial_weight: float = 0.1):
        """Add a synaptic connection to another neuron"""
        self.connections[target_neuron_id] = initial_weight
        
    def activate(self, input_signal: float, environmental_factors: Dict[str, float] = None) -> float:
        """Activate the neuron with environmental adaptation"""
        if environmental_factors is None:
            environmental_factors = {'temperature': 1.0, 'nutrients': 1.0, 'ph': 1.0}
        
        # Environmental modulation
        env_factor = (environmental_factors.get('temperature', 1.0) * 
                     environmental_factors.get('nutrients', 1.0) * 
                     environmental_factors.get('ph', 1.0)) ** (1/3)
        
        # Apply dendrite strength and environmental factors
        modulated_input = input_signal * self.dendrite_strength * env_factor
        
        # Biological activation with adaptation
        if modulated_input > self.activation_threshold:
            activation = math.tanh(modulated_input * self.growth_factor)
            self.last_activation = activation
            
            # Metabolic cost and growth
            self.metabolic_energy *= 0.99  # Energy consumption
            if activation > 0.8:
                self.growth_factor *= 1.001  # Strengthen with high activation
            
            # Adaptive threshold adjustment
            self.activation_threshold += (activation - self.activation_threshold) * self.adaptation_rate
            
            self.age += 1
            return activation
        else:
            # Synaptic depression for low activity
            self.dendrite_strength *= 0.999
            return 0.0
    
    def hebbian_learning(self, pre_activation: float, post_activation: float, 
                        learning_rate: float = 0.01):
        """Implement Hebbian learning rule: neurons that fire together, wire together"""
        for target_id in self.connections:
            # Strengthen connections when both neurons are active
            delta_weight = learning_rate * pre_activation * post_activation
            self.connections[target_id] += delta_weight
            
            # Weight decay to prevent runaway growth
            self.connections[target_id] *= 0.995

class MyceliumNeuralNetwork:
    """Neural network that grows like mycelium with environmental adaptation"""
    
    def __init__(self, input_size: int = 4, hidden_size: int = 8, output_size: int = 2):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Create layers
        self.input_layer = [BiologicalNeuron(f"input_{i}") for i in range(input_size)]
        self.hidden_layer = [BiologicalNeuron(f"hidden_{i}", 
                                            activation_threshold=random.uniform(0.3, 0.7)) 
                           for i in range(hidden_size)]
        self.output_layer = [BiologicalNeuron(f"output_{i}") for i in range(output_size)]
        
        # Initialize connections with biological variability
        self.initialize_connections()
        
        # Environmental parameters
        self.environment = {
            'temperature': 1.0,
            'nutrients': 1.0,
            'ph': 1.0,
            'oxygen': 1.0,
            'toxins': 0.0
        }
        
        # Network growth parameters
        self.growth_cycles = 0
        self.network_fitness = 0.0
        
    def initialize_connections(self):
        """Initialize network connections with biological randomness"""
        # Input to hidden connections
        for input_neuron in self.input_layer:
            for hidden_neuron in self.hidden_layer:
                # Random connection strength with biological bias
                weight = random.gauss(0.0, 0.3)
                input_neuron.add_connection(hidden_neuron.neuron_id, weight)
        
        # Hidden to output connections
        for hidden_neuron in self.hidden_layer:
            for output_neuron in self.output_layer:
                weight = random.gauss(0.0, 0.3)
                hidden_neuron.add_connection(output_neuron.neuron_id, weight)
    
    def forward_pass(self, inputs: List[float]) -> List[float]:
        """Process input through the biological neural network"""
        if len(inputs) != self.input_size:
            raise ValueError(f"Expected {self.input_size} inputs, got {len(inputs)}")
        
        # Input layer activation
        input_activations = []
        for i, neuron in enumerate(self.input_layer):
            activation = neuron.activate(inputs[i], self.environment)
            input_activations.append(activation)
        
        # Hidden layer activation
        hidden_activations = []
        for hidden_neuron in self.hidden_layer:
            # Collect weighted inputs from input layer
            weighted_sum = 0.0
            for i, input_neuron in enumerate(self.input_layer):
                if hidden_neuron.neuron_id in input_neuron.connections:
                    weight = input_neuron.connections[hidden_neuron.neuron_id]
                    weighted_sum += input_activations[i] * weight
            
            activation = hidden_neuron.activate(weighted_sum, self.environment)
            hidden_activations.append(activation)
        
        # Output layer activation
        outputs = []
        for output_neuron in self.output_layer:
            weighted_sum = 0.0
            for i, hidden_neuron in enumerate(self.hidden_layer):
                if output_neuron.neuron_id in hidden_neuron.connections:
                    weight = hidden_neuron.connections[output_neuron.neuron_id]
                    weighted_sum += hidden_activations[i] * weight
            
            activation = output_neuron.activate(weighted_sum, self.environment)
            outputs.append(activation)
        
        return outputs
    
    def adapt_to_environment(self, environmental_changes: Dict[str, float]):
        """Adapt network structure and parameters to environmental changes"""
        # Update environment
        for param, value in environmental_changes.items():
            if param in self.environment:
                self.environment[param] = value
        
        # Environmental stress adaptation
        stress_level = (self.environment.get('toxins', 0.0) + 
                       abs(self.environment.get('temperature', 1.0) - 1.0) +
                       abs(self.environment.get('ph', 1.0) - 1.0))
        
        if stress_level > 0.5:
            # Under stress: reduce thresholds (easier activation)
            for neuron in self.hidden_layer + self.output_layer:
                neuron.activation_threshold *= 0.98
                neuron.adaptation_rate *= 1.02
        else:
            # Favorable conditions: increase selectivity
            for neuron in self.hidden_layer + self.output_layer:
                neuron.activation_threshold *= 1.001
                neuron.growth_factor *= 1.001
    
    def biological_learning(self, training_data: List[Tuple[List[float], List[float]]], 
                          epochs: int = 100):
        """Train the network using bio-inspired learning mechanisms"""
        print(f"[BIO-ML] Starting biological learning with {len(training_data)} samples")
        
        for epoch in range(epochs):
            total_error = 0.0
            
            for inputs, targets in training_data:
                # Forward pass
                outputs = self.forward_pass(inputs)
                
                # Calculate error (fitness measure)
                error = sum((outputs[i] - targets[i]) ** 2 for i in range(len(outputs)))
                total_error += error
                
                # Biological adaptation based on performance
                if error < 0.1:  # Good performance
                    # Reward: strengthen successful pathways
                    self.reward_successful_pathways()
                else:  # Poor performance
                    # Adapt: modify network structure
                    self.adapt_network_structure()
            
            # Environmental adaptation every 10 epochs
            if epoch % 10 == 0:
                avg_error = total_error / len(training_data)
                if epoch % 20 == 0:
                    print(f"  Epoch {epoch:3d}: Avg Error = {avg_error:.4f}, "
                          f"Network Fitness = {1.0 / (1.0 + avg_error):.4f}")
                
                # Simulate environmental changes
                self.simulate_environmental_changes()
            
            self.growth_cycles += 1
        
        final_fitness = 1.0 / (1.0 + total_error / len(training_data))
        self.network_fitness = final_fitness
        print(f"[BIO-ML] Learning complete. Final fitness: {final_fitness:.4f}")
        return final_fitness
    
    def reward_successful_pathways(self):
        """Strengthen connections that contribute to successful outcomes"""
        for layer in [self.input_layer, self.hidden_layer]:
            for neuron in layer:
                if neuron.last_activation > 0.5:
                    for connection_id in neuron.connections:
                        neuron.connections[connection_id] *= 1.01  # Small strengthening
    
    def adapt_network_structure(self):
        """Modify network structure for better performance"""
        # Random structural changes (like biological mutation)
        if random.random() < 0.05:  # 5% chance of structural change
            # Add new connection or modify existing ones
            layer = random.choice([self.input_layer, self.hidden_layer])
            neuron = random.choice(layer)
            
            if neuron.connections:
                connection_id = random.choice(list(neuron.connections.keys()))
                # Small random perturbation
                neuron.connections[connection_id] += random.gauss(0.0, 0.1)
    
    def simulate_environmental_changes(self):
        """Simulate natural environmental fluctuations"""
        # Random environmental variations
        env_changes = {}
        for param in ['temperature', 'nutrients', 'ph', 'oxygen']:
            if random.random() < 0.3:  # 30% chance of change
                current_value = self.environment.get(param, 1.0)
                change = random.gauss(0.0, 0.1)
                new_value = max(0.1, min(2.0, current_value + change))
                env_changes[param] = new_value
        
        if env_changes:
            self.adapt_to_environment(env_changes)

class BiologicalMLOptimizer:
    """Optimize machine learning models using biological principles"""
    
    def __init__(self):
        self.networks = {}
        self.optimization_history = []
    
    def create_network(self, network_id: str, input_size: int, hidden_size: int, output_size: int):
        """Create a new biological neural network"""
        network = MyceliumNeuralNetwork(input_size, hidden_size, output_size)
        self.networks[network_id] = network
        print(f"[BIO-ML] Created network '{network_id}' with architecture {input_size}-{hidden_size}-{output_size}")
        return network
    
    def train_network(self, network_id: str, training_data: List[Tuple[List[float], List[float]]], 
                     epochs: int = 100) -> Dict[str, Any]:
        """Train a biological neural network"""
        if network_id not in self.networks:
            raise ValueError(f"Network '{network_id}' not found")
        
        network = self.networks[network_id]
        start_time = time.time()
        
        final_fitness = network.biological_learning(training_data, epochs)
        
        training_time = time.time() - start_time
        
        result = {
            'network_id': network_id,
            'final_fitness': final_fitness,
            'training_time': training_time,
            'growth_cycles': network.growth_cycles,
            'environment': network.environment.copy()
        }
        
        self.optimization_history.append(result)
        return result
    
    def predict(self, network_id: str, inputs: List[float]) -> List[float]:
        """Make prediction using trained network"""
        if network_id not in self.networks:
            raise ValueError(f"Network '{network_id}' not found")
        
        return self.networks[network_id].forward_pass(inputs)
    
    def compare_biological_approaches(self, training_data: List[Tuple[List[float], List[float]]]):
        """Compare different biological neural network configurations"""
        print("[BIO-ML] Comparing biological neural network approaches...")
        
        architectures = [
            ('small', 4, 6, 2),
            ('medium', 4, 10, 2), 
            ('large', 4, 16, 2)
        ]
        
        results = {}
        
        for name, input_size, hidden_size, output_size in architectures:
            network_id = f"bio_net_{name}"
            network = self.create_network(network_id, input_size, hidden_size, output_size)
            
            # Train with different environmental conditions
            if name == 'small':
                network.environment['temperature'] = 0.8  # Cooler
            elif name == 'medium':
                network.environment['nutrients'] = 1.2    # Rich
            elif name == 'large':
                network.environment['toxins'] = 0.1       # Slightly stressed
            
            result = self.train_network(network_id, training_data, epochs=50)
            results[name] = result
            
            print(f"  {name.upper()}: fitness={result['final_fitness']:.4f}, "
                  f"time={result['training_time']:.2f}s")
        
        # Find best approach
        best_approach = max(results.items(), key=lambda x: x[1]['final_fitness'])
        print(f"[BIO-ML] Best approach: {best_approach[0].upper()} "
              f"(fitness: {best_approach[1]['final_fitness']:.4f})")
        
        return results

def demo_bio_ml_integration():
    """Demonstrate bio-inspired machine learning integration"""
    print("[DEMO] Bio-Inspired Machine Learning Integration")
    print("=" * 50)
    
    # Create optimizer
    optimizer = BiologicalMLOptimizer()
    
    # Generate sample training data (XOR-like problem with environmental factors)
    print("\n[DATA] Generating bio-inspired training data...")
    training_data = []
    
    # Mycelium growth prediction based on environmental conditions
    for _ in range(100):
        temp = random.uniform(-1, 1)      # Temperature variation
        humidity = random.uniform(-1, 1)  # Humidity variation  
        nutrients = random.uniform(-1, 1) # Nutrient availability
        ph = random.uniform(-1, 1)        # pH level
        
        # Target: growth rate and branching factor
        growth_rate = max(0, (temp * 0.3 + humidity * 0.4 + nutrients * 0.5 - abs(ph) * 0.2))
        branching = max(0, (nutrients * 0.6 + humidity * 0.2 - abs(temp - 0.2) * 0.3))
        
        training_data.append(([temp, humidity, nutrients, ph], [growth_rate, branching]))
    
    # Test bio-inspired neural network
    print(f"[TRAINING] Training on {len(training_data)} mycelium growth samples...")
    network = optimizer.create_network("mycelium_predictor", 4, 8, 2)
    result = optimizer.train_network("mycelium_predictor", training_data, epochs=100)
    
    # Test predictions
    print("\n[PREDICTION] Testing mycelium growth predictions:")
    test_conditions = [
        ([0.5, 0.8, 0.9, 0.1], "Optimal conditions"),
        ([-0.8, 0.2, 0.3, -0.5], "Stress conditions"),  
        ([0.0, 0.0, 1.0, 0.0], "High nutrients only")
    ]
    
    for inputs, description in test_conditions:
        prediction = optimizer.predict("mycelium_predictor", inputs)
        print(f"  {description}: growth={prediction[0]:.3f}, branching={prediction[1]:.3f}")
    
    # Compare different biological approaches
    print(f"\n[COMPARISON] Comparing biological network architectures:")
    comparison = optimizer.compare_biological_approaches(training_data[:50])  # Smaller subset for speed
    
    return result

if __name__ == "__main__":
    demo_bio_ml_integration()