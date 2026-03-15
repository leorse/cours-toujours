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
- Dialogues monologue (personnage + texte)
- Dialogues SMS (deux personnages avec sprites)
- Mode flash adaptatif (ciblage points faibles)
- Renforcement adaptatif (règle 60/20/20)
- Système de mastery (0→3) pour les étapes flash/validation
- Gamification (XP, niveaux, confettis, flash animation)
- Thème clair/sombre
- Panel admin complet (stats, debug, validation)
- Agrégation hiérarchique des stats par tags
- Condition `first_view` sur les dialogues et événements
- Exercices inline dans les cours (`&&id&&`)
- Rendu KaTeX pour les formules mathématiques
- Blueprints visuels pour les fractions (Pizza, Grid, Cylinder)

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

- **Mobile** : le layout SMS/dialogues masque les avatars en dessous de 768px.
- **Pas de retour arrière** sur les exercices : une fois soumis, impossible de revenir.
- **Pas de feedback immédiat** en mode monologue (pas d'animation de transition entre slides).

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
