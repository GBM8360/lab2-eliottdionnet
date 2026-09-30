---
title: 3. Mouvement soudain du patient
description: Simulation d'une rotation soudaine de la tête pendant une acquisition cartésienne et artefacts résultants
---

## Introduction du problème

On suppose que pendant l'acquisition le patient tourne soudainement la tête de 20° puis
reste immobile. On simule ce mouvement et on interprète l'image résultante.

## Rappel théorique

D'après une propriété de la
[transformée de Fourier](https://fr.wikipedia.org/wiki/Transformation_de_Fourier) si
l'objet tourne d'un angle $\theta$ son espace des k tourne du même angle. Avec $R_\theta$
la matrice de rotation et $f_\theta(\mathbf r) = f(R_\theta^{-1}\mathbf r)$ l'objet tourné
on a

```{math}
:label: eq-rotation
F_\theta(\mathbf k) = F\big(R_\theta^{-1}\,\mathbf k\big).
```

Un mouvement soudain ne donne donc pas une image proprement tournée. Les colonnes acquises
avant le mouvement viennent de $F$ et celles d'après de $F_\theta$. L'image reconstruite
est la transformée inverse d'un espace des k hybride assemblé à partir de deux positions
différentes de la tête, puisque l'objet réel a changé de position pendant l'acquisition.

## Modèle

### Le k-espace hybride

Soit $W$ la fenêtre qui vaut 1 pour les colonnes acquises avant le mouvement et 0 pour les
autres. Elle ne dépend que de $k_y$. L'espace des k mesuré s'écrit

```{math}
:label: eq-hybride
K_{\text{mot}} = W \cdot K + (1 - W)\cdot K_\theta .
```

En repassant dans l'image on obtient une convolution notée $\circledast_y$ qui agit
uniquement le long de la phase puisque $W$ ne dépend que de $k_y$

```{math}
:label: eq-hybride-image
I_{\text{mot}} = I_\theta + w \circledast_y \big(I - I_\theta\big),
\qquad \text{où } w = \mathcal F^{-1}_y\{W\}.
```

L'artefact est donc la différence entre les deux positions de la tête étalée par le noyau
$w$ le long de la phase. Il est nul là où la tête n'a presque pas bougé
($I \approx I_\theta$) et rien ne s'étale le long de la lecture.

### Cas particulier du mouvement pile au milieu de l'acquisition

Si le mouvement a lieu au milieu de l'acquisition $W$ est une marche qui coupe l'espace des
k en $k_y = 0$. Sa transformée inverse fait apparaître la
[transformée de Hilbert](https://fr.wikipedia.org/wiki/Transformation_de_Hilbert)
$\mathcal H_y$ (noyau en $1/(\pi y)$) et on obtient

```{math}
:label: eq-hilbert
I_{\text{mot}} = \tfrac{1}{2}\big(I + I_\theta\big)
\;+\; \tfrac{i}{2}\,\mathcal H_y\big\{I_\theta - I\big\}.
```

On peut lire les deux termes séparément.

1. $\tfrac12(I + I_\theta)$ est une double exposition où les deux positions de la tête sont
   superposées à moitié d'intensité chacune.
2. $\tfrac{i}{2}\mathcal H_y\{I_\theta - I\}$ est la différence entre les deux positions
   étalée par un noyau en $1/y$. Ce noyau décroît lentement si bien que l'artefact ne reste
   pas collé aux bords qui ont bougé et s'étend loin le long de la phase.

### Cas général

Si la coupure n'est pas au centre la structure reste la même mais la répartition de
l'énergie entre les deux positions change beaucoup. L'[égalité de
Parseval](https://fr.wikipedia.org/wiki/%C3%89galit%C3%A9_de_Parseval) permet de lire
directement dans l'espace des k la part d'énergie mesurée avant le mouvement

```{math}
:label: eq-energie-avant
\eta(n_s) = \frac{\sum_{n < n_s}\sum_{u} |K[u, n]|^2}{\sum_{n}\sum_{u} |K[u, n]|^2}.
```


## Figure interactive

Le curseur choisit la ligne à laquelle le mouvement a lieu, donc l'instant du mouvement.
La première position montre l'image sans mouvement pour comparer.
Le trait rouge sépare dans l'espace des k les lignes acquises avant le mouvement
de celles acquises après.

:::{iframe} /figures/fig-mouvement.html
:label: fig-mouvement-embed
:class: kfig
:width: 100%
:placeholder: img/fig-mouvement-static.png

Rotation soudaine de 20° pendant une acquisition cartésienne. Espace des k hybride puis
magnitude et phase (de $-\pi$ à $\pi$) de l'image selon la ligne à laquelle le mouvement a
lieu.
:::

Voir [](#fig-mouvement-embed). Autour du centre on ne voit jamais une tête nettement
dédoublée ou franchement tournée.
## Interprétation

L'artefact est la différence entre les deux positions de la tête étalée le long de la
phase par le noyau $w$.

Quand le mouvement a lieu au centre {eq}`eq-hilbert` montre que l'image est la
superposition à parts égales des deux positions plus un terme qui étale leur différence.
Comme on l'a vu à la [page 1](./01-masquage.md) les basses fréquences portent l'essentiel
du contraste et les hautes fréquences les contours. C'est donc la position de la tête qui
possède ces basses fréquences qui impose le contraste, et l'autre n'apparaît plus qu'à
travers des contours et l'étalement.

## Correction de l'artefact

Un patient qui bouge, ça n'a rien de rare. Est-ce qu'on peut donc corriger l'artefact ou
est-ce qu'il faut relancer l'acquisition ?

Ici oui car on connaît tout à la fois l'angle $\theta$, l'instant de la rotation et son
centre. D'après {eq}`eq-rotation` les lignes acquises après le mouvement sont des mesures de
la tête d'origine prises aux points tournés $R_\theta^{-1}\mathbf k$. Il suffit de les
remettre à leur vraie place dans l'espace des k puis de reconstruire avec une transformée
de Fourier non uniforme.

En réalité cela semble cependant assez complexe pour plusieurs raisons :

- la tête peut basculer hors du plan de coupe et le tissu qui en sort ne peut pas être
  récupéré par une correction 2D ;
- le mouvement n'est pas instantané donc chaque ligne a sa propre position et son propre
  $\theta$ ;
- le centre de rotation est inconnu, il y a donc aussi une translation possible à prendre
  en compte.

## Et si le patient bougeait vraiment ?

Dans la réalité un patient ne tourne pas la tête d'un coup à un instant précis pour se
figer ensuite. La dernière figure simule donc un mouvement continu où chaque ligne est
acquise avec la tête à l'angle $\theta(t)$ du moment. L'angle maximal va jusqu'à 90° et on
peut choisir entre quatre mouvements. La rotation brusque fait tourner la tête en 0,2 s
autour de $t = 1{,}1$ s. La dérive lente la fait tourner doucement pendant toute
l'acquisition comme un patient qui se relâche. Le hochement la fait aller et venir à peu
près une fois par seconde. Le hochement asymétrique fait la même chose autour d'un centre
tiré au hasard, si bien que la tête penche plus d'un côté que de l'autre. Le bouton « autre
centre » en tire un nouveau.

Le bouton lance l'acquisition ligne par ligne. On suit en même temps la position de la tête,
l'espace des k qui se remplit et l'image qu'on obtiendrait en arrêtant l'acquisition à cet
instant.

:::{iframe} /figures/fig-mouvement-continu.html
:label: fig-mouvement-continu
:class: kfig kfig-live
:width: 100%
:placeholder: img/fig-mouvement-continu-static.png

Acquisition cartésienne d'une tête qui bouge pendant toute l'acquisition. Position de la
tête à l'instant $t$, espace des k acquis jusque-là et image reconstruite avec ces lignes.
:::
