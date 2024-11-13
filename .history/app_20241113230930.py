from flask import Flask, request, jsonify
from dataclasses import dataclass
import random
from typing import List, Dict
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@dataclass
class Item:
    name: str
    weight: int
    value: int

class Individual:
    def __init__(self, bits: List[int], items: List[Item], max_weight: int):
        self.bits = bits
        self.items = items
        self.max_weight = max_weight
    
    def __str__(self):
        return str(self.bits)
    
    def __hash__(self):
        return hash(str(self.bits))
    
    def fitness(self) -> float:
        total_value = sum([
            bit * item.value
            for item, bit in zip(self.items, self.bits)
        ])

        total_weight = sum([
            bit * item.weight
            for item, bit in zip(self.items, self.bits)
        ])

        if total_weight <= self.max_weight:
            return total_value
        # Instead of returning 0, return a negative fitness proportional to how much we exceed the weight
        return -abs(total_weight - self.max_weight)
    
    def get_selected_items(self) -> List[Dict]:
        return [
            {"name": item.name, "weight": item.weight, "value": item.value}
            for item, bit in zip(self.items, self.bits)
            if bit == 1
        ]
    
    def get_total_weight(self) -> int:
        return sum([
            bit * item.weight
            for item, bit in zip(self.items, self.bits)
        ])

def generate_initial_population(count: int, items: List[Item], max_weight: int) -> List[Individual]:
    population = []
    attempts = 0
    max_attempts = count * 10  # Limit attempts to prevent infinite loops
    
    while len(population) < count and attempts < max_attempts:
        bits = [random.choice([0, 1]) for _ in items]
        individual = Individual(bits, items, max_weight)
        
        # Always add to population, even if it exceeds weight limit
        # The fitness function will handle invalid solutions
        if str(bits) not in [str(x.bits) for x in population]:  # Avoid duplicates
            population.append(individual)
        
        attempts += 1
    
    # If we couldn't generate enough unique individuals, fill with random ones
    while len(population) < count:
        bits = [random.choice([0, 1]) for _ in items]
        population.append(Individual(bits, items, max_weight))
    
    return population

def selection(population: List[Individual]) -> List[Individual]:
    parents = []
    tournament_size = 4
    
    # Ensure we have enough individuals for tournament
    if len(population) < tournament_size:
        return random.sample(population, 2)
    
    # Tournament selection
    for _ in range(2):
        tournament = random.sample(population, tournament_size)
        winner = max(tournament, key=lambda x: x.fitness())
        parents.append(winner)
    
    return parents

def crossover(parents: List[Individual], items: List[Item], max_weight: int, crossover_rate: float) -> List[Individual]:
    if random.random() > crossover_rate:
        return parents
    
    N = len(items)
    crossover_point = random.randint(1, N-1)  # Avoid trivial crossovers
    
    child1_bits = parents[0].bits[:crossover_point] + parents[1].bits[crossover_point:]
    child2_bits = parents[1].bits[:crossover_point] + parents[0].bits[crossover_point:]
    
    return [
        Individual(child1_bits, items, max_weight),
        Individual(child2_bits, items, max_weight)
    ]

def mutate(individuals: List[Individual], mutation_rate: float):
    for individual in individuals:
        for i in range(len(individual.bits)):
            if random.random() < mutation_rate:
                individual.bits[i] = 1 - individual.bits[i]  # Flip the bit

def next_generation(
    population: List[Individual],
    items: List[Item],
    max_weight: int,
    crossover_rate: float,
    mutation_rate: float
) -> List[Individual]:
    next_gen = []
    elite_count = max(1, len(population) // 10)  # Keep top 10% of population
    
    # Elitism - keep best solutions
    sorted_population = sorted(population, key=lambda x: x.fitness(), reverse=True)
    next_gen.extend(sorted_population[:elite_count])
    
    # Generate rest of population
    while len(next_gen) < len(population):
        parents = selection(population)
        children = crossover(parents, items, max_weight, crossover_rate)
        mutate(children, mutation_rate)
        next_gen.extend(children)
    
    return next_gen[:len(population)]

@app.route('/solve', methods=['POST'])
def solve_knapsack():
    data = request.json
    max_weight = data.get('max_weight', 15)
    population_size = data.get('population_size', 6)
    generations = data.get('generations', 100)
    crossover_rate = data.get('crossover_rate', 0.53)
    mutation_rate = data.get('mutation_rate', 0.013)
    
    # Define items with more meaningful values
    items = [
        Item("Laptop", 7, 10),
        Item("Phone", 2, 8),
        Item("Camera", 1, 7),
        Item("Tablet", 9, 12)
    ]
    
    # Initialize population
    population = generate_initial_population(population_size, items, max_weight)
    
    # Evolution process
    best_solution = None
    best_fitness = float('-inf')  # Changed from 0 to handle negative fitness values
    
    for _ in range(generations):
        population = next_generation(
            population,
            items,
            max_weight,
            crossover_rate,
            mutation_rate
        )
        
        # Track best solution
        current_best = max(population, key=lambda x: x.fitness())
        if current_best.fitness() > best_fitness:
            best_solution = current_best
            best_fitness = current_best.fitness()
    
    # Only return solutions that meet weight constraint
    if best_solution and best_solution.get_total_weight() <= max_weight:
        return jsonify({
            'selected_items': best_solution.get_selected_items(),
            'total_value': best_solution.fitness(),
            'total_weight': best_solution.get_total_weight()
        })
    
    # If no valid solution was found, return the empty knapsack
    return jsonify({
        'selected_items': [],
        'total_value': 0,
        'total_weight': 0
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)