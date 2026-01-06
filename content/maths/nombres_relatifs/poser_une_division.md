## 2 Poser une division

Poser une division (souvent appelée "la potence") est une méthode visuelle qui permet de décomposer le calcul étape par étape. Voici comment s'organiser et procéder.

---

### 1. La structure : "La Potence"

Pour commencer, on dessine une ligne verticale et une barre horizontale pour séparer les quatre éléments de la division :

* Le **Dividende** (a) se place à gauche.
* Le **Diviseur** (b) se place en haut à droite, au-dessus de la barre.
* Le **Quotient** (q) s'écrira sous le diviseur.
* Le **Reste** (r) apparaîtra en bas à gauche à la fin des calculs.

$$
\begin{array}{r|l}
\text{Dividende } (a) & \text{Diviseur } (b) \\ \hline
\dots & \text{Quotient } (q) \\
\text{Reste } (r) & 
\end{array}
$$

---

### 2. La Méthode pas à pas

Prenons l'exemple de **157 divisé par 4**.

1. **On commence par la gauche** : On regarde le premier chiffre du dividende (1). Est-ce que 4 rentre dans 1 ? Non. On prend alors les deux premiers chiffres : **15**.
2. **On cherche le multiple** : Combien de fois 4 rentre-t-il dans 15 ?
* $4 \times 3 = 12$
* $4 \times 4 = 16$ (trop grand !)
* On choisit donc **3**. On écrit 3 au quotient.


3. **On soustrait** : On fait $15 - 12 = 3$. On écrit ce résultat sous le 15.
4. **On "abaisse"** : On fait descendre le chiffre suivant, le **7**, à côté du 3. On a maintenant **37**.
5. **On recommence** : Combien de fois 4 rentre-t-il dans 37 ?
* $4 \times 9 = 36$
* $4 \times 10 = 40$ (trop grand !)
* On écrit **9** au quotient à côté du 3.


6. **On termine** : On fait $37 - 36 = 1$. Il n'y a plus de chiffres à abaisser. **1** est notre reste.


Voici à quoi ressemble le calcul posé mathématiquement :

$$
\begin{array}{r|l}
157 & 4 \\ \hline
\underline{-12\phantom{0}} & 39 \\
37 & \text{Quotient} \\
\underline{-36} & \\
\mathbf{1} & \text{Reste}
\end{array}
$$


### Vérification du résultat

Pour être sûr de ne pas s'être trompé, on applique la formule de la division euclidienne :

$$
157 = 4 \times 39 + 1
$$

$$
157 = 156 + 1
$$

$$
157 = 157
$$


> **Règle d'or** : Le reste (**1**) est bien inférieur au diviseur (**4**). Si ton reste est égal ou plus grand que le diviseur, c'est que tu peux encore mettre le diviseur "une fois de plus" dans le quotient !