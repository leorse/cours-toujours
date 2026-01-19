from sqlmodel import Session, select, func
from typing import List, Dict, Any
from src.models import ExerciseLog, ExerciseTemplate
from src.content_manager import ContentManager
from src.exercise_engine import ExerciseEngine
import random

class ReinforcementEngine:
    @staticmethod
    def generate_reinforcement_exercises(session: Session, user_id: int, scope_tag: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Génère une série d'exercices de renforcement basée sur le profil utilisateur.
        Règle des 60/20/20 :
        - 60% sur les points faibles (taux de réussite faible)
        - 20% d'exercices faciles (difficulté 1)
        - 20% de théorie (ici, des exercices simples ou rappels si on avait le format)
        """
        
        # 1. Analyse du profil : récupérer les logs pour les tags commençant par scope_tag
        logs = session.exec(select(ExerciseLog).where(
            ExerciseLog.user_id == user_id,
            ExerciseLog.tag.like(f"{scope_tag}%")
        )).all()
        
        tag_stats = {} # {tag: {correct: X, total: Y}}
        for log in logs:
            if log.tag not in tag_stats:
                tag_stats[log.tag] = {"correct": 0, "total": 0}
            tag_stats[log.tag]["total"] += 1
            if log.is_correct:
                tag_stats[log.tag]["correct"] += 1
        
        # Calculer le taux de réussite par tag et trier par le plus faible
        fail_rates = []
        for tag, stats in tag_stats.items():
            rate = stats["correct"] / stats["total"]
            fail_rates.append((tag, rate))
        
        fail_rates.sort(key=lambda x: x[1]) # Trier par taux croissant (les pires d'abord)
        
        weak_tags = [t[0] for t in fail_rates if t[1] < 0.8] # Tags avec moins de 80% de réussite
        
        exercises = []
        
        # - 60% Points Faibles
        nb_weak = int(count * 0.6)
        if weak_tags:
            for _ in range(nb_weak):
                tag = random.choice(weak_tags)
                templates = ContentManager.select_templates([tag])
                if templates:
                    exercises.append(ExerciseEngine.generate_exercise(random.choice(templates)))
        
        # - 20% Faciles (Motivation)
        nb_easy = int(count * 0.2)
        easy_templates = ContentManager.select_templates([scope_tag], difficulty=1)
        if easy_templates:
            for _ in range(nb_easy):
                exercises.append(ExerciseEngine.generate_exercise(random.choice(easy_templates)))
                
        # - 20% Remplissage / Rappels (on complète jusqu'à 'count')
        remaining = count - len(exercises)
        all_templates = ContentManager.select_templates([scope_tag])
        if all_templates:
            for _ in range(remaining):
                exercises.append(ExerciseEngine.generate_exercise(random.choice(all_templates)))
                
        random.shuffle(exercises)
        return exercises
