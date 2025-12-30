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
from sqlmodel import Session, select
from src.models import Subject, Course, RoadStep
from src.database import engine

CONTENT_DIR = "content"

def sync_content():
    print("🔄 Démarrage de la synchronisation du contenu (Mode Route)...")
    
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
                
                # Charger le fichier road.yaml
                road_path = os.path.join(subject_path, "road.yaml")
                if not os.path.exists(road_path):
                    print(f"⚠️ Aucun fichier road.yaml trouvé pour {subject_folder}. Utilisation du meta.yaml legacy ?")
                    # On pourrait gérer un fallback, mais ici on impose la nouvelle structure
                    continue

                with open(road_path, "r", encoding="utf-8") as f:
                    road_data = yaml.safe_load(f)
                    if not road_data or "road" not in road_data:
                        print(f"❌ Format invalide pour {road_path}")
                        continue

                # 2. Synchroniser les cours et les étapes dans l'ordre de la route
                global_step_order = 0
                for course_entry in road_data["road"]:
                    course_id = course_entry["id"]
                    title = course_entry.get("title", course_id.capitalize())
                    generator = course_entry.get("generator", "generic")
                    theory_file = course_entry.get("theory_file")

                    # Charger le contenu markdown si spécifié
                    content = ""
                    exercises = []
                    if theory_file:
                        full_theory_path = os.path.join(subject_path, theory_file)
                        if os.path.exists(full_theory_path):
                            with open(full_theory_path, "r", encoding="utf-8") as tf:
                                post = frontmatter.load(tf)
                                content = post.content
                                exercises = post.get("exercises", [])
                                session_config = post.get("session", {})
                        else:
                            print(f"⚠️ Fichier théorie manquant: {full_theory_path}")
                            session_config = {}

                    # Upsert du cours
                    course = session.get(Course, course_id)
                    if not course:
                        course = Course(
                            id=course_id,
                            title=title,
                            content_markdown=content,
                            generator_type=generator,
                            exercises=exercises,
                            session_config=session_config,
                            subject_id=subject.id
                        )
                    else:
                        course.title = title
                        course.content_markdown = content
                        course.generator_type = generator
                        course.exercises = exercises
                        course.session_config = session_config
                    
                    session.add(course)
                    session.flush() # Pour avoir l'ID si nécessaire

                    # Synchroniser les étapes du cours
                    for step_entry in course_entry.get("steps", []):
                        stype = step_entry["type"]
                        stitle = step_entry.get("title", stype.capitalize())
                        step_id = f"{course_id}_{stype}"
                        
                        step = session.get(RoadStep, step_id)
                        if not step:
                            step = RoadStep(
                                id=step_id,
                                title=stitle,
                                type=stype,
                                order=global_step_order,
                                course_id=course_id,
                                subject_id=subject.id
                            )
                        else:
                            step.title = stitle
                            step.order = global_step_order
                        
                        session.add(step)
                        global_step_order += 1
        
        session.commit()
        print("✅ Synchronisation terminée.")
