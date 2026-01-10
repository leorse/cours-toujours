from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional

from src.database import create_db_and_tables, get_session
from src.models import User, Subject, Course, SubjectProgress, SubmitRequest, RoadStep, RoadStepProgress, TestSubmitRequest
from src.content_manager import ContentManager
from src.test_generator import TestGenerator
from src.fraction_generator import FractionGenerator
from src.models import ExerciseLog, Exercise, ExerciseTemplate
from src.generators import ExerciseFactory
from src.exercise_engine import ExerciseEngine
import re
import time

def smart_compare(user_val, correct_val, ex_type: Optional[str] = None):
    """
    Compares two values handling strings vs lists, and fractions/floats.
    """
    if user_val is None:
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

app = FastAPI(title="Cours Toujours!", lifespan=lifespan)

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
def step_page(step_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    step = ContentManager.get_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    # Progression check: is the previous step completed or is current step activated?
    if step.order > 0 and not step.activated and not user.is_admin:
        all_steps = ContentManager.get_steps_for_subject(step.subject_id)
        if step.order < len(all_steps):
            prev_step = all_steps[step.order - 1]
            progress = session.exec(select(RoadStepProgress).where(
                RoadStepProgress.user_id == user.id,
                RoadStepProgress.step_id == prev_step.id,
                RoadStepProgress.is_completed == True
            )).first()
            if not progress:
                # We could redirect here if we wanted to enforce strictly
                pass

    if step.type == "cours":
        progress = session.exec(select(RoadStepProgress).where(
            RoadStepProgress.user_id == user.id,
            RoadStepProgress.step_id == step_id
        )).first()
        
        # Charger le markdown
        content = ""
        exercises = []
        if step.content_file:
            content = ContentManager.get_step_content(step.subject_id, step.content_file)
            if content:
                    # Parser les exercices &&id&&
                    def replace_exo(match):
                        ex_id = match.group(1)
                        # Pour les cours, on peut encore avoir des exercices statiques ou des templates
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
        
        return templates.TemplateResponse("unit.html", {
            "request": request,
            "user": user,
            "step": step,
            "course": dummy_course,
            "user_progress": progress
        })
    else:
        # Render exercise page (test.html style)
        exercises = []
        
        if step.type in ["practice", "exam", "sequence"]:
            # Logic de sélection
            selection = step.selection
            if selection:
                # Si c'est une liste de sélections (ex: exam)
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
                    # Sélection unique (practice simple)
                    target = selection.get("target", [])
                    count = selection.get("count", 10)
                    diff = selection.get("difficulty")
                    
                    templates_list = ContentManager.select_templates(target, diff)
                    if templates_list:
                        for _ in range(count):
                            t = random.choice(templates_list)
                            exercises.append(ExerciseEngine.generate_exercise(t))
        
        elif step.type == "reinforcement":
            from src.reinforcement_engine import ReinforcementEngine
            exercises = ReinforcementEngine.generate_reinforcement_exercises(
                session, 
                user.id, 
                step.scope or step.subject_id, 
                count=10
            )

        if not exercises:
             # Fallback
             exercises = []
        
        if step.type == "flash": # Flash peut être un type spécial si souhaité, sinon practice
            return templates.TemplateResponse("flash.html", {
                "request": request,
                "user": user,
                "step": step,
                "course": {"title": step.title, "subject_id": step.subject_id},
                "exercises": exercises
            })

        return templates.TemplateResponse("test.html", {
            "request": request,
            "user": user,
            "step": step,
            "course": {"title": step.title, "subject_id": step.subject_id},
            "exercises": exercises
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

    xp_gained = 0
    results = {}
    first_time = False

    for exercise in submission.generated_exercises:
        ex_id = exercise.get("id")
        ex_type = exercise.get("type")
        correct_val = exercise.get("answer")
        user_val = submission.answers.get(ex_id)
        
        is_correct = smart_compare(user_val, correct_val, ex_type=ex_type)
        results[ex_id] = { "correct": is_correct, "correct_answer": correct_val }
        
        # --- LOGGING ---
        try:
             # Extract tag if present
             tag = exercise.get("tag", "unknown")
             
             log_entry = ExerciseLog(
                 user_id=user.id,
                 tag=tag,
                 question_id=ex_id,
                 is_correct=is_correct,
                 timestamp=time.time(),
                 difficulty=exercise.get("meta", {}).get("difficulty", "unknown") 
             )
             session.add(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")

        if is_correct:
            xp_gained += 10

    # Calculate Mastery for Flash Steps OR Validation Steps
    # User wants mastery tiers for "tests" (validation) and "flash".
    if step.type.startswith("flash") or step.type == "validation":
        total_questions = len(submission.generated_exercises)
        score = sum(1 for r in results.values() if r["correct"])
        
        progress = session.exec(select(RoadStepProgress).where(
            RoadStepProgress.user_id == user.id,
            RoadStepProgress.step_id == step.id
        )).first()
        
        if not progress:
            progress = RoadStepProgress(user_id=user.id, step_id=step.id, is_completed=False, mastery=0)
            session.add(progress)
            first_time = True
            
        current_mastery = progress.mastery
        
        if score == total_questions:
            # Streak +1 (Max 3)
            current_mastery = min(3, current_mastery + 1)
        else:
            # Any error -> Drop by 1 (Min 0)
             current_mastery = max(0, current_mastery - 1)
            
        progress.mastery = current_mastery
        
        # Mark completed logic (e.g. > 50%)
        # For validation, maybe we want strict 50%? kept same.
        if score >= total_questions / 2:
            if not progress.is_completed:
                 progress.is_completed = True
                 first_time = True
        
        progress.answers = submission.answers
        session.add(progress)
    
    else:
        # Standard logic (Practice, etc.) - No Mastery tracking requested yet, or simple.
        # Keeping simple completion for practice.
        nb_correct = len([r for r in results.values() if r["correct"]])
         
        if len(submission.generated_exercises) > 0 and nb_correct >= len(submission.generated_exercises) / 2:
            progress = session.exec(select(RoadStepProgress).where(
                RoadStepProgress.user_id == user.id, 
                RoadStepProgress.step_id == step.id
            )).first()
            
            if not progress:
                progress = RoadStepProgress(user_id=user.id, step_id=step.id, is_completed=True)
                session.add(progress)
                first_time = True
            else:
                if not progress.is_completed:
                    progress.is_completed = True
                    first_time = True
                session.add(progress)
            
            # Update answers
            if progress:
                progress.answers = submission.answers
                session.add(progress)

    # Award XP if first time completed (or first time played handling above)
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
