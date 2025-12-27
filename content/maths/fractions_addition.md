---
id: math_04
title: "Addition & Soustraction"
order: 4
exercises:
  - id: add_ex_01
    type: "qcm"
    question: "Combien fait $\\frac{1}{5} + \\frac{2}{5}$ ?"
    options: ["$\\frac{3}{5}$", "$\\frac{3}{10}$", "$\\frac{1}{5}$"]
    answer: "$\\frac{3}{5}$"
  - id: add_ex_02
    type: "qcm"
    question: "Combien fait $\\frac{1}{2} + \\frac{1}{4}$ ?"
    options: ["$\\frac{2}{6}$", "$\\frac{3}{4}$", "$\\frac{2}{4}$"]
    answer: "$\\frac{3}{4}$"
---

# Addition et Soustraction

Pour additionner (ou soustraire) des fractions, il faut faire attention à leur dénominateur.

### 1. Dénominateurs identiques
Si les dénominateurs sont les mêmes, c'est facile ! On additionne seulement les numérateurs. Le dénominateur ne change pas.

$$ \frac{1}{5} + \frac{2}{5} = \frac{1+2}{5} = \frac{3}{5} $$

<div class="fraction-demo" data-config='{"visual": "GRID", "parts": 5, "participants": [{"name": "1/5", "fraction": "1/5", "color": "#e74c3c"}, {"name": "2/5", "fraction": "2/5", "color": "#3498db"}]}'></div>

### 2. Dénominateurs différents
Si les dénominateurs sont différents, on ne peut pas additionner directement. Il faut d'abord les mettre au **même dénominateur**.

**Exemple :** $\frac{1}{2} + \frac{1}{4}$

On sait que $\frac{1}{2} = \frac{2}{4}$ (en multipliant haut et bas par 2).
L'addition devient :
$$ \frac{2}{4} + \frac{1}{4} = \frac{3}{4} $$

Visualisons cela avec des parts de pizza :
*   $\frac{1}{2}$ (la moitié, en rouge)
*   $\frac{1}{4}$ (un quart, en bleu)

<div class="fraction-demo" data-config='{"visual": "PIZZA", "parts": 4, "participants": [{"name": "1/2", "fraction": "2/4", "color": "#e74c3c"}, {"name": "1/4", "fraction": "1/4", "color": "#3498db"}]}'></div>

On voit bien que cela fait 3 quarts ($\frac{3}{4}$) au total.
