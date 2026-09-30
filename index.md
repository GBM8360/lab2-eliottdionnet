---
title: Introduction
description: Explication interactive de l'exercice 3 du TP1
---

## Pourquoi ce livre ?

Nous allons reprendre et détailler trois questions de l'exercice 3 du TP1. Au TP1 on
les avait traitées avec des images fixes ; ici chaque page a une figure interactive, ce
qui permet de voir l'effet apparaître petit à petit au lieu de juste le constater.

## Prérequis

Le lecteur doit être à l'aise avec les notions de base de la théorie de Fourier. Quand
un résultat classique est utilisé, on met un lien vers Wikipédia plutôt que de le
redémontrer.

## Plan du livre

Ce livre répond à trois questions, chacune sur sa propre page :

1. [](./01-masquage.md)
2. [](./02-sous-echantillonnage.md)
3. [](./03-mouvement.md)


L'axe horizontal des figures correspond la direction d'encodage de phase. La case  échelle fixe garde la même échelle de gris que l'image de
référence, ce qui permet de comparer les intensités d'une position du curseur à l'autre.

(sec-fondements)=
## Résolution et FOV

### Le FOV

Reconstruire l'image, c'est faire une
[transformée de Fourier discrète](https://fr.wikipedia.org/wiki/Transformation_de_Fourier_discr%C3%A8te)
inverse, l'image est une somme de termes en $e^{i2\pi\, u\,\Delta k\, x}$, avec $u$
entier. Si on remplace $x$ par $x + 1/\Delta k$, chaque terme est multiplié par
$e^{i2\pi u} = 1$. Donc :

```{math}
:label: eq-periodicite
\hat\rho\!\left(x + \frac{1}{\Delta k}\right) = \hat\rho(x)
\qquad\text{pour tout } x .
```

L'image reconstruite est périodique, de période $1/\Delta k$, on ne peut pas voir
plus loin que cette période sans voir l'image se répéter. Soit le FOV

```{math}
:label: eq-fov
\text{FOV} = \frac{1}{\Delta k}.
```

 Échantillonner l'espace des k tous les $\Delta k$, c'est le
multiplier par un [peigne de Dirac](https://fr.wikipedia.org/wiki/Peigne_de_Dirac). La
transformée inverse d'un peigne de pas $\Delta k$ est un peigne de pas $1/\Delta k$,
et un produit devient une
convolution :

```{math}
:label: eq-peigne
S(k)\sum_{u\in\mathbb Z}\delta(k - u\,\Delta k)
\;\xrightarrow{\;\mathcal F^{-1}\;}\;
\frac{1}{\Delta k}\sum_{p\in\mathbb Z}\rho\!\left(x - \frac{p}{\Delta k}\right).
```

L'image reconstruite est donc une somme de copies de l'objet, décalées de
$\text{FOV} = 1/\Delta k$. Si l'objet mesure $L$ dans cette direction, les copies ne se
chevauchent pas tant que

```{math}
:label: eq-nyquist
L \le \text{FOV} = \frac{1}{\Delta k}
\quad\Longleftrightarrow\quad
\Delta k \le \frac{1}{L}.
```

C'est le [critère de Nyquist](https://fr.wikipedia.org/wiki/Th%C3%A9or%C3%A8me_d'%C3%A9chantillonnage)
appliqué à l'espace des k. S'il n'est pas respecté, les copies se recouvrent (repliement spectral) [page 2](./02-sous-echantillonnage.md).

### La résolution

On ne mesure qu'un nombre fini $N$ de points, pour $|k| \le k_{\max} = N\Delta k/2$.
Cela revient à multiplier l'espace des k complet par une fenêtre rectangulaire de
largeur $N\Delta k$. L'image est l'objet vrai convolué par
la transformée inverse de cette fenêtre, un
[sinus cardinal](https://fr.wikipedia.org/wiki/Sinus_cardinal) :

```{math}
:label: eq-psf
\hat\rho = \rho \circledast h,
\qquad
h(x) = N\Delta k\;\operatorname{sinc}(N\Delta k\, x).
```

Un point de l'objet devient un sinc dont les premiers zéros sont en
$x = \pm 1/(N\Delta k)$. Deux points plus proches que ça se confondent :

```{math}
:label: eq-resolution
\Delta x = \frac{1}{N\,\Delta k} = \frac{\text{FOV}}{N} = \frac{1}{2\,k_{\max}}.
```



:::{important} Les deux règles à retenir pour la suite
- L'espacement $\Delta k$ entre les échantillons fixe le FOV {eq}`eq-fov`.
- L'étendue $N\Delta k = 2k_{\max}$ couverte fixe la résolution {eq}`eq-resolution`.
:::

## Afficher l'espace des k : linéaire ou logarithmique ?

La [](#fig-lin-vs-log) montre la même donnée deux fois : à gauche la magnitude brute
$|K|$ en échelle linéaire, à droite en échelle logarithmique.

:::{figure} img/kspace-lin-vs-log.png
:label: fig-lin-vs-log
:width: 80%

Magnitude de l'espace des k combiné, en échelle linéaire (gauche) et logarithmique
(droite).
:::

En échelle linéaire, l'image paraît presque entièrement noire, avec juste un petit point
brillant au centre. C'est normal : le centre de l'espace des k est la somme de tout le
signal de l'image, alors que les points en périphérie ( contours,
textures) portent beaucoup moins d'énergie. Sur ce jeu de données, la plus grande valeur
est environ 30 000 fois la plus petite. Un affichage linéaire donne donc presque toute la
dynamique à quelques pixels centraux, et les autres valeurs tombent dans le niveau 0 ou 1
sur 255, elles apparaissent noires.

L'affichage logarithmique utilise

```{math}
:label: eq-log
D[u, v] = \ln\big(|K[u, v]| + \varepsilon\big),
```

où $\varepsilon$ est la plus petite valeur non nulle de $|K|$ (problème de log(0)). Le logarithme écrase la dynamique, un
facteur 30 000 ne fait plus qu'un écart d'environ 10, et la structure de l'espace des k
devient visible.

:::{important} Attention
Le passage au log est purement un choix d'affichage : il ne modifie ni les données ni la
reconstruction.
:::
