import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.generators import ExerciseFactory

def test_factory():
    recipe = [
        {
            "type": "calcul", 
            "subtype": "multiplication", 
            "difficulty": "medium",
            "weight": 2
        },
        {
            "type": "probleme",
            "categories": ["pizza"],
            "difficulty": "simple",
            "weight": 1
        },
        {
            "type": "cours",
            "interaction": "qcm",
            "weight": 1
        }
    ]
    
    print("Generating 10 exercises from recipe...")
    exercises = ExerciseFactory.create_exercises(recipe, 10)
    
    for ex in exercises:
        print(f"[{ex['type']}] ({ex.get('tag')}) {ex['question']} -> {ex['answer']}")
        if "meta" in ex and "visual_blueprint" in ex["meta"]:
            print(f"   Blueprint: {ex['meta']['visual_blueprint']}")

if __name__ == "__main__":
    test_factory()
