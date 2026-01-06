import os
import yaml
import frontmatter
from typing import List, Dict, Optional, Any
from src.models import Subject, RoadStep, Course, Exercise

CONTENT_DIR = "content"

class ContentManager:
    _subjects: Dict[str, Subject] = {}
    _road_steps: Dict[str, RoadStep] = {}
    _exercises: Dict[str, Exercise] = {}
    
    @classmethod
    def load_all(cls):
        print("🔄 Chargement dynamique du contenu depuis cours.yaml...")
        cls._subjects = {}
        cls._road_steps = {}
        cls._exercises = {}
        
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
            
            # Resolve path if not directly found (simple search in content/)
            if not os.path.exists(road_path):
                found = False
                for root, dirs, files in os.walk(CONTENT_DIR):
                    if rel_path in files:
                        road_path = os.path.join(root, rel_path)
                        found = True
                        break
                if not found:
                    print(f"⚠️ Fichier de route non trouvé: {rel_path}")
                    continue

            # subject_id est le dossier parent du fichier road
            subject_path = os.path.dirname(road_path)
            subject_id = os.path.basename(subject_path)
            
            # 1. Charger les exercices du dossier sujet
            cls._load_exercises(subject_id, subject_path)
            
            # 2. Charger la route
            cls._load_road_from_file(subject_id, road_path)
            
        print(f"✅ Chargement terminé: {len(cls._subjects)} sujets, {len(cls._road_steps)} étapes, {len(cls._exercises)} exercices.")

    @classmethod
    def _load_exercises(cls, subject_id: str, subject_path: str):
        for root, dirs, files in os.walk(subject_path):
            for filename in files:
                if filename.endswith(".yaml") and filename not in ["road.yaml", "road_2.yaml", "meta.yaml", "cours.yaml"]:
                    yaml_path = os.path.join(root, filename)
                    try:
                        with open(yaml_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                            if data and "exercices" in data:
                                for ex_data in data["exercices"]:
                                    ex_id = ex_data.get("id")
                                    if ex_id:
                                        cls._exercises[ex_id] = Exercise(
                                            id=ex_id,
                                            subject_id=subject_id,
                                            data=ex_data
                                        )
                    except Exception as e:
                        print(f"❌ Erreur lors du chargement de {yaml_path}: {e}")

    @classmethod
    def _load_road_from_file(cls, subject_id: str, road_path: str):
        try:
            with open(road_path, "r", encoding="utf-8") as f:
                road_data = yaml.safe_load(f)
            
            if not road_data: return

            subject_name = road_data.get("title", subject_id.capitalize())
            cls._subjects[subject_id] = Subject(id=subject_id, name=subject_name)
            
            if "road" in road_data:
                for idx, step_entry in enumerate(road_data["road"]):
                    step_id = step_entry["id"]
                    cls._road_steps[step_id] = RoadStep(
                        id=step_id,
                        title=step_entry.get("title", step_id.capitalize()),
                        subtitle=step_entry.get("subtitle"),
                        type=step_entry.get("type", "theory"),
                        order=idx,
                        subject_id=subject_id,
                        ref_id=step_entry.get("ref_id"),
                        page_file=step_entry.get("page"),
                        activated=step_entry.get("activated", False)
                    )
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {road_path}: {e}")

    @classmethod
    def get_subjects(cls) -> List[Subject]:
        return list(cls._subjects.values())

    @classmethod
    def get_subject(cls, subject_id: str) -> Optional[Subject]:
        return cls._subjects.get(subject_id)

    @classmethod
    def get_steps_for_subject(cls, subject_id: str) -> List[RoadStep]:
        steps = [s for s in cls._road_steps.values() if s.subject_id == subject_id]
        return sorted(steps, key=lambda x: x.order)

    @classmethod
    def get_step(cls, step_id: str) -> Optional[RoadStep]:
        return cls._road_steps.get(step_id)

    @classmethod
    def get_exercise(cls, ex_id: str) -> Optional[Exercise]:
        return cls._exercises.get(ex_id)

    @classmethod
    def get_step_content(cls, subject_id: str, page_file: str) -> Optional[str]:
        subject_path = os.path.join(CONTENT_DIR, subject_id)
        page_path = os.path.join(subject_path, page_file)
        if os.path.exists(page_path):
            with open(page_path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    @classmethod
    def get_exercises_for_subject(cls, subject_id: str) -> List[Exercise]:
        return [ex for ex in cls._exercises.values() if ex.subject_id == subject_id]
