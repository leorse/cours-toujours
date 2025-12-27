import os
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
                # Création / Mise à jour de la matière
                subject = session.get(Subject, subject_folder)
                if not subject:
                    subject = Subject(id=subject_folder, name=subject_folder.capitalize())
                    session.add(subject)
                
                # 2. Parcourir les fichiers Markdown (Cours)
                for filename in os.listdir(subject_path):
                    if filename.endswith(".md"):
                        file_path = os.path.join(subject_path, filename)
                        
                        with open(file_path, "r", encoding="utf-8") as f:
                            post = frontmatter.load(f)
                        
                        meta = post.metadata
                        content = post.content
                        course_id = meta.get("id")

                        if not course_id:
                            continue

                        # Upsert du cours
                        course = session.get(Course, course_id)
                        if not course:
                            course = Course(
                                id=course_id,
                                title=meta.get("title", "Sans titre"),
                                order=meta.get("order", 99),
                                content_markdown=content,
                                exercises=meta.get("exercises", []),
                                subject_id=subject.id
                            )
                        else:
                            course.title = meta.get("title", "Sans titre")
                            course.order = meta.get("order", 99)
                            course.content_markdown = content
                            course.exercises = meta.get("exercises", [])
                            course.subject_id = subject.id
                        
                        session.add(course)
        
        session.commit()
        print("✅ Synchronisation terminée.")
