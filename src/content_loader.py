import os
import yaml
import frontmatter
from sqlmodel import Session
from src.models import Subject, Course
from src.database import engine

CONTENT_DIR = "content"

def sync_content():
    print("🔄 Démarrage de la synchronisation du contenu...")
    
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
                
                # Charger l'ordre des catégories si disponible
                subject_meta_path = os.path.join(subject_path, "meta.yaml")
                category_order_map = {}
                if os.path.exists(subject_meta_path):
                    with open(subject_meta_path, "r", encoding="utf-8") as f:
                        subject_meta = yaml.safe_load(f)
                        if subject_meta and "categories" in subject_meta:
                            category_order_map = {name: idx for idx, name in enumerate(subject_meta["categories"])}

                # 2. Explorer récursivement pour trouver des fichiers .md
                for root, dirs, files in os.walk(subject_path):
                    # Charger l'ordre des cours dans cette sous-catégorie
                    category_meta_path = os.path.join(root, "meta.yaml")
                    course_order_map = {}
                    if os.path.exists(category_meta_path):
                        with open(category_meta_path, "r", encoding="utf-8") as f:
                            category_meta = yaml.safe_load(f)
                            if category_meta and "courses" in category_meta:
                                course_order_map = {cid: idx for idx, cid in enumerate(category_meta["courses"])}

                    for filename in files:
                        if filename.endswith(".md"):
                            file_path = os.path.join(root, filename)
                            
                            # Déterminer la catégorie
                            rel_path = os.path.relpath(root, subject_path)
                            category_folder_name = None
                            category_desc = None
                            cat_order = 999
                            
                            if rel_path != ".":
                                # La catégorie est basée sur le dossier relatif
                                category_folder_name = rel_path.split(os.sep)[0] # On prend seulement le 1er niveau pour la catégorie
                                cat_order = category_order_map.get(category_folder_name, 999)
                                
                                category_desc = category_folder_name.replace("_", " ").capitalize()
                                if "Fractions" in category_desc: category_desc = "Fractions"

                            with open(file_path, "r", encoding="utf-8") as f:
                                try:
                                    post = frontmatter.load(f)
                                except Exception as e:
                                    print(f"❌ Erreur lors du chargement de {file_path}: {e}")
                                    continue
                            
                            meta = post.metadata
                            content = post.content
                            course_id = meta.get("id")

                            if not course_id:
                                continue

                            # Déterminer l'ordre
                            order = course_order_map.get(course_id, meta.get("order", 99))

                            # Upsert du cours
                            course = session.get(Course, course_id)
                            if not course:
                                course = Course(
                                    id=course_id,
                                    title=meta.get("title", "Sans titre"),
                                    order=order,
                                    content_markdown=content,
                                    exercises=meta.get("exercises", []),
                                    subject_id=subject.id,
                                    category_name=category_desc,
                                    category_order=cat_order
                                )
                            else:
                                course.title = meta.get("title", "Sans titre")
                                course.order = order
                                course.content_markdown = content
                                course.exercises = meta.get("exercises", [])
                                course.subject_id = subject.id
                                course.category_name = category_desc
                                course.category_order = cat_order
                            
                            session.add(course)
        
        session.commit()
        print("✅ Synchronisation terminée.")
