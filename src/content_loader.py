import os
import yaml
import frontmatter
from sqlmodel import Session
from src.models import Subject, Course
from src.database import engine

CONTENT_DIR = "content"

import os
import yaml
import frontmatter
from sqlmodel import Session, select, delete
from src.models import Subject, Course, RoadStep, Exercise
from src.database import engine

CONTENT_DIR = "content"

def sync_content():
    print("🔄 Démarrage de la synchronisation du contenu (Nouveaux Format)...")
    
    with Session(engine) as session:
        if not os.path.exists(CONTENT_DIR):
            os.makedirs(CONTENT_DIR)
            print(f"⚠️ Dossier {CONTENT_DIR} créé.")
            return

        # 1. Parcourir les dossiers (Matières)
        for subject_folder in os.listdir(CONTENT_DIR):
            subject_path = os.path.join(CONTENT_DIR, subject_folder)
            
            if os.path.isdir(subject_path):
                subject = session.get(Subject, subject_folder)
                if not subject:
                    display_name = subject_folder.replace("_", " ").capitalize()
                    subject = Subject(id=subject_folder, name=display_name)
                    session.add(subject)
                
                # --- A. Charger tous les exercices YAML (récursivement) ---
                for root, dirs, files in os.walk(subject_path):
                    for filename in files:
                        if filename.endswith(".yaml") and filename not in ["road.yaml", "road_2.yaml", "meta.yaml"]:
                            yaml_path = os.path.join(root, filename)
                            with open(yaml_path, "r", encoding="utf-8") as f:
                                data = yaml.safe_load(f)
                                if data and "exercices" in data:
                                    for ex_data in data["exercices"]:
                                        ex_id = ex_data.get("id")
                                        if not ex_id: continue
                                        
                                        exercise = session.get(Exercise, ex_id)
                                        if not exercise:
                                            exercise = Exercise(id=ex_id, subject_id=subject.id, data=ex_data)
                                        else:
                                            exercise.data = ex_data
                                            exercise.subject_id = subject.id
                                        session.add(exercise)
                
                session.flush()

                # --- B. Charger le fichier road.yaml ---
                # Priorité à road_2.yaml si présent pour le test
                road_path = os.path.join(subject_path, "road_2.yaml")
                if not os.path.exists(road_path):
                    road_path = os.path.join(subject_path, "road.yaml")
                
                if not os.path.exists(road_path):
                    print(f"⚠️ Aucun fichier road.yaml trouvé pour {subject_folder}.")
                    continue

                with open(road_path, "r", encoding="utf-8") as f:
                    road_data = yaml.safe_load(f)
                    if not road_data or "road" not in road_data:
                        print(f"❌ Format invalide pour {road_path}")
                        continue

                # 2. Synchroniser les étapes de la route
                # On peut choisir de vider les étapes existantes ou de faire un upsert intelligent
                # Ici on va rester sur l'upsert par ID
                
                global_step_order = 0
                for step_entry in road_data["road"]:
                    step_id = step_entry["id"]
                    stitle = step_entry.get("title", step_id.capitalize())
                    ssubtitle = step_entry.get("subtitle")
                    stype = step_entry.get("type")
                    
                    # Nouveaux champs
                    ref_id = step_entry.get("ref_id")
                    page_file = step_entry.get("page")
                    
                    step = session.get(RoadStep, step_id)
                    if not step:
                        step = RoadStep(
                            id=step_id,
                            title=stitle,
                            subtitle=ssubtitle,
                            type=stype,
                            order=global_step_order,
                            subject_id=subject.id,
                            ref_id=ref_id,
                            page_file=page_file
                        )
                    else:
                        step.title = stitle
                        step.subtitle = ssubtitle
                        step.type = stype
                        step.order = global_step_order
                        step.ref_id = ref_id
                        step.page_file = page_file
                    
                    session.add(step)
                    global_step_order += 1
        
        session.commit()
        print("✅ Synchronisation terminée.")
