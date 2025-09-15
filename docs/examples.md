# 🚀 Examples Gallery

Explore the power of Mycelium-EI-Lang through practical examples.

## 🧬 Genetic Algorithm Examples

### Basic Optimization

```mycelium
environment {
    temperature: 24.0,
    humidity: 85.0,
    nutrients: 100.0
}

function sphere_fitness(x) {
    let sum = 0
    for i in range(len(x)) {
        sum = sum + (x[i] * x[i])
    }
    return -sum  // Minimize the sphere function
}

function main() {
    print("🧬 Genetic Algorithm Optimization")
    
    let result = genetic_optimize(
        fitness_function="sphere_fitness",
        dimensions=10,
        population_size=50,
        generations=100
    )
    
    print("Best solution:", result.best_solution)
    print("Best fitness:", result.best_fitness)
}
```

### Traveling Salesman Problem

```mycelium
function tsp_fitness(tour) {
    let cities = [
        [0, 0], [1, 2], [3, 1], [5, 2], [6, 4], 
        [4, 4], [3, 6], [1, 5], [2, 3]
    ]
    
    let total_distance = 0
    for i in range(len(tour) - 1) {
        let city1 = cities[tour[i]]
        let city2 = cities[tour[i + 1]]
        
        let dx = city1[0] - city2[0]
        let dy = city1[1] - city2[1]
        total_distance = total_distance + sqrt(dx*dx + dy*dy)
    }
    
    return -total_distance  // Minimize distance
}

function main() {
    print("🗺️ Traveling Salesman Problem")
    
    let tour = genetic_optimize(
        fitness_function="tsp_fitness",
        dimensions=9,
        population_size=100,
        generations=500
    )
    
    print("Optimal tour:", tour.best_solution)
    print("Tour distance:", -tour.best_fitness)
}
```

## 🐜 Swarm Intelligence Examples

### Particle Swarm Optimization

```mycelium
function rastrigin(x) {
    let A = 10
    let n = len(x)
    let sum = A * n
    
    for i in range(n) {
        sum = sum + (x[i]*x[i] - A * cos(2 * pi * x[i]))
    }
    
    return -sum  // Minimize Rastrigin function
}

function main() {
    print("🐜 Particle Swarm Optimization")
    
    let swarm = swarm_optimize(
        fitness_function="rastrigin",
        dimensions=20,
        num_particles=30,
        iterations=200
    )
    
    print("Global optimum:", swarm.best_solution)
    print("Best fitness:", swarm.best_fitness)
}
```

### Multi-Objective Optimization

```mycelium
function multi_objective_fitness(x) {
    // Minimize both objectives
    let obj1 = sum([xi*xi for xi in x])
    let obj2 = sum([(xi-2)*(xi-2) for xi in x])
    
    // Weighted sum approach
    return -(0.5 * obj1 + 0.5 * obj2)
}

function main() {
    print("🎯 Multi-Objective Optimization")
    
    let pareto = swarm_optimize(
        fitness_function="multi_objective_fitness",
        dimensions=5,
        num_particles=40,
        iterations=300
    )
    
    print("Pareto optimal solution:", pareto.best_solution)
}
```

## 🧠 Bio-Neural Networks

### Image Classification Network

```mycelium
function load_mnist_data() {
    // Simplified MNIST data loading
    let train_images = load_dataset("mnist_train_images.csv")
    let train_labels = load_dataset("mnist_train_labels.csv") 
    return [train_images, train_labels]
}

function main() {
    print("🧠 Bio-Neural Network Training")
    
    // Create network: 784 inputs (28x28), 128 hidden, 10 outputs
    let network = create_bio_network("mnist_classifier", 784, 128, 10)
    
    // Load training data
    let [images, labels] = load_mnist_data()
    
    // Train the network
    let training_result = train_bio_network(
        network_id="mnist_classifier",
        data=images,
        labels=labels,
        epochs=50
    )
    
    print("Training completed:", training_result.status)
    print("Final accuracy:", training_result.accuracy)
}
```

### Adaptive Learning Network

```mycelium
function create_adaptive_network() {
    let network = create_bio_network("adaptive", 10, 20, 5)
    
    // Set adaptive learning parameters
    set_network_property(network, "learning_rate", 0.01)
    set_network_property(network, "adaptation_rate", 0.001)
    set_network_property(network, "plasticity", 0.8)
    
    return network
}

function main() {
    print("🔄 Adaptive Neural Network")
    
    let adaptive_net = create_adaptive_network()
    
    // Simulate online learning
    for epoch in range(100) {
        let sample_data = generate_random_data(10, 1)
        let target = compute_target(sample_data)
        
        let result = train_bio_network(
            network_id="adaptive",
            data=[sample_data],
            labels=[target],
            epochs=1
        )
        
        if epoch % 20 == 0 {
            print(f"Epoch {epoch}: Loss = {result.loss}")
        }
    }
}
```

## ⚛️ Quantum Computing Examples

### Quantum Entanglement

```mycelium
function demonstrate_entanglement() {
    print("⚛️ Quantum Entanglement Demonstration")
    
    // Create entangled pair
    let entangled = quantum_entangle(qubit1=0, qubit2=1)
    print("Entangled qubits:", entangled)
    
    // Measure first qubit
    let measurement1 = quantum_measure(0)
    print("Qubit 0 measurement:", measurement1)
    
    // Measure second qubit (should be correlated)
    let measurement2 = quantum_measure(1)
    print("Qubit 1 measurement:", measurement2)
    
    return [measurement1, measurement2]
}

function main() {
    for trial in range(10) {
        let [m1, m2] = demonstrate_entanglement()
        print(f"Trial {trial}: ({m1}, {m2})")
    }
}
```

### Quantum Optimization

```mycelium
function quantum_annealing_optimization() {
    print("🌀 Quantum Annealing Optimization")
    
    // Define problem Hamiltonian
    let problem = quantum_hamiltonian([
        [1, -1, 0, 0],
        [-1, 2, -1, 0], 
        [0, -1, 2, -1],
        [0, 0, -1, 1]
    ])
    
    // Run quantum annealing
    let result = quantum_anneal(
        hamiltonian=problem,
        annealing_time=100,
        temperature_schedule="linear"
    )
    
    print("Ground state energy:", result.energy)
    print("Optimal configuration:", result.state)
    
    return result
}

function main() {
    quantum_annealing_optimization()
}
```

## 🌱 Cultivation Systems

### Bioreactor Monitoring

```mycelium
function setup_bioreactor() {
    print("🌱 Bioreactor Cultivation System")
    
    // Create cultivation environment
    let bioreactor = create_cultivation("bioreactor_alpha")
    
    // Set optimal conditions
    set_cultivation_parameter(bioreactor, "temperature", 37.0)
    set_cultivation_parameter(bioreactor, "pH", 7.2)
    set_cultivation_parameter(bioreactor, "dissolved_oxygen", 80.0)
    set_cultivation_parameter(bioreactor, "agitation_speed", 200)
    
    return bioreactor
}

function monitor_growth_cycle() {
    let reactor = setup_bioreactor()
    
    for hour in range(72) {  // 72-hour cultivation
        let status = monitor_cultivation(reactor)
        
        print(f"Hour {hour}:")
        print(f"  Cell density: {status.cell_density} cells/mL")
        print(f"  Nutrient level: {status.nutrients}%")
        print(f"  Growth rate: {status.growth_rate}")
        
        // Automatic nutrient feeding
        if status.nutrients < 20 {
            add_nutrients(reactor, amount=50)
            print("  🍯 Nutrients added")
        }
        
        // Alert conditions
        if status.temperature > 40 or status.temperature < 35 {
            print("  ⚠️ Temperature warning!")
        }
        
        wait(3600)  // Wait 1 hour
    }
}

function main() {
    monitor_growth_cycle()
}
```

### Ecosystem Simulation

```mycelium
function create_ecosystem() {
    print("🌍 Ecosystem Simulation")
    
    // Create multiple cultivation systems
    let forest = create_cultivation("forest_patch")
    let pond = create_cultivation("water_system")
    let soil = create_cultivation("soil_microbiome")
    
    // Set ecosystem parameters
    set_ecosystem_connection(forest, pond, "water_flow", 0.3)
    set_ecosystem_connection(forest, soil, "nutrient_cycle", 0.8)
    set_ecosystem_connection(pond, soil, "mineral_exchange", 0.5)
    
    return [forest, pond, soil]
}

function simulate_seasonal_changes() {
    let [forest, pond, soil] = create_ecosystem()
    
    let seasons = ["spring", "summer", "autumn", "winter"]
    
    for season in seasons {
        print(f"🗓️ {season.upper()} Season")
        
        // Adjust environmental parameters
        if season == "spring" {
            modify_cultivation(forest, "growth_factor", 1.5)
            modify_cultivation(pond, "algae_bloom", 1.2)
        } else if season == "summer" {
            modify_cultivation(forest, "photosynthesis", 2.0)
            modify_cultivation(pond, "evaporation", 1.8)
        } else if season == "autumn" {
            modify_cultivation(forest, "leaf_drop", 3.0)
            modify_cultivation(soil, "decomposition", 1.6)
        } else {  // winter
            modify_cultivation(forest, "dormancy", 0.3)
            modify_cultivation(pond, "ice_cover", 0.1)
        }
        
        // Monitor ecosystem health
        for month in range(3) {
            let forest_status = monitor_cultivation(forest)
            let pond_status = monitor_cultivation(pond)
            let soil_status = monitor_cultivation(soil)
            
            print(f"  Month {month + 1}:")
            print(f"    Forest biomass: {forest_status.biomass}")
            print(f"    Pond clarity: {pond_status.water_quality}")
            print(f"    Soil richness: {soil_status.nutrients}")
        }
    }
}

function main() {
    simulate_seasonal_changes()
}
```

## 🔬 Advanced Applications

### Protein Folding Prediction

```mycelium
function predict_protein_structure(sequence) {
    print("🧬 Protein Folding Prediction")
    
    // Use genetic algorithm to find optimal folding
    let folding = genetic_optimize(
        fitness_function=lambda coords: calculate_folding_energy(coords, sequence),
        dimensions=len(sequence) * 3,  // 3D coordinates for each amino acid
        population_size=200,
        generations=1000
    )
    
    return folding.best_solution
}

function calculate_folding_energy(coordinates, sequence) {
    // Simplified energy calculation
    let energy = 0
    
    for i in range(len(sequence) - 1) {
        let pos1 = coordinates[i*3:(i+1)*3]
        let pos2 = coordinates[(i+1)*3:(i+2)*3]
        
        // Distance-based energy
        let distance = euclidean_distance(pos1, pos2)
        energy = energy + bond_energy(sequence[i], sequence[i+1], distance)
    }
    
    return -energy  // Minimize energy
}

function main() {
    let protein_sequence = "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSF"
    let structure = predict_protein_structure(protein_sequence)
    
    print("Predicted structure coordinates:", structure)
    visualize_protein_structure(structure, protein_sequence)
}
```

### Financial Portfolio Optimization

```mycelium
function optimize_portfolio(returns, risk_tolerance) {
    print("💰 Portfolio Optimization")
    
    function portfolio_fitness(weights) {
        // Normalize weights to sum to 1
        let total = sum(weights)
        let normalized = [w / total for w in weights]
        
        // Calculate expected return
        let expected_return = sum([w * r for w, r in zip(normalized, returns)])
        
        // Calculate risk (simplified as variance)
        let risk = sum([w * w for w in normalized])
        
        // Risk-adjusted return
        return expected_return - risk_tolerance * risk
    }
    
    let optimal_weights = genetic_optimize(
        fitness_function="portfolio_fitness", 
        dimensions=len(returns),
        population_size=100,
        generations=300
    )
    
    return optimal_weights.best_solution
}

function main() {
    // Historical returns for different assets
    let asset_returns = [0.08, 0.12, 0.06, 0.15, 0.10, 0.07, 0.09]
    let risk_tolerance = 0.5
    
    let weights = optimize_portfolio(asset_returns, risk_tolerance)
    
    print("Optimal portfolio allocation:")
    let assets = ["Stocks", "Bonds", "Real Estate", "Crypto", "Gold", "Cash", "Commodities"]
    
    for i in range(len(assets)) {
        print(f"  {assets[i]}: {weights[i] * 100:.1f}%")
    }
}
```

## 🌐 WebAssembly Examples

### Browser Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>Mycelium-EI-Lang WebAssembly Demo</title>
</head>
<body>
    <h1>🧬 Bio-Algorithm Visualization</h1>
    <canvas id="evolution-canvas" width="800" height="600"></canvas>
    
    <script src="mycelium-wasm.js"></script>
    <script>
        async function runEvolution() {
            const mycelium = new MyceliumWASM();
            await mycelium.initialize();
            
            // Run genetic algorithm
            const result = mycelium.geneticAlgorithm({
                populationSize: 50,
                dimensions: 2,
                generations: 100,
                fitnessFunc: (x) => -(x[0]*x[0] + x[1]*x[1])
            });
            
            console.log('Evolution complete:', result);
            
            // Visualize result
            const canvas = document.getElementById('evolution-canvas');
            const ctx = canvas.getContext('2d');
            
            // Draw population
            result.population.forEach(individual => {
                const x = (individual[0] + 5) / 10 * canvas.width;
                const y = (individual[1] + 5) / 10 * canvas.height;
                
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, Math.PI * 2);
                ctx.fillStyle = '#4CAF50';
                ctx.fill();
            });
            
            // Highlight best solution
            const best = result.solution;
            const bestX = (best[0] + 5) / 10 * canvas.width;
            const bestY = (best[1] + 5) / 10 * canvas.height;
            
            ctx.beginPath();
            ctx.arc(bestX, bestY, 8, 0, Math.PI * 2);
            ctx.fillStyle = '#FF4444';
            ctx.fill();
        }
        
        runEvolution();
    </script>
</body>
</html>
```

## 📊 Performance Examples

### Benchmark Comparison

```mycelium
function benchmark_algorithms() {
    print("📊 Algorithm Performance Benchmark")
    
    let problem_sizes = [10, 50, 100, 500, 1000]
    let algorithms = ["genetic", "swarm", "ant_colony"]
    
    for size in problem_sizes {
        print(f"\nProblem size: {size} dimensions")
        
        for algorithm in algorithms {
            let start_time = current_time()
            
            if algorithm == "genetic" {
                genetic_optimize("sphere", size, 50, 100)
            } else if algorithm == "swarm" {
                swarm_optimize("sphere", size, 30, 100)  
            } else if algorithm == "ant_colony" {
                ant_optimize("sphere", size, 20, 100)
            }
            
            let elapsed = current_time() - start_time
            print(f"  {algorithm}: {elapsed:.2f} seconds")
        }
    }
}

function gpu_acceleration_test() {
    print("🚀 GPU Acceleration Test")
    
    // Enable GPU acceleration
    enable_gpu_acceleration()
    
    let start = current_time()
    let result_gpu = genetic_optimize("sphere", 1000, 500, 200)
    let gpu_time = current_time() - start
    
    // Disable GPU acceleration
    disable_gpu_acceleration()
    
    start = current_time()
    let result_cpu = genetic_optimize("sphere", 1000, 500, 200)
    let cpu_time = current_time() - start
    
    print(f"CPU time: {cpu_time:.2f} seconds")
    print(f"GPU time: {gpu_time:.2f} seconds") 
    print(f"Speedup: {cpu_time / gpu_time:.2f}x")
}

function main() {
    benchmark_algorithms()
    gpu_acceleration_test()
}
```

---

## 📚 More Examples

- **[Basic Examples](https://github.com/MichaelCrowe11/pulsar-lang/tree/main/examples)** - Simple getting started examples
- **[Advanced Algorithms](https://github.com/MichaelCrowe11/pulsar-lang/tree/main/examples/advanced)** - Complex optimization problems
- **[Real-world Applications](https://github.com/MichaelCrowe11/pulsar-lang/tree/main/examples/applications)** - Industry use cases
- **[Research Papers](https://github.com/MichaelCrowe11/pulsar-lang/tree/main/examples/research)** - Academic implementations

**Ready to try these examples?** 

1. [Install Mycelium-EI-Lang](installation.md)
2. Copy any example code
3. Save as a `.myc` file
4. Run with: `python -c "from mycelium_ei import run_file; run_file('example.myc')"`

[← Installation](installation.md) • [Language Reference →](language-reference.md)