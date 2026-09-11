import random

from mycelium_ei.bio.algorithms import (AntColonyOptimization, BiologicalOptimizer, GeneticAlgorithm,
                                        ParticleSwarmOptimization, sphere_function)
from mycelium_ei.bio.ml import BiologicalMLOptimizer
from mycelium_ei.bio.cultivation import CultivationMonitoringPlatform
from mycelium_ei.network import MyceliumNetwork, SignalType


def test_genetic_algorithm_improves_sphere(capsys):
    random.seed(1)
    ga = GeneticAlgorithm(population_size=30, gene_length=3, max_generations=40)
    best = ga.optimize(sphere_function, verbose=False)
    assert best.fitness > -0.05
    assert len(best.genes) == 3


def test_particle_swarm_is_pure_python_and_converges(capsys):
    random.seed(1)
    pso = ParticleSwarmOptimization(num_particles=20, dimensions=3, max_iterations=40)
    position, fitness = pso.optimize(sphere_function, verbose=False)
    assert isinstance(position, list) and len(position) == 3
    assert fitness > -0.05
    assert all(-1.0 <= x <= 1.0 for x in position)


def test_ant_colony_returns_bounded_solution(capsys):
    random.seed(1)
    aco = AntColonyOptimization(num_ants=15, num_variables=3, max_iterations=20)
    solution, fitness = aco.optimize(lambda x: 1.0 - sum(v * v for v in x), verbose=False)
    assert len(solution) == 3
    assert all(-1.0 <= v <= 1.0 for v in solution)
    assert fitness > 0.5


def test_biological_optimizer_facade_and_compare(capsys):
    random.seed(2)
    opt = BiologicalOptimizer()
    result = opt.optimize("pso", sphere_function, 2, num_particles=10, max_iterations=5)
    assert set(result) >= {"best_solution", "best_fitness", "iterations", "computation_time"}
    results = opt.compare_algorithms(sphere_function, dimensions=2)
    assert set(results) == {"genetic", "pso", "aco"}
    assert all("error" not in r for r in results.values())


def test_bio_ml_network_train_and_predict(capsys):
    random.seed(3)
    ml = BiologicalMLOptimizer()
    ml.create_network("n", 2, 3, 1)
    data = [([0.1, 0.9], [0.5]), ([0.8, 0.2], [0.1])]
    result = ml.train_network("n", data, epochs=5)
    assert result["growth_cycles"] == 5
    prediction = ml.predict("n", [0.5, 0.5])
    assert len(prediction) == 1


def test_cultivation_platform_reading_and_health(capsys):
    random.seed(4)
    platform = CultivationMonitoringPlatform()
    controller = platform.create_cultivation("batch")
    reading = controller.get_current_reading()
    assert 15.0 < reading.temperature < 35.0
    health = controller.analyze_cultivation_health(reading)
    assert 0.0 <= health["health_score"] <= 1.0
    assert isinstance(controller.check_alerts(reading), list)


def test_network_sequential_ids_and_propagation(capsys):
    network = MyceliumNetwork("t")
    a = network.add_node()
    b = network.add_node()
    c = network.add_node()
    assert [a.node_id, b.node_id, c.node_id] == ["node_01", "node_02", "node_03"]
    a.connect_to(b)
    b.connect_to(c)
    network.broadcast_signal(SignalType.ALERT, {"message": "low"})
    out = capsys.readouterr().out
    assert "Node node_02: Received alert signal" in out
    assert "Node node_03: Received alert signal" in out
    assert network.get_stats()["connections"] == 2
