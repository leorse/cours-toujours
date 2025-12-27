
import random
import math
from typing import List, Dict, Any
from src.models import Course

class TestGenerator:
    @staticmethod
    def simplify_fraction(num: int, den: int):
        gcd = math.gcd(num, den)
        return num // gcd, den // gcd

    @staticmethod
    def generate_fraction_simplification() -> Dict[str, Any]:
        # Avoid 1/1 if possible, or include it.
        # Let's generate non-simplified fractions.
        
        # Pick simplified base
        den_base = random.randint(2, 12)
        num_base = random.randint(1, den_base - 1)
        
        # Ensure it is simplified to start with (so we can multiply up)
        # Actually gcd(num_base, den_base) should be 1
        while math.gcd(num_base, den_base) != 1:
             den_base = random.randint(2, 12)
             num_base = random.randint(1, den_base - 1)

        # Multiply by random factor to get the "problem"
        factor = random.randint(2, 6)
        num_problem = num_base * factor
        den_problem = den_base * factor
        
        question = f"Simplifiez la fraction $\\frac{{{num_problem}}}{{{den_problem}}}$"
        correct_answer = f"$\\frac{{{num_base}}}{{{den_base}}}$"
        
        # Generate distractors
        options = set()
        options.add(correct_answer)
        
        # Distractor 1: intermediate simplification (if possible)
        if factor > 2 and factor % 2 == 0:
             n_half = num_problem // 2
             d_half = den_problem // 2
             options.add(f"$\\frac{{{n_half}}}{{{d_half}}}$")
        
        # Distractor 2: random wrong fraction
        while len(options) < 4:
            d_rand = random.randint(2, 20)
            n_rand = random.randint(1, d_rand)
            options.add(f"$\\frac{{{n_rand}}}{{{d_rand}}}$")
            
        options_list = list(options)
        random.shuffle(options_list)
        
        return {
            "id": f"gen_simp_{random.randint(1000, 9999)}",
            "type": "qcm",
            "question": question,
            "options": options_list,
            "answer": correct_answer
        }

    @staticmethod
    def generate_test(course: Course, total_questions: int = 20) -> List[Dict[str, Any]]:
        # 1. Get existing course exercises
        existing_exercises = course.exercises if course.exercises else []
        
        # 2. Add them to list
        test_questions = [ex for ex in existing_exercises]
        
        # 3. Fill with generated questions
        needed = total_questions - len(test_questions)
        if needed > 0:
            for _ in range(needed):
                test_questions.append(TestGenerator.generate_fraction_simplification())
        
        # 4. Shuffle
        random.shuffle(test_questions)
        
        return test_questions

    @staticmethod
    def generate_flash(courses: List[Course], total_questions: int = 15) -> List[Dict[str, Any]]:
        """
        Generates a random mix of questions from multiple courses.
        """
        all_manual_exercises = []
        for course in courses:
            if course.exercises:
                all_manual_exercises.extend(course.exercises)
        
        # Take up to half from manual exercises
        manual_count = min(len(all_manual_exercises), total_questions // 2)
        flash_questions = random.sample(all_manual_exercises, manual_count) if all_manual_exercises else []
        
        # Fill the rest with generated questions
        while len(flash_questions) < total_questions:
            # For now we only have fraction simplification, but we could add more
            flash_questions.append(TestGenerator.generate_fraction_simplification())
            
        random.shuffle(flash_questions)
        return flash_questions
