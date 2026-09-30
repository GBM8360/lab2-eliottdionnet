# k-space Explorer — TP2 GBM8360E

Livre interactif MyST qui reprend l'exercice 3 du TP1 (masquage, sous-échantillonnage et
mouvement dans l'espace des k) avec des figures interactives et les équations dérivées en
entier. Le site est reconstruit et publié sur GitHub Pages à chaque push sur `main`.

Site : https://gbm8360.github.io/lab2-eliottdionnet/

## Travailler en local

```bash
conda create -n myst python=3.13 -y && conda activate myst
pip install -r requirements.txt mystmd
myst start --execute             # aperçu sur http://localhost:3000
```

Tout doit être installé dans le **même** environnement : si `myst` et `numpy`/`scipy` sont
dans deux environnements différents, l'exécution des notebooks échoue.

## Contenu

```
myst.yml                         configuration : titre, sigles, toc, feuille de style
index.md                         introduction + fondements (signal, DFT, FOV, résolution)
01-masquage.md                   page 1 : masquage du centre de l'espace des k
02-sous-echantillonnage.md       page 2 : sous-échantillonnage et repliement
03-mouvement.md                  page 3 : mouvement soudain du patient
notebooks/kspace_fig.py          fonctions partagées : chargement, reconstruction,
                                 génération des figures HTML interactives
notebooks/0x-*.ipynb             un notebook par page, qui produit sa figure
figures/fig-*.html               figures interactives (générées par les notebooks ;
                                 fig-masquage-centre.html recalcule l'image en direct)
img/*.png                        images statiques (intro + vignettes pour le PDF)
styles/figures.css               donne aux iframes une hauteur adaptée à leur largeur
bibliography/references.bib      références BibTeX
.github/workflows/deploy.yml     build + publication
```

## Comment les figures sont intégrées

Chaque notebook écrit une page HTML autonome dans `figures/` (Plotly + un curseur HTML),
copiée telle quelle dans le site grâce à `static_files` dans `myst.yml`, puis intégrée dans
la page par :

```markdown
:::{iframe} /figures/fig-masquage.html
:label: fig-masquage-embed
:class: kfig
:width: 100%
:placeholder: img/fig-masquage-static.png
Légende…
:::
```

- `:class: kfig` active `styles/figures.css`. Le thème MyST impose sinon à toute iframe
  une hauteur de 60 % de sa largeur, en ignorant la hauteur donnée dans le Markdown, ce qui
  rognait les figures.
- La page HTML occupe toute la hauteur de son cadre et Plotly ajuste les images pour
  qu'elles y tiennent : 3 panneaux côte à côte sur un écran large, onglets sur un
  téléphone.
- `:placeholder:` fournit l'image utilisée dans l'export PDF, où une iframe ne peut pas
  s'afficher.
- MyST ne réécrit pas le `src` d'une iframe. Sur GitHub Pages, le site est servi sous
  `/lab2-eliottdionnet/`, donc le workflow préfixe `/figures/` par `BASE_URL` avant le
  build (étape « Prefix iframe paths with BASE_URL »).

## Données

`kspace_combined.npy` : espace des k complexe combiné, forme `(128, 88)` =
(lecture antéro-postérieure, encodage de phase gauche-droite). Téléchargé automatiquement
depuis la release du laboratoire 1 s'il est absent de `notebooks/data/`.
