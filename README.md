# Cours Toujours!

Une application d'apprentissage interactive et ludique pour les cours (mathématiques, etc.).

## Fonctionnalités

- **Progression Modulaire** : Apprentissage par thèmes et chapitres.
- **Exercices Interactifs** : Questions à choix multiples, glisser-déposer, et plus.
- **Gamification** : Accumulez de l'XP et montez en niveau.
- **Support des Maths** : Rendu des formules mathématiques avec KaTeX et fractions visuelles.

## Installation

1.  **Cloner le dépôt**
2.  **Créer un environnement virtuel**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    ```
3.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

## Lancement

Démarrer le serveur FastAPI :
```bash
python -m uvicorn src.main:app --reload
```
L'application sera accessible sur `http://127.0.0.1:8000`.

## Contenu

Le contenu est chargé depuis des fichiers Markdown situés dans le dossier `content/`.
