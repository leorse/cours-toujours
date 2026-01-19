import random
from typing import List, Dict, Any
from src.generators.base import ExerciseGenerator

class ProblemGenerator(ExerciseGenerator):
    SCENARIOS = {
        "pizza": [
            {
                "template": "Tom a commandé une pizza coupée en {total} parts. Il en mange {taken}. Combien de parts reste-t-il ?",
                "vars": lambda diff: {"total": (t := random.choice([4, 6, 8])), "taken": random.randint(1, t-1)},
                "calc": lambda v: v["total"] - v["taken"],
                "blueprint": lambda v: {"type": "pizza", "total": v["total"], "highlighted": v["taken"], "style": "eaten"}
            },
            {
                "template": "Alice partage une pizza de {total} parts avec Tom. Tom prend {alice_share} parts et Alice en prend {tom_share}. Combien de parts ont-ils mangé en tout ?",
                "vars": lambda diff: {"total": (t := random.choice([6, 8, 10, 12])), "alice_share": random.randint(1, t//2), "tom_share": random.randint(1, t//2)},
                "calc": lambda v: v["alice_share"] + v["tom_share"],
                "blueprint": lambda v: {"type": "pizza", "total": v["total"], "highlighted": v["alice_share"] + v["tom_share"]}
            }
        ],
        "chocolat": [
            {
                "template": "Une tablette de chocolat a {rows} rangées de {cols} carrés. Combien y a-t-il de carrés au total ?",
                "vars": lambda diff: {"rows": random.randint(2, 5), "cols": random.randint(3, 6)},
                "calc": lambda v: v["rows"] * v["cols"],
                "blueprint": lambda v: {"type": "grid", "rows": v["rows"], "cols": v["cols"], "highlighted": 0}
            },
            {
                "template": "Tom a mangé {eaten} carrés d'une tablette de {rows} par {cols}. Combien en reste-t-il ?",
                "vars": lambda diff: {"rows": (r:=random.randint(3, 5)), "cols": (c:=random.randint(4, 8)), "eaten": random.randint(1, r*c - 1)},
                "calc": lambda v: v["rows"] * v["cols"] - v["eaten"],
                "blueprint": lambda v: {"type": "grid", "rows": v["rows"], "cols": v["cols"], "highlighted": v["eaten"], "style": "missing"}
            }
        ],
        "liquide": [
            {
                "template": "Un verre doseur contient {level} ml de lait. Alice ajoute {add} ml. Quel est le volume total ?",
                "vars": lambda diff: {"level": random.randint(50, 200), "add": random.randint(20, 100)},
                "calc": lambda v: v["level"] + v["add"],
                "blueprint": lambda v: {"type": "beaker", "capacity": 500, "level_start": v["level"], "level_end": v["level"] + v["add"]}
            }
        ]
    }

    def generate(self, config: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        categories = config.get("categories", ["pizza", "liquide", "chocolat"])
        exercises = []
        
        for _ in range(count):
            cat = random.choice(categories)
            if cat not in self.SCENARIOS:
                continue
                
            scenario = random.choice(self.SCENARIOS[cat])
            
            # Generate variables based on difficulty (placeholder for now)
            variables = scenario["vars"](config.get("difficulty", "medium"))
            
            # Create question text
            question = scenario["template"].format(**variables)
            
            # Calculate answer
            answer = str(scenario["calc"](variables))
            
            # Generate Blueprint
            blueprint = scenario["blueprint"](variables)
            
            tag = f"math:probleme:{cat}"
            
            exercises.append({
                "id": f"prob_{cat}_{random.randint(10000, 99999)}",
                "type": "input", 
                "question": question,
                "answer": answer,
                "tag": tag,
                "meta": {
                    "visual_blueprint": blueprint
                }
            })
            
        return exercises
