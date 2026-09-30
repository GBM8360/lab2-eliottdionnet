---
title: 2. Sous-échantillonner l'espace des k
description: Effet du sous-échantillonnage d'une direction de l'espace des k sur le FOV et le repliement
---

## Introduction du problème

On sous-échantillonne l'espace des k de moitié dans une direction et on affiche l'espace
des k résultant ainsi que la magnitude de l'image reconstruite, en interprétant le
résultat à l'aide des équations de FOV et de résolution.

## Rappel théorique

Le [théorème d'échantillonnage](https://fr.wikipedia.org/wiki/Th%C3%A9or%C3%A8me_d'%C3%A9chantillonnage)
dit qu'il faut échantillonner un signal au moins deux fois plus vite que sa plus haute
fréquence pour pouvoir le reconstruire. Sinon une fréquence trop haute se replie sur les
fréquences plus basses c'est le repliement spectral.

Ici on échantillonne l'espace des k, donc le repliement se voit directement sur l'image.
Comme vu en [introduction](#sec-fondements) la reconstruction donne des copies de l'objet
espacées du FOV {eq}`eq-peigne` si l'objet tient dans le FOV, les copies ne se touchent
pas {eq}`eq-nyquist`.

## Modèle

On note $r$ le facteur de sous-échantillonnage, on garde une ligne de phase sur $r$ et on met les autres à zéro.

### Le FOV est divisé par $r$

On échantillonne donc avec un pas $r\,\Delta k$ au lieu de $\Delta k$. D'après
{eq}`eq-fov`, le FOV devient

```{math}
:label: eq-fov-eff
\text{FOV}_{\text{eff}} = \frac{1}{r\,\Delta k} = \frac{\text{FOV}}{r}.
```

Les copies de l'objet dans {eq}`eq-peigne` sont maintenant espacées de $\text{FOV}/r$ au
lieu de $\text{FOV}$. On remarque que pour $r = 1$, soit si on garde toutes les
lignes de l'espace des k on retrouve bien le FOV de départ sans repliement.

### Quand est-ce que ça replie ?

En combinant {eq}`eq-nyquist` et {eq}`eq-fov-eff`, il n'y a pas de repliement tant que

```{math}
:label: eq-rmax
r \le \frac{\text{FOV}}{L} ,
```

où $L$ est la taille de l'objet dans la direction sous-échantillonnée.

### Ce qui ne change pas

La résolution ne bouge pas, les lignes les plus éloignées du centre sont toujours là, donc $k_{\max}$ et $\Delta x$ restent les mêmes
{eq}`eq-resolution`. Cependant avec $r$ fois moins de mesures  le bruit augmente.

## Figure interactive

Fais varier le facteur de sous-échantillonnage (×1 à ×10) et regarde le repliement
apparaître.

:::{iframe} /figures/fig-sous-echantillonnage.html
:label: fig-sous-ech-embed
:class: kfig
:width: 100%
:placeholder: img/fig-sous-echantillonnage-static.png

Effet du sous-échantillonnage de l'espace des k le long de l'encodage de phase
(gauche-droite) sur l'image reconstruite (magnitude et phase de $-\pi$ à $\pi$), pour des
facteurs allant de ×1 (référence) à ×10.
:::

Voir [](#fig-sous-ech-embed). À ×1, on retrouve l'image de référence. Dès ×2, des copies de
la tête apparaissent, décalées le long de la direction de phase et superposées les unes aux
autres. Plus $r$ augmente, plus il y a de copies dans le FOV d'origine, puisqu'elles sont
espacées de $\text{FOV}/r$ {eq}`eq-fov-eff`.

## Interprétation

Le repliement apparaît parce que le FOV effectif {eq}`eq-fov-eff` devient plus petit que
l'objet {eq}`eq-rmax`. L'image devient alors une superposition de $r$ copies décalées de
$\text{FOV}/r$, seulement dans la direction sous-échantillonnée. La résolution, elle, ne
change pas, puisque $k_{\max}$ est conservé.

Pour retrouver le FOV sans perdre de résolution, il faudrait revenir à un $\Delta k$ plus
fin (donc acquérir toutes les lignes et y passer plus de temps).
