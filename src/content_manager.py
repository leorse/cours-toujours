import os
import yaml
import frontmatter
from typing import List, Dict, Optional, Any
from src.models import Subject, Chapter, RoadStep, Course, Exercise, ExerciseTemplate, Event

CONTENT_DIR = "content"

class ContentManager:
    _subjects: Dict[str, Subject] = {}
    _chapters: Dict[str, Chapter] = {}
    _road_steps: Dict[str, RoadStep] = {}
    _templates: Dict[str, ExerciseTemplate] = {}
    _events: Dict[str, Event] = {}

    @classmethod
    def load_all(cls):
        print("🔄 Chargement dynamique du contenu...")
        cls._subjects = {}
        cls._chapters = {}
        cls._road_steps = {}
        cls._templates = {}
        
        cours_path = os.path.join(CONTENT_DIR, "cours.yaml")
        if not os.path.exists(cours_path):
            print("⚠️ Fichier cours.yaml manquant.")
            return
        
        # Charger les personnages
        cls._load_characters()

        try:
            with open(cours_path, "r", encoding="utf-8") as f:
                cours_data = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Erreur lecture cours.yaml: {e}")
            return
            
        if not cours_data or "cours" not in cours_data:
            print("❌ Format invalide pour cours.yaml")
            return

        if not cours_data or "cours" not in cours_data:
            print("❌ Format invalide pour cours.yaml")
            return
            
        cls._events = {}

        for entry in cours_data["cours"]:
            if "events" in entry:
                for evt_data in entry["events"]:
                     e_id = evt_data.get("id")
                     if e_id:
                         cls._events[e_id] = Event(
                             id=e_id,
                             type=evt_data.get("type"),
                             conditions=evt_data.get("conditions"),
                             content=evt_data.get("content")
                         )
                continue

            page_entry = entry.get("page")

            # 3 formats supportés :
            # 1. page: chemin.yaml                        (string)
            # 2. page:\n    content: chemin.yaml\n    image: ... (dict imbriqué, indentation correcte)
            # 3. page: null + content:/image: en clés sœurs  (mauvaise indentation YAML tolérée)
            if isinstance(page_entry, dict):
                rel_path = page_entry.get("content")
                subject_image = page_entry.get("image")
            elif isinstance(page_entry, str):
                rel_path = page_entry
                subject_image = None
            elif page_entry is None and "content" in entry:
                rel_path = entry.get("content")
                subject_image = entry.get("image")
            else:
                continue

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
            cls._load_road(subject_id, road_path, subject_image)
            
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
                                            tags=t_data.get("tags") or t_data.get("target") or [],
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
    def _load_road(cls, subject_id: str, road_path: str, subject_image: str = None):
        try:
            with open(road_path, "r", encoding="utf-8") as f:
                road_data = yaml.safe_load(f)
            if not road_data: return

            subject_name = road_data.get("title", subject_id.capitalize())
            cls._subjects[subject_id] = Subject(id=subject_id, name=subject_name, image=subject_image)
            
            global_idx = 0

            # Format avec chapitres : chapters: [{id, title, icon, road: [...] ou road: "fichier.yaml"}]
            if "chapters" in road_data:
                for chap_order, chap_entry in enumerate(road_data["chapters"]):
                    chap_id = chap_entry.get("id", f"chap_{chap_order}")
                    cls._chapters[chap_id] = Chapter(
                        id=chap_id,
                        title=chap_entry.get("title", chap_id),
                        subject_id=subject_id,
                        order=chap_order,
                        icon=chap_entry.get("icon")
                    )
                    road_val = chap_entry.get("road", [])
                    # road peut être une liste inline ou un chemin vers un fichier yaml
                    if isinstance(road_val, str):
                        chap_file = os.path.join(os.path.dirname(road_path), road_val)
                        road_entries = cls._load_chapter_file(chap_file)
                    else:
                        road_entries = road_val
                    cls._load_steps(subject_id, road_entries, global_idx, chap_id)
                    loaded = len([s for s in cls._road_steps.values() if s.chapter_id == chap_id])
                    print(f"  📌 Chapitre '{chap_id}': {loaded} étapes chargées")
                    global_idx += len(road_entries)

            # Format plat legacy : road: [...]
            elif "road" in road_data:
                cls._load_steps(subject_id, road_data["road"], global_idx, chapter_id=None)
        except Exception as e:
            print(f"❌ Erreur route {road_path}: {e}")

    @classmethod
    def _load_chapter_file(cls, file_path: str) -> list:
        """Charge un fichier yaml de chapitre et retourne la liste des étapes (clé 'chapter:')."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and "chapter" in data:
                return data["chapter"]
            else:
                print(f"⚠️ Clé 'chapter' introuvable dans {file_path}. Clés: {list(data.keys()) if data else 'vide'}")
        except Exception as e:
            print(f"❌ Erreur lecture chapitre {file_path}: {e}")
        return []

    @classmethod
    def _load_steps(cls, subject_id: str, road_entries: list, start_idx: int, chapter_id: Optional[str]):
        global_idx = start_idx
        for step_entry in road_entries:
            s_type = step_entry.get("type", "cours")

            if s_type == "sequence":
                repeat = step_entry.get("repeat", 1)
                step_config = step_entry.get("step_config", {})
                for i in range(1, repeat + 1):
                    raw_id = f"{step_entry['id']}_{i}"
                    s_id = f"{subject_id}.{raw_id}"
                    title = step_entry.get("title", "").replace("{index}", str(i))
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
                        chapter_id=chapter_id,
                        selection=selection,
                        activated=step_entry.get("activated", False),
                        pages=step_config.get("pages", [])
                    )
                    global_idx += 1
            else:
                raw_id = step_entry["id"]
                s_id = f"{subject_id}.{raw_id}"
                cls._road_steps[s_id] = RoadStep(
                    id=s_id,
                    title=step_entry.get("title", s_id.capitalize()),
                    subtitle=step_entry.get("subtitle"),
                    type=s_type,
                    order=global_idx,
                    subject_id=subject_id,
                    chapter_id=chapter_id,
                    content_file=step_entry.get("content"),
                    selection=step_entry.get("selection"),
                    scope=step_entry.get("scope"),
                    strategy=step_entry.get("strategy", "weakest_points"),
                    activated=step_entry.get("activated", False),
                    pages=step_entry.get("pages", [])
                )
                global_idx += 1

    @classmethod
    def get_subjects(cls) -> List[Subject]: return list(cls._subjects.values())
    @classmethod
    def get_all_subjects(cls) -> Dict[str, Subject]: return cls._subjects
    @classmethod
    def get_subject(cls, subject_id: str) -> Optional[Subject]: return cls._subjects.get(subject_id)
    @classmethod
    def get_all_templates(cls) -> Dict[str, ExerciseTemplate]: return cls._templates
    @classmethod
    def get_chapters_for_subject(cls, subject_id: str) -> List[Chapter]:
        chapters = [c for c in cls._chapters.values() if c.subject_id == subject_id]
        return sorted(chapters, key=lambda x: x.order)
    @classmethod
    def get_steps_for_subject(cls, subject_id: str) -> List[RoadStep]:
        steps = [s for s in cls._road_steps.values() if s.subject_id == subject_id]
        return sorted(steps, key=lambda x: x.order)
    @classmethod
    def get_steps_for_chapter(cls, chapter_id: str) -> List[RoadStep]:
        steps = [s for s in cls._road_steps.values() if s.chapter_id == chapter_id]
        return sorted(steps, key=lambda x: x.order)
    @classmethod
    def get_step(cls, step_id: str) -> Optional[RoadStep]: return cls._road_steps.get(step_id)
    @classmethod
    def get_template(cls, t_id: str) -> Optional[ExerciseTemplate]: return cls._templates.get(t_id)
    @classmethod
    def get_events(cls) -> List[Event]: return list(cls._events.values())
    @classmethod
    def get_event(cls, event_id: str) -> Optional[Event]: return cls._events.get(event_id)

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

    _characters: Dict[str, Any] = {}

    @classmethod
    def _load_characters(cls):
        char_path = os.path.join("config", "personnages.yaml")
        if not os.path.exists(char_path):
            print("⚠️ Fichier personnages.yaml manquant.")
            return
            
        try:
            with open(char_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "personnages" in data:
                    cls._characters = {c["name"]: c for c in data["personnages"]}
        except Exception as e:
            print(f"❌ Erreur lecture personnages.yaml: {e}")

    @classmethod
    def get_characters(cls) -> Dict[str, Any]:
        return cls._characters
