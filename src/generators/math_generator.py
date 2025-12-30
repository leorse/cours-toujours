import random
import math
from typing import List, Dict, Any
from src.generators.base import ExerciseGenerator

class MathGenerator(ExerciseGenerator):
    def generate(self, config: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        subtype = config.get("subtype", "addition") # addition, multiplication...
        difficulty = config.get("difficulty", "medium")
        focus = config.get("focus") # Optional: int, e.g. 7 for table of 7

        exercises = []
        for _ in range(count):
            ex = self._generate_one(subtype, difficulty, focus)
            exercises.append(ex)
        return exercises

    def _generate_one(self, op_type: str, difficulty: str, focus: Any) -> Dict[str, Any]:
        # Tag logic: math:calcul:{op_type}
        tag = f"math:calcul:{op_type}"
        
        if difficulty == "simple":
            range_a, range_b = (1, 10), (1, 10)
        elif difficulty == "medium":
            range_a, range_b = (10, 50), (1, 30)
        elif difficulty == "hard":
            range_a, range_b = (50, 200), (10, 100)
        else: # random
             range_a, range_b = (1, 50), (1, 50)
        
        # Override for Multiplication tables if focus is set
        if op_type == "multiplication" and focus is not None:
            try:
                table = int(focus)
                a = table
                b = random.randint(1, 10)
            except ValueError:
                a = random.randint(*range_a)
                b = random.randint(*range_b)
        else:
            a = random.randint(*range_a)
            b = random.randint(*range_b)

        # Logic per operation
        if op_type == "addition":
            question = f"Combien font ${a} + {b}$ ?"
            answer = str(a + b)
            
        elif op_type == "soustraction":
            if difficulty == "simple" and a < b:
                a, b = b, a
            question = f"Combien font ${a} - {b}$ ?"
            answer = str(a - b)
            
        elif op_type == "multiplication":
            if difficulty == "simple" and not focus: 
                a, b = random.randint(1, 5), random.randint(1, 10)
            question = f"Combien font ${a} \\times {b}$ ?"
            answer = str(a * b)
            
        elif op_type == "division":
            # Ensure integer result
            divisor = random.randint(2, 10)
            quotient = random.randint(1, 10 if difficulty == "simple" else 20)
            dividend = divisor * quotient
            question = f"Combien font ${dividend} \\div {divisor}$ ?"
            answer = str(quotient)
        else:
            # Fallback
            question = "1 + 1 ?"
            answer = "2"

        return {
            "id": f"cal_{op_type}_{random.randint(10000, 99999)}",
            "type": "input",
            "question": question,
            "answer": answer,
            "tag": tag,
            "meta": {}
        }
