"""
Mycelium-EI-Lang Interpreter
Core runtime for bio-inspired programming language
"""

import ast
import sys
import random
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
import json


class MyceliumInterpreter:
    """Main interpreter for Mycelium-EI-Lang"""
    
    def __init__(self):
        self.environment = {}
        self.globals = {}
        self.functions = {}
        self.cultivation_systems = {}
        self.bio_networks = {}
        
        # Register built-in functions
        self._register_builtins()
    
    def _register_builtins(self):
        """Register built-in functions"""
        self.globals.update({
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'genetic_optimize': self._genetic_optimize,
            'swarm_optimize': self._swarm_optimize,
            'ant_optimize': self._ant_optimize,
            'create_bio_network': self._create_bio_network,
            'train_bio_network': self._train_bio_network,
            'create_cultivation': self._create_cultivation,
            'monitor_cultivation': self._monitor_cultivation,
            'quantum_entangle': self._quantum_entangle,
        })
    
    def execute(self, code: str) -> Any:
        """Execute Mycelium code"""
        try:
            # Parse code
            tree = ast.parse(code)
            
            # Execute statements
            result = None
            for node in tree.body:
                result = self._execute_node(node)
            
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def _execute_node(self, node: ast.AST) -> Any:
        """Execute an AST node"""
        if isinstance(node, ast.FunctionDef):
            self.functions[node.name] = node
            return None
        
        elif isinstance(node, ast.Assign):
            value = self._evaluate(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.globals[target.id] = value
            return value
        
        elif isinstance(node, ast.Expr):
            return self._evaluate(node.value)
        
        elif isinstance(node, ast.If):
            condition = self._evaluate(node.test)
            if condition:
                for stmt in node.body:
                    self._execute_node(stmt)
            elif node.orelse:
                for stmt in node.orelse:
                    self._execute_node(stmt)
        
        elif isinstance(node, ast.While):
            while self._evaluate(node.test):
                for stmt in node.body:
                    self._execute_node(stmt)
        
        elif isinstance(node, ast.For):
            iterator = self._evaluate(node.iter)
            for value in iterator:
                if isinstance(node.target, ast.Name):
                    self.globals[node.target.id] = value
                for stmt in node.body:
                    self._execute_node(stmt)
        
        elif isinstance(node, ast.Return):
            return self._evaluate(node.value) if node.value else None
        
        return None
    
    def _evaluate(self, node: ast.AST) -> Any:
        """Evaluate an expression"""
        if isinstance(node, ast.Constant):
            return node.value
        
        elif isinstance(node, ast.Name):
            return self.globals.get(node.id, None)
        
        elif isinstance(node, ast.BinOp):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
            elif isinstance(node.op, ast.Mod):
                return left % right
            elif isinstance(node.op, ast.Pow):
                return left ** right
        
        elif isinstance(node, ast.Compare):
            left = self._evaluate(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._evaluate(comparator)
                
                if isinstance(op, ast.Eq):
                    if not (left == right):
                        return False
                elif isinstance(op, ast.NotEq):
                    if not (left != right):
                        return False
                elif isinstance(op, ast.Lt):
                    if not (left < right):
                        return False
                elif isinstance(op, ast.LtE):
                    if not (left <= right):
                        return False
                elif isinstance(op, ast.Gt):
                    if not (left > right):
                        return False
                elif isinstance(op, ast.GtE):
                    if not (left >= right):
                        return False
                
                left = right
            return True
        
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name and func_name in self.globals:
                func = self.globals[func_name]
                args = [self._evaluate(arg) for arg in node.args]
                
                if callable(func):
                    return func(*args)
                elif func_name in self.functions:
                    return self._call_function(self.functions[func_name], args)
        
        elif isinstance(node, ast.List):
            return [self._evaluate(elt) for elt in node.elts]
        
        elif isinstance(node, ast.Dict):
            return {
                self._evaluate(k): self._evaluate(v)
                for k, v in zip(node.keys, node.values)
            }
        
        return None
    
    def _call_function(self, func_def: ast.FunctionDef, args: List[Any]) -> Any:
        """Call a user-defined function"""
        # Save current globals
        saved_globals = self.globals.copy()
        
        # Set parameters
        for param, arg in zip(func_def.args.args, args):
            self.globals[param.arg] = arg
        
        # Execute function body
        result = None
        for stmt in func_def.body:
            result = self._execute_node(stmt)
            if isinstance(stmt, ast.Return):
                break
        
        # Restore globals
        self.globals = saved_globals
        
        return result
    
    # Bio-computing functions
    def _genetic_optimize(self, fitness_func: str, dimensions: int, 
                         population_size: int, generations: int) -> Dict:
        """Genetic algorithm optimization"""
        # Initialize population
        population = np.random.rand(population_size, dimensions)
        
        best_fitness = float('-inf')
        best_solution = None
        
        for gen in range(generations):
            # Evaluate fitness (simplified)
            fitness = np.array([
                -np.sum(individual ** 2)  # Sphere function
                for individual in population
            ])
            
            # Track best
            gen_best_idx = np.argmax(fitness)
            if fitness[gen_best_idx] > best_fitness:
                best_fitness = fitness[gen_best_idx]
                best_solution = population[gen_best_idx].copy()
            
            # Selection (tournament)
            selected = []
            for _ in range(population_size):
                idx1, idx2 = random.sample(range(population_size), 2)
                winner = idx1 if fitness[idx1] > fitness[idx2] else idx2
                selected.append(population[winner].copy())
            
            # Crossover and mutation
            offspring = []
            for i in range(0, population_size - 1, 2):
                parent1, parent2 = selected[i], selected[i + 1]
                
                # Crossover
                if random.random() < 0.7:
                    point = random.randint(1, dimensions - 1)
                    child1 = np.concatenate([parent1[:point], parent2[point:]])
                    child2 = np.concatenate([parent2[:point], parent1[point:]])
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation
                for child in [child1, child2]:
                    if random.random() < 0.01:
                        idx = random.randint(0, dimensions - 1)
                        child[idx] = random.random()
                
                offspring.extend([child1, child2])
            
            population = np.array(offspring[:population_size])
        
        return {
            'best_solution': best_solution.tolist() if best_solution is not None else None,
            'best_fitness': float(best_fitness),
            'generations': generations
        }
    
    def _swarm_optimize(self, fitness_func: str, dimensions: int,
                       num_particles: int, iterations: int) -> Dict:
        """Particle swarm optimization"""
        # Initialize swarm
        positions = np.random.rand(num_particles, dimensions) * 10 - 5
        velocities = np.random.rand(num_particles, dimensions) * 2 - 1
        
        personal_best_positions = positions.copy()
        personal_best_fitness = np.array([
            -np.sum(pos ** 2) for pos in positions
        ])
        
        global_best_idx = np.argmax(personal_best_fitness)
        global_best_position = personal_best_positions[global_best_idx].copy()
        global_best_fitness = personal_best_fitness[global_best_idx]
        
        w = 0.7  # inertia
        c1 = 1.5  # cognitive
        c2 = 1.5  # social
        
        for _ in range(iterations):
            # Update velocities and positions
            for i in range(num_particles):
                r1, r2 = random.random(), random.random()
                
                velocities[i] = (w * velocities[i] + 
                                c1 * r1 * (personal_best_positions[i] - positions[i]) +
                                c2 * r2 * (global_best_position - positions[i]))
                
                positions[i] += velocities[i]
                
                # Evaluate fitness
                fitness = -np.sum(positions[i] ** 2)
                
                # Update personal best
                if fitness > personal_best_fitness[i]:
                    personal_best_fitness[i] = fitness
                    personal_best_positions[i] = positions[i].copy()
                
                # Update global best
                if fitness > global_best_fitness:
                    global_best_fitness = fitness
                    global_best_position = positions[i].copy()
        
        return {
            'best_solution': global_best_position.tolist(),
            'best_fitness': float(global_best_fitness),
            'iterations': iterations
        }
    
    def _ant_optimize(self, fitness_func: str, dimensions: int,
                     num_ants: int, iterations: int) -> Dict:
        """Ant colony optimization (simplified)"""
        # Initialize pheromone trails
        pheromones = np.ones((dimensions, 10)) * 0.1
        
        best_solution = None
        best_fitness = float('-inf')
        
        for _ in range(iterations):
            solutions = []
            
            for _ in range(num_ants):
                # Build solution
                solution = []
                for d in range(dimensions):
                    # Select based on pheromone levels
                    probs = pheromones[d] / np.sum(pheromones[d])
                    choice = np.random.choice(10, p=probs)
                    solution.append(choice / 10.0)
                
                solutions.append(solution)
            
            # Evaluate solutions
            fitness_values = [
                -np.sum(np.array(sol) ** 2) for sol in solutions
            ]
            
            # Update best
            iter_best_idx = np.argmax(fitness_values)
            if fitness_values[iter_best_idx] > best_fitness:
                best_fitness = fitness_values[iter_best_idx]
                best_solution = solutions[iter_best_idx]
            
            # Update pheromones
            pheromones *= 0.9  # evaporation
            
            for sol, fitness in zip(solutions, fitness_values):
                if fitness > 0:
                    for d, val in enumerate(sol):
                        idx = int(val * 10)
                        if idx < 10:
                            pheromones[d, idx] += fitness
        
        return {
            'best_solution': best_solution,
            'best_fitness': float(best_fitness),
            'iterations': iterations
        }
    
    def _create_bio_network(self, network_id: str, input_size: int,
                           hidden_size: int, output_size: int) -> str:
        """Create a bio-inspired neural network"""
        self.bio_networks[network_id] = {
            'input_size': input_size,
            'hidden_size': hidden_size,
            'output_size': output_size,
            'weights_ih': np.random.randn(hidden_size, input_size) * 0.1,
            'weights_ho': np.random.randn(output_size, hidden_size) * 0.1,
            'bias_h': np.zeros(hidden_size),
            'bias_o': np.zeros(output_size)
        }
        return f"Bio-network '{network_id}' created"
    
    def _train_bio_network(self, network_id: str, data: List, 
                          labels: List, epochs: int) -> Dict:
        """Train a bio-inspired neural network"""
        if network_id not in self.bio_networks:
            return {'error': f"Network '{network_id}' not found"}
        
        network = self.bio_networks[network_id]
        
        # Simplified training (would implement backprop)
        for _ in range(epochs):
            # Forward pass
            for x, y in zip(data, labels):
                x = np.array(x)
                hidden = np.tanh(network['weights_ih'] @ x + network['bias_h'])
                output = network['weights_ho'] @ hidden + network['bias_o']
                
                # Update weights (simplified)
                network['weights_ho'] += np.random.randn(*network['weights_ho'].shape) * 0.001
                network['weights_ih'] += np.random.randn(*network['weights_ih'].shape) * 0.001
        
        return {'status': 'trained', 'epochs': epochs}
    
    def _create_cultivation(self, cultivation_id: str) -> str:
        """Create a cultivation monitoring system"""
        self.cultivation_systems[cultivation_id] = {
            'temperature': 24.0,
            'humidity': 85.0,
            'nutrients': 100.0,
            'growth_rate': 1.0,
            'health': 100.0
        }
        return f"Cultivation system '{cultivation_id}' created"
    
    def _monitor_cultivation(self, cultivation_id: str) -> Dict:
        """Monitor cultivation system status"""
        if cultivation_id not in self.cultivation_systems:
            return {'error': f"Cultivation '{cultivation_id}' not found"}
        
        system = self.cultivation_systems[cultivation_id]
        
        # Simulate growth
        system['nutrients'] *= 0.99
        system['growth_rate'] = system['nutrients'] / 100 * system['temperature'] / 24
        system['health'] = min(100, system['humidity'] * system['growth_rate'])
        
        return system.copy()
    
    def _quantum_entangle(self, qubit1: int, qubit2: int) -> str:
        """Create quantum entanglement (simulated)"""
        state = random.choice(['00', '11'])
        return f"Qubits {qubit1} and {qubit2} entangled in state |{state}⟩"


def main():
    """Main entry point for CLI"""
    interpreter = MyceliumInterpreter()
    
    if len(sys.argv) > 1:
        # Execute file
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                code = f.read()
            result = interpreter.execute(code)
            if result is not None:
                print(result)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Interactive mode
        print("Mycelium-EI-Lang v0.1.0")
        print("Type 'exit' to quit\n")
        
        while True:
            try:
                code = input(">>> ")
                if code.lower() == 'exit':
                    break
                
                result = interpreter.execute(code)
                if result is not None:
                    print(result)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()