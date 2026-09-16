---
title: Getting started
---

## Publish first, edit second

1. **Use this template** > name your repo `lab2-<your-github-username>`, set it
   **Public**, owner `GBM8360`.

2. **Turn on GitHub Pages — once.**

   :::{important} Your first build will fail, and that's expected
   Pages is off by default on a new repository. A workflow can't switch it on for you:
   creating a Pages site requires *admin* rights on the repo, and the token a workflow
   runs with only ever has *write*. So this one step is manual.

   **Settings > Pages > Build and deployment > Source > GitHub Actions**
   :::

3. **Re-run the build.** Actions tab > click the failed run > **Re-run failed jobs**.
   This time the workflow installs Python and Node, runs every notebook, builds the
   HTML, and publishes it.

4. Open `https://gbm8360.github.io/lab2-<your-username>/`.

5. Edit `index.md` on the GitHub website, commit, and watch it redeploy — no manual
   steps from here on.

You now have a published website. Everything after this is content.

## Working locally

```bash
git clone https://github.com/GBM8360/lab2-<your-username>.git
cd lab2-<your-username>
conda create -n myst python=3.13 -y && conda activate myst
pip install -r requirements.txt
myst start                       # live preview at http://localhost:3000
```

:::{warning} Use one environment for everything
`pip install -r requirements.txt` installs MyST *and* the packages your notebooks
import. If MyST ends up in a different environment from `numpy` and `plotly`, then
`myst build --execute` starts a kernel that can't import them — and the error will
point at your notebook instead of at the environment. The CI build uses Python 3.13
too, so a build that works locally works there.
:::

`myst start` opens a live-reloading preview: save a file, the browser updates. This is
much faster than pushing and waiting for the Action.

When you're happy:

```bash
git add -A && git commit -m "Add my k-space chapter" && git push
```

## What the repository contains

| Path | What it is |
|---|---|
| `myst.yml` | The whole configuration: title, authors, table of contents, bibliography, abbreviations |
| `index.md` | The landing page |
| `0*.md` | Content pages, listed in `myst.yml`'s `toc` |
| `notebooks/` | Jupyter notebooks whose outputs get embedded into the pages |
| `bibliography/references.bib` | BibTeX entries for `{cite:p}` |
| `.github/workflows/deploy.yml` | The GitHub Action that builds and publishes |
| `requirements.txt` | Python packages, installed both locally and in CI |

## What the GitHub Action does

It's worth reading `deploy.yml` once — it's short. On every push to `main`, GitHub
rents you a fresh Linux machine that:

1. checks out your repository
2. checks that Pages is configured (this is the step that fails until you've done the
   one-time setup above)
3. installs Python, your `requirements.txt`, Node, and `mystmd`
4. runs `myst build --html --execute` — the `--execute` flag **runs your notebooks**,
   so the published figures always match the code in the repo
5. uploads the result and deploys it to Pages

"It works on my machine" stops being an argument: if it builds here, it builds for
everyone.

## When the build fails

Go to the **Actions** tab, click the red run, and expand the failed step. The real
error is usually near the bottom of the log. Common ones:

| Symptom | Cause |
|---|---|
| `Create Pages site failed. Error: Resource not accessible by integration` | Pages isn't enabled yet. Do the one-time setup above, then re-run |
| Same error on the **deploy** step, and the job's token list shows `Pages: read` | The organization has workflow permissions set to read-only — an org owner must change *Settings > Actions > General > Workflow permissions* to **Read and write** |
| A figure is missing and the page shows nothing where it should be | The notebook isn't listed in `myst.yml`'s `toc`. MyST only builds files in the toc, so `:::{figure} #label` has nothing to embed — and it fails **silently** |
| `Could not find bibtex entry for key ...` | Citation key isn't in `bibliography/references.bib` |
| `Unknown target for cross reference` | `[](#label)` points at a label that doesn't exist |
| `No kernel named python3` | Notebook metadata expects a kernel that CI doesn't have — re-save from Jupyter |
| Figures missing on the site but fine locally | Notebook outputs weren't committed **and** `--execute` was removed |
| Site loads but CSS is broken | `BASE_URL` doesn't match the repository name |

## Exporting to PDF

`myst.yml` declares a PDF export, so the same source produces a website *and* a PDF.

**In CI:** a separate `pdf` job builds it on every push and attaches it to the run. Go to
the **Actions** tab > click a run > scroll to **Artifacts** > download `book-pdf`. That
job installs LaTeX, so it takes a few minutes longer than the website; it is marked
non-blocking, so if the PDF fails your site still publishes.

The export uses **Typst** with the `plain_typst_book` template. Two things about that
are worth knowing if you change it:

- **The template must be a *book* template.** MyST's default is an *article* template,
  which renders only one document — you get a title page and a single chapter, with no
  warning that the rest of your book was dropped.
- **Typst, not LaTeX.** MyST can render PDFs through either. LaTeX chokes on content
  that is perfectly valid MyST — admonitions nested inside numbered lists, some Unicode
  — and fails *partway*, silently truncating your book. Typst handles it, and installs
  as a single binary instead of a multi-gigabyte TeX distribution.

The export also lists its pages explicitly under `articles:`. Without that, it sweeps in
**every** built page — including notebooks, which reprint their entire source code and a
duplicate of the figure. The cost is that a new chapter must be added in two places:
`toc` (for the website) and `articles` (for the PDF).

**Locally:** `myst build --typst`, which needs the Typst CLI
(`conda install -c conda-forge typst`, or see [typst.app](https://typst.app)). You do not
need it for `myst start` or for the website.

:::{note} How interactive figures reach the PDF
A Plotly slider is JavaScript, so print can't run it. The template handles this by
having each figure emit **two representations at once**:

```python
pio.renderers.default = "plotly_mimetype+png"
```

The website uses the interactive one; the PDF uses a static PNG snapshot. The snapshot
shows whichever frame is visible by default, so pick that default to be the frame worth
printing.

Without the `+png` half, MyST warns `Figure with no non-caption content` and the PDF
gets a caption with nothing above it. This needs `kaleido` installed — it's in
`requirements.txt`.
:::
