import random
from typing import List, Dict, Any
from src.generators.base import ExerciseGenerator

class CourseGenerator(ExerciseGenerator):
    DEFINITIONS = [
        {"term": "Somme", "def": "Résultat d'une addition.", "clue": "Résultat de 5 + 3"},
        {"term": "Différence", "def": "Résultat d'une soustraction.", "clue": "Résultat de 10 - 4"},
        {"term": "Produit", "def": "Résultat d'une multiplication.", "clue": "Résultat de 6 x 7"},
        {"term": "Quotient", "def": "Résultat d'une division.", "clue": "Résultat de 20 / 4"},
        {"term": "Termes", "def": "Nombres que l'on additionne ou soustrait.", "clue": "Dans 5 + 3, 5 et 3 sont des..."},
        {"term": "Facteurs", "def": "Nombres que l'on multiplie.", "clue": "Dans 5 x 3, 5 et 3 sont des..."}
    ]

    def generate(self, config: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        mode = config.get("mode", "definition") # definition (find term by def) or reverse
        exercises = []
        
        for _ in range(count):
            item = random.choice(self.DEFINITIONS)
            
            if mode == "definition":
                question = f"Quel est le terme mathématique pour : {item['def']} ?"
                answer = item["term"]
            else:
                question = f"Quelle est la définition de : {item['term']} ?"
                answer = item["def"] # Note: handling free text answers for defs might be hard, strictly speaking QCM is better or fuzzy match.
                # Assuming simple keyword match or flashcard style for now.
            
            # Use QCM if specified in config, otherwise input
            ex_type = config.get("interaction", "input") # input | qcm
            
            ex = {
                "id": f"cours_{random.randint(1000, 9999)}",
                "type": ex_type,
                "question": question,
                "answer": answer,
                "tag": "math:vocabulaire",
                "meta": {}
            }
            
            if ex_type == "qcm":
                options = [item["term"]]
                while len(options) < 3:
                    other = random.choice(self.DEFINITIONS)["term"]
                    if other not in options:
                        options.append(other)
                random.shuffle(options)
                ex["options"] = options
                
            exercises.append(ex)
            
        return exercises
