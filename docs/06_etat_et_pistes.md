# État du projet et pistes d'évolution

## Branches Git actives

| Branche | Description probable |
|---|---|
| `main` | Branche principale stable |
| `dialogues` | Développement du système de dialogues (branche courante) |
| `theme` | Ajout du thème nature (mergé) |
| `generation_test` | Tests du système de génération d'exercices (mergé) |
| `parcours` | Travaux sur le parcours |

---

## Ce qui fonctionne

- Système de parcours multi-étapes multi-pages
- Génération d'exercices déclaratifs via templates YAML
- Correction automatique avec `smart_compare` (strings, nombres, fractions, listes)
- **Feedback coloré après correction** : vert/rouge, lecture seule, revisit avec bonnes réponses affichées
- Dialogues monologue (personnage + texte)
- Dialogues SMS (deux personnages avec sprites)
- Condition `first_view` sur les dialogues de page (suivi via `UserEvent` préfixé `step_page_*`)
- Mode flash adaptatif (ciblage points faibles)
- Renforcement adaptatif (règle 60/20/20)
- Système de mastery (0→3) pour les étapes flash/validation
- Gamification (XP, niveaux, confettis, flash animation)
- Thème clair/sombre
- Panel admin complet (stats, debug, validation)
- Agrégation hiérarchique des stats par tags
- Exercices inline dans les cours (`&&id&&`)
- Rendu KaTeX pour les formules mathématiques
- Blueprints visuels pour les fractions (Pizza, Grid, Cylinder)
- **Tables Markdown** : bordures, alternance de lignes, scroll horizontal sur mobile
- **PWA installable** : manifest + service worker (cache-first static/CDN, network-first pages)
- **Design responsive** : breakpoints 480/640/768px, touch targets 44px
- **Drag-drop mobile** : module `touch_dragdrop.js` (tap-sélect-tap, détection `pointer: coarse`)

---

## Points de fragilité / dette technique

### Architecture

- **Deux systèmes de génération coexistent** : `ExerciseEngine` (templates YAML déclaratifs) et `generators/` (procédural). Le code `generators/` est peu utilisé et partiellement intégré.
- **Contenu chargé une seule fois** au démarrage : toute modification de YAML nécessite un redémarrage du serveur (pas de rechargement à chaud).
- **Pas de pagination** des résultats en base : acceptable pour un petit groupe d'élèves, à revoir pour une utilisation à grande échelle.

### Sécurité

- **Authentification sans mot de passe** : volontaire pour la simplicité d'usage en classe, mais à sécuriser si déployé sur Internet.
- **`eval()` dans `ExerciseEngine`** : les expressions évaluées viennent des fichiers YAML éditoriaux (non de l'utilisateur). Risque limité mais à documenter clairement.
- **Admin identifié par nom** : `_ADMIN` dans le username, sans token ni vérification forte.

### Qualité du code

- **Code mort** en fin de `main.py` (lignes 1083-1116) : bloc `debug_user_details` suivi d'un bloc orphelin inaccessible (après le `return`).
- **Fichiers legacy** : `src/test_generator.py`, plusieurs scripts dans `scripts/`.
- **`exos.yaml`** dans `calculs/` : utilise un format `exercices` + `generators` mélangé qui n'est pas entièrement compatible avec le ContentManager actuel.

### UX

- **Pas de retour arrière** sur les exercices : une fois soumis, impossible de revenir.
- **Pas de feedback immédiat** en mode monologue (pas d'animation de transition entre slides).
- **Icônes PWA** : `logo.png` est utilisé tel quel pour les icônes 192px et 512px. Pour un install prompt correct sur tous les navigateurs, générer des fichiers `logo-192.png` et `logo-512.png` aux bonnes dimensions.

---

## Pistes d'évolution suggérées

### Pédagogie

- Ajouter d'autres matières (français, géographie, sciences)
- Implémenter un vrai système de badges/récompenses
- Permettre à l'enseignant de configurer les parcours via une interface
- Ajouter des exercices de type "construction" (tracer, placer sur axe)

### Technique

- Recharger le contenu à chaud (watcher sur le dossier `content/`)
- Ajouter une API REST documentée (Swagger déjà intégré via FastAPI : `/docs`)
- Séparer la logique de `main.py` en routers FastAPI dédiés
- Unifier les deux systèmes de génération (YAML déclaratif comme référence)
- Ajouter des tests unitaires (le dossier `scripts/test_factory.py` existe déjà partiellement)
- Authentification légère par PIN ou code de classe

### Déploiement

- Dockerisation
- Passage à PostgreSQL pour un déploiement multi-instances
- Système de sauvegarde de la base SQLite
- Générer des icônes PWA aux dimensions correctes (192×192 et 512×512) depuis `logo.png`
- Incrémenter `CACHE_NAME` dans `sw.js` à chaque déploiement pour forcer le rechargement du cache
