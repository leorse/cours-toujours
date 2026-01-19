import os
import yaml
import frontmatter
from typing import List, Dict, Optional, Any
from src.models import Subject, RoadStep, Course, Exercise, ExerciseTemplate

CONTENT_DIR = "content"

class ContentManager:
    _subjects: Dict[str, Subject] = {}
    _road_steps: Dict[str, RoadStep] = {}
    _templates: Dict[str, ExerciseTemplate] = {}
    
    @classmethod
    def load_all(cls):
        print("🔄 Chargement dynamique du contenu...")
        cls._subjects = {}
        cls._road_steps = {}
        cls._templates = {}
        
        cours_path = os.path.join(CONTENT_DIR, "cours.yaml")
        if not os.path.exists(cours_path):
            print("⚠️ Fichier cours.yaml manquant.")
            return

        try:
            with open(cours_path, "r", encoding="utf-8") as f:
                cours_data = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Erreur lecture cours.yaml: {e}")
            return
            
        if not cours_data or "cours" not in cours_data:
            print("❌ Format invalide pour cours.yaml")
            return

        for entry in cours_data["cours"]:
            rel_path = entry.get("page")
            if not rel_path: continue
            
            road_path = os.path.join(CONTENT_DIR, rel_path)
            
            if not os.path.exists(road_path):
                # Simple fallback
                for root, dirs, files in os.walk(CONTENT_DIR):
                    if rel_path in files:
                        road_path = os.path.join(root, rel_path)
                        break

            if not os.path.exists(road_path):
                print(f"⚠️ Route non trouvée: {rel_path}")
                continue

            subject_path = os.path.dirname(road_path)
            subject_id = os.path.basename(subject_path)
            
            # 1. Charger les templates d'exercices
            cls._load_templates(subject_id, subject_path)
            
            # 2. Charger la route
            cls._load_road(subject_id, road_path)
            
        print(f"✅ Chargement terminé: {len(cls._subjects)} sujets, {len(cls._road_steps)} étapes, {len(cls._templates)} templates.")

    @classmethod
    def _load_templates(cls, subject_id: str, subject_path: str):
        for root, dirs, files in os.walk(subject_path):
            for filename in files:
                if filename.endswith(".yaml") and filename not in ["road.yaml", "road_2.yaml", "meta.yaml", "cours.yaml", "route_math.yaml"]:
                    yaml_path = os.path.join(root, filename)
                    try:
                        with open(yaml_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                            if not data: continue
                            
                            # On gère 'generators' et 'templates'
                            for key in ["generators", "templates"]:
                                if key in data:
                                    for t_data in data[key]:
                                        t_id = t_data.get("id")
                                        if not t_id: continue
                                        
                                        cls._templates[t_id] = ExerciseTemplate(
                                            id=t_id,
                                            tags=t_data.get("tags", []),
                                            difficulty=t_data.get("difficulty", 1),
                                            vars=t_data.get("vars", {}),
                                            content=t_data.get("content", {}),
                                            logic=t_data.get("logic"),
                                            render_type=t_data.get("render_type"),
                                            interaction=t_data.get("interaction", "input"),
                                            multiple=t_data.get("multiple", False),
                                            type="math_engine" if key == "generators" else "template"
                                        )
                    except Exception as e:
                        print(f"❌ Erreur templates {yaml_path}: {e}")

    @classmethod
    def _load_road(cls, subject_id: str, road_path: str):
        try:
            with open(road_path, "r", encoding="utf-8") as f:
                road_data = yaml.safe_load(f)
            if not road_data: return

            subject_name = road_data.get("title", subject_id.capitalize())
            cls._subjects[subject_id] = Subject(id=subject_id, name=subject_name)
            
            if "road" in road_data:
                global_idx = 0
                for step_entry in road_data["road"]:
                    s_type = step_entry.get("type", "cours")
                    
                    if s_type == "sequence":
                        # Expansion de la séquence
                        repeat = step_entry.get("repeat", 1)
                        step_config = step_entry.get("step_config", {})
                        
                        for i in range(1, repeat + 1):
                            s_id = f"{step_entry['id']}_{i}"
                            # Remplacement de {index} dans les strings de config
                            title = step_entry.get("title", "").replace("{index}", str(i))
                            
                            # On clone et adapte la selection
                            selection = None
                            if "selection" in step_config:
                                raw_sel = yaml.dump(step_config["selection"])
                                selection = yaml.safe_load(raw_sel.replace("{index}", str(i)))

                            cls._road_steps[s_id] = RoadStep(
                                id=s_id,
                                title=title,
                                type=step_config.get("type", "practice"),
                                order=global_idx,
                                subject_id=subject_id,
                                selection=selection,
                                activated=step_entry.get("activated", False),
                                pages=step_config.get("pages", [])
                            )
                            global_idx += 1
                    else:
                        s_id = step_entry["id"]
                        cls._road_steps[s_id] = RoadStep(
                            id=s_id,
                            title=step_entry.get("title", s_id.capitalize()),
                            subtitle=step_entry.get("subtitle"),
                            type=s_type,
                            order=global_idx,
                            subject_id=subject_id,
                            content_file=step_entry.get("content"),
                            selection=step_entry.get("selection"),
                            scope=step_entry.get("scope"),
                            strategy=step_entry.get("strategy", "weakest_points"),
                            activated=step_entry.get("activated", False),
                            pages=step_entry.get("pages", [])
                        )
                        global_idx += 1
        except Exception as e:
            print(f"❌ Erreur route {road_path}: {e}")

    @classmethod
    def get_subjects(cls) -> List[Subject]: return list(cls._subjects.values())
    @classmethod
    def get_all_subjects(cls) -> Dict[str, Subject]: return cls._subjects
    @classmethod
    def get_subject(cls, subject_id: str) -> Optional[Subject]: return cls._subjects.get(subject_id)
    @classmethod
    def get_all_templates(cls) -> Dict[str, ExerciseTemplate]: return cls._templates
    @classmethod
    def get_steps_for_subject(cls, subject_id: str) -> List[RoadStep]:
        steps = [s for s in cls._road_steps.values() if s.subject_id == subject_id]
        return sorted(steps, key=lambda x: x.order)
    @classmethod
    def get_step(cls, step_id: str) -> Optional[RoadStep]: return cls._road_steps.get(step_id)
    @classmethod
    def get_template(cls, t_id: str) -> Optional[ExerciseTemplate]: return cls._templates.get(t_id)

    @classmethod
    def get_step_content(cls, subject_id: str, content_file: str) -> Optional[str]:
        # On cherche le fichier md dans content/subject_id/content_file
        # Ou content/content_file si content_file est un chemin relatif à content/
        search_paths = [
            os.path.join(CONTENT_DIR, subject_id, content_file),
            os.path.join(CONTENT_DIR, content_file)
        ]
        for p in search_paths:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
        return None

    @classmethod
    def get_dialogue(cls, subject_id: str, dialogue_file: str) -> Optional[List[Dict[str, Any]]]:
        # Search in subject folder or root content
        search_paths = [
            os.path.join(CONTENT_DIR, subject_id, dialogue_file),
            os.path.join(CONTENT_DIR, dialogue_file)
        ]
        for p in search_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data and "dialogue" in data:
                            return data["dialogue"]
                except Exception as e:
                    print(f"❌ Erreur dialogue {p}: {e}")
        return None

    @classmethod
    def select_templates(cls, target_tags: List[str], difficulty: Optional[int] = None) -> List[ExerciseTemplate]:
        results = []
        for t in cls._templates.values():
            # Check if all target tags are present in template tags
            if all(tag in t.tags for tag in target_tags):
                if difficulty is None or t.difficulty == difficulty:
                    results.append(t)
        return results
