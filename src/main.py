from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional

from src.database import create_db_and_tables, get_session
from src.models import User, Subject, Course, SubjectProgress, SubmitRequest, CourseProgress, TestSubmitRequest
from src.content_loader import sync_content
from src.test_generator import TestGenerator
from src.fraction_generator import FractionGenerator

def smart_compare(user_val, correct_val):
    """
    Compares two values handling strings vs lists, and fractions/floats.
    """
    if user_val is None:
        return False
        
    s_user = str(user_val).strip()
    s_correct = str(correct_val).strip()
    
    # 1. Direct string match
    if s_user == s_correct:
        return True
        
    # 2. Numeric/Fraction match
    try:
        v1 = FractionGenerator.parse_fraction(s_user)
        v2 = FractionGenerator.parse_fraction(s_correct)
        # Only consider match if they are not both zero (unless string matched "0") 
        # OR if we trust parse_fraction not to false-positive on random text.
        # FractionGenerator.parse_fraction returns 0.0 on error. 
        # So we must verify if they were actually numbers.
        
        # Let's try to validate if they look like numbers/fractions first
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
    sync_content()
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
        
    subjects = session.exec(select(Subject)).all()
    
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
        
    subject = session.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    courses = session.exec(select(Course).where(Course.subject_id == subject_id).order_by(Course.order)).all()
    
    # Calculate completed courses
    completed_entries = session.exec(select(CourseProgress).where(
        CourseProgress.user_id == user.id, 
        CourseProgress.is_completed == True
    )).all()
    completed_courses = [c.course_id for c in completed_entries]
    
    return templates.TemplateResponse("subject.html", {
        "request": request,
        "user": user,
        "subject": subject,
        "courses": courses,
        "completed_courses": completed_courses
    })

@app.get("/unit/{course_id}", response_class=HTMLResponse)
def unit_page(course_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Get user progress for this course
    progress = session.exec(select(CourseProgress).where(
        CourseProgress.user_id == user.id,
        CourseProgress.course_id == course_id
    )).first()

    return templates.TemplateResponse("unit.html", {
        "request": request,
        "user": user,
        "course": course,
        "user_progress": progress
    })

@app.post("/submit")
def submit(submission: SubmitRequest, session: Session = Depends(get_session)):
    course = session.get(Course, submission.course_id)
    user = session.get(User, submission.user_id)
    
    if not course or not user:
        raise HTTPException(status_code=404, detail="Not found")

    # Check if already completed
    existing_progress = session.exec(select(CourseProgress).where(
        CourseProgress.user_id == user.id,
        CourseProgress.course_id == course.id
    )).first()

    if existing_progress and existing_progress.is_completed:
        return {"xp_gained": 0, "results": {}, "total_xp": user.total_xp, "already_completed": True}

    xp_gained = 0
    results = {}

    for exercise in course.exercises:
        ex_id = exercise.get("id")
        correct_val = exercise.get("answer")
        user_val = submission.answers.get(ex_id)
        
        # Enhanced comparison logic
        is_correct = smart_compare(user_val, correct_val)
        results[ex_id] = is_correct
        if is_correct:
            xp_gained += 10

    # Save Progress (Always save/update answers, but only mark completed if we want to lock it)
    # Strategy: Mark completed if submitted (assuming all exercises attempted? Or just one submission attempt?)
    # For now, let's mark as completed if they submit to prevent farming.
    
    if not existing_progress:
        existing_progress = CourseProgress(
            user_id=user.id, 
            course_id=course.id, 
            is_completed=True,
            answers=submission.answers
        )
        session.add(existing_progress)
    else:
        existing_progress.is_completed = True
        existing_progress.answers = submission.answers
        session.add(existing_progress)

    if xp_gained > 0:
        user.total_xp += xp_gained
        session.add(user)

        # Update Progress
        progress = session.exec(select(SubjectProgress).where(
            SubjectProgress.user_id == user.id,
            SubjectProgress.subject_id == course.subject_id
        )).first()

        if not progress:
            progress = SubjectProgress(user_id=user.id, subject_id=course.subject_id, score=0)
        
        progress.score += xp_gained
        session.add(progress)
    
    session.commit()

    return {"xp_gained": xp_gained, "results": results, "total_xp": user.total_xp}


@app.get("/test/{course_id}", response_class=HTMLResponse)
def test_page(course_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Generate Exercises
    exercises = TestGenerator.generate_test(course, total_questions=20)
    
    return templates.TemplateResponse("test.html", {
        "request": request,
        "user": user,
        "course": course,
        "exercises": exercises
    })

@app.get("/flash/{subject_id}", response_class=HTMLResponse)
def flash_page(subject_id: str, request: Request, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/")
        
    subject = session.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    courses = session.exec(select(Course).where(Course.subject_id == subject_id)).all()
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found for this subject")
        
    # Generate Exercises from all courses
    exercises = TestGenerator.generate_flash(courses, total_questions=15)
    
    # We use a dummy course object to satisfy the template/submission logic
    # Or we can pass it differently. Let's create a minimal course-like dict for the frontend.
    flash_course = {
        "id": f"flash_{subject_id}",
        "title": f"Mode Flash : {subject.name}",
        "subject_id": subject_id
    }
    
    return templates.TemplateResponse("flash.html", {
        "request": request,
        "user": user,
        "course": flash_course,
        "exercises": exercises
    })

@app.post("/submit_test")
def submit_test(submission: TestSubmitRequest, session: Session = Depends(get_session)):
    user = session.get(User, submission.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_flash = submission.course_id.startswith("flash_")
    subject_id = None
    
    if is_flash:
        # Expected ID format: flash_maths
        subject_id = submission.course_id.replace("flash_", "")
    else:
        course = session.get(Course, submission.course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        subject_id = course.subject_id

    xp_gained = 0
    results = {}

    for exercise in submission.generated_exercises:
        ex_id = exercise.get("id")
        correct_val = exercise.get("answer")
        user_val = submission.answers.get(ex_id)
        
        # Comparison logic
        is_correct = False
        
        # Normalize input to list if it's a drag-drop (often list) but passed as list of 1
        # Or if correct answer is string but user sent list of 1 string
        
        def normalize(val):
            if isinstance(val, list):
                return [str(v).strip() for v in val]
            return [str(val).strip()]

        c_norm = normalize(correct_val)
        u_norm = normalize(user_val) if user_val else []

        # If size mismatch, it's wrong (unless allow partial? No)
        # If size mismatch, it's wrong usually
        if len(c_norm) != len(u_norm):
             is_correct = False
        else:
             # Check item by item with smart_compare
             is_correct = all(smart_compare(u, c) for u, c in zip(u_norm, c_norm))

        results[ex_id] = { "correct": is_correct, "correct_answer": correct_val }
        if is_correct:
            xp_gained += 15 # Bonus XP

    if xp_gained > 0:
        user.total_xp += xp_gained
        session.add(user)
        
        progress = session.exec(select(SubjectProgress).where(
            SubjectProgress.user_id == user.id,
            SubjectProgress.subject_id == subject_id
        )).first()

        if not progress:
            progress = SubjectProgress(user_id=user.id, subject_id=subject_id, score=0)
        
        progress.score += xp_gained
        session.add(progress)

    session.commit()
    
    return {"xp_gained": xp_gained, "results": results, "total_xp": user.total_xp}
