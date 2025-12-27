import random
import math
from typing import List, Dict, Any
from src.models import Course

class TestGenerator:
    @staticmethod
    def generate_step_exercises(course: Course, step_type: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Génère des exercices pour une étape spécifique d'un cours.
        """
        gen_type = course.generator_type
        
        # Déterminer la difficulté en fonction du type de step
        difficulty = "medium"
        if not step_type:
            difficulty = "medium"
        elif "simple" in step_type:
            difficulty = "simple"
        elif "hard" in step_type or "difficult" in step_type:
            difficulty = "hard"
        elif "validation" in step_type:
            difficulty = "mix" # Un mélange pour la validation

        # Dispatch vers le bon générateur
        if not gen_type:
            return [TestGenerator.generate_lorem_exercise() for _ in range(count)]
            
        if gen_type == "addition":
            return MathGenerator.generate(count, "addition", difficulty)
        elif gen_type == "soustraction":
            return MathGenerator.generate(count, "soustraction", difficulty)
        elif gen_type == "multiplication":
            return MathGenerator.generate(count, "multiplication", difficulty)
        elif gen_type == "division":
            return MathGenerator.generate(count, "division", difficulty)
        elif "fraction" in gen_type:
            return FractionTestGenerator.generate(count, gen_type, difficulty)
        else:
            # Fallback
            return [TestGenerator.generate_lorem_exercise() for _ in range(count)]

    @staticmethod
    def generate_lorem_exercise() -> Dict[str, Any]:
        return {
            "id": f"lorem_{random.randint(1000, 9999)}",
            "type": "qcm",
            "question": "Question de test dynamique ?",
            "options": ["Réponse A", "Réponse B (Bonne)", "Réponse C"],
            "answer": "Réponse B (Bonne)"
        }

    # -- Legacy methods (to be kept/refactored if still used by flash mode) --
    @staticmethod
    def generate_flash(courses: List[Course], total_questions: int = 15) -> List[Dict[str, Any]]:
        flash_questions = []
        for _ in range(total_questions):
            course = random.choice(courses)
            # On génère un mix de difficultés pour le mode flash
            diff = random.choice(["simple", "medium", "hard"])
            exercises = TestGenerator.generate_step_exercises(course, f"practice_{diff}", 1)
            if exercises:
                flash_questions.append(exercises[0])
        return flash_questions

class MathGenerator:
    @staticmethod
    def generate(count: int, op_type: str, difficulty: str) -> List[Dict[str, Any]]:
        exercises = []
        for i in range(count):
            # Paramètres de difficulté
            if difficulty == "simple":
                range_a, range_b = (1, 10), (1, 10)
            elif difficulty == "medium":
                range_a, range_b = (10, 50), (1, 30)
            elif difficulty == "hard":
                range_a, range_b = (50, 200), (10, 100)
            else: # mix
                d = random.choice(["simple", "medium", "hard"])
                return MathGenerator.generate(count, op_type, d)

            a = random.randint(*range_a)
            b = random.randint(*range_b)
            
            if op_type == "addition":
                question = f"Combien font ${a} + {b}$ ?"
                answer = str(a + b)
            elif op_type == "soustraction":
                # Éviter les résultats négatifs pour le simple
                if difficulty == "simple" and a < b: a, b = b, a
                question = f"Combien font ${a} - {b}$ ?"
                answer = str(a - b)
            elif op_type == "multiplication":
                if difficulty == "simple": a, b = random.randint(1, 5), random.randint(1, 10)
                question = f"Combien font ${a} \\times {b}$ ?"
                answer = str(a * b)
            elif op_type == "division":
                # Assurer un résultat entier
                b = random.randint(2, 10)
                res = random.randint(1, 10 if difficulty == "simple" else 20)
                a = b * res
                question = f"Combien font ${a} \\div {b}$ ?"
                answer = str(res)
            else:
                continue

            exercises.append({
                "id": f"math_{op_type}_{difficulty}_{i}_{random.randint(100, 999)}",
                "type": "input",
                "question": question,
                "answer": answer
            })
        return exercises

class FractionTestGenerator:
    @staticmethod
    def generate(count: int, gen_type: str, difficulty: str) -> List[Dict[str, Any]]:
        # Integration with existing FractionGenerator logic
        # For now, let's reuse simplification or generic fraction questions
        exercises = []
        for i in range(count):
            # We can use TestGenerator's old simplification generator here or similar
            # Placeholder for expansion
            exercises.append(FractionTestGenerator.generate_one_simplification(difficulty))
        return exercises

    @staticmethod
    def generate_one_simplification(difficulty: str) -> Dict[str, Any]:
        # Reuse logic from original TestGenerator
        if difficulty == "simple": f_range = (2, 5)
        elif difficulty == "medium": f_range = (5, 10)
        else: f_range = (10, 20)
        
        factor = random.randint(*f_range)
        den_base = random.randint(2, 12)
        num_base = random.randint(1, den_base - 1)
        while math.gcd(num_base, den_base) != 1:
            den_base = random.randint(2, 12)
            num_base = random.randint(1, den_base - 1)
            
        num_p, den_p = num_base * factor, den_base * factor
        return {
            "id": f"frac_simp_{random.randint(1000, 9999)}",
            "type": "input", # Change to input for better challenge
            "question": f"Simplifiez la fraction $\\frac{{{num_p}}}{{{den_p}}}$",
            "answer": f"{num_base}/{den_base}"
        }
