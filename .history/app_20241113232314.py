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
    """Generate initial population of individuals"""
    population = []
    attempts = 0
    max_attempts = count * 10
    
    while len(population) < count and attempts < max_attempts:
        # Generate random bits for each item
        bits = [random.choice([0, 1]) for _ in range(len(items))]
        individual = Individual(bits, items, max_weight)
        
        # Check if this individual is unique
        if str(bits) not in [str(x.bits) for x in population]:
            population.append(individual)
        
        attempts += 1
    
    # If we couldn't generate enough unique individuals, fill with random ones
    while len(population) < count:
        bits = [random.choice([0, 1]) for _ in range(len(items))]
        population.append(Individual(bits, items, max_weight))
    
    return population

def selection(population: List[Individual]) -> List[Individual]:
    """Select parents using tournament selection"""
    if len(population) < 4:
        return random.sample(population, min(2, len(population)))
    
    # Tournament selection
    parents = []
    for _ in range(2):
        tournament = random.sample(population, 4)
        winner = max(tournament, key=lambda x: x.fitness())
        parents.append(winner)
    
    return parents

def crossover(parents: List[Individual], items: List[Item], max_weight: int, crossover_rate: float) -> List[Individual]:
    """Perform crossover between parents"""
    if len(parents) < 2 or random.random() > crossover_rate:
        return parents
    
    N = len(items)
    crossover_point = random.randint(1, N-1)
    
    child1_bits = parents[0].bits[:crossover_point] + parents[1].bits[crossover_point:]
    child2_bits = parents[1].bits[:crossover_point] + parents[0].bits[crossover_point:]
    
    return [
        Individual(child1_bits, items, max_weight),
        Individual(child2_bits, items, max_weight)
    ]

def mutate(individuals: List[Individual], mutation_rate: float):
    """Perform mutation on individuals"""
    for individual in individuals:
        for i in range(len(individual.bits)):
            if random.random() < mutation_rate:
                individual.bits[i] = 1 - individual.bits[i]

def next_generation(
    population: List[Individual],
    items: List[Item],
    max_weight: int,
    crossover_rate: float,
    mutation_rate: float
) -> List[Individual]:
    """Generate the next generation of individuals"""
    next_gen = []
    elite_count = max(1, len(population) // 10)
    
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
    """Main endpoint for solving the knapsack problem"""
    try:
        data = request.json
        max_weight = data.get('max_weight', 15)
        population_size = data.get('population_size', 6)
        generations = data.get('generations', 100)
        crossover_rate = data.get('crossover_rate', 0.53)
        mutation_rate = data.get('mutation_rate', 0.013)
        
        # Get items from request
        items_data = data.get('items', [])
        if not items_data:
            return jsonify({'error': 'No items provided'})
        
        # Convert items data to Item objects
        items = [Item(item['name'], int(item['weight']), int(item['value'])) 
                for item in items_data]
        
        # Initialize population
        population = generate_initial_population(population_size, items, max_weight)
        
        # Evolution process
        best_solution = None
        best_fitness = float('-inf')
        
        for _ in range(generations):
            population = next_generation(
                population,
                items,
                max_weight,
                crossover_rate,
                mutation_rate
            )
            
            current_best = max(population, key=lambda x: x.fitness())
            if current_best.fitness() > best_fitness:
                best_solution = current_best
                best_fitness = current_best.fitness()
        
        if best_solution and best_solution.get_total_weight() <= max_weight:
            return jsonify({
                'selected_items': best_solution.get_selected_items(),
                'total_value': best_solution.fitness(),
                'total_weight': best_solution.get_total_weight()
            })
        
        return jsonify({
            'selected_items': [],
            'total_value': 0,
            'total_weight': 0
        })
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)