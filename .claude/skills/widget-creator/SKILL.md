---
name: widget-creator
description: "Crée ou modifie un widget d'exercice ou d'affichage pour Parcours. Génère le YAML, le composant React, et met à jour les dispatchers. Utiliser quand on veut un nouveau type de widget (image, fraction, fill-in, tableau, etc.) ou modifier un widget existant."
argument-hint: "[description du widget souhaité]"
user-invocable: true
---

# Widget Creator — Parcours

Ce skill crée ou modifie un widget dans l'application Parcours (Java Spring Boot + React/TypeScript).

## Processus à suivre

Quand l'utilisateur décrit un widget :

1. **Analyser** la description. Si ambigu, demander :
   - Type de réponse : saisie libre / QCM / affichage pur (pas de réponse)
   - Variables nécessaires (valeurs fixes, plages aléatoires, listes de choix)
   - Champs d'affichage custom (images, slots, icônes…)
2. **Générer le YAML** (bloc complet prêt à coller dans un fichier `cours-back/content/<sujet>/`)
3. **Créer le composant React** dans `cours-front/src/components/exercises/`
4. **Mettre à jour les deux dispatchers** (ExerciseSession + CoursContent)
5. **Récapituler** les fichiers modifiés + commandes de test

---

## Architecture de référence

### Backend — rarement à modifier

- `cours-back/src/main/java/fr/parcours/model/content/ExerciseTemplate.java`
  Champs : `id`, `tags`, `vars`, `content`, `logic`, `interaction`, `renderType`, `multiple`, `type`

- `cours-back/src/main/java/fr/parcours/service/ExerciseEngineService.java`
  Interpole `{var}` et `[[expr]]` dans tous les champs `content:`, passe tout dans `GeneratedExercise.data`

- `cours-back/src/main/java/fr/parcours/model/dto/GeneratedExercise.java`
  Champs standard + `data: Map<String, Object>` — tous les champs `content:` du YAML s'y retrouvent interpolés

**Backend à modifier seulement si :**
- Nouveau format de correction non standard → `SmartCompareService.java`
- Nouveau champ de template au-delà de `content:` → `ExerciseTemplate.java`

### Frontend — deux dispatchers à mettre à jour

- `cours-front/src/components/ExerciseSession.tsx` — `renderEx()` ligne ~51, switch sur `ex.type`
- `cours-front/src/components/CoursContent.tsx` — `InlineExo()` ligne ~48, même logique
- Composants : `cours-front/src/components/exercises/`
- `MdText` disponible dans `cours-front/src/components/exercises/MdText.tsx` — markdown + KaTeX

**Types existants :** `input` (défaut), `qcm` / `multiselect`, `drag_drop` / `dragdrop`

---

## Format YAML complet

```yaml
# Section generators: — exercice dynamique avec variables aléatoires
generators:
  - id: mon_widget_id
    tags: ["sujet.sous-sujet.tag"]
    difficulty: 1              # 1=facile  2=moyen  3=difficile
    interaction: mon_type      # ← DOIT correspondre exactement au case dans les dispatchers
    multiple: false            # true = checkboxes multi-sélection
    vars:
      a: { min: 1, max: 10 }   # entier aléatoire dans [1..10]
      b: [1, 5, 20]            # choix aléatoire dans la liste
      c: 42                    # valeur fixe
    content:
      question: "Question avec {a} et {b} ?"
      answer: "[[{a}*{b}]]"    # string — ou indices [0,2] pour QCM
      explanation: "Car **{a}** × {b} = [[{a}*{b}]]"
      unit: "kg"               # optionnel, affiché après l'input
      options:                 # pour QCM seulement
        - "Option {a}"
        - "[[{a}*{b}]]"
      # Champs custom libres → accessibles via exercise.data côté front :
      image_src: "/images/schema_{a}.png"
      caption: "Illustration pour {a}"
      slots: ["___", "{b}", "___"]
    logic: "{a} * {b}"         # si réponse calculée — écrase content.answer

# Section templates: — problème à texte fixe (pas de générateur)
templates:
  - id: mon_template_id
    tags: ["sujet.tag"]
    difficulty: 2
    interaction: mon_type
    vars:
      n: { min: 3, max: 8 }
    content:
      question: "Problème avec {n} éléments..."
      answer: "[[{n}*5]]"
      unit: "items"
      icon: "mon_icone"        # champ custom → exercise.data.icon
```

### Règles importantes

| Règle | Détail |
|---|---|
| `interaction` | Doit être le nom **exact** du `case` dans les dispatchers frontend |
| `{var}` | Substitution dans **tous** les champs `content:` |
| `[[expr]]` | Évaluation arithmétique : `+` `-` `*` `/` et parenthèses |
| `content:` | Tous les champs sont passés interpolés dans `exercise.data` côté front |
| `logic:` | Si présent, calcule la réponse automatiquement (écrase `content.answer`) |
| QCM `answer:` | Liste d'entiers = indices dans `options:` (ex : `[0, 2]` = 1re et 3e options) |
| Placement | Fichier YAML dans `cours-back/content/<sujet>/` |

---

## Template composant React

Créer `cours-front/src/components/exercises/MonWidget.tsx` :

```tsx
import type { GeneratedExercise } from '../../api/steps'
import MdText from './MdText'
import styles from './Exercise.module.css'

interface Props {
  exercise: GeneratedExercise
  value: unknown          // adapter le type selon le widget
  onChange: (v: unknown) => void
  readonly?: boolean
  correct?: boolean
}

export default function MonWidget({ exercise, value, onChange, readonly, correct }: Props) {
  // Lire les champs custom depuis exercise.data
  const data = (exercise.data ?? {}) as Record<string, unknown>
  // Exemples :
  // const imageSrc = data.image_src as string
  // const slots = data.slots as string[]

  return (
    <div className={styles.ex}>
      <p className={styles.q}><MdText>{exercise.question}</MdText></p>

      {/* ── Zone de réponse ── */}
      {/* Implémenter ici l'interface de saisie */}

      {exercise.unit && <span className={styles.unit}>{exercise.unit}</span>}

      {readonly && exercise.explanation && (
        <p className={styles.expl}><MdText>{exercise.explanation}</MdText></p>
      )}
    </div>
  )
}
```

**CSS :** réutiliser `Exercise.module.css` (classes `ex`, `q`, `expl`, `input`, `unit`, `correct`, `incorrect`).
Créer un nouveau `.module.css` uniquement si les classes existantes sont insuffisantes.

---

## Mettre à jour les dispatchers

### `cours-front/src/components/ExerciseSession.tsx`

Dans la fonction `renderEx()` (ligne ~51), ajouter avant le `return` final :

```typescript
if (t === 'mon_type') return <MonWidget exercise={ex} value={value} onChange={onChange} />
```

### `cours-front/src/components/CoursContent.tsx`

Dans le composant `InlineExo()`, étendre la détection du type :

```typescript
const isMonType = exercise.type === 'mon_type' || exercise.renderType === 'mon_type'
```

Puis dans le JSX, ajouter un cas avant le fallback `InputExercise` :

```tsx
{isMonType ? (
  <MonWidget
    exercise={exercise}
    value={answer}
    onChange={setAnswer}
    readonly={revealed}
  />
) : isQcm ? (
  <QcmExercise ... />
) : (
  <InputExercise ... />
)}
```

---

## Cas backend nécessitant des modifications

### Nouveau format de réponse (rare)

Exemple : fraction `"3/4"`, coordonnées `"(x,y)"`, intervalle `"[2;5]"`.

Modifier `cours-back/src/main/java/fr/parcours/service/SmartCompareService.java` :
- Ajouter une branche de comparaison **avant** le fallback `equalsIgnoreCase`
- Pattern : détecter le format, parser, comparer sémantiquement

### Widget d'affichage pur (pas de réponse)

Pour un widget qui n'attend aucune réponse (image, schéma annoté, vidéo) :
- Le frontend soumet `""` pour ce widget
- Côté backend, `SmartCompare` retourne `false` mais on peut marquer l'exercice comme non évalué
- Alternative : déclarer `answer: "display"` et le widget ne collecte pas de réponse

### Nouveau champ de template (très rare)

Si le champ dépasse ce que `content:` peut porter (ex : champ structurel comme `sub_type`) :
- Modifier `ExerciseTemplate.java` — ajouter le champ avec `private String monChamp;` (Lombok génère getter/setter)

---

## Tester le widget

### Rechargement YAML sans redémarrage

```bash
# Via curl (récupérer le cookie SESSION depuis les DevTools → Application → Cookies)
curl -X POST http://localhost:8080/api/admin/reload-content \
     -H "Cookie: SESSION=<valeur>"
```

Ou via un compte admin connecté dans le navigateur (appel fetch depuis la console DevTools).

### Checklist de test

1. `cd cours-back && mvn spring-boot:run` — backend démarré
2. `cd cours-front && npm run dev` — frontend démarré
3. Naviguer vers une étape qui référence le template
4. **DevTools → Network** : inspecter la réponse `/api/steps/:id`
   - Vérifier que `exercises[0].type` = le type déclaré
   - Vérifier que `exercises[0].data` contient les champs custom
5. Le widget s'affiche et collecte la réponse
6. Après soumission : widget en mode `readonly`, explication visible
7. `cd cours-front && npx tsc --noEmit` — pas d'erreur TypeScript

### Erreurs fréquentes

| Symptôme | Cause probable |
|---|---|
| Widget ne s'affiche pas (fallback input) | `interaction:` YAML ≠ `case` exact dans le dispatcher |
| `exercise.data` vide ou undefined | Champs custom au niveau racine du template au lieu de dans `content:` |
| Réponse toujours incorrecte | Format de réponse non géré par `SmartCompareService` |
| Variables non remplacées | Nom de variable entre `{}` ne correspond pas à une clé dans `vars:` |
| `[[expr]]` non calculé | Expression contient des caractères non arithmétiques |

---

## Checklist de livraison

```
[ ] YAML ajouté dans cours-back/content/<sujet>/
[ ] Nouveaux tags déclarés dans tags.yaml si applicable
[ ] Composant React créé dans cours-front/src/components/exercises/
[ ] ExerciseSession.tsx mis à jour (renderEx)
[ ] CoursContent.tsx mis à jour (InlineExo)
[ ] npx tsc --noEmit passe sans erreur
[ ] Rechargement YAML testé (reload-content)
[ ] Widget testé en mode saisie
[ ] Widget testé en mode review (readonly après soumission)
```
