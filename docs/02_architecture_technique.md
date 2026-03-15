# Architecture Technique

## Vue d'ensemble

L'application suit une architecture **MVC allégée** :
- **Modèle** : `models.py` + `database.py` (SQLModel/SQLite)
- **Vue** : Templates Jinja2 + JS vanilla
- **Contrôleur** : Routes FastAPI dans `main.py`

Le contenu pédagogique est découplé du code : il réside dans des fichiers YAML/Markdown chargés au démarrage par le `ContentManager`.

---

## Backend — FastAPI

### Point d'entrée (`src/main.py`)

Le fichier `main.py` est le cœur de l'application. Il contient :

- **Lifespan** (`@asynccontextmanager`) : initialise la BDD et charge le contenu au démarrage
- **Dépendances** : `get_session()` (injection SQLModel), `get_current_user()` (cookie `user_id`)
- **Routes GET** : pages HTML rendues côté serveur via Jinja2
- **Routes POST** : endpoints JSON pour la soumission d'exercices

### Routes principales

| Route | Méthode | Description |
|---|---|---|
| `/` | GET | Page d'accueil / sélection utilisateur |
| `/login` | POST | Connexion par cookie |
| `/users/` | POST | Création d'un utilisateur |
| `/logout` | GET | Suppression du cookie |
| `/dashboard` | GET | Tableau de bord (matières + progression) |
| `/subjects/{id}` | GET | Page d'une matière (liste des étapes) |
| `/step/{id}` | GET | Page d'une étape (cours, exercices, dialogue) |
| `/flash/{subject_id}` | GET | Mode flash adaptatif |
| `/event/{event_id}` | GET | Événement global (dialogue d'intro) |
| `/submit_step` | POST | Soumission étape théorique |
| `/submit_test_step` | POST | Soumission étape exercices (avec correction) |
| `/log_exercise` | POST | Log individuel d'un exercice (mode flash) |
| `/sw.js` | GET | Service Worker PWA (doit précéder le mount StaticFiles) |
| `/manifest.json` | GET | Web App Manifest PWA |

### Routes Admin (préfixe `/admin/`)

| Route | Description |
|---|---|
| `/admin/reset_all` | Réinitialise toute la progression de l'utilisateur admin |
| `/admin/validate_all` | Valide toutes les étapes (mastery=3, XP=99999) |
| `/admin/validate_step/{id}` | Valide une étape spécifique |
| `/admin/invalidate_step/{id}` | Invalide une étape spécifique |

### Routes Debug (réservées à `_ADMIN`)

| Route | Description |
|---|---|
| `/debug/stats` | Vue globale de tous les utilisateurs |
| `/debug/exercises` | Liste tous les templates d'exercices |
| `/debug/dialogues` | Liste tous les fichiers de dialogue |
| `/debug/animations` | Test des animations |
| `/debug/view_dialogue` | Prévisualisation d'un dialogue |
| `/debug/test/{mode}/{template_id}` | Test d'un template d'exercice |
| `/debug/user/{user_id}` | Détail des stats d'un utilisateur |

---

## Authentification

Système **minimaliste sans mot de passe** :
- L'utilisateur choisit son nom dans une liste ou en crée un nouveau
- Un cookie `user_id` est posé (entier correspondant à l'id BDD)
- Aucun hash, aucune session serveur : adapté à un usage mono-réseau (classe)

L'admin est identifié par la présence de `_ADMIN` dans le `username`.

---

## Logique de comparaison des réponses (`smart_compare`)

Fonction centrale pour corriger les exercices :

1. **Listes** : comparaison ordonnée (cloze, drag-drop) ou non ordonnée (multiselect)
2. **Égalité stricte** (chaînes)
3. **Comparaison numérique/fractions** : parsing via `FractionGenerator.parse_fraction()`, tolérance de `0.0001`

---

## ContentManager (`src/content_manager.py`)

Singleton de classe (méthodes/attributs `@classmethod`) chargé une seule fois au démarrage.

### Données stockées en mémoire

```python
_subjects:    Dict[str, Subject]           # { "maths": Subject(...) }
_road_steps:  Dict[str, RoadStep]          # { "intro_mul": RoadStep(...) }
_templates:   Dict[str, ExerciseTemplate]  # { "ex_mul_01": ExerciseTemplate(...) }
_events:      Dict[str, Event]             # { "intro_mul_dialogue": Event(...) }
_characters:  Dict[str, Any]              # { "Crac": {...}, "Moggy": {...} }
```

### Pipeline de chargement

```
cours.yaml
  ├── events → _events
  └── pages (route_math.yaml, ...)
        ├── _load_templates() → scan YAML dans le dossier sujet
        └── _load_road()      → lit le fichier route, crée Subject + RoadSteps
```

### Expansion des séquences

Les étapes de type `sequence` avec `repeat: N` sont **expansées à la lecture** :
- `sequence_tables` avec `repeat: 10` → 10 étapes `sequence_tables_1` ... `sequence_tables_10`
- Les chaînes `{index}` dans `title` et `selection` sont remplacées par la valeur courante

---

## ExerciseEngine (`src/exercise_engine.py`)

Génère une instance d'exercice à partir d'un `ExerciseTemplate` :

1. **Variables** : tirées aléatoirement selon config (`list` → `random.choice`, `dict{min,max}` → `random.randint`)
2. **Interpolation du contenu** : syntaxe `{var}` (f-string like) et `[[ expr ]]` (eval Python sécurisé sans builtins)
3. **Calcul de la réponse** :
   - `template.logic` : expression Python évaluée avec les variables
   - `content.answer` : réponse statique, avec résolution d'indices pour les QCM
4. **Objet final** retourné au frontend avec : `id`, `type`, `question`, `options`, `answer`, `tags`, `meta`

> ⚠️ L'utilisation de `eval()` est limitée aux expressions mathématiques simples sans builtins. Les variables injectées viennent des templates YAML éditoriaux, pas de l'utilisateur.

---

## ReinforcementEngine (`src/reinforcement_engine.py`)

Sélection adaptative selon la **règle 60/20/20** :

| Part | Critère |
|---|---|
| 60% | Tags avec taux de réussite < 80% (points faibles) |
| 20% | Templates de difficulté 1 (motivation, exercices faciles) |
| 20% | Complétion aléatoire dans le scope |

Basé sur les `ExerciseLog` filtrés par `scope_tag` (ex: `"math.calcul.mul"`).

---

## FractionGenerator (`src/fraction_generator.py`)

Génère des **blueprints visuels** pour représenter les fractions :

- `PIZZA` → angles SVG (start/end en degrés)
- `GRID` → assignation de cellules dans une grille R×C
- `CYLINDER` → pourcentages de remplissage

Le rendu SVG final est délégué au frontend (`static/js/fraction_renderer.js`).

---

## Générateurs d'exercices (`src/generators/`)

Architecture extensible basée sur le pattern **Strategy** :

- `ExerciseGenerator` (ABC) : interface `generate(config, count)`
- `MathGenerator` : génère additions, soustractions, multiplications, divisions avec gestion des difficultés et des tables
- `ExerciseFactory` : registre de générateurs, distribution pondérée selon `weight`

> Note : Ce système de générateurs procéduraux (`generators/`) coexiste avec le système déclaratif de templates YAML (`ExerciseEngine`). Le système YAML est le plus utilisé actuellement.

---

## Frontend

### Templates Jinja2

| Template | Rôle |
|---|---|
| `base.html` | Layout commun : navbar, thème, popup, flash animation |
| `index.html` | Page d'accueil / login |
| `dashboard.html` | Tableau de bord matières |
| `subject.html` | Liste des étapes d'une matière |
| `unit.html` | Page de cours (contenu MD + exercices inline) |
| `test.html` | Session d'exercices (practice, exam, validation) |
| `flash.html` | Mode flash (exercices rapides) |
| `dialogue.html` | Scènes de dialogue (monologue ou SMS) |
| `debug/*.html` | Outils d'administration |

### CSS

- **`style.css`** : styles principaux (thème, layout, composants)
- **`responsive.css`** : breakpoints additifs desktop-first
  - `@media (max-width: 768px)` : navbar, dialogue chat, monologue empilé
  - `@media (max-width: 640px)` : grilles 1 colonne, touch targets 44px, fonts flash
  - `@media (max-width: 480px)` : padding réduit, drag-drop 44px, masquage liens admin

### JavaScript

- **`blueprint_renderer.js`** : rendu SVG des blueprints de fractions
- **`fraction_renderer.js`** : utilitaires fractions
- **`touch_dragdrop.js`** : drag-drop tactile (pattern tap-sélect-tap)
  - Détection via `window.matchMedia('(pointer: coarse)')` — jamais UA sniffing
  - Délégation d'événement sur le container (compatible avec DOM injecté dynamiquement)
  - Exposition : `window.TouchDragDrop.init(containerEl, onPlace)`
- **`sw.js`** : Service Worker PWA
  - Précache au `install` : assets `/static/*` + CDN (KaTeX, Marked, Confetti)
  - Cache-first pour les assets statiques
  - Network-first pour les pages HTML
  - Stale-while-revalidate pour CDN
  - Jamais mis en cache : routes POST (`/submit_*`, `/log_*`, `/login`)
  - Versioning via `CACHE_NAME = 'parcours-vN'` — incrémenter à chaque déploiement
- Logique inline dans les templates (soumission exercices, confettis, KaTeX auto-render)

### PWA

- **`static/manifest.json`** : nom "Parcours", thème vert `#55a630`, `display: standalone`, icône `logo.png`
- Le SW doit être servi depuis `/sw.js` (scope `/`) : la route FastAPI est déclarée **avant** `app.mount("/static", ...)` pour prendre priorité
- Enregistrement SW dans `base.html` via `navigator.serviceWorker.register('/sw.js')`

### Bibliothèques CDN

| Lib | Usage |
|---|---|
| KaTeX 0.16.9 | Rendu des formules LaTeX (`$...$`) |
| Marked.js | Parsing Markdown → HTML |
| Canvas Confetti | Animation de succès |
| Google Fonts (Fredoka, Inter) | Typographie |
