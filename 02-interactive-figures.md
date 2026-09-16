---
title: Interactive figures
kernelspec:
  name: python3
  display_name: Python 3
---

## The pattern

An interactive figure lives in **two places**, and that separation is the point:

| Where | What it holds |
|---|---|
| `notebooks/figure-demo.ipynb` | the computation — a cell tagged `#| label: figDemo` |
| this page | the narrative — `:::{figure} #figDemo` with a caption and a label |

The caption, the number and the cross-reference belong to the *prose*, not the notebook.
So the figure renumbers itself when you insert another one above it, and you can refer
to it from anywhere as [](#demoPlot).

Here is the figure, embedded from the notebook:

:::{figure} #figDemo
:label: demoPlot
A sine wave whose frequency is set by the slider. This is Plotly's standard slider
example — replace it with something of your own.
:::

## A second example: animating an xarray dataset

The same idea, written as a `code-cell` in this page rather than embedded from a
notebook. This is Plotly's [animated `imshow` example](https://plotly.com/python/imshow/#animations-of-xarray-datasets),
verbatim — an `animation_frame` over the time axis of a labelled array, with the
colour window fixed by `zmin`/`zmax` so every frame is scaled the same way.

```{code-cell} python
:label: xarrayAnim
import plotly.express as px
import xarray as xr
# Load xarray from dataset included in the xarray tutorial
ds = xr.tutorial.open_dataset('air_temperature').air[:20]
fig = px.imshow(ds, animation_frame='time', zmin=220, zmax=300, color_continuous_scale='RdBu_r')
fig.show()
```

## How it actually works

Drag the slider. Notice how fast it responds: there is **no kernel** behind this page.
The notebook ran **once**, in GitHub Actions, when the site was built. Every frame you
can reach was computed then and shipped inside the HTML. The slider is plain JavaScript
choosing between them.

That is why this is free to host, can't go down, and will still work years from now.

> **Your slider is not computing. It's choosing.**

Which gives you the one real constraint: **you must precompute every frame the reader
can reach.** The sweep is part of the design. A slider can't answer a question you
didn't anticipate.

````{admonition} Click to see the code that made this figure
:class: tip, dropdown

The recipe is always the same:

1. add one trace per slider position, all with `visible=False`
2. turn one on as the default
3. build a `steps` list where each step flips exactly one trace visible

```python
import numpy as np
import plotly.graph_objects as go

fig = go.Figure()
for step in np.arange(0, 5, 0.1):
    fig.add_trace(go.Scatter(visible=False, name=f"v = {step:.1f}",
                             x=np.arange(0, 10, 0.01),
                             y=np.sin(step * np.arange(0, 10, 0.01))))
fig.data[10].visible = True

steps = []
for i in range(len(fig.data)):
    vis = [False] * len(fig.data)
    vis[i] = True
    steps.append(dict(method="update", args=[{"visible": vis}]))

fig.update_layout(sliders=[dict(active=10, steps=steps,
                                currentvalue={"prefix": "Frequency: "})])
```

Hiding source code in a dropdown like this keeps the page readable while staying fully
reproducible. The qMRI mOOC uses the same trick throughout.
````

## Making your own

Two practical notes:

**Keep the page light.** Every frame ships to the reader. A dozen slider positions of a
128×88 image is fine; two hundred at full precision is not. Rounding display values
(`np.round(z, 3)`, or casting an image to `uint8`) roughly halves the page size and
costs nothing visually.

**Emit a static fallback.** Set `pio.renderers.default = "plotly_mimetype+png"` once in
the notebook and every figure ships both an interactive version and a PNG. The website
uses the first, the PDF the second. The snapshot captures whichever frame is visible by
default — so make that default the frame you would have chosen if you only got one.

**Window your colours consistently.** If each frame auto-scales its own brightness, the
artifact you're trying to show gets normalised away as the reader drags. Fix the scale
once, from a reference frame, and apply it to all of them.

## Cross-references and citations

Cross-reference anything with a label: [](#demoPlot), or an equation like [](#eqDFT).

$$
S(k_x, k_y) = \iint \rho(x, y)\, e^{-i 2\pi (k_x x + k_y y)}\, dx\, dy
$$ (eqDFT)

Cite with `{cite:p}` and a key from `bibliography/references.bib`, like this
{cite:p}`Nishimura2010` or this {cite:p}`Larson2023`. The bibliography page builds
itself.

## An alternative: code directly in Markdown

You don't have to use `.ipynb`. MyST can execute a `code-cell` written straight into a
Markdown file, which means one file per chapter and much cleaner git diffs:

````
```{code-cell} python
:label: myFigure
import plotly.graph_objects as go
...
```
````

Either approach works. Notebooks match how the mOOC is built today; `code-cell` is
tidier to review. Pick one and be consistent.
