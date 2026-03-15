# Base de Données

## Moteur

**SQLite** via **SQLModel** (wrapper Pydantic + SQLAlchemy).

Fichier : `content.db` (à la racine du projet, ignoré par git).

Création automatique au démarrage via `SQLModel.metadata.create_all(engine)`.

---

## Schéma

### `user`

Représente un élève ou un administrateur.

| Colonne | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Identifiant auto-incrémenté |
| `username` | TEXT | Nom affiché. Contient `_ADMIN` pour les admins |
| `avatar` | TEXT | Nom du fichier avatar (non utilisé activement) |
| `total_xp` | INTEGER | Total de XP accumulés |

**Propriété calculée** : `is_admin` → `True` si `"_ADMIN"` dans `username`

---

### `subjectprogress`

Score cumulatif d'un utilisateur pour une matière.

| Colonne | Type | Description |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK → user | |
| `subject_id` | TEXT | Ex: `"maths"` |
| `score` | INTEGER | Somme des XP gagnés dans cette matière |

---

### `roadstepprogress`

Progression d'un utilisateur sur une étape du parcours.

| Colonne | Type | Description |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK → user | |
| `step_id` | TEXT | Ex: `"intro_mul"`, `"sequence_tables_3"` |
| `is_completed` | BOOLEAN | Étape validée |
| `mastery` | INTEGER | Niveau de maîtrise (0 à 3) |
| `answers` | JSON | Dernières réponses soumises |

---

### `userevent`

Trace des événements globaux vus par l'utilisateur (pour la condition `first_view`).

| Colonne | Type | Description |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK → user | |
| `event_id` | TEXT | Ex: `"intro_mul_dialogue"` |
| `timestamp` | FLOAT | Timestamp UNIX de la première vue |

---

### `exerciselog`

Historique de chaque exercice soumis. Utilisé par le mode flash et le renforcement.

| Colonne | Type | Description |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK → user | |
| `tag` | TEXT (indexé) | Tags comma-separated ex: `"math.calcul.mul,format.word_problem"` |
| `question_id` | TEXT | ID généré de l'exercice |
| `is_correct` | BOOLEAN | Résultat |
| `timestamp` | FLOAT | Timestamp UNIX |
| `difficulty` | TEXT | Niveau de difficulté (stringifié) |

---

## Modèles non-persistés (mémoire uniquement)

Ces modèles sont chargés depuis les fichiers YAML par le `ContentManager` et stockés en RAM :

| Modèle | Source | Description |
|---|---|---|
| `Subject` | `route_*.yaml` | Matière (id, nom) |
| `Course` | (legacy) | Cours (peu utilisé) |
| `RoadStep` | `route_*.yaml` | Étape du parcours |
| `ExerciseTemplate` | Fichiers `*exos*.yaml` | Template de génération d'exercice |
| `Event` | `cours.yaml` | Événement global (dialogue d'intro) |

---

## Relations

```
User
 ├── SubjectProgress (1→N)
 ├── RoadStepProgress (1→N)
 ├── UserEvent (1→N)
 └── ExerciseLog (1→N)
```

---

## Scripts de migration

| Script | Rôle |
|---|---|
| `scripts/add_mastery_column.py` | Ajoute la colonne `mastery` à `roadstepprogress` |
| `scripts/migrate_db.py` | Migration générique |

Ces scripts sont utiles lors de l'évolution du schéma sans recréer la base depuis zéro.
