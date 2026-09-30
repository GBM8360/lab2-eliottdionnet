---
title: 1. Masquer le centre de l'espace des k
description: Effet de la troncature du centre de l'espace des k sur le FOV et la résolution
---

## Introduction du problème

On masque la région centrale de l'espace des k et on affiche l'espace des k résultant
ainsi que la magnitude de l'image reconstruite, en interprétant le résultat à l'aide des
équations qui caractérisent le FOV et la résolution {cite:p}`Larson2023`.

## Rappel théorique

On a vu dans l'[introduction](#sec-fondements) que le FOV et la résolution dépendent tous
les deux de l'échantillonnage de l'espace des k, mais pas de la même façon :

- $\text{FOV} = 1/\Delta k$ {eq}`eq-fov` ;
- $\Delta x = 1/(N\,\Delta k)$ {eq}`eq-resolution`.

Le FOV ne dépend que de l'espacement $\Delta k$ entre les échantillons, la résolution que
de l'étendue $N\Delta k = 2k_{\max}$ couverte. Masquer le centre ne touche à aucun des
deux : les points restants sont toujours sur la même grille (même $\Delta k$) et les
points les plus loin du centre sont toujours là (même $k_{\max}$). Le FOV et la résolution
nominale ne bougent donc pas. Ce qui change, ce sont les fréquences spatiales encore
présentes dans l'image.

| Opération | Change $\Delta k$ ? | Change $k_{\max}$ ? | FOV | Résolution | Effet visible |
|---|---|---|---|---|---|
| Masquage central (cette page) | Non | Non | Inchangé | Inchangée (nominale) | Perte des basses fréquences |

## Modèle

### Le masque et son effet sur l'image

On met à zéro un rectangle centré de demi-côtés $a_x$ (lecture) et $a_y$ (phase). En
notant $\Pi(t) = 1$ si $|t| < 1/2$ et 0 sinon, le masque s'écrit

```{math}
:label: eq-masque
M(k_x, k_y) = 1 - \Pi\!\left(\frac{k_x}{2a_x}\right)\Pi\!\left(\frac{k_y}{2a_y}\right),
\qquad
K_M = M \cdot K .
```

Le masque vaut donc « 1 moins une fenêtre ». La transformée de Fourier est linéaire, et un
produit dans l'espace des k devient une
[convolution](https://fr.wikipedia.org/wiki/Produit_de_convolution) dans l'image, d'où :

```{math}
:label: eq-masque-image
I_M = I - I \circledast h_a,
\qquad
h_a(x, y) = 2a_x \operatorname{sinc}(2a_x\, x)\;\cdot\; 2a_y \operatorname{sinc}(2a_y\, y).
```

Le terme $I \circledast h_a$ est l'image passée dans un filtre passe-bas : une image floue
qui ne contient que les fréquences $|k_x| < a_x$, $|k_y| < a_y$. En la retirant on
applique à l'image un filtre passe-haut. Tout ce qui varie lentement disparaît, et on
garde ce qui varie vite (les bords, les détails fins).

### Combien d'énergie retire-t-on ?

D'après l'[égalité de Parseval](https://fr.wikipedia.org/wiki/%C3%89galit%C3%A9_de_Parseval),
l'énergie de l'image est égale  à celle de l'espace des k. La
fraction d'énergie qu'on enlève à l'image est donc exactement la fraction d'énergie
masquée dans l'espace des k :

```{math}
:label: eq-energie-masque
\frac{E_{\text{retirée}}}{E_{\text{totale}}}
= \frac{\sum_{(u,v)\,\in\,\text{masque}} |K[u, v]|^2}{\sum_{u,v} |K[u, v]|^2}.
```

Sur nos données ($f$ est la demi-largeur du masque, en pourcentage de la demi-dimension
de la matrice) :

| $f$ | Surface masquée | Énergie retirée |
|---|---|---|
| 5 % | 0,2 % | 70,8 % |
| 10 % | 0,9 % | 83,5 % |
| 20 % | 3,4 % | 90,0 % |
| 30 % | 8,8 % | 93,7 % |
| 50 % | 25 % | 96,9 % |
| 90 % | 78,9 % | 99,7 % |

Le centre concentre presque toute l'énergie : avec seulement 0,2 % des points masqués, on
perd déjà 71 % de l'énergie de l'image. C'est ce qui explique la perte de contraste.

## Figure interactive

Fais varier la taille du masque central avec le curseur et regarde en direct l'effet sur
l'espace des k et sur l'image reconstruite. Coche « échelle fixe » pour voir la perte
d'intensité globale, au lieu d'une image réétirée à chaque position.

:::{iframe} /figures/fig-masquage.html
:label: fig-masquage-embed
:class: kfig
:width: 100%
:placeholder: img/fig-masquage-static.png

Effet du masquage central de l'espace des k (à gauche, $\log|K|$ masqué) sur la magnitude
(au centre) et la phase (à droite, de $-\pi$ à $\pi$) de l'image reconstruite, pour une
demi-largeur de masque de 0 à 90 % de la demi-dimension de la matrice.
:::

Voir [](#fig-masquage-embed). À 0 %, l'image de référence est intacte. Plus le masque
grandit, plus l'espace des k perd ses basses fréquences, celles qui portent l'essentiel du
contraste global. Les hautes fréquences qui restent portent les contours, et continuent à
dessiner une silhouette de plus en plus creuse de l'image.

## Interprétation

Le résultat colle avec {eq}`eq-fov` et {eq}`eq-resolution` : le FOV et la résolution
nominale ne changent pas, puisque $\Delta k$ et $N\Delta k$ restent les mêmes. Ce qui se
dégrade, c'est le contenu :

- {eq}`eq-masque-image` montre que l'image masquée est l'image d'origine moins sa version
  passe-bas. C'est un filtre passe-haut, qui garde les transitions rapides (contours) et
  retire les variations lentes (le contraste entre grandes régions).
- {eq}`eq-energie-masque` chiffre la perte : quelques dixièmes de pour cent des points de
  l'espace des k suffisent à retirer plus des deux tiers de l'énergie de l'image.

## Et si on décentre le masque ?
Et Si le masque n'est plus forcément au centre ? 

:::{iframe} /figures/fig-masquage-centre.html
:label: fig-masquage-centre
:class: kfig kfig-live
:width: 100%
:placeholder: img/fig-masquage-centre-static.png

Masque rectangulaire de taille et de position réglables dans l'espace des k : espace des
k masqué, magnitude et phase de l'image reconstruite.
:::
On remarque bien que c'est lorsque le masque passe au niveau du centre qu'il y a une vrai variation visuelle.