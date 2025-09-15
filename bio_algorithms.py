#!/usr/bin/env python3
"""
Bio-Inspired Algorithms for Mycelium-EI-Lang
Implements genetic algorithms, swarm intelligence, and evolutionary computation
"""

import random
import math
import time
import numpy as np
from typing import List, Dict, Any, Callable, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import copy

# Genetic Algorithm Implementation
class Individual:
    """Represents an individual in the genetic algorithm population"""
    
    def __init__(self, genes: List[float], fitness: float = 0.0):
        self.genes = genes
        self.fitness = fitness
        self.age = 0
        self.generation = 0
    
    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.1):
        """Apply mutation to the individual"""
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                # Gaussian mutation with environmental adaptation
                self.genes[i] += random.gauss(0, mutation_strength)
                self.genes[i] = max(-1.0, min(1.0, self.genes[i]))  # Clamp to [-1, 1]
    
    def crossover(self, other: 'Individual', crossover_rate: float = 0.7) -> Tuple['Individual', 'Individual']:
        """Perform crossover with another individual"""
        if random.random() > crossover_rate:
            return copy.deepcopy(self), copy.deepcopy(other)
        
        # Multi-point crossover with bio-inspired segment exchange
        child1_genes = self.genes.copy()
        child2_genes = other.genes.copy()
        
        # Random crossover points (simulating genetic recombination)
        num_points = random.randint(1, min(3, len(self.genes) // 2))
        crossover_points = sorted(random.sample(range(len(self.genes)), num_points))
        
        swap = False
        last_point = 0
        
        for point in crossover_points + [len(self.genes)]:
            if swap:
                child1_genes[last_point:point] = other.genes[last_point:point]
                child2_genes[last_point:point] = self.genes[last_point:point]
            swap = not swap
            last_point = point
        
        child1 = Individual(child1_genes)
        child2 = Individual(child2_genes)
        child1.generation = max(self.generation, other.generation) + 1
        child2.generation = max(self.generation, other.generation) + 1
        
        return child1, child2
    
    def __str__(self):
        return f"Individual(fitness={self.fitness:.3f}, gen={self.generation}, genes={self.genes[:3]}...)"

class GeneticAlgorithm:
    """Evolutionary optimization using genetic algorithms"""
    
    def __init__(self, 
                 population_size: int = 50,
                 gene_length: int = 10,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7,
                 elitism_rate: float = 0.1,
                 max_generations: int = 100):
        
        self.population_size = population_size
        self.gene_length = gene_length
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_rate = elitism_rate
        self.max_generations = max_generations
        
        self.population = []
        self.generation = 0
        self.best_individual = None
        self.fitness_history = []
        
        # Environmental adaptation parameters
        self.adaptive_mutation = True
        self.diversity_threshold = 0.1
        
    def initialize_population(self):
        """Create initial population with random individuals"""
        self.population = []
        for _ in range(self.population_size):
            genes = [random.uniform(-1, 1) for _ in range(self.gene_length)]
            individual = Individual(genes)
            self.population.append(individual)
        
        print(f"[GENETIC] Initialized population of {self.population_size} individuals")
    
    def evaluate_population(self, fitness_function: Callable[[List[float]], float]):
        """Evaluate fitness for entire population"""
        for individual in self.population:
            individual.fitness = fitness_function(individual.genes)
            individual.age += 1
        
        # Sort by fitness (descending)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Update best individual
        if not self.best_individual or self.population[0].fitness > self.best_individual.fitness:
            self.best_individual = copy.deepcopy(self.population[0])
        
        # Track fitness history
        avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
        self.fitness_history.append({
            'generation': self.generation,
            'best_fitness': self.population[0].fitness,
            'average_fitness': avg_fitness,
            'diversity': self.calculate_diversity()
        })
    
    def calculate_diversity(self) -> float:
        """Calculate population diversity for adaptive mechanisms"""
        if len(self.population) < 2:
            return 1.0
        
        total_distance = 0.0
        count = 0
        
        for i in range(len(self.population)):
            for j in range(i + 1, min(i + 10, len(self.population))):  # Sample for efficiency
                distance = sum((a - b) ** 2 for a, b in zip(self.population[i].genes, self.population[j].genes))
                total_distance += math.sqrt(distance)
                count += 1
        
        return total_distance / count if count > 0 else 1.0
    
    def selection(self) -> List[Individual]:
        """Select individuals for reproduction using tournament selection"""
        selected = []
        
        # Elitism - keep best individuals
        num_elite = int(self.population_size * self.elitism_rate)
        selected.extend(copy.deepcopy(self.population[:num_elite]))
        
        # Tournament selection for the rest
        tournament_size = 3
        while len(selected) < self.population_size:
            tournament = random.sample(self.population, min(tournament_size, len(self.population)))
            tournament.sort(key=lambda x: x.fitness, reverse=True)
            selected.append(copy.deepcopy(tournament[0]))
        
        return selected
    
    def evolve_generation(self, fitness_function: Callable[[List[float]], float]):
        """Evolve one generation"""
        # Evaluate fitness
        self.evaluate_population(fitness_function)
        
        # Adaptive mutation based on diversity
        if self.adaptive_mutation:
            diversity = self.calculate_diversity()
            if diversity < self.diversity_threshold:
                self.mutation_rate = min(0.3, self.mutation_rate * 1.1)  # Increase mutation
            else:
                self.mutation_rate = max(0.05, self.mutation_rate * 0.95)  # Decrease mutation
        
        # Selection
        selected = self.selection()
        
        # Crossover and mutation
        new_population = []
        
        # Keep elite
        num_elite = int(self.population_size * self.elitism_rate)
        new_population.extend(selected[:num_elite])
        
        # Generate offspring
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = parent1.crossover(parent2, self.crossover_rate)
            
            child1.mutate(self.mutation_rate)
            child2.mutate(self.mutation_rate)
            
            new_population.extend([child1, child2])
        
        # Trim to exact population size
        self.population = new_population[:self.population_size]
        self.generation += 1
    
    def optimize(self, fitness_function: Callable[[List[float]], float], 
                target_fitness: Optional[float] = None,
                verbose: bool = True) -> Individual:
        """Run the complete genetic algorithm optimization"""
        
        self.initialize_population()
        
        for gen in range(self.max_generations):
            self.evolve_generation(fitness_function)
            
            if verbose and gen % 10 == 0:
                best_fitness = self.population[0].fitness
                avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
                diversity = self.calculate_diversity()
                
                print(f"Gen {gen:3d}: Best={best_fitness:.4f}, Avg={avg_fitness:.4f}, "
                      f"Diversity={diversity:.3f}, MutRate={self.mutation_rate:.3f}")
            
            # Early stopping if target reached
            if target_fitness and self.population[0].fitness >= target_fitness:
                print(f"[TARGET] Target fitness {target_fitness} reached at generation {gen}")
                break
        
        print(f"[EVOLUTION] Complete. Best fitness: {self.best_individual.fitness:.4f}")
        return self.best_individual

# Swarm Intelligence - Particle Swarm Optimization
class Particle:
    """Particle in PSO swarm"""
    
    def __init__(self, dimensions: int, bounds: Tuple[float, float] = (-1.0, 1.0)):
        self.position = np.random.uniform(bounds[0], bounds[1], dimensions)
        self.velocity = np.random.uniform(-0.1, 0.1, dimensions)
        self.best_position = self.position.copy()
        self.best_fitness = float('-inf')
        self.fitness = float('-inf')
        
    def update_velocity(self, global_best_position: np.ndarray, 
                       w: float = 0.7, c1: float = 2.0, c2: float = 2.0):
        """Update particle velocity"""
        r1, r2 = np.random.random(2)
        
        cognitive = c1 * r1 * (self.best_position - self.position)
        social = c2 * r2 * (global_best_position - self.position)
        
        self.velocity = w * self.velocity + cognitive + social
        
        # Velocity clamping
        max_velocity = 0.5
        self.velocity = np.clip(self.velocity, -max_velocity, max_velocity)
    
    def update_position(self, bounds: Tuple[float, float] = (-1.0, 1.0)):
        """Update particle position"""
        self.position += self.velocity
        self.position = np.clip(self.position, bounds[0], bounds[1])

class ParticleSwarmOptimization:
    """Particle Swarm Optimization algorithm"""
    
    def __init__(self, num_particles: int = 30, dimensions: int = 10,
                 max_iterations: int = 100, bounds: Tuple[float, float] = (-1.0, 1.0)):
        
        self.num_particles = num_particles
        self.dimensions = dimensions
        self.max_iterations = max_iterations
        self.bounds = bounds
        
        self.swarm = [Particle(dimensions, bounds) for _ in range(num_particles)]
        self.global_best_position = np.random.uniform(bounds[0], bounds[1], dimensions)
        self.global_best_fitness = float('-inf')
        self.fitness_history = []
        
        # PSO parameters (adaptive)
        self.w = 0.9  # Inertia weight
        self.c1 = 2.0  # Cognitive parameter
        self.c2 = 2.0  # Social parameter
        
    def optimize(self, fitness_function: Callable[[np.ndarray], float], 
                verbose: bool = True) -> Tuple[np.ndarray, float]:
        """Run PSO optimization"""
        
        print(f"[PSO] Starting with {self.num_particles} particles")
        
        for iteration in range(self.max_iterations):
            # Evaluate all particles
            for particle in self.swarm:
                particle.fitness = fitness_function(particle.position)
                
                # Update personal best
                if particle.fitness > particle.best_fitness:
                    particle.best_fitness = particle.fitness
                    particle.best_position = particle.position.copy()
                
                # Update global best
                if particle.fitness > self.global_best_fitness:
                    self.global_best_fitness = particle.fitness
                    self.global_best_position = particle.position.copy()
            
            # Update velocities and positions
            # Adaptive inertia weight (decreases over time)
            self.w = 0.9 - 0.4 * iteration / self.max_iterations
            
            for particle in self.swarm:
                particle.update_velocity(self.global_best_position, self.w, self.c1, self.c2)
                particle.update_position(self.bounds)
            
            # Track progress
            avg_fitness = np.mean([p.fitness for p in self.swarm])
            self.fitness_history.append({
                'iteration': iteration,
                'best_fitness': self.global_best_fitness,
                'average_fitness': avg_fitness
            })
            
            if verbose and iteration % 10 == 0:
                print(f"Iter {iteration:3d}: Best={self.global_best_fitness:.4f}, "
                      f"Avg={avg_fitness:.4f}, w={self.w:.3f}")
        
        print(f"[PSO] Complete. Best fitness: {self.global_best_fitness:.4f}")
        return self.global_best_position, self.global_best_fitness

# Ant Colony Optimization
class Ant:
    """Individual ant in the colony"""
    
    def __init__(self, num_variables: int):
        self.num_variables = num_variables
        self.solution = []
        self.fitness = 0.0
        
    def construct_solution(self, pheromones: np.ndarray, heuristic: np.ndarray, 
                          alpha: float = 1.0, beta: float = 2.0):
        """Construct solution using pheromone trails and heuristic information"""
        self.solution = []
        
        for var in range(self.num_variables):
            # Probabilistic selection based on pheromone and heuristic
            probabilities = (pheromones[var] ** alpha) * (heuristic[var] ** beta)
            probabilities = probabilities / np.sum(probabilities)
            
            # Select value based on probability distribution
            selected_idx = np.random.choice(len(probabilities), p=probabilities)
            value = (selected_idx / len(probabilities)) * 2 - 1  # Scale to [-1, 1]
            self.solution.append(value)

class AntColonyOptimization:
    """Ant Colony Optimization for continuous problems"""
    
    def __init__(self, num_ants: int = 25, num_variables: int = 10, 
                 max_iterations: int = 100, evaporation_rate: float = 0.1):
        
        self.num_ants = num_ants
        self.num_variables = num_variables
        self.max_iterations = max_iterations
        self.evaporation_rate = evaporation_rate
        
        # Discretization for continuous problems
        self.num_bins = 20
        self.pheromones = np.ones((num_variables, self.num_bins))
        self.heuristic = np.ones((num_variables, self.num_bins))
        
        self.best_solution = None
        self.best_fitness = float('-inf')
        self.fitness_history = []
        
    def optimize(self, fitness_function: Callable[[List[float]], float], 
                verbose: bool = True) -> Tuple[List[float], float]:
        """Run ACO optimization"""
        
        print(f"[ACO] Starting with {self.num_ants} ants")
        
        for iteration in range(self.max_iterations):
            ants = [Ant(self.num_variables) for _ in range(self.num_ants)]
            
            # Construct solutions
            for ant in ants:
                ant.construct_solution(self.pheromones, self.heuristic)
                ant.fitness = fitness_function(ant.solution)
                
                # Update best solution
                if ant.fitness > self.best_fitness:
                    self.best_fitness = ant.fitness
                    self.best_solution = ant.solution.copy()
            
            # Update pheromones
            self.pheromones *= (1 - self.evaporation_rate)  # Evaporation
            
            # Pheromone deposition
            for ant in ants:
                if ant.fitness > 0:  # Only deposit if fitness is positive
                    for var_idx, value in enumerate(ant.solution):
                        bin_idx = int((value + 1) / 2 * (self.num_bins - 1))  # Map to bin
                        bin_idx = max(0, min(self.num_bins - 1, bin_idx))
                        self.pheromones[var_idx][bin_idx] += ant.fitness
            
            # Track progress
            avg_fitness = np.mean([ant.fitness for ant in ants])
            self.fitness_history.append({
                'iteration': iteration,
                'best_fitness': self.best_fitness,
                'average_fitness': avg_fitness
            })
            
            if verbose and iteration % 10 == 0:
                print(f"Iter {iteration:3d}: Best={self.best_fitness:.4f}, Avg={avg_fitness:.4f}")
        
        print(f"[ACO] Complete. Best fitness: {self.best_fitness:.4f}")
        return self.best_solution, self.best_fitness

# Bio-Inspired Optimization Suite
class BiologicalOptimizer:
    """Unified interface for bio-inspired optimization algorithms"""
    
    def __init__(self):
        self.algorithms = {
            'genetic': GeneticAlgorithm,
            'pso': ParticleSwarmOptimization,
            'aco': AntColonyOptimization
        }
        self.results_history = []
    
    def optimize(self, algorithm: str, fitness_function: Callable, 
                dimensions: int = 10, **kwargs) -> Dict[str, Any]:
        """Run optimization with specified algorithm"""
        
        if algorithm not in self.algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        print(f"[BIO-OPT] Running {algorithm.upper()} optimization...")
        
        start_time = time.time()
        
        if algorithm == 'genetic':
            # Filter kwargs for GeneticAlgorithm constructor
            ga_kwargs = {k: v for k, v in kwargs.items() 
                        if k in ['population_size', 'mutation_rate', 'crossover_rate', 
                                'elitism_rate', 'max_generations']}
            ga = GeneticAlgorithm(gene_length=dimensions, **ga_kwargs)
            best_individual = ga.optimize(fitness_function)
            result = {
                'algorithm': algorithm,
                'best_solution': best_individual.genes,
                'best_fitness': best_individual.fitness,
                'generations': ga.generation,
                'fitness_history': ga.fitness_history,
                'computation_time': time.time() - start_time
            }
            
        elif algorithm == 'pso':
            # Filter kwargs for PSO constructor
            pso_kwargs = {k: v for k, v in kwargs.items() 
                         if k in ['num_particles', 'max_iterations', 'bounds']}
            pso = ParticleSwarmOptimization(dimensions=dimensions, **pso_kwargs)
            best_position, best_fitness = pso.optimize(fitness_function)
            result = {
                'algorithm': algorithm,
                'best_solution': best_position.tolist(),
                'best_fitness': best_fitness,
                'iterations': pso.max_iterations,
                'fitness_history': pso.fitness_history,
                'computation_time': time.time() - start_time
            }
            
        elif algorithm == 'aco':
            # Filter kwargs for ACO constructor
            aco_kwargs = {k: v for k, v in kwargs.items() 
                         if k in ['num_ants', 'max_iterations', 'evaporation_rate']}
            aco = AntColonyOptimization(num_variables=dimensions, **aco_kwargs)
            best_solution, best_fitness = aco.optimize(fitness_function)
            result = {
                'algorithm': algorithm,
                'best_solution': best_solution,
                'best_fitness': best_fitness,
                'iterations': aco.max_iterations,
                'fitness_history': aco.fitness_history,
                'computation_time': time.time() - start_time
            }
        
        self.results_history.append(result)
        
        print(f"[SUCCESS] {algorithm.upper()} optimization completed in {result['computation_time']:.2f}s")
        print(f"[RESULT] Best fitness: {result['best_fitness']:.6f}")
        
        return result
    
    def compare_algorithms(self, fitness_function: Callable, dimensions: int = 10,
                          algorithms: List[str] = None) -> Dict[str, Any]:
        """Compare multiple algorithms on the same problem"""
        
        if algorithms is None:
            algorithms = ['genetic', 'pso', 'aco']
        
        print(f"[COMPARE] Comparing algorithms: {algorithms}")
        results = {}
        
        for algo in algorithms:
            try:
                result = self.optimize(algo, fitness_function, dimensions, 
                                     max_generations=50, max_iterations=50)
                results[algo] = result
            except Exception as e:
                print(f"[ERROR] {algo} failed: {e}")
                results[algo] = {'error': str(e)}
        
        # Find best overall
        best_algo = max([r for r in results.values() if 'error' not in r], 
                       key=lambda x: x['best_fitness'], default=None)
        
        if best_algo:
            print(f"[WINNER] {best_algo['algorithm'].upper()} "
                  f"with fitness {best_algo['best_fitness']:.6f}")
        
        return results

# Test functions for optimization
def sphere_function(x):
    """Sphere function (global minimum at origin)"""
    return -sum(xi**2 for xi in x)  # Negative for maximization

def rastrigin_function(x):
    """Rastrigin function (highly multimodal)"""
    n = len(x)
    A = 10
    return -(A * n + sum(xi**2 - A * math.cos(2 * math.pi * xi) for xi in x))

def rosenbrock_function(x):
    """Rosenbrock function (banana function)"""
    result = 0
    for i in range(len(x) - 1):
        result += 100 * (x[i+1] - x[i]**2)**2 + (1 - x[i])**2
    return -result

def mycelium_growth_function(x):
    """Bio-inspired fitness function for mycelium growth optimization"""
    if len(x) < 6:
        return 0
    
    # Parameters: [temperature_factor, humidity_factor, nutrients, ph_factor, light, co2]
    temp_opt = 1 - abs(x[0] - 0.7)**2  # Optimal around 0.7
    humidity_opt = 1 - abs(x[1] - 0.8)**2  # Optimal around 0.8
    nutrients = max(0, x[2])  # Nutrients should be positive
    ph_opt = 1 - abs(x[3] - 0.3)**2  # Optimal around 0.3 (slightly acidic)
    light_factor = 1 / (1 + abs(x[4]))  # Lower light preferred
    co2_factor = max(0, x[5])  # CO2 should be positive
    
    # Combined fitness with interaction effects
    base_fitness = temp_opt * humidity_opt * nutrients * ph_opt * light_factor * co2_factor
    
    # Bonus for balanced conditions
    balance_bonus = 1.0 / (1 + sum(abs(xi) for xi in x) / len(x))
    
    return base_fitness + balance_bonus

if __name__ == "__main__":
    # Demonstration
    print("[DEMO] Bio-Inspired Algorithms Demo")
    print("=" * 40)
    
    optimizer = BiologicalOptimizer()
    
    # Test mycelium growth optimization
    print("\n[MYCELIUM] Optimizing Growth Conditions")
    results = optimizer.compare_algorithms(mycelium_growth_function, dimensions=6)
    
    # Show best solution
    best_result = max([r for r in results.values() if 'error' not in r], 
                     key=lambda x: x['best_fitness'])
    
    print(f"\n[OPTIMAL] Growth Conditions:")
    parameters = ['Temperature', 'Humidity', 'Nutrients', 'pH', 'Light', 'CO2']
    for i, (param, value) in enumerate(zip(parameters, best_result['best_solution'])):
        print(f"  {param}: {value:.3f}")
    
    print(f"\n[MAX] Growth Fitness: {best_result['best_fitness']:.6f}")