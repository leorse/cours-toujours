# Système de Contenu

Le contenu pédagogique est entièrement **déclaratif**, défini dans des fichiers YAML et Markdown, sans nécessiter de modification du code Python.

---

## Point d'entrée : `content/cours.yaml`

Manifeste principal qui liste :

1. Les **événements globaux** (dialogues d'introduction)
2. Les **fichiers de route** de chaque matière

```yaml
cours:
  - events:
      - conditions: first_view
        type: dialogue
        id: intro_mul_dialogue
        content: "calculs/dialogue_intro.yaml"
  - page: maths/route_math.yaml
  - page: fourre_tout/route_test.yaml
```

---

## Fichier de route : `route_*.yaml`

Définit le **parcours d'une matière** : son titre et la liste ordonnée des étapes.

```yaml
title: "Maîtrise des Mathématiques"
road:
  - id: intro_mul
    title: "Le Concept de Multiplication"
    pages:
      - type: dialogue
        content: "calculs/dialogue_intro.yaml"
      - type: cours
        content: "calculs/multiplications.md"

  - id: sequence_tables
    type: sequence
    repeat: 10
    title: "Entraînement : Table de {index}"
    step_config:
      type: practice
      selection:
        target: ["math.calcul.mul.table_{index}"]
        count: 2
        difficulty: 1
```

### Types d'étapes

| Type | Pages | Description |
|---|---|---|
| (défaut) | via `pages:` | Étape multi-pages |
| `sequence` | via `step_config.pages` | Génère N étapes automatiquement (`repeat`) |
| `cours` | — | Page de contenu Markdown |
| `practice` | — | Session d'exercices |
| `exam` | — | Identique à practice |
| `validation` / `flash` | — | Exercices avec mastery |
| `reinforcement` | — | Exercices adaptatifs |
| `dialogue` | — | Scène dialoguée |

### Sélection d'exercices (`selection`)

La selection peut être un dictionnaire unique ou une liste :

```yaml
# Cas simple
selection:
  target: ["math.calcul.mul"]
  count: 10
  difficulty: 2

# Cas mixte (exam multi-sources)
selection:
  - { target: ["math.calcul.mul"], count: 10, difficulty: 2 }
  - { target: ["format.word_problem"], count: 5, difficulty: 3 }
```

`target` est une liste de tags : un template est sélectionné si **tous** les tags sont présents.

---

## Templates d'exercices (YAML)

Fichiers YAML dans les sous-dossiers de matière (ex: `maths/calculs/exos.yaml`).

### Format `templates` (déclaratif)

```yaml
templates:
  - id: ex_mul_word_01
    tags: ["math.calcul.mul", "format.word_problem"]
    difficulty: 2
    vars:
      a: { min: 2, max: 12 }
      b: { min: 2, max: 12 }
      fruit: ["pommes", "oranges", "poires"]
    content:
      question: "Un marchand a {a} caisses de {fruit}. Chaque caisse contient {b} {fruit}. Combien en a-t-il au total ?"
      explanation: "{a} × {b} = [[ {a} * {b} ]]"
    logic: "{a} * {b}"
    interaction: input
```

#### Variables

| Type de config | Comportement |
|---|---|
| `list` | `random.choice(list)` |
| `{min, max}` | `random.randint(min, max)` |
| valeur fixe | constante |

#### Interpolation du contenu

- `{var}` → valeur de la variable (format Python)
- `[[ expr ]]` → évaluation Python (ex: `[[ {a} * {b} ]]`)

#### Réponse

- Via `logic:` → expression évaluée avec les variables
- Via `content.answer:` → valeur fixe ou indice dans `options`

#### Interaction / Rendu

| `interaction` | Affichage |
|---|---|
| `input` | Champ texte |
| `qcm` | Boutons radio |
| `multiselect` | Checkboxes |
| `cloze` | Texte à trous |
| `drag_drop` | Glisser-déposer |

`render_type` peut forcer un rendu visuel spécial (ex: `fraction_visual`).

### Format `generators` (procédural)

Utilisé pour des exercices générés algorithmiquement (pas de template déclaratif) :

```yaml
generators:
  - id: gen_mul_table_3
    tags: ["math.calcul.mul.table_3"]
    type: math_engine
    difficulty: 1
    logic: multiplication
    ...
```

---

## Fichiers Markdown (contenu cours)

Les cours sont écrits en **Markdown** avec support KaTeX pour les formules :

```markdown
# Les Multiplications

La multiplication est une **addition répétée**.

$3 \times 4 = 3 + 3 + 3 + 3 = 12$

## Exercice intégré

&&ex_mul_inline_01&&
```

La syntaxe `&&template_id&&` permet d'**insérer un exercice inline** dans un cours. Le `ContentManager` remplace le placeholder par l'exercice généré.

---

## Fichiers de dialogue (YAML)

```yaml
dialogue:
  - id: intro_gribouille
  - type: "monologue"
  - message:
    - page: "Bienvenue dans ton parcours de **Mathématiques**."
      image: "gribouille_coucou.png"
    - page: "On a un beau programme devant nous."
      image: "gribouille_doigt_leve.png"
```

Pour un dialogue entre personnages (`type: dialogue`) :

```yaml
dialogue:
  - type: "dialogue"
  - message:
    - Crac: "Salut Moggy ! Tu connais les fractions ?"
      emotion: "interrogation"
    - Moggy: "Bien sûr ! La moitié c'est 1/2."
      emotion: "sur"
    - Crac: "Exactement !"
      emotion: "content"
```

### Condition `first_view`

```yaml
dialogue:
  - conditions:
    - first_view
  - message: [...]
```

Permet de ne montrer le dialogue qu'une seule fois par utilisateur.

---

## Personnages (`config/personnages.yaml`)

```yaml
personnages:
  - name: "Crac"
    spritesheet: "tete_lapin.png"
    width: 379
    height: 379
    emotions:
      - name: "content"
        coords: [0, 0]      # colonne, ligne dans la spritesheet
      - name: "interrogation"
        coords: [0, 1]
      ...
```

La spritesheet est une grille 2×3 de 379×379 px par sprite. Le positionnement CSS `background-position` est calculé via les coordonnées.

---

## Arborescence du contenu actuel

```
content/
├── cours.yaml                          # Manifeste
├── maths/
│   ├── route_math.yaml                 # Parcours mathématiques
│   ├── calculs/
│   │   ├── multiplications.md          # Cours
│   │   ├── additions.md
│   │   ├── soustractions.md
│   │   ├── divisions.md
│   │   ├── exos.yaml                   # Templates exercices calculs
│   │   ├── dialogue_intro.yaml         # Dialogue d'introduction
│   │   └── dialogue_crac_moggy.yaml    # Dialogue Crac & Moggy
│   ├── fractions/
│   │   ├── fractions.md
│   │   ├── fractions_addition.md
│   │   ├── fractions_multiplication.md
│   │   ├── fractions_division.md
│   │   ├── fractions_demo.md
│   │   └── meta.yaml
│   └── nombres_relatifs/
│       ├── arthimetique_relatif.md
│       ├── nombres_relatif_multiplications.md
│       ├── critere_divisibilite.md
│       ├── les_facteurs.md
│       ├── poser_une_division.md
│       ├── exos.yaml
│       ├── exos_relatif.yaml
│       └── meta.yaml
└── fourre_tout/
    └── route_test.yaml                 # Route de test/bac à sable
```
