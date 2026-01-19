import random
import uuid
from typing import List, Dict, Any
from src.generators.base import ExerciseGenerator

class DivisibilityGenerator(ExerciseGenerator):
    def generate(self, config: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        exercises = []
        difficulty = config.get("difficulty", "medium")
        # Default to 2 if not specified, but could be 3, 5, 9, 10
        divisor = config.get("divisor", 2)
        
        # Adjust range based on difficulty
        if difficulty == "easy":
            max_val = 100
        elif difficulty == "medium":
            max_val = 1000
        else: # hard
            max_val = 10000
            
        for _ in range(count):
            numbers = []
            correct_numbers = []
            
            # Generate 6 candidates
            # Try to ensure we have at least one correct and one incorrect
            while len(numbers) < 6:
                n = random.randint(2, max_val)
                if n in numbers:
                    continue
                
                numbers.append(n)
            
            for n in numbers:
                if n % divisor == 0:
                    correct_numbers.append(str(n))
            
            # Options as strings
            options = [str(n) for n in numbers]
            # No need to shuffle as they were added in random order
            
            ex = {
                "id": f"gen_div_{uuid.uuid4().hex[:8]}",
                "type": "multiselect",
                "question": f"Quels sont les nombres divisibles par {divisor} ?",
                "options": options,
                "answer": correct_numbers,
                "tag": f"math:arithmetique:divisibilite:{divisor}",
                "meta": {"difficulty": difficulty}
            }
            exercises.append(ex)
            
        return exercises
