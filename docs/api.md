# 📚 API Documentation

Complete reference for Mycelium-EI-Lang's built-in functions and Python API.

## Python API

### MyceliumInterpreter Class

The core interpreter for executing Mycelium-EI-Lang code.

```python
from mycelium_ei import MyceliumInterpreter

interpreter = MyceliumInterpreter()
result = interpreter.execute("print('Hello, Mycelium!')")
```

#### Methods

##### `execute(code: str) -> Any`

Execute Mycelium-EI-Lang code and return the result.

**Parameters:**
- `code` (str): The Mycelium source code to execute

**Returns:**
- `Any`: The result of the last expression in the code

**Example:**
```python
result = interpreter.execute('''
    let x = genetic_optimize("sphere", 5, 20, 50)
    return x.best_fitness
''')
print(f"Best fitness: {result}")
```

### Convenience Functions

#### `run_code(source: str) -> None`

Execute Mycelium code directly.

```python
from mycelium_ei import run_code

run_code('''
    print("Running bio-optimization...")
    let result = swarm_optimize("rastrigin", 10, 30, 100)
    print("Completed:", result.best_solution)
''')
```

#### `run_file(filename: str) -> None`

Execute a Mycelium file.

```python
from mycelium_ei import run_file

run_file("my_algorithm.myc")
```

## Built-in Functions

### Genetic Algorithm Functions

#### `genetic_optimize(fitness_function, dimensions, population_size, generations) -> Dict`

Run genetic algorithm optimization.

**Parameters:**
- `fitness_function` (str): Name of the fitness function to optimize
- `dimensions` (int): Number of dimensions in the solution space
- `population_size` (int): Size of the population
- `generations` (int): Number of generations to evolve

**Returns:**
- `Dict`: Results containing `best_solution`, `best_fitness`, and `generations`

**Example:**
```mycelium
let result = genetic_optimize("sphere_function", 10, 50, 100)
print("Best solution:", result.best_solution)
print("Best fitness:", result.best_fitness)
```

### Swarm Intelligence Functions

#### `swarm_optimize(fitness_function, dimensions, num_particles, iterations) -> Dict`

Run particle swarm optimization.

**Parameters:**
- `fitness_function` (str): Name of the fitness function to optimize  
- `dimensions` (int): Number of dimensions in the solution space
- `num_particles` (int): Number of particles in the swarm
- `iterations` (int): Number of iterations to run

**Returns:**
- `Dict`: Results containing `best_solution`, `best_fitness`, and `iterations`

**Example:**
```mycelium
let swarm = swarm_optimize("rastrigin", 20, 30, 200)
print("Global optimum:", swarm.best_solution)
```

#### `ant_optimize(fitness_function, dimensions, num_ants, iterations) -> Dict`

Run ant colony optimization.

**Parameters:**
- `fitness_function` (str): Name of the fitness function to optimize
- `dimensions` (int): Number of dimensions in the solution space  
- `num_ants` (int): Number of ants in the colony
- `iterations` (int): Number of iterations to run

**Returns:**
- `Dict`: Results containing `best_solution`, `best_fitness`, and `iterations`

### Bio-Neural Network Functions

#### `create_bio_network(network_id, input_size, hidden_size, output_size) -> str`

Create a bio-inspired neural network.

**Parameters:**
- `network_id` (str): Unique identifier for the network
- `input_size` (int): Number of input neurons
- `hidden_size` (int): Number of hidden layer neurons
- `output_size` (int): Number of output neurons

**Returns:**
- `str`: Confirmation message

**Example:**
```mycelium
let network = create_bio_network("classifier", 784, 128, 10)
print(network)  // "Bio-network 'classifier' created"
```

#### `train_bio_network(network_id, data, labels, epochs) -> Dict`

Train a bio-inspired neural network.

**Parameters:**
- `network_id` (str): ID of the network to train
- `data` (List): Training data samples
- `labels` (List): Corresponding labels
- `epochs` (int): Number of training epochs

**Returns:**
- `Dict`: Training results with `status` and `epochs`

### Cultivation System Functions

#### `create_cultivation(cultivation_id) -> str`

Create a cultivation monitoring system.

**Parameters:**
- `cultivation_id` (str): Unique identifier for the cultivation system

**Returns:**
- `str`: Confirmation message

**Example:**
```mycelium
let bioreactor = create_cultivation("reactor_1")
print(bioreactor)  // "Cultivation system 'reactor_1' created"
```

#### `monitor_cultivation(cultivation_id) -> Dict`

Monitor cultivation system status.

**Parameters:**
- `cultivation_id` (str): ID of the cultivation system

**Returns:**
- `Dict`: System status including `temperature`, `humidity`, `nutrients`, `growth_rate`, and `health`

**Example:**
```mycelium
let status = monitor_cultivation("reactor_1")
print("Temperature:", status.temperature)
print("Growth rate:", status.growth_rate)
print("Health:", status.health)
```

### Quantum Computing Functions

#### `quantum_entangle(qubit1, qubit2) -> str`

Create quantum entanglement between two qubits.

**Parameters:**
- `qubit1` (int): Index of the first qubit
- `qubit2` (int): Index of the second qubit

**Returns:**
- `str`: Description of the entangled state

**Example:**
```mycelium
let entangled = quantum_entangle(0, 1)
print(entangled)  // "Qubits 0 and 1 entangled in state |00⟩"
```

### Utility Functions

#### `print(*args) -> None`

Print values to the console.

**Parameters:**
- `*args`: Variable number of arguments to print

**Example:**
```mycelium
print("Hello", "world", 123)
print("Result:", result.best_fitness)
```

#### `len(obj) -> int`

Get the length of an object.

**Parameters:**
- `obj`: Object to measure (list, string, etc.)

**Returns:**
- `int`: Length of the object

#### `range(start, stop=None, step=1) -> List`

Generate a range of numbers.

**Parameters:**
- `start` (int): Starting value (or stop if stop is None)
- `stop` (int, optional): Ending value
- `step` (int): Step size

**Returns:**
- `List[int]`: List of numbers in the range

## Node.js API

### MyceliumCompiler Class

```javascript
const { MyceliumCompiler } = require('@michaelcrowe11/mycelium-ei-lang');

const compiler = new MyceliumCompiler({
    pythonPath: 'python3',  // Optional
    debug: false           // Optional
});
```

#### Methods

##### `compile(code) -> Promise<Object>`

Compile Mycelium code.

**Parameters:**
- `code` (string): Mycelium source code

**Returns:**
- `Promise<Object>`: Compilation result

**Example:**
```javascript
const result = await compiler.compile(`
    function fibonacci(n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }
`);

console.log(result.success);  // true
```

##### `run(filePath) -> Promise<Object>`

Execute a Mycelium file.

**Parameters:**
- `filePath` (string): Path to the .myc file

**Returns:**
- `Promise<Object>`: Execution result

### BioOptimizer Class

```javascript
const { BioOptimizer } = require('@michaelcrowe11/mycelium-ei-lang');

const optimizer = new BioOptimizer();
```

#### Methods

##### `genetic(options) -> Promise<Object>`

Run genetic algorithm optimization.

**Parameters:**
- `options` (Object): Configuration object
  - `fitness` (string): Fitness function name
  - `dimensions` (number): Problem dimensions
  - `population` (number): Population size
  - `generations` (number): Number of generations

**Example:**
```javascript
const result = await optimizer.genetic({
    fitness: 'sphere',
    dimensions: 10,
    population: 50,
    generations: 100
});

console.log('Best solution:', result.solution);
```

##### `swarm(options) -> Promise<Object>`

Run particle swarm optimization.

##### `antColony(options) -> Promise<Object>`

Run ant colony optimization.

## WebAssembly API

### MyceliumWASM Class

```javascript
const mycelium = new MyceliumWASM();
await mycelium.initialize();
```

#### Methods

##### `geneticAlgorithm(options) -> Object`

Run genetic algorithm in WebAssembly.

**Parameters:**
- `options` (Object): Algorithm configuration
  - `populationSize` (number): Size of population
  - `dimensions` (number): Problem dimensions  
  - `generations` (number): Number of generations
  - `mutationRate` (number): Mutation rate
  - `fitnessFunc` (function): Fitness function

**Example:**
```javascript
const result = mycelium.geneticAlgorithm({
    populationSize: 50,
    dimensions: 10,
    generations: 100,
    mutationRate: 0.01,
    fitnessFunc: (x) => -x.reduce((a, b) => a + b*b, 0)
});
```

##### `particleSwarmOptimization(options) -> Object`

Run particle swarm optimization in WebAssembly.

##### `quantumCircuit(numQubits) -> Object`

Create a quantum circuit simulator.

**Returns an object with methods:**
- `hadamard(qubitIdx)`: Apply Hadamard gate
- `pauliX(qubitIdx)`: Apply Pauli-X gate
- `cnot(controlIdx, targetIdx)`: Apply CNOT gate
- `measure(qubitIdx)`: Measure a qubit
- `measureAll()`: Measure all qubits

**Example:**
```javascript
const circuit = mycelium.quantumCircuit(2);
circuit.hadamard(0);
circuit.cnot(0, 1);
const measurements = circuit.measureAll();
console.log('Bell state measurement:', measurements);
```

## Error Handling

### Python Exceptions

```python
from mycelium_ei import MyceliumInterpreter

interpreter = MyceliumInterpreter()

try:
    result = interpreter.execute("invalid_function()")
except Exception as e:
    print(f"Execution error: {e}")
```

### JavaScript Error Handling  

```javascript
try {
    const result = await compiler.compile("invalid syntax");
} catch (error) {
    console.error('Compilation failed:', error.message);
}
```

## Type Definitions

### TypeScript Definitions

```typescript
interface OptimizationResult {
    solution: number[];
    fitness: number;
    generations?: number;
    iterations?: number;
}

interface NetworkTrainingResult {
    status: string;
    epochs: number;
    accuracy?: number;
    loss?: number;
}

interface CultivationStatus {
    temperature: number;
    humidity: number;
    nutrients: number;
    growth_rate: number;
    health: number;
}

class MyceliumCompiler {
    constructor(options?: {
        pythonPath?: string;
        debug?: boolean;
    });
    
    compile(code: string): Promise<{
        success: boolean;
        output?: string;
    }>;
    
    run(filePath: string): Promise<{
        success: boolean;
        output?: string;
    }>;
}
```

## Configuration

### Environment Variables

- `MYCELIUM_PYTHON_PATH`: Path to Python interpreter
- `MYCELIUM_DEBUG`: Enable debug output (0 or 1)
- `MYCELIUM_GPU_ENABLED`: Enable GPU acceleration (0 or 1)
- `MYCELIUM_MAX_WORKERS`: Maximum parallel workers

### Python Configuration

```python
from mycelium_ei import MyceliumInterpreter

interpreter = MyceliumInterpreter()
interpreter.set_config('max_workers', 8)
interpreter.set_config('enable_gpu', True)
interpreter.set_config('debug_mode', False)
```

## Performance Tips

1. **Use appropriate population sizes**: Start with 20-50 for small problems
2. **Enable GPU acceleration**: For large-scale optimizations
3. **Batch operations**: Process multiple problems together
4. **Use WebAssembly**: For browser-based applications
5. **Profile your fitness functions**: They're often the bottleneck

## Examples by Use Case

### Bioinformatics
- [Protein folding prediction](examples.md#protein-folding-prediction)
- [Gene sequence analysis](examples.md#gene-sequence-analysis)
- [Phylogenetic tree construction](examples.md#phylogenetic-trees)

### Machine Learning
- [Neural architecture search](examples.md#neural-architecture-search)
- [Hyperparameter optimization](examples.md#hyperparameter-optimization)
- [Feature selection](examples.md#feature-selection)

### Financial Modeling
- [Portfolio optimization](examples.md#financial-portfolio-optimization)
- [Risk management](examples.md#risk-management)
- [Algorithmic trading](examples.md#algorithmic-trading)

### Engineering
- [Structural optimization](examples.md#structural-optimization)
- [Control system design](examples.md#control-systems)
- [Resource allocation](examples.md#resource-allocation)

---

**Need help with the API?**

- [View Examples](examples.md) for practical usage
- [Read Language Reference](language-reference.md) for syntax
- [Check GitHub Issues](https://github.com/MichaelCrowe11/pulsar-lang/issues) for known problems
- [Join Discord](#) for community support (coming soon)

[← Examples](examples.md) • [Language Reference →](language-reference.md)