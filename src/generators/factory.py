from typing import List, Dict, Any
from src.generators.base import ExerciseGenerator
import random

class ExerciseFactory:
    _generators: Dict[str, ExerciseGenerator] = {}

    @classmethod
    def register(cls, type_name: str, generator: ExerciseGenerator):
        """Register a new generator type."""
        cls._generators[type_name] = generator

    @classmethod
    def create_exercises(cls, recipe: List[Dict[str, Any]], total_count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate a mixed set of exercises based on a recipe.
        
        Args:
            recipe: List of generator configs (from YAML 'generators').
                   Example: [{'type': 'calcul', 'weight': 2}, {'type': 'probleme'}]
            total_count: Total number of exercises to generate.
        """
        exercises = []
        
        # Calculate weights to distribute count
        # If weight is missing, default to 1
        weighted_recipe = []
        total_weight = 0
        for item in recipe:
            w = item.get('weight', 1)
            weighted_recipe.append((item, w))
            total_weight += w
            
        if total_weight == 0:
            return []

        # Distribute counts
        # We'll do a simple distribution for now
        generated_count = 0
        
        for item, weight in weighted_recipe:
            # Calculate proportion
            count_for_item = int((weight / total_weight) * total_count)
            # Ensure at least 1 if count > 0 and weight > 0 (logic can be improved)
            
            gen_type = item.get('type')
            if gen_type in cls._generators:
                generator = cls._generators[gen_type]
                item_exercises = generator.generate(item, count_for_item)
                exercises.extend(item_exercises)
                generated_count += len(item_exercises)
            else:
                print(f"Warning: Generator type '{gen_type}' not found.")

        # If we have a shortfall due to rounding, fill up with random choice from recipe
        while len(exercises) < total_count:
            item = random.choice(recipe)
            gen_type = item.get('type')
            if gen_type in cls._generators:
                exercises.extend(cls._generators[gen_type].generate(item, 1))
            else:
                break # Avoid infinite loop if no valid generators

        # Shuffle results
        random.shuffle(exercises)
        return exercises[:total_count]
