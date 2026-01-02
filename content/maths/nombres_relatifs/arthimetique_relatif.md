# Chapitre : Arithmétique et Relatifs 🚀

Bienvenue dans ce cours ! On va apprendre à diviser le monde en parts égales et à jongler avec les signes plus et moins.

## 1. Multiples et Diviseurs
La **division euclidienne** est la base de l'arithmétique. Contrairement à la division classique qui peut donner un résultat à virgule, la division euclidienne ne travaille qu'avec des **nombres entiers**.

### Définition Mathématique

Effectuer la division euclidienne d'un nombre entier  (le dividende) par un nombre entier  (le diviseur, différent de zéro), c'est trouver deux nombres entiers uniques : le **quotient** () et le **reste** ().

Ces nombres doivent répondre à deux conditions impératives :

1. **L'égalité** : 
2. **La contrainte du reste** : Le reste doit être strictement plus petit que le diviseur ().

---

### L'analogie du partage de bonbons

Pour mieux visualiser ces termes techniques, reprenons ton exemple des bonbons :

* ** (Dividende)** : C'est le nombre total de bonbons que tu as au départ (ton stock).
* ** (Diviseur)** : C'est le nombre de personnes qui participent au partage (tes amis).
* ** (Quotient)** : C'est la part entière que reçoit chaque ami. Tout le monde a la même quantité.
* ** (Reste)** : Ce sont les bonbons qui restent sur la table parce qu'il n'y en a pas assez pour en redonner un à chacun sans faire de jaloux.

---

### Exemples Concrets

Voici deux situations pour illustrer comment ces chiffres interagissent :

#### Exemple 1 : Un partage avec un reste

Tu as **17** bonbons et tu veux les partager entre **5** amis.

* Chaque ami reçoit **3** bonbons (cela fait 15 bonbons distribués).
* Il en reste **2** dans le paquet.
* **L'équation** : 
* *Vérification* : Le reste (**2**) est bien plus petit que le nombre d'amis (**5**).

#### Exemple 2 : Un partage "parfait" (Divisibilité)

Tu as **24** bonbons pour **6** amis.

* Chaque ami reçoit exactement **4** bonbons.
* Il en reste **0**.
* **L'équation** : 
* *Note* : Quand le reste est **0**, on dit que 24 est **divisible** par 6.

---

### Ce qu'il faut retenir sur les chiffres

* Le **Quotient ()** représente la "taille du groupe" ou le "nombre de fois" que le diviseur rentre dans le dividende.
* Le **Reste ()** est ce qui empêche le nombre d'être parfaitement divisible. Si tu ajoutes des bonbons pour que le reste atteigne la valeur de , tu peux alors donner un bonbon de plus à tout le monde, et ton quotient  augmente de 1.


> **La règle d'or :** Si le reste est **$0$**, alors $a$ est un **multiple** de $b$, et $b$ est un **diviseur** de $a$.

&&math_div_qcm_01&&

---

## 2 Poser une division

Poser une division (souvent appelée "la potence") est une méthode visuelle qui permet de décomposer le calcul étape par étape. Voici comment s'organiser et procéder.

---

### 1. La structure : "La Potence"

Pour commencer, on dessine une ligne verticale et une barre horizontale pour séparer les quatre éléments de la division :

* Le **Dividende** () se place à gauche.
* Le **Diviseur** () se place en haut à droite, au-dessus de la barre.
* Le **Quotient** () s'écrira sous le diviseur.
* Le **Reste** () apparaîtra en bas à gauche à la fin des calculs.

---

### 2. La Méthode pas à pas

Prenons l'exemple de **157 divisé par 4**.

1. **On commence par la gauche** : On regarde le premier chiffre du dividende (1). Est-ce que 4 rentre dans 1 ? Non. On prend alors les deux premiers chiffres : **15**.
2. **On cherche le multiple** : Combien de fois 4 rentre-t-il dans 15 ?
* 
*  (trop grand !)
* On choisit donc **3**. On écrit 3 au quotient.


3. **On soustrait** : On fait . On écrit ce résultat sous le 15.
4. **On "abaisse"** : On fait descendre le chiffre suivant, le **7**, à côté du 3. On a maintenant **37**.
5. **On recommence** : Combien de fois 4 rentre-t-il dans 37 ?
* .
* On écrit **9** au quotient à côté du 3.


6. **On termine** : On fait . Il n'y a plus de chiffres à abaisser. **1** est notre reste.


Voici à quoi ressemble le calcul posé mathématiquement :

$$\begin{array}{r|l}
\text{1 5 7} & \text{4} \ \cline{2-2}

* \underline{1 \ 2} \phantom{0} & \mathbf{3 \ 9} \
3 \ 7 & \text{Quotient} \
* \underline{3 \ 6} & \
\mathbf{1} & \
\text{Reste} &
\end{array}$$

### Vérification du résultat

Pour être sûr de ne pas s'être trompé, on applique la formule de la division euclidienne :


> **Règle d'or** : Le reste (**1**) est bien inférieur au diviseur (**4**). Si ton reste est égal ou plus grand que le diviseur, c'est que tu peux encore mettre le diviseur "une fois de plus" dans le quotient !


---

## 3. Les Critères de Divisibilité
Pas besoin de calculatrice ! Pour savoir si un nombre est divisible, regarde-le bien :
* **Par 2, 5 ou 10** : Regarde le dernier chiffre.
* **Par 3 ou 9** : Fais la somme de tous ses chiffres.
* **Par 4** : Regarde les deux derniers chiffres.


### 1. La Position de l'Unité (2, 5 et 10)

Pour ces trois nombres, tout se joue sur le **dernier chiffre** (celui des unités). C'est le seul qui détermine si le nombre entier peut être partagé équitablement.

* **Divisibilité par 2** : Le nombre doit être **pair**. Cela signifie que son dernier chiffre appartient à la liste suivante : **0, 2, 4, 6 ou 8**.
* *Exemple* : **1 574** est divisible par 2 car il se termine par 4.
* *Exemple* : **3 891** ne l'est pas car il se termine par 1 (impair).


* **Divisibilité par 5** : Le nombre doit se terminer par un "chiffre pivot" de la table de 5, soit **0 ou 5**.
* *Exemple* : **245** est divisible par 5.
* *Exemple* : **1 090** est divisible par 5 (et par 10 aussi !).


* **Divisibilité par 10** : C'est la règle la plus stricte. Le nombre doit impérativement se terminer par **0**.
* *Exemple* : **5 600** est divisible par 10.


### 2. La Somme Magique (3 et 9)

Ici, peu importe le dernier chiffre. Ce qui compte, c'est la **valeur totale** du nombre quand on additionne ses composants.

* **Divisibilité par 3** : Si vous additionnez tous les chiffres du nombre et que le résultat est dans la **table de 3** (3, 6, 9, 12...), alors le nombre entier est divisible par 3.
* *Exemple* : Pour **453**, on fait 4 + 5 + 3 = **12**. Comme 12 est dans la table de 3, 453 est divisible par 3.


* **Divisibilité par 9** : C'est le même principe, mais le total doit être un multiple de 9 (9, 18, 27...).
* *Exemple* : Pour **8 901**, on fait 8 + 9 + 0 + 1 = **18**. Comme 18 est dans la table de 9, 8 901 est divisible par 9.


### 3. Le Bloc de Fin (4)

Pour le chiffre 4, on ne regarde pas seulement le dernier chiffre, mais les **deux derniers** (les dizaines et les unités). Si ce bloc de deux chiffres forme un nombre que l'on peut diviser par 4, alors tout le nombre, aussi grand soit-il, est divisible par 4.

* **Le secret** : Un nombre est divisible par 4 si on peut diviser sa moitié par 2.
* *Exemple* : **1 024**. On prend les deux derniers chiffres : **24**. Comme 24 est dans la table de 4 (), alors 1 024 est divisible par 4.
* *Exemple* : **7 518**. On prend **18**. 18 n'est pas dans la table de 4 ( et  le sont). Donc 7 518 n'est pas divisible par 4.

### Tableau Récapitulatif

| Diviseur | La condition porte sur... | Propriété requise |
| --- | --- | --- |
| **2** | Le dernier chiffre | Doit être 0, 2, 4, 6, 8 |
| **5** | Le dernier chiffre | Doit être 0 ou 5 |
| **10** | Le dernier chiffre | Doit être 0 |
| **3** | La somme des chiffres | Doit être 3, 6, 9, 12, ... |
| **9** | La somme des chiffres | Doit être 9, 18, 27, ... |
| **4** | Les deux derniers chiffres | Doivent former un multiple de 4 |


&&math_div_crit_01&&


---

## 4. Multiplier et Diviser les Relatifs
Ici, c'est la fête des signes. La règle est simple :
1.  **Même signe** : Le résultat est **positif (+)**.
2.  **Signes contraires** : Le résultat est **négatif (-)**.

$$(-5) \times (-3) = +15$$
$$(+10) \div (-2) = -5$$

&&math_rel_calc_01&&

---

## 5. La règle des facteurs
Si tu multiplies plein de nombres d'un coup, compte les signes **$(-)$** :
* Nombre de $(-)$ **Pair** $\rightarrow$ Résultat **$+$**
* Nombre de $(-)$ **Impair** $\rightarrow$ Résultat **$-$**

&&math_rel_multi_01&&