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