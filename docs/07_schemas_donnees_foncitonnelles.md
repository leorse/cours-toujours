Ce que vois l'élève.
* menu (sélection de l'utilisation  ou connexion)
  * matières (Math, histoires, sciences...)
    * chapitres (multiplications, fractions, etc...)
    * étapes (lexique sur les multiplication, exercices de multiplications, etc...)
        * cours (texte + exercices inline)
          * pages (sous-parties du cours)
        * exercices (exercices en mode pratique)
        * examen (exercices en mode examen)
        * quiz (exercices en mode quiz)

# Le menu

# Matières
Une matière est un ensemble de chapitres. Elle correspond à une matière scolaire (Math, Histoire, etc...). L'élève peut les faire dans l'ordre qu'il veut, indépendamment de son niveau et de son expérience.

Une matière contient:
 * un nom (mathématiques)
 * une image (icône)
 * un ensemble de chapitres

Dans le menu il est affiché avec son nom et son icône, ainsi que la moyenne de ses chapitres.


# Chapitres
Les chapitres sont les sous-parties d'une matière. Ils sont organisés en étapes. Les chapitres doivent être débloquée pour pouvoir être traités, le premier étant toujours débloqué. Les chapitres ont des dépendances entre eux (avoir fais les multiplications avant de faire les fractions par exemple).

Une chapitre contient:
 * un nom (les multiplications)
 * un ensemble d'étapes
 * une dépendance vers un autre chapitre (Le chapitre fraction ne peux être débloqué que si le chapitre multiplication est terminé)

Dans le menu des chapitres il est affiché avec son nom et son état (en cours, terminé, bloqué), la note moyenne de l'utilisation.

# Etapes
Une étape est une partie d'un chapitre. Elle contient:
 * un nom (les tables de 1 à 10)
 * un ensemble de pages
 * une dépendance vers une autre étape (les tables de 1 à 10 ne peuvent être débloqué que si les tables de 1 à 5 sont terminées)
 * une icone (une icone pour les cours, une pour les exercices, etc...)
 * une ou plusieurs note, il est en effet possible de refaire autant de fois qu'on le veut une étape d'exercices, la meilleure note est alors comptabilisée.
 * un badge ou trophée si l'utilisateur  à obtenu une certaine note sur cette étape (or, argent, platine, bronze...)

# Pages
Une page est une sous partie d'une étape. Elle contient:
 * un contenu (texte, images, vidéos, etc...)
 * un ensemble d'exercices inline 
 * un ensemble d'exercices

Le contenu peut être
* une page de cours, avec des images, des vidéos, des textes, etc... Dans cette page de cours il peut y avoir des widgets (image qu'on peut agrandir, vidéo, frise, exercice)
* une page d'exercice (la page entière est un widget de type exercice)
* un dialogue (la page entière est un widget de type dialogue)

On a la possibilté de retourner à la page suivante ou précédente. On ne peut aller à la page suivante que si on y est déjà allé.

La page est validée si l'utilisateur est à arrivée à la fin en ayant fait tous les exercices et qu'ils soient corrects.

# Widgets

Un widget est un élément interactif dans une page. Il peut être:
- **Exercice** : un exercice inline ou une page entière d'exercice (7 types)
- **Dialogue** : un dialogue entre deux personnages (2 types)
- une frise chronologique _(à implémenter)_
- une image agrandissable _(à implémenter)_
- une vidéo _(à implémenter)_
- un quiz _(à implémenter)_

Les widgets ont une même base : on les insère dans une page via leur `id` (`&&widget_id&&` dans le markdown d'un cours), et on les configure dans un fichier YAML. Chaque widget peut rapporter de l'XP ou non, avoir une note ou non.

> **Note technique :** dans le code actuel, les widgets s'appellent encore "exercices" ou "dialogues". Le terme "widget" est le nom fonctionnel cible. Un renommage est prévu.

---

## Structure commune à tous les widgets

```yaml
# Champs communs à tout widget
id: mon_widget_01          # Identifiant unique, référencé dans le markdown par &&mon_widget_01&&
type: exercice             # Type de widget : exercice | dialogue | frise | image | video | quiz
tags: ["math.calcul.mul"]  # Tags hiérarchiques pour le ciblage et les statistiques
difficulty: 1              # Niveau de difficulté : 1 (facile) | 2 (moyen) | 3 (difficile)
xp: true                   # Rapporte de l'XP ou non (défaut : true)
scored: true               # Compte dans la note de l'étape (défaut : true)
explanation: ""            # Explication affichée après la réponse (optionnel)
```

L'objet généré (transmis au frontend) a toujours cette forme de base :

```json
{
  "id": "mon_widget_01_5423",
  "template_id": "mon_widget_01",
  "type": "input",
  "question": "...",
  "options": [],
  "answer": "...",
  "explanation": "...",
  "tags": ["math.calcul.mul"],
  "meta": { "difficulty": 1 }
}
```

---

## Widgets Exercice (existants)

Les exercices peuvent être définis de deux façons :
- **Statique** : question/réponse fixe
- **Générateur** : variables aléatoires interpolées au moment de la génération

Les générateurs utilisent :
- `{var}` pour interpoler une variable dans le texte
- `[[expression]]` pour évaluer une expression Python (ex: `[[{a} * {b}]]`)
- `logic: "{a} * {b}"` pour calculer la réponse automatiquement

---

### 1. Input — Réponse libre

L'élève tape sa réponse dans un champ texte. Accepte les nombres entiers, décimaux, et les fractions (`1/4`).

```yaml
# Définition statique
- id: calc_mul_01
  interaction: input
  tags: ["math.calcul.mul"]
  difficulty: 1
  content:
    question: "Combien font 7 × 8 ?"
    answer: "56"
    unit: ""             # Unité affichée après l'input (ex: "cm", "kg") — optionnel
    explanation: "7 × 8 = 56"

# Définition avec générateur
- id: gen_mul_basic
  interaction: input
  tags: ["math.calcul.mul"]
  difficulty: 1
  vars:
    a: { min: 1, max: 10 }
    b: { min: 1, max: 10 }
  content:
    question: "Combien font {a} × {b} ?"
    explanation: "On multiplie {a} par {b}."
  logic: "{a} * {b}"    # Expression Python évaluée pour calculer la réponse
```

**Validation :** comparaison directe de chaîne, puis comparaison numérique avec tolérance ±0.0001 (accepte `"56"`, `56`, `56.0`). Les fractions sont parsées (`"1/4"` → `0.25`).

---

### 2. QCM — Choix unique

L'élève choisit une seule réponse parmi plusieurs boutons.

```yaml
- id: gen_mul_cours_02
  interaction: qcm
  tags: ["math.calcul.mul"]
  difficulty: 1
  vars:
    a: { min: 2, max: 9 }
    b: { min: 2, max: 9 }
  content:
    question: "Combien font {a} × {b} ?"
    options:
      - "[[{a} + 10]]"     # Option calculée
      - "[[{a} * {b}]]"    # Bonne réponse (index 1)
      - "[[{b} + 10]]"
      - "[[{a} + {b}]]"
    answer: [1]            # Index(es) de la/des bonne(s) réponse(s)
    explanation: "La réponse est {a} × {b} = [[{a} * {b}]]"
```

**Validation :** l'index est converti en texte lors de la génération. Comparaison de chaîne exacte.

---

### 3. Multiselect — Choix multiple

L'élève choisit plusieurs réponses. Un sous-titre "(Plusieurs réponses possibles)" est affiché automatiquement.

```yaml
- id: gen_mul_cours_01
  interaction: qcm
  multiple: true           # Active le mode multiselect
  tags: ["math.calcul.mul.proprietes"]
  difficulty: 1
  vars:
    a: { min: 2, max: 9 }
    b: { min: 2, max: 9 }
  content:
    question: "{a} × {b} est-il égal à {b} × {a} ?"
    options:
      - "Oui, car la multiplication est commutative."
      - "Non, l'ordre change le résultat."
      - "Oui, le résultat est identique dans les deux cas."
      - "Cela ne fonctionne que pour les additions."
    answer: [0, 2]         # Les deux bonnes réponses
```

**Validation :** les deux listes sont triées avant comparaison (l'ordre de sélection n'importe pas).

---

### 4. Drag & Drop — Glisser-déposer

L'élève glisse des étiquettes dans des zones vides d'un texte à trous. Les zones sont matérialisées par `???` dans le template.

```yaml
- id: div_cloze_01
  interaction: drag_drop
  tags: ["math.arithmetique"]
  difficulty: 2
  content:
    question: "Complète l'égalité avec les bons termes :"
    template: "??? = ??? × ??? + ???"   # ??? marque chaque zone de dépôt
    options: ["reste", "dividende", "diviseur", "quotient"]
    answer: ["dividende", "diviseur", "quotient", "reste"]  # Ordre des zones
    explanation: "dividende = diviseur × quotient + reste"
```

**Validation :** comparaison de tableau ordonnée (la position dans chaque zone doit correspondre).

> **Limitation mobile :** le drag & drop HTML5 natif ne fonctionne pas sur les écrans tactiles. Un remplacement par tap-to-place est prévu.

---

### 5. Cloze — Sélection dans menu déroulant

L'élève sélectionne une valeur dans un `<select>` intégré dans le texte. Les zones sont matérialisées par `???`.

```yaml
- id: geo_cloze_01
  interaction: cloze
  tags: ["math.geometrie"]
  difficulty: 1
  content:
    question: "Complète la phrase :"
    template: "Un triangle a ??? côtés et ??? angles."
    options: ["2", "3", "4", "5"]     # Même liste proposée pour chaque zone
    answer: ["3", "3"]                 # Réponse attendue pour chaque zone, dans l'ordre
    explanation: "Un triangle a 3 côtés et 3 angles."
```

**Validation :** comparaison de tableau ordonnée (même logique que drag_drop).

---

### 6. Fraction Scénario — Visualisation graphique

Affiche une représentation visuelle d'une fraction (pizza, grille ou cylindre) et pose une question dessus. La réponse est un input libre.

```yaml
- id: frac_pizza_01
  interaction: fraction_scenario
  tags: ["math.fractions"]
  difficulty: 2
  content:
    question: "Quelle fraction est coloriée ?"
    answer: "3/8"
    visual: PIZZA           # PIZZA | GRID | CYLINDER
    parts: 8                # Nombre total de parts
    participants:
      - name: "Résultat"
        fraction: "3/8"
        color: "#e74c3c"    # Couleur de la zone (optionnel)
    explanation: "3 parts sur 8 sont coloriées, soit 3/8."
```

Les trois visuels disponibles :

| Visuel | Description | Usage typique |
|--------|-------------|---------------|
| `PIZZA` | Camembert SVG découpé en secteurs | Fractions simples, partages |
| `GRID` | Grille rectangulaire colorée | Multiplications de fractions, aires |
| `CYLINDER` | Barre verticale de niveau | Volumes, pourcentages |

**Validation :** la réponse est parsée comme fraction ou décimal. Tolérance ±0.0001 (`"3/8"`, `"0.375"` et `0.375` sont équivalents).

---

## Widgets Dialogue (existants)

Les dialogues sont des pages entières. Ils sont définis dans des fichiers YAML séparés et référencés dans la route.

### Structure commune aux dialogues

```yaml
dialogue:
  - id: nom_du_dialogue
  - type: monologue        # monologue | dialogue
  - message:
    - ...                  # Liste des messages (structure différente selon le type)
```

---

### 7. Monologue — Personnage unique

Un personnage s'exprime seul, bulle de texte à droite, image à gauche. L'élève clique "Suivant" pour avancer.

```yaml
dialogue:
  - id: intro_gribouille
  - type: monologue
  - message:
    - page: "Bienvenue dans ton parcours de **Mathématiques** !"
      image: "gribouille_coucou.png"       # Fichier dans /static/images/
    - page: "On va revoir les multiplications ensemble."
      image: "gribouille_doigt_leve.png"
    - page: "Pas de panique, on y va étape par étape !"
      image: "gribouille_joie.png"
```

Chaque message peut avoir une image différente pour varier l'expression du personnage.

---

### 8. Dialogue SMS — Deux personnages

Deux personnages échangent dans une interface style messagerie. Les messages apparaissent un par un. Chaque personnage a un spritesheet d'émotions.

```yaml
dialogue:
  - id: dial_crac_moggy
  - type: dialogue
  - personnages:
    - name: "Crac"         # Personnage gauche
    - name: "Moggy"        # Personnage droite (miroir horizontal)
  - message:
    - Crac: "Coucou Moggy, ça va ?"
      emotion: "parle"
    - Moggy: "Impec ! Et toi ?"
      emotion: "parle"
    - Crac: "On va revoir les **multiplications** !"
      emotion: "content"
    - Moggy: "J'ai du mal avec les tables..."
      emotion: "interrogation"
    - Crac: "Pas de souci, on y va ensemble !"
      emotion: "content"
```

La configuration des personnages (spritesheet, dimensions, émotions) est définie séparément dans le système de configuration des personnages :

```yaml
# Configuration d'un personnage (chargée par le backend)
personnage:
  name: "Crac"
  spritesheet: "crac_sprites.png"   # Image contenant toutes les poses
  width: 200                         # Largeur d'une frame en pixels
  height: 300                        # Hauteur d'une frame en pixels
  emotions:
    - name: "parle"
      coords: [0, 0]                 # [colonne, ligne] dans la grille du spritesheet
    - name: "content"
      coords: [1, 0]
    - name: "interrogation"
      coords: [2, 0]
    - name: "sur"
      coords: [3, 0]
```

---

## Widgets à implémenter

---

### 9. Frise chronologique _(à implémenter)_

Affiche une ligne du temps avec des événements à placer ou à lire.

```yaml
- id: frise_ww2_01
  type: frise
  tags: ["histoire.ww2"]
  content:
    titre: "Les grandes dates de la Seconde Guerre Mondiale"
    orientation: horizontal       # horizontal | vertical
    interactive: false            # true = l'élève place les événements, false = lecture seule
    events:
      - date: "1939"
        label: "Début de la guerre"
        description: "L'Allemagne envahit la Pologne le 1er septembre."
        color: "#e74c3c"          # Optionnel
        image: "invasion_pologne.png"  # Optionnel
      - date: "1944"
        label: "Débarquement en Normandie"
        description: "Les Alliés débarquent le 6 juin."
      - date: "1945"
        label: "Fin de la guerre"
        description: "Capitulation de l'Allemagne le 8 mai."
```

---

### 10. Image agrandissable _(à implémenter)_

Affiche une image cliquable qui s'ouvre en plein écran avec légendes optionnelles.

```yaml
- id: img_table_pythagore
  type: image
  content:
    src: "table_pythagore.png"        # Fichier dans /static/images/
    alt: "Table de Pythagore"
    caption: "La table de Pythagore de 1 à 10"   # Légende sous l'image
    zoomable: true                    # Permet l'agrandissement au clic (défaut : true)
    annotations:                      # Points cliquables sur l'image (optionnel)
      - x: 45                         # Position en % de la largeur
        y: 20                         # Position en % de la hauteur
        label: "3 × 4 = 12"
```

---

### 11. Vidéo _(à implémenter)_

Intègre une vidéo locale ou externe dans la page de cours.

```yaml
- id: video_intro_mul
  type: video
  content:
    src: "intro_multiplication.mp4"   # Fichier local dans /static/videos/
    # OU
    youtube_id: "dQw4w9WgXcQ"         # ID YouTube (embed)
    titre: "Introduction à la multiplication"
    autoplay: false                   # Défaut : false
    sous_titres: "intro_mul_fr.vtt"   # Fichier de sous-titres (optionnel)
    obligatoire: true                 # Si true, l'élève doit regarder jusqu'à la fin avant de continuer
```