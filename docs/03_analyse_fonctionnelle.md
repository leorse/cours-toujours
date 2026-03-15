# Analyse Fonctionnelle

## Parcours utilisateur

### 1. Connexion

L'utilisateur arrive sur `/` et voit la liste des profils existants. Il peut :
- **Sélectionner** un profil existant → connexion directe (cookie `user_id`)
- **Créer** un nouveau profil (saisie d'un nom)

Aucun mot de passe. Si déjà connecté, redirection directe vers le dashboard.

---

### 2. Dashboard

Page `/dashboard` : présente toutes les **matières disponibles** avec leur score de progression.

Avant l'affichage, le système vérifie s'il existe un **événement global** non vu (ex: dialogue d'introduction). Si oui, redirection automatique vers l'événement.

---

### 3. Page matière

Page `/subjects/{id}` : affiche la **liste ordonnée des étapes** du parcours.

Chaque étape est visuellement marquée :
- Complétée ✓ ou non
- Niveau de maîtrise (mastery 0 à 3)

Les étapes sont définies dans les fichiers `route_math.yaml` de chaque matière.

---

### 4. Étapes du parcours

Une **étape** (`RoadStep`) peut comporter plusieurs **pages** séquentielles. Les types de pages sont :

| Type | Description |
|---|---|
| `cours` | Contenu Markdown + exercices inline intégrés |
| `dialogue` | Scène de dialogue entre personnages |
| `practice` | Session d'exercices avec sélection par tags/difficulté |
| `exam` | Identique à practice (traitement côté serveur différent) |
| `validation` | Exercices avec système de maîtrise (mastery) |
| `flash` | Session courte d'exercices rapides |
| `reinforcement` | Exercices adaptés aux points faibles de l'élève |

#### Navigation multi-pages

Le paramètre `page_idx` (query string) permet de naviguer entre les pages d'une étape. La progression d'une page à l'autre est gérée par les boutons "Suivant" / "Continuer" côté frontend, ou par redirection après soumission.

---

### 5. Types d'exercices

| Type (`interaction`) | Rendu | Exemple |
|---|---|---|
| `input` | Champ de saisie libre | "Combien font $3 \times 6$ ?" |
| `qcm` | Boutons de choix unique | Réponse parmi 4 options |
| `multiselect` | Cases à cocher | Plusieurs bonnes réponses |
| `cloze` | Texte à trous | Compléter une phrase |
| `drag_drop` | Glisser-déposer | Réordonner des éléments |

Le `render_type` peut forcer un rendu visuel particulier (ex: `fraction_visual` pour afficher un blueprint SVG).

---

### 6. Soumission et correction

Deux endpoints distincts selon le type d'étape :

#### `/submit_step` — Étapes théoriques
- Marque l'étape comme complétée
- Attribue 20 XP (première complétion uniquement)

#### `/submit_test_step` — Étapes avec exercices

1. **Correction** : chaque exercice est comparé via `smart_compare()`
2. **XP** : +10 XP par exercice correct (seulement à la première réussite)
3. **Progression** :
   - Si `>= 50%` de réponses correctes → étape marquée complétée
   - Pour les étapes `flash` / `validation` : système de **mastery** (0→3)

#### Système de Mastery (0 à 3)

| Résultat | Effet |
|---|---|
| 100% correct | mastery + 1 (max 3) |
| < 100% | mastery - 1 (min 0) |

L'étape devient "complétée" dès que `passed` (≥50%) et qu'elle n'était pas encore validée.

---

### 7. Mode Flash adaptatif

Route `/flash/{subject_id}` :

1. Récupère l'historique des exercices de l'utilisateur (`ExerciseLog`)
2. Calcule le taux de réussite par tag
3. Sélectionne les templates :
   - **70%** des exercices ciblent les 3 tags les plus faibles
   - **30%** sont tirés aléatoirement parmi les tags connus
4. Présente une session de 10 exercices

Si aucun historique → sélection purement aléatoire.

---

### 8. Système de Renforcement

L'étape `reinforcement` génère des exercices via `ReinforcementEngine` :

- **60%** sur les points faibles (taux < 80%)
- **20%** exercices faciles (difficulté 1)
- **20%** complétion aléatoire dans le scope

---

### 9. Dialogues et personnages

#### Personnages

Deux personnages définis dans `config/personnages.yaml` :
- **Crac** (lapin) — spritesheet `tete_lapin.png`
- **Moggy** (chat) — spritesheet `tete_chat.png`

Chaque personnage a 6 émotions : `content`, `serieux`, `interrogation`, `moue`, `sur`, `parle`

Les sprites sont organisés en spritesheet 2×3 (colonnes × lignes), positionnés par CSS `background-position`.

#### Types de dialogue

**Monologue** (`type: monologue`) :
- Un personnage avec bulle de dialogue
- Navigation slide par slide avec "Suivant"
- Image statique (illustrations `gribouille_*.png`)

**Dialogue SMS** (`type: dialogue`) :
- Interface style messagerie instantanée
- Deux personnages visibles en sidebar (avatars spritesheet)
- Messages apparaissent un par un côté gauche/droite
- Animation `popIn` sur chaque bulle

#### Conditions

Un dialogue peut avoir une condition `first_view` : il ne s'affiche qu'une seule fois par utilisateur, puis est automatiquement sauté (redirection vers la page suivante).

---

### 10. Gamification

| Élément | Fonctionnement |
|---|---|
| **XP** | +10 par exercice correct (première fois), +20 pour étape théorique |
| **Niveau** | `(total_xp // 100) + 1` affiché dans la navbar |
| **Confettis** | Animation canvas-confetti lors d'une bonne réponse |
| **Flash animation** | Éclair animé au changement d'étape |
| **Score matière** | Cumulatif par `SubjectProgress` |

---

### 11. Interface Admin

Accessible aux utilisateurs dont le `username` contient `_ADMIN`.

**Actions rapides (navbar)** :
- "Tout Valider" → valide toutes les étapes (mastery=3, XP=99999)
- "Tout Reset" → réinitialise toute la progression

**Panel Debug** (`/debug/`) :
- Stats globales de tous les utilisateurs (progression, taux de réussite)
- Détail par utilisateur avec agrégation hiérarchique des tags
- Liste et test de tous les templates d'exercices
- Liste et prévisualisation de tous les dialogues
- Galerie des animations
- Validation/invalidation individuelle des étapes

#### Agrégation hiérarchique des tags (debug user)

Un tag `math.calcul.mul.table_3` est agrégé en :
- `math`
- `math.calcul`
- `math.calcul.mul`
- `math.calcul.mul.table_3`

Cela permet d'afficher des stats à chaque niveau de granularité.

---

### 12. Thème clair / sombre

Bascule dans la navbar (icône soleil/lune).
- Persisté en `localStorage` sous la clé `"theme"`
- Activation via la classe `dark-mode` sur `<body>`
- Variables CSS redéfinies dans `:root` pour les deux modes
