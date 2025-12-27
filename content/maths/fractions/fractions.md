---
id: math_01
title: "Les Fractions"
order: 1
exercises:
  - id: fraction_cours_01
    type: "qcm"
    question: "Combien fait $\\frac{1}{2} + \\frac{1}{2}$ ?"
    options: ["1", "2", "$\\frac{1}{4}$"]
    answer: "1"
  - id: fraction_cours_02
    type: "drag_drop"
    template: "Le numérateur est le chiffre du ???."
    options: ["haut", "bas"]
    answer: "haut"
  - id: ex_viz_01
    type: "fraction_scenario"
    visual: "PIZZA"
    parts: 4
    participants:
      - name: "Part"
        fraction: "3/4"
        color: "#27ae60"
    question: "Quelle fraction de la pizza est colorée en vert ?"
    answer: "3/4"
  - id: ex_viz_02
    type: "fraction_scenario"
    visual: "CYLINDER"
    parts: 5
    participants:
      - name: "Liquid"
        fraction: "2/5"
        color: "#2980b9"
    question: "Quelle est la fraction du liquide dans le récipient ?"
    answer: "2/5"
  - id: ex_viz_03
    type: "fraction_scenario"
    visual: "GRID"
    parts: 10
    participants:
      - name: "Selection"
        fraction: "1/2"
        color: "#8e44ad"
    question: "Sur ce quadrillage de 10 cases, quelle fraction est colorée ? (Indice: c'est la moitié)"
    answer: "1/2"
---



Une fraction représente une partie d'un tout. Elle s'écrit sous la forme :

$$ \frac{a}{b} $$

Où **a** est le numérateur et **b** est le dénominateur. Par exemple, dans la fraction $\frac{1}{2}$, 1 est le numérateur et 2 est le dénominateur.


### 1. Que représentent ces nombres ?

Pour bien comprendre une fraction, on peut imaginer le partage d'une unité (comme un gâteau ou une pizza) :

* **Le dénominateur (b) :** Il indique en combien de **parts égales** l'unité a été découpée. Il "dénomme" la fraction (des demis, des tiers, des quarts...).
* **Le numérateur (a) :** Il indique le **nombre de parts** que l'on prend ou que l'on colorie. Il "numère" (compte) les parts.

> **Attention :** Le dénominateur **b** ne peut jamais être égal à 0, car on ne peut pas diviser par zéro.

### 2. Représentations Visuelles

Pour mieux comprendre, regardons des objets du quotidien.

#### La Pizza

**$\frac{1}{2}$ (Un demi)** : C'est la moitié de la pizza.
<div class="fraction-demo" data-config='{"visual": "PIZZA", "parts": 2, "participants": [{"name": "Half", "fraction": "1/2", "color": "#e67e22"}]}'></div>

**$\frac{1}{4}$ (Un quart)** : Si vous la coupez en 4 parts égales, une seule part représente 1/4.
<div class="fraction-demo" data-config='{"visual": "PIZZA", "parts": 4, "participants": [{"name": "Quarter", "fraction": "1/4", "color": "#3498db"}]}'></div>

#### Le Chocolat

Imaginez une tablette de chocolat avec des carrés.
Si la tablette a **12 carrés**, prendre $\frac{1}{4}$ de la tablette revient à prendre **3 carrés** (car $12 \div 4 = 3$).

<div class="fraction-demo" data-config='{"visual": "GRID", "parts": 12, "participants": [{"name": "Choco", "fraction": "1/4", "color": "#8e44ad"}]}'></div>

---

### 3. Comment lire une fraction ?

* $\frac{1}{2}$ se lit : **un demi**
* $\frac{1}{3}$ se lit : **un tiers**
* $\frac{1}{4}$ se lit : **un quart**
* $\frac{2}{5}$ se lit : **deux cinquièmes**

### 4. Différents types de fractions

| Type | Description | Exemple |
| --- | --- | --- |
| **Fraction propre** | Numérateur < Dénominateur | $\frac{1}{2}$ |
| **Fraction impropre** | Numérateur > Dénominateur | $\frac{3}{2}$ |

*Passez maintenant aux exercices pour tester vos connaissances !*
