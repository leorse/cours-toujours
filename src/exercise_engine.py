import random
import re
from typing import Any, Dict, List, Optional
from src.models import ExerciseTemplate

class ExerciseEngine:
    @staticmethod
    def interpolate(text: str, variables: Dict[str, Any]) -> str:
        if not isinstance(text, str):
            return text
            
        # 1. Évaluation des expressions [[ expr ]]
        def eval_expr(match):
            raw_expr = match.group(1)
            # On injecte les variables dans l'expression elle-même si besoin
            # (ex: [[ {a} * 2 ]])
            try:
                expr = raw_expr.format(**variables)
                res = eval(expr, {"__builtins__": {}}, variables)
                if isinstance(res, float):
                    return str(int(res) if res.is_integer() else round(res, 2))
                return str(res)
            except Exception:
                return f"ERR({raw_expr})"

        processed = re.sub(r"\[\[(.+?)\]\]", eval_expr, text)
        
        # 2. Formatage standard {var}
        try:
            return processed.format(**variables)
        except Exception:
            return processed

    @staticmethod
    def generate_exercise(template: ExerciseTemplate, difficulty_context: Optional[int] = None) -> Dict[str, Any]:
        """
        Génère une instance d'exercice à partir d'un template.
        Fixe les variables, évalue la logique et remplit le contenu.
        """
        # 1. Génération des variables
        variables = {}
        for var_name, config in template.vars.items():
            if isinstance(config, list):
                variables[var_name] = random.choice(config)
            elif isinstance(config, dict):
                v_min = config.get("min", 0)
                v_max = config.get("max", 10)
                variables[var_name] = random.randint(v_min, v_max)
            else:
                variables[var_name] = config

        # 2. Interpolation du contenu (question, options, etc.)
        content = {}
        for key, value in template.content.items():
            if isinstance(value, str):
                content[key] = ExerciseEngine.interpolate(value, variables)
            elif isinstance(value, list):
                content[key] = [
                    ExerciseEngine.interpolate(v, variables) if isinstance(v, str) else v 
                    for v in value
                ]
            else:
                content[key] = value

        # 3. Évaluation de la logique ou récupération de la réponse fixe
        answer = None
        if template.logic:
            # On remplace {var} par leur valeur
            logic_str = template.logic.format(**variables)
            try:
                answer = eval(logic_str, {"__builtins__": {}}, variables)
                if isinstance(answer, float):
                    answer = int(answer) if answer.is_integer() else round(answer, 2)
            except Exception as e:
                print(f"❌ Erreur évaluation logic '{logic_str}': {e}")
                answer = "ERROR"
        elif "answer" in content:
            # Réponse statique dans le contenu (ex: QCM)
            answer = content["answer"]
            options = content.get("options", [])
            if options:
                if isinstance(answer, list):
                    # Si ce sont des indices, on récupère les labels correspondants
                    answer = [options[a] if isinstance(a, int) and 0 <= a < len(options) else a for a in answer]
                    # Si c'est un QCM à choix unique, on aplatit la liste
                    if not template.multiple and len(answer) == 1:
                        answer = answer[0]
                elif isinstance(answer, int) and 0 <= answer < len(options):
                    answer = options[answer]

        # 4. Construction de l'objet final pour le frontend
        ex_type = template.interaction or "input"
        if template.multiple and ex_type == "qcm":
            ex_type = "multiselect"

        return {
            "id": f"{template.id}_{random.randint(1000, 9999)}",
            "template_id": template.id,
            "type": ex_type,
            "render_type": template.render_type,
            "multiple": template.multiple,
            "question": content.get("question", ""),
            "options": content.get("options", []),
            # On ne force pas le string si c'est une liste (pour smart_compare)
            "answer": answer if isinstance(answer, list) else str(answer),
            "explanation": content.get("explanation", ""),
            "unit": content.get("unit", ""),
            "variables": variables,
            "tags": template.tags,
            "meta": {
                "difficulty": template.difficulty
            }
        }
