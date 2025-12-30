from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

# --- Modèles de Base de Données ---

class Subject(SQLModel, table=True):
    id: str = Field(primary_key=True) # ex: "maths"
    name: str
    courses: List["Course"] = Relationship(back_populates="subject")
    road_steps: List["RoadStep"] = Relationship(back_populates="subject")

class Course(SQLModel, table=True):
    id: str = Field(primary_key=True) # ex: "math_01"
    title: str
    content_markdown: str
    generator_type: str = Field(default="generic") # addition, soustraction, etc.
    
    # Stockage des exercices statiques (extraits du markdown)
    exercises: List[dict] = Field(default=[], sa_column=Column(JSON))
    session_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    subject_id: str = Field(foreign_key="subject.id")
    subject: Subject = Relationship(back_populates="courses")
    road_steps: List["RoadStep"] = Relationship(back_populates="course")

class RoadStep(SQLModel, table=True):
    id: str = Field(primary_key=True) # course_id_theory, course_id_simple, etc.
    title: str
    type: str # theory, validation, practice_simple, practice_medium, practice_hard
    order: int # Global order on the road
    
    course_id: str = Field(foreign_key="course.id")
    subject_id: str = Field(foreign_key="subject.id")
    
    course: Course = Relationship(back_populates="road_steps")
    subject: Subject = Relationship(back_populates="road_steps")

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
    subject_id: str = Field(foreign_key="subject.id")
    score: int = Field(default=0)
    
    user: User = Relationship(back_populates="progress")

class RoadStepProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    step_id: str = Field(foreign_key="roadstep.id")
    is_completed: bool = Field(default=False)
    mastery: int = Field(default=0) # 0 to 3
    answers: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    user: User = Relationship(back_populates="step_progress")

class ExerciseLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    # hierarchical tag: "math:calcul:addition"
    tag: str = Field(index=True)
    question_id: str
    is_correct: bool
    timestamp: float 
    
    # Optional: store full context if needed
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
