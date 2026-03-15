# Vue d'ensemble — Cours Toujours!

## Présentation

**Cours Toujours!** est une application web d'apprentissage interactif et gamifié, conçue pour accompagner des élèves (niveau collège/lycée professionnel) dans l'acquisition de compétences en mathématiques.

L'application propose un parcours structuré, des exercices générés dynamiquement, des dialogues scénarisés entre personnages, et un système de progression par XP (points d'expérience).

---

## Objectif pédagogique

L'application cible des élèves qui ont besoin de revoir les fondamentaux mathématiques dans un cadre engageant. Le contenu actuel couvre :

- Les **calculs de base** : multiplications, additions, soustractions, divisions
- Les **fractions** : opérations, comparaisons, représentations visuelles
- Les **nombres relatifs** : arithmétique, facteurs, critères de divisibilité

---

## Fonctionnalités principales

| Fonctionnalité | Description |
|---|---|
| Parcours progressif | Étapes ordonnées par matière, débloquées au fur et à mesure |
| Dialogues scénarisés | Personnages animés qui introduisent les notions |
| Exercices générés | Questions dynamiques avec variables aléatoires |
| Mode Flash | Session courte d'entraînement ciblant les points faibles |
| Renforcement adaptatif | Exercices sélectionnés selon l'historique de l'élève |
| Gamification | XP, niveaux, confettis, animations de réussite |
| Thème clair/sombre | Bascule persistée en localStorage |
| Interface admin | Debug, validation, reset, visualisation des stats |

---

## Stack technologique

| Couche | Technologie |
|---|---|
| Backend | Python 3 / FastAPI |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Base de données | SQLite (`content.db`) |
| Templates | Jinja2 |
| Frontend | HTML5 / CSS3 (vanilla) |
| Math rendering | KaTeX (CDN) |
| Markdown | Marked.js (CDN) |
| Animations | Canvas Confetti (CDN) |
| Serveur | Uvicorn (ASGI) |
| Contenu | Fichiers YAML + Markdown |

---

## Lancement

```bash
python -m uvicorn src.main:app --reload
```

Accessible sur `http://127.0.0.1:8000`.

---

## Structure des dossiers

```
cours/
├── src/                    # Code Python (backend)
│   ├── main.py             # Application FastAPI, routes
│   ├── models.py           # Modèles SQLModel (BDD + API)
│   ├── database.py         # Connexion SQLite
│   ├── content_manager.py  # Chargement du contenu YAML
│   ├── exercise_engine.py  # Génération d'exercices depuis templates
│   ├── reinforcement_engine.py  # Sélection adaptative d'exercices
│   ├── fraction_generator.py    # Blueprints visuels fractions
│   ├── test_generator.py        # (legacy)
│   └── generators/         # Générateurs d'exercices par type
│       ├── base.py
│       ├── factory.py
│       ├── math_generator.py
│       └── ...
├── templates/              # Gabarits Jinja2 HTML
├── static/                 # CSS, JS, images
├── content/                # Contenu pédagogique (YAML + MD)
│   ├── cours.yaml          # Manifeste principal
│   └── maths/              # Matière mathématiques
│       ├── route_math.yaml # Définition du parcours
│       ├── calculs/        # Chapitre calculs
│       ├── fractions/      # Chapitre fractions
│       └── nombres_relatifs/
├── config/
│   └── personnages.yaml    # Personnages des dialogues
└── docs/                   # Documentation (ce dossier)
```
