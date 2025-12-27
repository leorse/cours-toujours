---
id: math_02
title: "Multiplication de Fractions"
order: 2
exercises:
  - id: mult_ex_01
    type: "qcm"
    question: "Combien fait $\\frac{1}{2} \\times \\frac{1}{2}$ ?"
    options: ["1", "$\\frac{1}{4}$", "$\\frac{2}{4}$"]
    answer: "$\\frac{1}{4}$"
  - id: mult_ex_02
    type: "fraction_scenario"
    visual: "PIZZA"
    parts: 4
    participants:
      - name: "Result"
        fraction: "1/4"
        color: "#e74c3c"
    question: "Voici le résultat de 1/2 x 1/2. Quelle est cette fraction ?"
    answer: "1/4"
---



Multiplier des fractions est plus simple que de les additionner ! Il suffit de multiplier les numérateurs entre eux et les dénominateurs entre eux.

$$ \frac{a}{b} \times \frac{c}{d} = \frac{a \times c}{b \times d} $$

### Exemple
Calculons $\frac{1}{2} \times \frac{1}{2}$ :
1.  On multiplie les numérateurs : $1 \times 1 = 1$
2.  On multiplie les dénominateurs : $2 \times 2 = 4$
3.  Résultat : $\frac{1}{4}$

### Visualisation
Prendre la moitié d'une moitié revient à prendre un quart.

Imaginez une demi-pizza :
<div class="fraction-demo" data-config='{"visual": "PIZZA", "parts": 2, "participants": [{"name": "Half", "fraction": "1/2", "color": "#e67e22"}]}'></div>

Si on prend la moitié de cette part (la partie rouge ci-dessous), on obtient un quart de la pizza totale :
<div class="fraction-demo" data-config='{"visual": "PIZZA", "parts": 4, "participants": [{"name": "Quarter", "fraction": "1/4", "color": "#e74c3c"}]}'></div>
