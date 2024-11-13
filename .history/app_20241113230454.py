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
        return 0
    
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
    population = set()
    while len(population) < count:
        bits = [random.choice([0, 1]) for _ in items]
        individual = Individual(bits, items, max_weight)
        if individual.fitness() > 0:  # Only add valid solutions
            population.add(hash(str(bits)))
    
    return [Individual(list(map(int, str(h)[1:-1].split(", "))), items, max_weight) 
            for h in population]

def selection(population: List[Individual]) -> List[Individual]:
    parents = []
    random.shuffle(population)
    
    # Tournament selection
    if population[0].fitness() > population[1].fitness():
        parents.append(population[0])
    else:
        parents.append(population[1])
    
    if population[2].fitness() > population[3].fitness():
        parents.append(population[2])
    else:
        parents.append(population[3])
    
    return parents

def crossover(parents: List[Individual], items: List[Item], max_weight: int, crossover_rate: float) -> List[Individual]:
    if random.random() > crossover_rate:
        return parents
    
    N = len(items)
    child1_bits = parents[0].bits[:N//2] + parents[1].bits[N//2:]
    child2_bits = parents[1].bits[:N//2] + parents[0].bits[N//2:]
    
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
    
    # Define items
    items = [
        Item("Laptop", 7, 5),
        Item("Phone", 2, 4),
        Item("Camera", 1, 7),
        Item("Tablet", 9, 2)
    ]
    
    # Initialize population
    population = generate_initial_population(population_size, items, max_weight)
    
    # Evolution process
    best_solution = None
    best_fitness = 0
    
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
    
    if best_solution:
        return jsonify({
            'selected_items': best_solution.get_selected_items(),
            'total_value': best_solution.fitness(),
            'total_weight': best_solution.get_total_weight()
        })
    
    return jsonify({'error': 'No valid solution found'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)