#!/usr/bin/env python3
"""
Advanced Cultivation Monitoring Platform for Mycelium-EI-Lang
Real-time monitoring, optimization, and control of biological cultivation systems
"""

import time
import random
import math
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

from network_framework import MyceliumNetwork, SignalType
from bio_algorithms import BiologicalOptimizer
from bio_ml_integration import BiologicalMLOptimizer

class CultivationStage(Enum):
    INITIALIZATION = "initialization"
    GROWTH = "growth"  
    MATURATION = "maturation"
    HARVEST = "harvest"
    DORMANT = "dormant"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class EnvironmentalReading:
    timestamp: datetime
    temperature: float
    humidity: float
    ph: float
    dissolved_oxygen: float
    nutrients: float
    light_intensity: float
    co2_level: float
    contamination_risk: float
    growth_rate: float

@dataclass
class CultivationAlert:
    timestamp: datetime
    level: AlertLevel
    category: str
    message: str
    suggested_action: str
    auto_correctable: bool

class SensorNetwork:
    """Simulated sensor network for cultivation monitoring"""
    
    def __init__(self, num_sensors: int = 8):
        self.sensors = {}
        self.baseline_params = {
            'temperature': 24.0,
            'humidity': 85.0,
            'ph': 6.5,
            'dissolved_oxygen': 8.0,
            'nutrients': 100.0,
            'light_intensity': 50.0,
            'co2_level': 400.0,
            'contamination_risk': 0.1
        }
        
        # Initialize sensors with slight variations
        for i in range(num_sensors):
            sensor_id = f"sensor_{i:02d}"
            self.sensors[sensor_id] = {
                'location': (random.uniform(0, 100), random.uniform(0, 100)),
                'calibration_offset': {param: random.gauss(0, 0.05) for param in self.baseline_params},
                'drift_rate': {param: random.gauss(0, 0.001) for param in self.baseline_params},
                'last_reading': None,
                'operational': True
            }
    
    def simulate_environmental_changes(self) -> Dict[str, float]:
        """Simulate natural environmental fluctuations"""
        current_time = time.time()
        
        # Diurnal temperature cycle
        temp_cycle = 2.0 * math.sin(2 * math.pi * (current_time % 86400) / 86400)
        
        # Random variations
        variations = {
            'temperature': self.baseline_params['temperature'] + temp_cycle + random.gauss(0, 1.0),
            'humidity': max(60, min(95, self.baseline_params['humidity'] + random.gauss(0, 3.0))),
            'ph': max(5.5, min(8.0, self.baseline_params['ph'] + random.gauss(0, 0.2))),
            'dissolved_oxygen': max(6.0, min(12.0, self.baseline_params['dissolved_oxygen'] + random.gauss(0, 0.5))),
            'nutrients': max(50, min(150, self.baseline_params['nutrients'] + random.gauss(0, 5.0))),
            'light_intensity': max(20, min(80, self.baseline_params['light_intensity'] + random.gauss(0, 5.0))),
            'co2_level': max(350, min(500, self.baseline_params['co2_level'] + random.gauss(0, 20.0))),
            'contamination_risk': max(0.0, min(1.0, self.baseline_params['contamination_risk'] + random.gauss(0, 0.05)))
        }
        
        return variations
    
    def get_sensor_reading(self, sensor_id: str) -> Optional[Dict[str, float]]:
        """Get reading from specific sensor"""
        if sensor_id not in self.sensors or not self.sensors[sensor_id]['operational']:
            return None
        
        sensor = self.sensors[sensor_id]
        base_reading = self.simulate_environmental_changes()
        
        # Apply sensor-specific calibration and drift
        reading = {}
        for param, value in base_reading.items():
            offset = sensor['calibration_offset'][param]
            drift = sensor['drift_rate'][param] * (time.time() % 3600)  # Hourly drift
            reading[param] = value + offset + drift
        
        # Add growth rate calculation
        reading['growth_rate'] = self.calculate_growth_rate(reading)
        
        sensor['last_reading'] = reading
        return reading
    
    def calculate_growth_rate(self, environmental_params: Dict[str, float]) -> float:
        """Calculate expected growth rate based on environmental conditions"""
        temp_factor = max(0, 1.0 - abs(environmental_params['temperature'] - 24.0) / 10.0)
        humidity_factor = max(0, environmental_params['humidity'] / 100.0)
        ph_factor = max(0, 1.0 - abs(environmental_params['ph'] - 6.5) / 2.0)
        oxygen_factor = max(0, environmental_params['dissolved_oxygen'] / 10.0)
        nutrient_factor = max(0, environmental_params['nutrients'] / 100.0)
        
        contamination_penalty = 1.0 - environmental_params['contamination_risk']
        
        growth_rate = (temp_factor * humidity_factor * ph_factor * 
                      oxygen_factor * nutrient_factor * contamination_penalty)
        
        return min(1.0, growth_rate)
    
    def get_network_average(self) -> Dict[str, float]:
        """Get average reading across all operational sensors"""
        operational_sensors = [s for s in self.sensors.values() if s['operational']]
        if not operational_sensors:
            return {}
        
        readings = []
        for sensor in operational_sensors:
            if sensor['last_reading']:
                readings.append(sensor['last_reading'])
        
        if not readings:
            # Get fresh readings
            for sensor_id in self.sensors:
                reading = self.get_sensor_reading(sensor_id)
                if reading:
                    readings.append(reading)
        
        if not readings:
            return {}
        
        # Calculate averages
        averages = {}
        for param in readings[0].keys():
            averages[param] = sum(r[param] for r in readings) / len(readings)
        
        return averages

class CultivationController:
    """Advanced cultivation system controller"""
    
    def __init__(self, cultivation_id: str):
        self.cultivation_id = cultivation_id
        self.stage = CultivationStage.INITIALIZATION
        self.start_time = datetime.now()
        self.sensor_network = SensorNetwork()
        self.mycelium_network = MyceliumNetwork(f"Cultivation_{cultivation_id}")
        self.bio_optimizer = BiologicalOptimizer()
        self.ml_optimizer = BiologicalMLOptimizer()
        
        # Control systems
        self.target_parameters = {
            'temperature': 24.0,
            'humidity': 85.0,
            'ph': 6.5,
            'dissolved_oxygen': 8.0,
            'nutrients': 100.0,
            'co2_level': 400.0
        }
        
        self.control_limits = {
            'temperature': (20.0, 28.0),
            'humidity': (70.0, 95.0),
            'ph': (6.0, 7.5),
            'dissolved_oxygen': (6.0, 10.0),
            'nutrients': (80.0, 120.0),
            'co2_level': (350.0, 450.0)
        }
        
        # Monitoring data
        self.readings_history = []
        self.alerts_history = []
        self.optimization_results = []
        self.prediction_model = None
        
        # Initialize ML model for growth prediction
        self.initialize_growth_prediction_model()
        
        print(f"[CULTIVATION] Initialized cultivation system '{cultivation_id}'")
    
    def initialize_growth_prediction_model(self):
        """Initialize biological neural network for growth prediction"""
        network_id = f"growth_predictor_{self.cultivation_id}"
        self.ml_optimizer.create_network(network_id, 8, 12, 3)  # 8 inputs, 3 outputs (growth, health, yield)
        
        # Generate initial training data
        training_data = self.generate_synthetic_training_data(50)
        result = self.ml_optimizer.train_network(network_id, training_data, epochs=30)
        
        self.prediction_model = network_id
        print(f"[CULTIVATION] Growth prediction model initialized (fitness: {result['final_fitness']:.3f})")
    
    def generate_synthetic_training_data(self, num_samples: int) -> List:
        """Generate synthetic training data for the growth model"""
        data = []
        for _ in range(num_samples):
            # Input: environmental parameters
            temp = random.uniform(18, 30)
            humidity = random.uniform(65, 95)
            ph = random.uniform(5.5, 8.0)
            oxygen = random.uniform(5, 12)
            nutrients = random.uniform(60, 140)
            light = random.uniform(20, 80)
            co2 = random.uniform(300, 500)
            contamination = random.uniform(0, 0.3)
            
            inputs = [temp, humidity, ph, oxygen, nutrients, light, co2, contamination]
            
            # Output: growth rate, health index, predicted yield
            growth_rate = max(0, min(1, 
                (1 - abs(temp - 24) / 8) * 
                (humidity / 100) * 
                (1 - abs(ph - 6.5) / 2) * 
                (oxygen / 10) * 
                (nutrients / 100) * 
                (1 - contamination)
            ))
            
            health_index = max(0, min(1, growth_rate * (1 - contamination * 2)))
            predicted_yield = growth_rate * health_index * random.uniform(0.8, 1.2)
            
            outputs = [growth_rate, health_index, predicted_yield]
            data.append((inputs, outputs))
        
        return data
    
    def get_current_reading(self) -> EnvironmentalReading:
        """Get current environmental reading"""
        avg_reading = self.sensor_network.get_network_average()
        if not avg_reading:
            return None
        
        reading = EnvironmentalReading(
            timestamp=datetime.now(),
            temperature=avg_reading['temperature'],
            humidity=avg_reading['humidity'],
            ph=avg_reading['ph'],
            dissolved_oxygen=avg_reading['dissolved_oxygen'],
            nutrients=avg_reading['nutrients'],
            light_intensity=avg_reading['light_intensity'],
            co2_level=avg_reading['co2_level'],
            contamination_risk=avg_reading['contamination_risk'],
            growth_rate=avg_reading['growth_rate']
        )
        
        self.readings_history.append(reading)
        return reading
    
    def analyze_cultivation_health(self, reading: EnvironmentalReading) -> Dict[str, Any]:
        """Analyze overall cultivation health using bio-ML"""
        if not self.prediction_model:
            return {'health_score': 0.5, 'predictions': None}
        
        inputs = [
            reading.temperature, reading.humidity, reading.ph,
            reading.dissolved_oxygen, reading.nutrients, reading.light_intensity,
            reading.co2_level, reading.contamination_risk
        ]
        
        try:
            predictions = self.ml_optimizer.predict(self.prediction_model, inputs)
            growth_pred, health_pred, yield_pred = predictions[0], predictions[1], predictions[2]
            
            # Calculate overall health score
            health_score = (growth_pred * 0.4 + health_pred * 0.4 + yield_pred * 0.2)
            
            return {
                'health_score': health_score,
                'predicted_growth': growth_pred,
                'health_index': health_pred,
                'predicted_yield': yield_pred,
                'recommendations': self.generate_recommendations(reading, predictions)
            }
        except Exception as e:
            print(f"[CULTIVATION] Prediction error: {e}")
            return {'health_score': 0.5, 'predictions': None}
    
    def generate_recommendations(self, reading: EnvironmentalReading, predictions: List[float]) -> List[str]:
        """Generate cultivation recommendations based on analysis"""
        recommendations = []
        
        if reading.temperature < 22:
            recommendations.append("Increase temperature - current too low for optimal growth")
        elif reading.temperature > 26:
            recommendations.append("Reduce temperature - current too high, may stress organism")
        
        if reading.humidity < 75:
            recommendations.append("Increase humidity - dry conditions detected")
        
        if reading.ph < 6.0:
            recommendations.append("Increase pH - conditions too acidic")
        elif reading.ph > 7.2:
            recommendations.append("Decrease pH - conditions too alkaline")
        
        if reading.nutrients < 85:
            recommendations.append("Add nutrients - nutrient levels below optimal range")
        
        if reading.contamination_risk > 0.2:
            recommendations.append("Contamination risk elevated - implement sterilization protocols")
        
        if predictions[0] < 0.5:  # Low predicted growth
            recommendations.append("Growth rate below optimal - review environmental parameters")
        
        return recommendations
    
    def optimize_cultivation_parameters(self) -> Dict[str, Any]:
        """Use bio-algorithms to optimize cultivation parameters"""
        print(f"[CULTIVATION] Running bio-optimization for cultivation '{self.cultivation_id}'")
        
        def cultivation_fitness(params):
            """Fitness function for cultivation optimization"""
            temp, humidity, ph, oxygen, nutrients, co2 = params
            
            # Penalty for out-of-bounds parameters
            penalties = 0
            if not (18 <= temp <= 30): penalties += abs(temp - 24) * 0.1
            if not (65 <= humidity <= 95): penalties += abs(humidity - 85) * 0.01
            if not (5.5 <= ph <= 8.0): penalties += abs(ph - 6.5) * 0.2
            if not (5 <= oxygen <= 12): penalties += abs(oxygen - 8) * 0.1
            if not (60 <= nutrients <= 140): penalties += abs(nutrients - 100) * 0.01
            if not (300 <= co2 <= 500): penalties += abs(co2 - 400) * 0.001
            
            # Growth rate calculation
            temp_factor = max(0, 1.0 - abs(temp - 24.0) / 8.0)
            humidity_factor = max(0, humidity / 100.0)
            ph_factor = max(0, 1.0 - abs(ph - 6.5) / 2.0)
            oxygen_factor = max(0, oxygen / 10.0)
            nutrient_factor = max(0, nutrients / 120.0)
            co2_factor = max(0.7, min(1.0, co2 / 400.0))
            
            fitness = (temp_factor * humidity_factor * ph_factor * 
                      oxygen_factor * nutrient_factor * co2_factor) - penalties
            
            return max(0, fitness)
        
        # Run optimization comparison
        results = self.bio_optimizer.compare_algorithms(cultivation_fitness, dimensions=6)
        
        # Get best result
        best_result = max([r for r in results.values() if 'error' not in r], 
                         key=lambda x: x['best_fitness'])
        
        # Update target parameters
        optimal_params = best_result['best_solution']
        param_names = ['temperature', 'humidity', 'ph', 'dissolved_oxygen', 'nutrients', 'co2_level']
        
        for i, param_name in enumerate(param_names):
            self.target_parameters[param_name] = optimal_params[i]
        
        optimization_result = {
            'timestamp': datetime.now(),
            'best_algorithm': best_result['algorithm'],
            'fitness': best_result['best_fitness'],
            'optimal_parameters': dict(zip(param_names, optimal_params)),
            'improvement': best_result['best_fitness'] - 0.5  # Baseline fitness
        }
        
        self.optimization_results.append(optimization_result)
        
        print(f"[CULTIVATION] Optimization complete. Best fitness: {best_result['best_fitness']:.4f}")
        return optimization_result
    
    def check_alerts(self, reading: EnvironmentalReading) -> List[CultivationAlert]:
        """Check for cultivation alerts based on current reading"""
        alerts = []
        timestamp = datetime.now()
        
        # Temperature alerts
        if reading.temperature < self.control_limits['temperature'][0]:
            alerts.append(CultivationAlert(
                timestamp, AlertLevel.WARNING, "temperature",
                f"Temperature too low: {reading.temperature:.1f}°C",
                "Increase heating system output", True
            ))
        elif reading.temperature > self.control_limits['temperature'][1]:
            alerts.append(CultivationAlert(
                timestamp, AlertLevel.WARNING, "temperature",
                f"Temperature too high: {reading.temperature:.1f}°C",
                "Increase cooling system output", True
            ))
        
        # Contamination alerts
        if reading.contamination_risk > 0.3:
            level = AlertLevel.CRITICAL if reading.contamination_risk > 0.6 else AlertLevel.WARNING
            alerts.append(CultivationAlert(
                timestamp, level, "contamination",
                f"Contamination risk elevated: {reading.contamination_risk:.1%}",
                "Implement sterilization protocols immediately", False
            ))
        
        # Growth rate alerts
        if reading.growth_rate < 0.3:
            alerts.append(CultivationAlert(
                timestamp, AlertLevel.WARNING, "growth",
                f"Growth rate below optimal: {reading.growth_rate:.2f}",
                "Review and optimize environmental parameters", False
            ))
        
        # pH alerts
        if reading.ph < self.control_limits['ph'][0] or reading.ph > self.control_limits['ph'][1]:
            alerts.append(CultivationAlert(
                timestamp, AlertLevel.WARNING, "ph",
                f"pH out of range: {reading.ph:.2f}",
                "Adjust pH buffer system", True
            ))
        
        # Store alerts
        self.alerts_history.extend(alerts)
        
        return alerts
    
    def update_cultivation_stage(self):
        """Update cultivation stage based on time and conditions"""
        runtime = datetime.now() - self.start_time
        
        if runtime < timedelta(hours=2):
            self.stage = CultivationStage.INITIALIZATION
        elif runtime < timedelta(hours=48):
            self.stage = CultivationStage.GROWTH
        elif runtime < timedelta(hours=120):
            self.stage = CultivationStage.MATURATION
        else:
            self.stage = CultivationStage.HARVEST
    
    def get_cultivation_report(self) -> Dict[str, Any]:
        """Generate comprehensive cultivation report"""
        if not self.readings_history:
            current_reading = self.get_current_reading()
        else:
            current_reading = self.readings_history[-1]
        
        health_analysis = self.analyze_cultivation_health(current_reading)
        recent_alerts = [a for a in self.alerts_history if a.timestamp > datetime.now() - timedelta(hours=1)]
        
        report = {
            'cultivation_id': self.cultivation_id,
            'stage': self.stage.value,
            'runtime': str(datetime.now() - self.start_time),
            'current_conditions': asdict(current_reading) if current_reading else {},
            'health_analysis': health_analysis,
            'recent_alerts': len(recent_alerts),
            'critical_alerts': len([a for a in recent_alerts if a.level == AlertLevel.CRITICAL]),
            'optimization_count': len(self.optimization_results),
            'last_optimization': self.optimization_results[-1] if self.optimization_results else None,
            'target_parameters': self.target_parameters,
            'sensor_status': len([s for s in self.sensor_network.sensors.values() if s['operational']])
        }
        
        return report

class CultivationMonitoringPlatform:
    """Main cultivation monitoring platform"""
    
    def __init__(self):
        self.cultivations = {}
        self.platform_start_time = datetime.now()
        self.monitoring_active = False
        self.monitoring_thread = None
        
    def create_cultivation(self, cultivation_id: str) -> CultivationController:
        """Create a new cultivation monitoring instance"""
        if cultivation_id in self.cultivations:
            raise ValueError(f"Cultivation '{cultivation_id}' already exists")
        
        controller = CultivationController(cultivation_id)
        self.cultivations[cultivation_id] = controller
        
        print(f"[PLATFORM] Created cultivation '{cultivation_id}'")
        return controller
    
    def start_monitoring(self, monitoring_interval: float = 30.0):
        """Start continuous monitoring of all cultivations"""
        if self.monitoring_active:
            print("[PLATFORM] Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(monitoring_interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        print(f"[PLATFORM] Started monitoring with {monitoring_interval}s interval")
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        cycle_count = 0
        
        while self.monitoring_active:
            try:
                cycle_count += 1
                print(f"\n[PLATFORM] Monitoring cycle {cycle_count}")
                
                for cult_id, controller in self.cultivations.items():
                    # Get current reading
                    reading = controller.get_current_reading()
                    if not reading:
                        continue
                    
                    # Check for alerts
                    alerts = controller.check_alerts(reading)
                    
                    # Update stage
                    controller.update_cultivation_stage()
                    
                    # Analyze health
                    health = controller.analyze_cultivation_health(reading)
                    
                    print(f"  {cult_id}: Stage={controller.stage.value}, "
                          f"Health={health['health_score']:.2f}, "
                          f"Growth={reading.growth_rate:.2f}, "
                          f"Alerts={len(alerts)}")
                    
                    # Auto-optimize if health is low
                    if health['health_score'] < 0.6 and cycle_count % 10 == 0:
                        print(f"  {cult_id}: Running auto-optimization due to low health")
                        controller.optimize_cultivation_parameters()
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"[PLATFORM] Monitoring error: {e}")
                time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("[PLATFORM] Monitoring stopped")
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get overall platform status"""
        total_alerts = sum(len(c.alerts_history) for c in self.cultivations.values())
        active_cultivations = len([c for c in self.cultivations.values() 
                                 if c.stage not in [CultivationStage.HARVEST, CultivationStage.DORMANT]])
        
        status = {
            'platform_uptime': str(datetime.now() - self.platform_start_time),
            'total_cultivations': len(self.cultivations),
            'active_cultivations': active_cultivations,
            'monitoring_active': self.monitoring_active,
            'total_alerts': total_alerts,
            'cultivation_status': {cult_id: controller.get_cultivation_report() 
                                 for cult_id, controller in self.cultivations.items()}
        }
        
        return status

def demo_cultivation_platform():
    """Demonstrate the advanced cultivation monitoring platform"""
    print("[DEMO] Advanced Cultivation Monitoring Platform")
    print("=" * 55)
    
    # Create platform
    platform = CultivationMonitoringPlatform()
    
    # Create test cultivations
    cultivation_1 = platform.create_cultivation("MyceliumBatch_001")
    cultivation_2 = platform.create_cultivation("MyceliumBatch_002") 
    
    print(f"\n[DEMO] Created {len(platform.cultivations)} cultivation batches")
    
    # Run some monitoring cycles manually
    print(f"\n[DEMO] Running manual monitoring cycles...")
    
    for cycle in range(5):
        print(f"\n--- Cycle {cycle + 1} ---")
        
        for cult_id, controller in platform.cultivations.items():
            # Get reading and analysis
            reading = controller.get_current_reading()
            health = controller.analyze_cultivation_health(reading)
            alerts = controller.check_alerts(reading)
            
            print(f"{cult_id}:")
            print(f"  Temperature: {reading.temperature:.1f}°C")
            print(f"  Growth Rate: {reading.growth_rate:.3f}")
            print(f"  Health Score: {health['health_score']:.3f}")
            print(f"  Alerts: {len(alerts)}")
            
            if health['recommendations']:
                print(f"  Recommendations: {len(health['recommendations'])} items")
            
            # Run optimization every 3rd cycle
            if cycle == 2:
                print(f"  Running optimization...")
                opt_result = controller.optimize_cultivation_parameters()
                print(f"  Optimization fitness: {opt_result['fitness']:.4f}")
        
        time.sleep(2)  # Short delay between cycles
    
    # Generate final reports
    print(f"\n[DEMO] Final Platform Status:")
    status = platform.get_platform_status()
    
    print(f"  Total Cultivations: {status['total_cultivations']}")
    print(f"  Active Cultivations: {status['active_cultivations']}")
    print(f"  Total Alerts Generated: {status['total_alerts']}")
    print(f"  Platform Uptime: {status['platform_uptime']}")
    
    print(f"\n[DEMO] Cultivation Reports:")
    for cult_id, report in status['cultivation_status'].items():
        print(f"  {cult_id}:")
        print(f"    Stage: {report['stage']}")
        print(f"    Health: {report['health_analysis']['health_score']:.3f}")
        print(f"    Recent Alerts: {report['recent_alerts']}")
        print(f"    Optimizations: {report['optimization_count']}")
    
    return platform

if __name__ == "__main__":
    demo_cultivation_platform()