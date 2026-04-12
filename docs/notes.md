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
- **Exercice** : un exercice inline ou une page entière d'exercice
- **Dialogue** : un dialogue entre deux personnages
- une frise chronologique
- une image agrandissable
- une vidéo
- un quiz
- ...

Les widget ont une même base, on l'insère dans une page et on le configure. L'exercice par exemple peut avoir différentes configurations (exercice de type QCM, exercice de type texte à trous, etc...), renvoyer de l'XP ou non, avoir une note ou non, etc...