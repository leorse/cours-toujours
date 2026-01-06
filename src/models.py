from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

# --- Modèles de Base de Données ---

# --- Modèles de Contenu (Fichiers) ---

class Subject(SQLModel):
    id: str # ex: "maths"
    name: str

class Course(SQLModel):
    id: str # ex: "math_01"
    title: str
    content_markdown: str
    generator_type: str = "generic"
    exercises: List[dict] = []
    session_config: Dict[str, Any] = {}
    subject_id: str

class Exercise(SQLModel):
    id: str
    subject_id: str
    data: Dict[str, Any] = {}

class RoadStep(SQLModel):
    id: str # course_id_theory, course_id_simple, etc.
    title: str
    subtitle: Optional[str] = None
    type: str # theory, validation, practice_simple, practice_medium, practice_hard, flash, page
    order: int # Global order on the road
    
    ref_id: Optional[str] = None # ID of the exercise if type is exercise-direct
    page_file: Optional[str] = None # Filename of the markdown page if type is theory
    
    course_id: Optional[str] = None
    subject_id: str
    activated: bool = False

# --- Modèles de Base de Données (Persistance Utilisateur) ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    avatar: str = "default_avatar.png"
    total_xp: int = Field(default=0)
    
    progress: List["SubjectProgress"] = Relationship(back_populates="user")
    step_progress: List["RoadStepProgress"] = Relationship(back_populates="user")

    @property
    def is_admin(self) -> bool:
        return "_ADMIN" in self.username

class SubjectProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    subject_id: str = Field(index=True)
    score: int = Field(default=0)
    
    user: User = Relationship(back_populates="progress")

class RoadStepProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    step_id: str = Field(index=True)
    is_completed: bool = Field(default=False)
    mastery: int = Field(default=0) # 0 to 3
    answers: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    user: User = Relationship(back_populates="step_progress")

class ExerciseLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    tag: str = Field(index=True)
    question_id: str
    is_correct: bool
    timestamp: float 
    difficulty: str


# --- Schémas API ---

class SubmitRequest(SQLModel):
    user_id: int
    step_id: str
    answers: Dict[str, Any] # { "ex_01": "1" or ["a", "b"] }

class TestSubmitRequest(SQLModel):
    user_id: int
    step_id: str
    answers: Dict[str, Any]
    generated_exercises: List[dict]
