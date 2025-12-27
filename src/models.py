from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

# --- Modèles de Base de Données ---

class Subject(SQLModel, table=True):
    id: str = Field(primary_key=True) # ex: "maths"
    name: str
    courses: List["Course"] = Relationship(back_populates="subject")

class Course(SQLModel, table=True):
    id: str = Field(primary_key=True) # ex: "math_01"
    title: str
    order: int
    content_markdown: str
    
    # Stockage des exercices en JSON (SQLite ne gère pas les tableaux nativement)
    exercises: List[dict] = Field(default=[], sa_column=Column(JSON))
    
    subject_id: str = Field(foreign_key="subject.id")
    subject: Subject = Relationship(back_populates="courses")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    avatar: str = "default_avatar.png"
    total_xp: int = Field(default=0)
    
    progress: List["SubjectProgress"] = Relationship(back_populates="user")
    course_progress: List["CourseProgress"] = Relationship(back_populates="user")


class SubjectProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    subject_id: str = Field(foreign_key="subject.id")
    score: int = Field(default=0)
    
    user: User = Relationship(back_populates="progress")

class CourseProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    course_id: str = Field(foreign_key="course.id")
    is_completed: bool = Field(default=False)
    answers: Dict[str, str] = Field(default={}, sa_column=Column(JSON))
    
    user: User = Relationship(back_populates="course_progress")


# --- Schémas API ---

class SubmitRequest(SQLModel):
    user_id: int
    course_id: str
    answers: Dict[str, Any] # { "ex_01": "1" or ["a", "b"] }

class TestSubmitRequest(SQLModel):
    user_id: int
    course_id: str
    answers: Dict[str, Any]
    generated_exercises: List[dict]

