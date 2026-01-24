from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional

from src.database import create_db_and_tables, get_session
from src.models import User, Subject, Course, SubjectProgress, SubmitRequest, RoadStep, RoadStepProgress, TestSubmitRequest, UserEvent, Event
from src.content_manager import ContentManager
from src.test_generator import TestGenerator
from src.fraction_generator import FractionGenerator
from src.models import ExerciseLog, Exercise, ExerciseTemplate
from src.generators import ExerciseFactory
from src.exercise_engine import ExerciseEngine
import re
import time
import random
import os

def check_global_events(user: User, session: Session) -> Optional[Event]:
    events = ContentManager.get_events()
    for event in events:
        if event.conditions == "first_view":
            # Check if user has seen it
            seen = session.exec(select(UserEvent).where(
                UserEvent.user_id == user.id,
                UserEvent.event_id == event.id
            )).first()
            if not seen:
                return event
    return None

def smart_compare(user_val, correct_val, ex_type: Optional[str] = None):
    """
    Compares two values handling strings vs lists, and fractions/floats.
    """
    if user_val is None or correct_val is None:
        return False
        
    # 0. List comparison
    if isinstance(user_val, list) and isinstance(correct_val, list):
        if len(user_val) != len(correct_val):
            return False
            
        u_list = [str(x).strip() for x in user_val]
        c_list = [str(x).strip() for x in correct_val]
        
        if ex_type == "multiselect":
            return sorted(u_list) == sorted(c_list)
        else:
            # For cloze (texte à trou) or drag_drop, order matters
            return u_list == c_list

    s_user = str(user_val).strip()
    s_correct = str(correct_val).strip()
    
    # 1. Direct string match
    if s_user == s_correct:
        return True
        
    # 2. Numeric/Fraction match
    try:
        v1 = FractionGenerator.parse_fraction(s_user)
        v2 = FractionGenerator.parse_fraction(s_correct)
        
        is_num_1 = any(c.isdigit() for c in s_user)
        is_num_2 = any(c.isdigit() for c in s_correct)
        
        if is_num_1 and is_num_2:
            return abs(v1 - v2) < 0.0001
    except:
        pass
        
    return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    ContentManager.load_all()
    yield

app = FastAPI(title="Parcours", lifespan=lifespan)

# Mount Static & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



# --- Dependencies ---
def get_current_user(request: Request, session: Session = Depends(get_session)) -> Optional[User]:
    user_id = request.cookies.get("user_id")
    if user_id:
        return session.get(User, int(user_id))
    return None

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    # Check if logged in
    current_user = get_current_user(request, session)
    if current_user:
         return RedirectResponse(url="/dashboard")
         
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

@app.post("/login")
def login(user_id: int = Form(...)):
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="user_id", value=str(user_id))
    return response

@app.post("/users/")
def create_user(username: str = Form(...), session: Session = Depends(get_session)):
    user = User(username=username)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Auto login
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id))
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    subjects = ContentManager.get_subjects()
    
    # Get progress dict {subject_id: total_score}
    progress_entries = session.exec(select(SubjectProgress).where(SubjectProgress.user_id == user.id)).all()
    progress = {p.subject_id: p.score for p in progress_entries}
    
    # Check global events
    evt = check_global_events(user, session)
    if evt:
        return RedirectResponse(url=f"/event/{evt.id}")

    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "subjects": subjects,
        "progress": progress
    })

@app.get("/subjects/{subject_id}", response_class=HTMLResponse)
def subject_page(subject_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    subject = ContentManager.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    # Get all road steps for this subject from ContentManager
    steps = ContentManager.get_steps_for_subject(subject_id)
    
    # Calculate completed steps
    completed_entries = []
    try:
        completed_entries = session.exec(select(RoadStepProgress).where(
            RoadStepProgress.user_id == user.id, 
            RoadStepProgress.is_completed == True
        )).all()
        
        all_progress = session.exec(select(RoadStepProgress).where(
            RoadStepProgress.user_id == user.id
        )).all()
        
        mastery_map = {p.step_id: p.mastery for p in all_progress}
        
    except Exception as e:
        print(f"ERROR fetching progress: {e}")
        mastery_map = {}
        
    completed_steps = [p.step_id for p in completed_entries]
    
    return templates.TemplateResponse("subject.html", {
        "request": request,
        "user": user,
        "subject": subject,
        "steps": steps,
        "completed_steps": completed_steps,
        "mastery_map": mastery_map
    })

@app.get("/step/{step_id}", response_class=HTMLResponse)
def step_page(step_id: str, request: Request, page_idx: int = 0, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    step = ContentManager.get_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    # Selection of current page
    active_page = None
    if step.pages:
        if page_idx < 0 or page_idx >= len(step.pages):
            return RedirectResponse(url=f"/subjects/{step.subject_id}")
        active_page = step.pages[page_idx]
    else:
        # Fallback to single page logic based on step fields
        active_page = {
            "type": step.type,
            "content": step.content_file,
            "selection": step.selection
        }

    # Handle Conditions (e.g., first_view)
    if active_page.get("type") == "dialogue":
        dialogue_content = ContentManager.get_dialogue(step.subject_id, active_page["content"])
        if not dialogue_content:
             # Skip if no dialogue found
             return RedirectResponse(url=f"/step/{step_id}?page_idx={page_idx + 1}")
        
        # Check conditions
        conditions = []
        for entry in dialogue_content:
            if "conditions" in entry:
                if isinstance(entry["conditions"], list):
                    conditions.extend(entry["conditions"])
                else:
                    conditions.append(entry["conditions"])
        
        if "first_view" in conditions:
            # Check if user has already seen this step
            progress = session.exec(select(RoadStepProgress).where(
                RoadStepProgress.user_id == user.id,
                RoadStepProgress.step_id == step.id
            )).first()
            if progress and progress.is_completed:
                # Redirect to next page
                return RedirectResponse(url=f"/step/{step_id}?page_idx={page_idx + 1}")

        # If we got here, render dialogue
        next_url = f"/step/{step_id}?page_idx={page_idx + 1}" if step.pages and page_idx + 1 < len(step.pages) else f"/subjects/{step.subject_id}"
        return templates.TemplateResponse("dialogue.html", {
            "request": request,
            "user": user,
            "step": step,
            "dialogue": dialogue_content,
            "characters": ContentManager.get_characters(),
            "next_url": next_url
        })

    # Rest of step logic (cours, practice, etc.)
    page_type = active_page.get("type", "cours")
    
    if page_type == "cours":
        progress = session.exec(select(RoadStepProgress).where(
            RoadStepProgress.user_id == user.id,
            RoadStepProgress.step_id == step_id
        )).first()
        
        content = ""
        exercises = []
        content_file = active_page.get("content")
        if content_file:
            content = ContentManager.get_step_content(step.subject_id, content_file)
            if content:
                def replace_exo(match):
                    ex_id = match.group(1)
                    template = ContentManager.get_template(ex_id)
                    if template:
                        ex_data = ExerciseEngine.generate_exercise(template)
                        exercises.append(ex_data)
                        return f"&&{ex_data['id']}&&"
                    else:
                        exercises.append({"type": "error", "question": f"Exercice {ex_id} non trouvé", "id": ex_id})
                        return match.group(0)
                
                content = re.sub(r"&&(?!&)(.+?)&&", replace_exo, content)
        
        dummy_course = {
            "title": step.title,
            "subject_id": step.subject_id,
            "content_markdown": content,
            "exercises": exercises
        }
        
        next_url = f"/step/{step_id}?page_idx={page_idx + 1}" if step.pages and page_idx + 1 < len(step.pages) else None

        return templates.TemplateResponse("unit.html", {
            "request": request,
            "user": user,
            "step": step,
            "course": dummy_course,
            "user_progress": progress,
            "page_idx": page_idx,
            "next_url": next_url
        })
    else:
        # Practice, Exam, etc.
        exercises = []
        selection = active_page.get("selection")
        
        if page_type in ["practice", "exam", "sequence", "validation", "flash"]:
            if selection:
                if isinstance(selection, list):
                    for sel_item in selection:
                        target = sel_item.get("target", [])
                        count = sel_item.get("count", 5)
                        diff = sel_item.get("difficulty")
                        templates_list = ContentManager.select_templates(target, diff)
                        if templates_list:
                            for _ in range(count):
                                t = random.choice(templates_list)
                                exercises.append(ExerciseEngine.generate_exercise(t))
                else:
                    target = selection.get("target", [])
                    count = selection.get("count", 10)
                    diff = selection.get("difficulty")
                    templates_list = ContentManager.select_templates(target, diff)
                    if templates_list:
                        for _ in range(count):
                            t = random.choice(templates_list)
                            exercises.append(ExerciseEngine.generate_exercise(t))
        
        elif page_type == "reinforcement":
            from src.reinforcement_engine import ReinforcementEngine
            exercises = ReinforcementEngine.generate_reinforcement_exercises(
                session, 
                user.id, 
                step.scope or step.subject_id, 
                count=10
            )

        next_url = f"/step/{step_id}?page_idx={page_idx + 1}" if step.pages and page_idx + 1 < len(step.pages) else None
        
        template_name = "flash.html" if page_type == "flash" else "test.html"
        
        return templates.TemplateResponse(template_name, {
            "request": request,
            "user": user,
            "step": step,
            "course": {"title": step.title, "subject_id": step.subject_id},
            "exercises": exercises,
            "page_idx": page_idx,
            "next_url": next_url
        })

@app.post("/submit_step")
def submit_step(submission: SubmitRequest, session: Session = Depends(get_session)):
    step = ContentManager.get_step(submission.step_id)
    user = session.get(User, submission.user_id)
    
    if not step or not user:
        raise HTTPException(status_code=404, detail="Not found")

    xp_gained = 0
    # For theory steps, we just mark as completed
    if step.type == "theory":
        xp_gained = 20
    
    # Save Progress
    progress = session.exec(select(RoadStepProgress).where(
        RoadStepProgress.user_id == user.id,
        RoadStepProgress.step_id == step.id
    )).first()

    if not progress:
        progress = RoadStepProgress(user_id=user.id, step_id=step.id, is_completed=True, answers=submission.answers)
        session.add(progress)
    else:
        if not progress.is_completed:
            progress.is_completed = True
            progress.answers = submission.answers
            session.add(progress)
        else:
            xp_gained = 0 # No double XP

    if xp_gained > 0:
        user.total_xp += xp_gained
        session.add(user)
        # Update Subject Progress
        sub_prog = session.exec(select(SubjectProgress).where(
            SubjectProgress.user_id == user.id,
            SubjectProgress.subject_id == step.subject_id
        )).first()
        if not sub_prog:
            sub_prog = SubjectProgress(user_id=user.id, subject_id=step.subject_id, score=0)
        sub_prog.score += xp_gained
        session.add(sub_prog)
    
    session.commit()
    return {"xp_gained": xp_gained, "total_xp": user.total_xp}

@app.post("/submit_test_step")
def submit_test_step(submission: TestSubmitRequest, session: Session = Depends(get_session)):
    user = session.get(User, submission.user_id)
    step = ContentManager.get_step(submission.step_id)
    if not user or not step:
        raise HTTPException(status_code=404, detail="Not found")

    # Fetch existing progress or initialize as None
    progress = session.exec(select(RoadStepProgress).where(
        RoadStepProgress.user_id == user.id,
        RoadStepProgress.step_id == step.id
    )).first()

    xp_gained = 0
    results = {}
    first_time = False

    # 1. Evaluate Exercises
    for exercise in submission.generated_exercises:
        ex_id = exercise.get("id")
        ex_type = exercise.get("type")
        correct_val = exercise.get("answer")
        user_val = submission.answers.get(ex_id)
        
        is_correct = smart_compare(user_val, correct_val, ex_type=ex_type)
        results[ex_id] = { "correct": is_correct, "correct_answer": correct_val }
        
        # Logging
        try:
             tag = exercise.get("tag", "unknown")
             log_entry = ExerciseLog(
                 user_id=user.id, tag=tag, question_id=ex_id, is_correct=is_correct,
                 timestamp=time.time(), difficulty=exercise.get("meta", {}).get("difficulty", "unknown") 
             )
             session.add(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")

        if is_correct:
            xp_gained += 10

    # 2. Update Progress Based on Step Type
    total_questions = len(submission.generated_exercises)
    nb_correct = sum(1 for r in results.values() if r["correct"])
    
    is_mastery_step = step.type.startswith("flash") or step.type == "validation"
    passed = total_questions > 0 and nb_correct >= total_questions / 2

    if is_mastery_step:
        if not progress:
            progress = RoadStepProgress(user_id=user.id, step_id=step.id, is_completed=False, mastery=0)
            session.add(progress)
            first_time = True
            
        # Mastery logic: Streak or drop
        if nb_correct == total_questions:
            progress.mastery = min(3, progress.mastery + 1)
        else:
            progress.mastery = max(0, progress.mastery - 1)
            
        if passed and not progress.is_completed:
            progress.is_completed = True
            first_time = True
        
        progress.answers = submission.answers
        session.add(progress)
    
    elif passed:
        # Standard practice
        if not progress:
            progress = RoadStepProgress(user_id=user.id, step_id=step.id, is_completed=True, mastery=0)
            session.add(progress)
            first_time = True
        else:
            if not progress.is_completed:
                progress.is_completed = True
                first_time = True
            progress.answers = submission.answers
            session.add(progress)

    # 3. Award XP
    if first_time and xp_gained > 0:
        user.total_xp += xp_gained
        session.add(user)
        
        sub_prog = session.exec(select(SubjectProgress).where(
            SubjectProgress.user_id == user.id,
            SubjectProgress.subject_id == step.subject_id
        )).first()
        
        if not sub_prog:
            sub_prog = SubjectProgress(user_id=user.id, subject_id=step.subject_id, score=0)
            session.add(sub_prog)
            
        sub_prog.score += xp_gained
        session.add(sub_prog)

    session.commit()
    
    return {
        "xp_gained": xp_gained if first_time else 0, 
        "results": results, 
        "total_xp": user.total_xp,
        "mastery": progress.mastery if progress else 0
    }

@app.get("/flash/{subject_id}", response_class=HTMLResponse)
def flash_page(subject_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    subject = ContentManager.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    # Generate Exercises (Flash Mode)
    # Since we don't have courses in DB anymore, we use TestGenerator differently or provide specific logic
    # For now, let's use a simplified approach for subject-wide flash
    dummy_course = type('obj', (object,), {'generator_type': 'multiplication'})
    exercises = TestGenerator.generate_step_exercises(dummy_course, "validation", count=15)
    
    flash_course = {
        "id": f"flash_{subject_id}",
        "title": f"Mode Flash : {subject.name}",
        "subject_id": subject_id
    }
    
    flash_step = {
        "id": f"flash_{subject_id}",
        "title": f"Mode Flash : {subject.name}",
        "type": "flash"
    }

    return templates.TemplateResponse("test.html", {
        "request": request,
        "user": user,
        "course": flash_course,
        "step": flash_step,
        "exercises": exercises
    })

@app.get("/event/{event_id}", response_class=HTMLResponse)
def event_page(event_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    event = ContentManager.get_event(event_id)
    if not event:
        return RedirectResponse(url="/dashboard")

    # Mark as seen
    seen = session.exec(select(UserEvent).where(
        UserEvent.user_id == user.id,
        UserEvent.event_id == event_id
    )).first()
    
    if not seen:
        ue = UserEvent(user_id=user.id, event_id=event_id, timestamp=time.time())
        session.add(ue)
        session.commit()
        
    if event.type == "dialogue":
        # Search for dialogue content
        dialogue_content = None
        # 1. Try direct path
        dialogue_content = ContentManager.get_dialogue("global", event.content)
        
        # 2. Try in subjects
        if not dialogue_content:
            for sub in ContentManager.get_subjects():
                dialogue_content = ContentManager.get_dialogue(sub.id, event.content)
                if dialogue_content: break
        
        if not dialogue_content:
             return RedirectResponse(url="/dashboard")
             
        # Create dummy step for template
        dummy_step = type('obj', (object,), {
            "id": event.id,
            "title": "Introduction", # Could be added to Event model
            "subject_id": "global",
            "type": "dialogue",
            "pages": [] 
        })

        return templates.TemplateResponse("dialogue.html", {
            "request": request,
            "user": user,
            "step": dummy_step,
            "dialogue": dialogue_content,
            "characters": ContentManager.get_characters(),
            "next_url": "/dashboard"
        })
        
    return RedirectResponse(url="/dashboard")


# --- Admin Routes ---

@app.get("/admin/reset_all")
def admin_reset_all(request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user or not user.is_admin:
         return RedirectResponse(url="/")
    
    # Delete all progress
    sub_progs = session.exec(select(SubjectProgress).where(SubjectProgress.user_id == user.id)).all()
    for sp in sub_progs:
        session.delete(sp)
        
    step_progs = session.exec(select(RoadStepProgress).where(RoadStepProgress.user_id == user.id)).all()
    for sp in step_progs:
        session.delete(sp)
    
    user.total_xp = 0
    session.add(user)
    session.commit()
    
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/admin/validate_all")
def admin_validate_all(request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user or not user.is_admin:
         return RedirectResponse(url="/")
         
    # Mark all steps as completed from ContentManager
    all_subjects = ContentManager.get_subjects()
    for sub in all_subjects:
        steps = ContentManager.get_steps_for_subject(sub.id)
        for step in steps:
            prog = session.exec(select(RoadStepProgress).where(
                RoadStepProgress.user_id == user.id,
                RoadStepProgress.step_id == step.id
            )).first()
            if not prog:
                prog = RoadStepProgress(user_id=user.id, step_id=step.id, is_completed=True, mastery=3)
                session.add(prog)
            else:
                prog.is_completed = True
                prog.mastery = 3
                session.add(prog)
                
        sub_prog = session.exec(select(SubjectProgress).where(
            SubjectProgress.user_id == user.id,
            SubjectProgress.subject_id == sub.id
        )).first()
        if not sub_prog:
            sub_prog = SubjectProgress(user_id=user.id, subject_id=sub.id, score=999)
        else:
            sub_prog.score = 999
        session.add(sub_prog)
             
    user.total_xp = 99999
    session.add(user)
    session.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/admin/validate_step/{step_id}")
def admin_validate_step(step_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user or not user.is_admin:
         return RedirectResponse(url="/")
    
    step = ContentManager.get_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
        
    progress = session.exec(select(RoadStepProgress).where(
        RoadStepProgress.user_id == user.id,
        RoadStepProgress.step_id == step_id
    )).first()
    
    if not progress:
        progress = RoadStepProgress(user_id=user.id, step_id=step_id, is_completed=True, mastery=3)
    else:
        progress.is_completed = True
        progress.mastery = 3
    session.add(progress)
    session.commit()
    return RedirectResponse(url=f"/subjects/{step.subject_id}", status_code=303)

@app.get("/admin/invalidate_step/{step_id}")
def admin_invalidate_step(step_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user or not user.is_admin:
         return RedirectResponse(url="/")
         
    step = ContentManager.get_step(step_id)
    if not step:
         raise HTTPException(status_code=404, detail="Step not found")

    progress = session.exec(select(RoadStepProgress).where(
        RoadStepProgress.user_id == user.id,
        RoadStepProgress.step_id == step_id
    )).first()
    
    if progress:
        session.delete(progress)
        session.commit()
        
    return RedirectResponse(url=f"/subjects/{step.subject_id}", status_code=303)

@app.get("/debug", response_class=HTMLResponse)
def debug_dashboard(request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user or not user.is_admin:
         # For development, allow access even if not admin, or just check if user exists
         if not user:
             return RedirectResponse(url="/")
    
    users = session.exec(select(User)).all()
    templates_dict = ContentManager.get_all_templates()
    subjects = ContentManager.get_all_subjects()
    
    # Group templates by subject (based on prefix of ID or subject_id in templates)
    grouped_templates = {}
    for t_id, t in templates_dict.items():
        # Try to find which subject this template belongs to
        # In this codebase, templates are usually loaded within a subject folder
        # We'll use a simple heuristic or just group them all
        subject_id = "global"
        # Heuristic: check if t_id starts with subject_id
        for s_id in subjects.keys():
            if t_id.startswith(s_id):
                subject_id = s_id
                break
        
        if subject_id not in grouped_templates:
            grouped_templates[subject_id] = []
        grouped_templates[subject_id].append(t)

    # Dialogues: events + file scan
    dialogue_list = []
    
    # 1. From Events
    for e in ContentManager.get_events():
        if e.type == "dialogue":
             dialogue_list.append({
                 "id": e.id,
                 "name": f"Event: {e.id}",
                 "path": e.content,
                 "subject": "global",
                 "type": "event"
             })

    # 2. From Filesystem (Ad-hoc)
    for root, dirs, files in os.walk("content"):
        for f in files:
            if "dialogue" in f and f.endswith(".yaml"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, "content")
                
                # Guess subject
                parts = rel_path.split(os.sep)
                subject_id = parts[0] if len(parts) > 1 else "global"
                if subject_id == "content": subject_id = "global"

                # Check if already in list
                if not any(d["path"] == rel_path or d["path"] == f for d in dialogue_list):
                     dialogue_list.append({
                         "id": f,
                         "name": f,
                         "path": rel_path,
                         "subject": subject_id,
                         "type": "file"
                     })

    return templates.TemplateResponse("debug.html", {
        "request": request,
        "user": user,
        "users": users,
        "grouped_templates": grouped_templates,
        "subjects": subjects,
        "dialogues": dialogue_list
    })

@app.get("/debug/view_dialogue", response_class=HTMLResponse)
def debug_view_dialogue(path: str, subject: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/")
    
    dialogue_content = ContentManager.get_dialogue(subject, path)
    if not dialogue_content:
        raise HTTPException(status_code=404, detail="Dialogue not found")
        
    dummy_step = type('obj', (object,), {
        "id": "debug",
        "title": f"Debug: {os.path.basename(path)}",
        "subject_id": subject,
        "type": "dialogue"
    })

    return templates.TemplateResponse("dialogue.html", {
        "request": request,
        "user": user,
        "step": dummy_step,
        "dialogue": dialogue_content,
        "characters": ContentManager.get_characters(),
        "next_url": "/debug"
    })

@app.get("/debug/test/{mode}/{template_id}", response_class=HTMLResponse)
def debug_test_exercise(mode: str, template_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    template = ContentManager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    exercises = [ExerciseEngine.generate_exercise(template) for _ in range(5)]
    
    subject_id = "debug"
    for s_id in ContentManager.get_all_subjects().keys():
        if template_id.startswith(s_id):
            subject_id = s_id
            break

    dummy_course = {
        "id": f"debug_{template_id}",
        "title": f"Test: {template_id}",
        "subject_id": subject_id
    }
    
    dummy_step = {
        "id": f"debug_{template_id}",
        "title": f"Test: {template_id}",
        "type": mode,
        "subject_id": subject_id
    }

    template_name = "test.html" if mode == "practice" else "flash.html"
    
    return templates.TemplateResponse(template_name, {
        "request": request,
        "user": user,
        "course": dummy_course,
        "step": dummy_step,
        "exercises": exercises
    })
