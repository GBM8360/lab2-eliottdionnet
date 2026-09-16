# MyST book template

A starting point for an interactive MyST book that builds and publishes itself to
GitHub Pages on every push.

Written for GBM8360E Laboratory 2, but there is nothing course-specific in it — reuse
it for any project that wants prose, executable notebooks and interactive figures in
one published site.

## Quick start

1. Click **Use this template** > name it `lab2-<your-github-username>`, set **Public**,
   owner `GBM8360`.

2. **The first Action run will fail. This is expected.** GitHub Pages is off by default
   on a new repository, and a workflow cannot switch it on for you — creating a Pages
   site needs *admin* rights, and the token a workflow gets only has *write*. So you do
   it once, by hand:

   > **Settings > Pages > Build and deployment > Source > GitHub Actions**

3. Re-run the build: **Actions** tab > click the failed run > **Re-run failed jobs**.

4. When it goes green, open `https://gbm8360.github.io/lab2-<your-username>/`.

From now on every push rebuilds and republishes automatically. Step 2 is a one-time
setup, not part of the normal loop.

Then work locally:

```bash
git clone https://github.com/GBM8360/lab2-<your-username>.git
cd lab2-<your-username>
conda create -n myst python=3.13 -y && conda activate myst
pip install -r requirements.txt
myst start                       # live preview at http://localhost:3000
```

Install everything into the **same** environment. If `myst` lives in one env and
`numpy`/`plotly` in another, `myst build --execute` launches a kernel that can't import
them, and the error points at your notebook rather than at the environment.

`pip install mystmd` brings MyST in without a separate Node install.

## What's here

```
myst.yml                     configuration: title, authors, TOC, bibliography, abbreviations
index.md                     landing page
01-getting-started.md        how to build, publish, and debug
02-interactive-figures.md    the interactive figure pattern + a worked example
notebooks/figure-demo.ipynb  the Plotly slider demo embedded in chapter 02
bibliography/references.bib  BibTeX entries
.github/workflows/deploy.yml the build-and-publish Action
requirements.txt             Python packages, used locally and in CI
```

## PDF

A separate `pdf` job builds a PDF on every push. Actions tab > a run > **Artifacts** >
`book-pdf`. It installs LaTeX so it is slower than the site build, and it is
non-blocking: a PDF failure never stops your website deploying.

Interactive figures appear in the PDF as static snapshots — each one emits both an
interactive and a PNG representation, and the renderer picks per medium. See
`01-getting-started.md`.

## Things to change first

- `myst.yml`: `title`, `authors`, `subtitle`
- `index.md`: the About section
- add your own pages as `.md` files and list them in `myst.yml`'s `toc`

## If the build fails

Actions tab > click the red run > expand the failed step; the real error is near the
bottom. `01-getting-started.md` lists the common ones. The two you are most likely to
hit first:

| Error in the log | Fix |
|---|---|
| `Create Pages site failed. Error: Resource not accessible by integration` | Pages isn't enabled yet — do step 2 above, then re-run |
| `Resource not accessible by integration` on **deploy**, with `Pages: read` in the job's token list | The organization has workflow permissions set to read-only. An org owner must set *Settings > Actions > General > Workflow permissions* to **Read and write** |

**Fallback:** if `myst build --html --execute` misbehaves in CI, drop `--execute` from
`.github/workflows/deploy.yml` and commit your notebooks with their outputs saved
instead. MyST will embed the saved outputs. The figures then only update when you
re-run the notebook yourself.
