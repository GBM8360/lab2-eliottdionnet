"""Chargement, reconstruction et figures HTML interactives (intégrées via {iframe})."""

import base64
import json
import os
import urllib.request
import zipfile

import numpy as np

DATA_DIR = "data"
NPY_PATH = os.path.join(DATA_DIR, "kspace_combined.npy")
RELEASE_URL = (
    "https://github.com/GBM8360/laboratory_1/releases/download/v0.1/"
    "subject-02_raw_kspace.zip"
)

N_RO, N_PE = 128, 88
TR_MS = 25.0  # temps entre deux lignes de phase


def load_kspace():
    """K combiné (128, 88) = (lecture, phase), téléchargé si absent."""
    if not os.path.exists(NPY_PATH):
        os.makedirs(DATA_DIR, exist_ok=True)
        zip_path = os.path.join(DATA_DIR, "subject-02_raw_kspace.zip")
        urllib.request.urlretrieve(RELEASE_URL, zip_path)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(DATA_DIR)
        for root, _, files in os.walk(DATA_DIR):
            if "kspace_combined.npy" in files:
                src = os.path.join(root, "kspace_combined.npy")
                if src != NPY_PATH:
                    os.replace(src, NPY_PATH)
                break
    return np.load(NPY_PATH)


def ifft2c(K):
    """k -> image (DC au centre du tableau)."""
    return np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(K)))


def fft2c(I):
    """image -> k."""
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(I)))


def log_mag(K):
    """log(|K| + eps), eps = plus petite valeur non nulle."""
    m = np.abs(K)
    eps = m[m > 0].min() if np.any(m > 0) else 1e-6
    return np.log(m + eps)


def _q8(arr, lo=None, hi=None):
    # 8 bits + base64 : ~5x plus léger que du JSON
    lo = float(arr.min()) if lo is None else float(lo)
    hi = float(arr.max()) if hi is None else float(hi)
    if hi <= lo:
        hi = lo + 1e-9
    q = np.clip((arr - lo) / (hi - lo) * 255, 0, 255).round().astype(np.uint8)
    return [base64.b64encode(q.tobytes()).decode("ascii"), lo, hi]


def make_frame(K_mod, label, kshapes=None):
    I = ifft2c(K_mod)
    return {
        "k": _q8(log_mag(K_mod)),
        "img": _q8(np.abs(I)),
        "ph": _q8(np.angle(I), -np.pi, np.pi),
        "label": label,
        "shapes": kshapes or [],
    }


# --- HTML / JS communs ---
_HEAD = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; }
  body {
    display: flex; flex-direction: column; overflow: hidden;
    font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    color: #1f2328; background: #fff; touch-action: pan-y;
    padding: 8px 10px 6px 10px;
  }
  .top { flex: 0 0 auto; }
  .row { display: flex; justify-content: space-between; align-items: baseline;
         gap: 10px; flex-wrap: wrap; font-size: 14px; }
  .row b, .ctl b { font-variant-numeric: tabular-nums; }
  .chk { font-size: 13px; color: #57606a; white-space: nowrap; cursor: pointer; }
  input[type=range] { width: 100%; margin: 6px 0 8px 0; }
  .ctls { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px 16px; }
  .ctl { font-size: 13px; }
  .btn { padding: 4px 12px; font-size: 13px; border: 1px solid #d0d7de; border-radius: 6px;
         background: #f6f8fa; cursor: pointer; color: #1f2328; }
  .btn.on { background: #1f2328; color: #fff; border-color: #1f2328; }
  .tabs { display: none; gap: 6px; margin-bottom: 6px; }
  .tab { flex: 1; padding: 6px 4px; font-size: 13px; border: 1px solid #d0d7de;
         background: #f6f8fa; border-radius: 6px; cursor: pointer; color: #1f2328; }
  .tab.on { background: #1f2328; color: #fff; border-color: #1f2328; }
  .panels { flex: 1 1 auto; min-height: 0; display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
  .panel { min-height: 0; display: flex; flex-direction: column; }
  .ptitle { flex: 0 0 auto; font-size: 13px; text-align: center; color: #57606a;
            padding-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .plot { flex: 1 1 auto; min-height: 0; position: relative; }
  .plot > div { position: absolute; inset: 0; }
  @media (max-width: 599px) {
    .tabs { display: flex; }
    .ctls { grid-template-columns: minmax(0, 1fr); }
    .panels { grid-template-columns: minmax(0, 1fr); }
    .panel { display: none; }
    .panel.on { display: flex; }
  }
</style>
</head>
<body>
"""

_PANELS = r"""
<div class="panels">
  <div class="panel on"><div class="ptitle">__TITLE_K__</div><div class="plot"><div id="pk"></div></div></div>
  <div class="panel"><div class="ptitle">|image| (magnitude)</div><div class="plot"><div id="pi"></div></div></div>
  <div class="panel"><div class="ptitle">phase(image), de −π à π</div><div class="plot"><div id="pp"></div></div></div>
</div>
"""

_TABS = r"""
  <div class="tabs">
    <button class="tab on" data-i="0">Espace des k</button>
    <button class="tab" data-i="1">|image|</button>
    <button class="tab" data-i="2">Phase</button>
  </div>
"""

_JS_COMMON = r"""
const GRAY = [[0, "rgb(0,0,0)"], [1, "rgb(255,255,255)"]];
const PHASE_CS = [[0.0,"rgb(5,48,97)"],[0.25,"rgb(67,147,195)"],[0.5,"rgb(247,247,247)"],
                  [0.75,"rgb(214,96,77)"],[1.0,"rgb(103,0,31)"]];
const PHASE_BAR = {thickness: 12, len: 0.9, outlinewidth: 0, x: 1.02, xpad: 0,
                   tickvals: [-Math.PI, -Math.PI / 2, 0, Math.PI / 2, Math.PI],
                   ticktext: ["−π", "−π/2", "0", "π/2", "π"], tickfont: {size: 11}};
const CFG = {responsive: true, displayModeBar: false, scrollZoom: false, doubleClick: false};

function layout(shapes, right) {
  return {
    autosize: true, margin: {t: 0, b: 0, l: 0, r: right || 0},
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", dragmode: false,
    xaxis: {visible: false, fixedrange: true, constrain: "domain"},
    yaxis: {visible: false, fixedrange: true, scaleanchor: "x", scaleratio: 1,
            autorange: "reversed", constrain: "domain"},
    shapes: shapes || []
  };
}
function hm(z, cs, w) {
  return {type: "heatmap", z: z, colorscale: cs, zmin: w[0], zmax: w[1],
          zsmooth: false, showscale: false, hoverinfo: "skip"};
}
function hmPhase(z) {
  return Object.assign(hm(z, PHASE_CS, [-Math.PI, Math.PI]), {showscale: true, colorbar: PHASE_BAR});
}
let first = true;
function plot3(tk, ti, tp, shapes) {
  const how = first ? "newPlot" : "react";
  Plotly[how]("pk", [tk], layout(shapes), CFG);
  Plotly[how]("pi", [ti], layout(), CFG);
  Plotly[how]("pp", [tp], layout(null, 52), CFG);
  first = false;
}
document.querySelectorAll(".tab").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(b => b.classList.remove("on"));
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("on"));
  btn.classList.add("on");
  document.querySelectorAll(".panel")[+btn.dataset.i].classList.add("on");
  ["pk", "pi", "pp"].forEach(id => Plotly.Plots.resize(id));
}));
"""

# --- figure à frames précalculées ---
_HTML = _HEAD + r"""
<div class="top">
  <div class="row">
    <span>__SLIDER_NAME__ : <b id="val"></b></span>
    <label class="chk"><input type="checkbox" id="fixed"> échelle fixe (réf.)</label>
  </div>
  <input type="range" id="slider" min="0" max="__NMAX__" step="1" value="__ACTIVE__"
         aria-label="__SLIDER_NAME__">
""" + _TABS + "</div>" + _PANELS + r"""
<script>
const NY = __NY__, NX = __NX__;
const KEYS = __KEYS__;
const FRAMES = __FRAMES__;
const REF = FRAMES[KEYS[__REF__]];
""" + _JS_COMMON + r"""
function decode(e) {
  const b = atob(e[0]), lo = e[1], s = (e[2] - e[1]) / 255, z = new Array(NY);
  let i = 0;
  for (let r = 0; r < NY; r++) {
    const row = new Array(NX);
    for (let c = 0; c < NX; c++) row[c] = lo + b.charCodeAt(i++) * s;
    z[r] = row;
  }
  return z;
}
const fixed = document.getElementById("fixed");
const slider = document.getElementById("slider");
function win(f, key) {
  return fixed.checked ? [REF[key][1], REF[key][2]] : [f[key][1], f[key][2]];
}
function draw() {
  const f = FRAMES[KEYS[+slider.value]];
  document.getElementById("val").innerHTML = f.label;
  plot3(hm(decode(f.k), GRAY, win(f, "k")),
        hm(decode(f.img), GRAY, win(f, "img")),
        hmPhase(decode(f.ph)), f.shapes);
}
slider.addEventListener("input", draw);
fixed.addEventListener("change", draw);
draw();
</script>
</body>
</html>
"""


def _write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return len(html) / 1e6


def write_figure(path, frames, *, slider_name, title_k, active=0, ref=0):
    keys = [str(i) for i in range(len(frames))]
    html = (
        _HTML.replace("__SLIDER_NAME__", slider_name)
        .replace("__TITLE_K__", title_k)
        .replace("__NMAX__", str(len(frames) - 1))
        .replace("__ACTIVE__", str(active))
        .replace("__REF__", str(ref))
        .replace("__NY__", str(N_RO))
        .replace("__NX__", str(N_PE))
        .replace("__KEYS__", json.dumps(keys))
        .replace("__FRAMES__", json.dumps(dict(zip(keys, frames)), separators=(",", ":")))
    )
    return _write(path, html)


# --- masque déplaçable, reconstruction dans le navigateur ---
_HTML_LIVE = _HEAD + r"""
<div class="top">
  <div class="ctls">
    <div class="ctl">Taille du masque : <b id="vf"></b>
      <input type="range" id="sf" min="0" max="90" step="1" value="__F0__"></div>
    <div class="ctl">Centre en lecture (↕) : <b id="vy"></b>
      <input type="range" id="sy" min="-60" max="60" step="1" value="__Y0__"></div>
    <div class="ctl">Centre en phase (↔) : <b id="vx"></b>
      <input type="range" id="sx" min="-40" max="40" step="1" value="__X0__"></div>
  </div>
  <div class="row" style="margin-bottom:6px">
    <button class="btn" id="play">▶ Animer</button>
    <label class="chk"><input type="checkbox" id="fixed"> échelle fixe (réf.)</label>
  </div>
""" + _TABS + "</div>" + _PANELS.replace("__TITLE_K__", "log|K| masqué") + r"""
<script>
const N0 = __N0__, N1 = __N1__, C0 = N0 / 2, C1 = N1 / 2;

const raw = Uint8Array.from(atob("__K__"), c => c.charCodeAt(0));
const KF = new Float32Array(raw.buffer);
const KR = new Float32Array(N0 * N1), KI = new Float32Array(N0 * N1);
for (let i = 0; i < N0 * N1; i++) { KR[i] = KF[2 * i]; KI[i] = KF[2 * i + 1]; }

const LOGEPS = __LOGEPS__;
const LOGK = new Float32Array(N0 * N1);
let lkmin = Infinity, lkmax = -Infinity;
for (let i = 0; i < N0 * N1; i++) {
  LOGK[i] = Math.log(Math.hypot(KR[i], KI[i]) + Math.exp(LOGEPS));
  lkmin = Math.min(lkmin, LOGK[i]); lkmax = Math.max(lkmax, LOGK[i]);
}

// DFT centrée (convention fftshift/ifftshift)
function table(N, C) {
  const c = new Float32Array(N * N), s = new Float32Array(N * N);
  for (let a = 0; a < N; a++) for (let b = 0; b < N; b++) {
    const ph = 2 * Math.PI * (((a - C) * (b - C)) % N) / N;
    c[a * N + b] = Math.cos(ph); s[a * N + b] = Math.sin(ph);
  }
  return [c, s];
}
const [C0t, S0t] = table(N0, C0), [C1t, S1t] = table(N1, C1);
const TR = new Float32Array(N0 * N1), TI = new Float32Array(N0 * N1);

function reconstruct(r0, r1, c0, c1) {
  for (let a = 0; a < N0; a++) {
    const inRow = a >= r0 && a < r1;
    for (let q = 0; q < N1; q++) {
      let sr = 0, si = 0;
      for (let b = 0; b < N1; b++) {
        if (inRow && b >= c0 && b < c1) continue;   // point masqué
        const kr = KR[a * N1 + b], ki = KI[a * N1 + b];
        const cr = C1t[b * N1 + q], ci = S1t[b * N1 + q];
        sr += kr * cr - ki * ci; si += kr * ci + ki * cr;
      }
      TR[a * N1 + q] = sr; TI[a * N1 + q] = si;
    }
  }
  const mag = new Array(N0), pha = new Array(N0);
  let mmax = 0;
  for (let p = 0; p < N0; p++) { mag[p] = new Array(N1); pha[p] = new Array(N1); }
  for (let q = 0; q < N1; q++) {
    for (let p = 0; p < N0; p++) {
      let sr = 0, si = 0;
      for (let a = 0; a < N0; a++) {
        const tr = TR[a * N1 + q], ti = TI[a * N1 + q];
        const cr = C0t[a * N0 + p], ci = S0t[a * N0 + p];
        sr += tr * cr - ti * ci; si += tr * ci + ti * cr;
      }
      const m = Math.hypot(sr, si) / (N0 * N1);
      mag[p][q] = m; pha[p][q] = Math.atan2(si, sr);
      if (m > mmax) mmax = m;
    }
  }
  return [mag, pha, mmax];
}
""" + _JS_COMMON + r"""
const sf = document.getElementById("sf"), sy = document.getElementById("sy"),
      sx = document.getElementById("sx"), fixed = document.getElementById("fixed");
const REFMAX = reconstruct(0, 0, 0, 0)[2];   // max de l'image sans masque

function draw() {
  const f = +sf.value, dy = +sy.value, dx = +sx.value;
  const h0 = Math.floor(C0 * f / 100), h1 = Math.floor(C1 * f / 100);
  const r0 = Math.max(0, C0 + dy - h0), r1 = Math.min(N0, C0 + dy + h0);
  const c0 = Math.max(0, C1 + dx - h1), c1 = Math.min(N1, C1 + dx + h1);
  const on = h0 > 0 && h1 > 0;
  document.getElementById("vf").textContent = f + " %";
  document.getElementById("vy").textContent = (dy > 0 ? "+" : "") + dy + " lignes";
  document.getElementById("vx").textContent = (dx > 0 ? "+" : "") + dx + " colonnes";

  const [mag, pha, mmax] = on ? reconstruct(r0, r1, c0, c1) : reconstruct(0, 0, 0, 0);
  const lk = new Array(N0);
  for (let a = 0; a < N0; a++) {
    lk[a] = new Array(N1);
    for (let b = 0; b < N1; b++)
      lk[a][b] = (on && a >= r0 && a < r1 && b >= c0 && b < c1) ? LOGEPS : LOGK[a * N1 + b];
  }
  const shapes = on ? [{type: "rect", x0: c0 - 0.5, x1: c1 - 0.5, y0: r0 - 0.5, y1: r1 - 0.5,
                        line: {color: "rgb(220,50,47)", width: 1.5}}] : [];
  plot3(hm(lk, GRAY, [lkmin, lkmax]),
        hm(mag, GRAY, [0, fixed.checked ? REFMAX : mmax]),
        hmPhase(pha), shapes);
}

let pending = false;
function request() {
  if (pending) return;
  pending = true;
  requestAnimationFrame(() => { pending = false; draw(); });
}
[sf, sy, sx].forEach(s => s.addEventListener("input", request));
fixed.addEventListener("change", request);

const play = document.getElementById("play");
let t = 0, timer = null;
play.addEventListener("click", () => {
  if (timer) {
    clearInterval(timer); timer = null;
    play.textContent = "▶ Animer"; play.classList.remove("on");
    return;
  }
  if (+sf.value === 0) sf.value = 15;
  play.textContent = "⏸ Pause"; play.classList.add("on");
  timer = setInterval(() => {
    t += 0.08;
    sy.value = Math.round(40 * Math.sin(t));
    sx.value = Math.round(28 * Math.cos(t));
    request();
  }, 60);
});
draw();
</script>
</body>
</html>
"""


def write_live_mask(path, K, *, f0=15, y0=20, x0=10):
    k32 = np.empty(K.size * 2, dtype=np.float32)
    k32[0::2] = K.real.ravel()
    k32[1::2] = K.imag.ravel()
    m = np.abs(K)
    html = (
        _HTML_LIVE.replace("__N0__", str(K.shape[0]))
        .replace("__N1__", str(K.shape[1]))
        .replace("__K__", base64.b64encode(k32.tobytes()).decode("ascii"))
        .replace("__LOGEPS__", repr(float(np.log(m[m > 0].min()))))
        .replace("__F0__", str(f0))
        .replace("__Y0__", str(y0))
        .replace("__X0__", str(x0))
    )
    return _write(path, html)


# --- mouvement continu, rotations faites dans le navigateur ---
_HTML_ANIM = _HEAD + r"""
<div class="top">
  <div class="ctls">
    <div class="ctl">Mouvement :
      <select id="prof" style="width:100%;margin:6px 0 8px 0;font-size:13px">
        <option value="soudain">rotation brusque au milieu</option>
        <option value="derive">dérive lente</option>
        <option value="oscill">hochement</option>
        <option value="asym">hochement asymétrique</option>
      </select></div>
    <div class="ctl">Angle maximal : <b id="vth"></b>
      <input type="range" id="sth" min="0" max="90" step="1" value="20"></div>
    <div class="ctl">Lignes acquises : <b id="vn"></b>
      <input type="range" id="sn" min="0" max="__N1__" step="1" value="__N1__"></div>
  </div>
  <div class="row" style="margin-bottom:6px">
    <span>
      <button class="btn" id="play">▶ Lancer l'acquisition</button>
      <button class="btn" id="dice" style="display:none">🎲 autre centre</button>
    </span>
    <span id="state" style="font-size:13px;color:#57606a"></span>
  </div>
  <div class="tabs">
    <button class="tab on" data-i="0">Patient</button>
    <button class="tab" data-i="1">Espace des k</button>
    <button class="tab" data-i="2">Image</button>
  </div>
</div>
<div class="panels">
  <div class="panel on"><div class="ptitle">position de la tête</div><div class="plot"><div id="pk"></div></div></div>
  <div class="panel"><div class="ptitle">log|K| acquis</div><div class="plot"><div id="pi"></div></div></div>
  <div class="panel"><div class="ptitle">image reconstruite</div><div class="plot"><div id="pp"></div></div></div>
</div>
<script>
const N0 = __N0__, N1 = __N1__, C0 = N0 / 2, C1 = N1 / 2;
const TR = __TR__, T = N1 * TR;               // secondes par ligne, durée totale
const LOGEPS = __LOGEPS__, LKMAX = __LKMAX__, REFMAX = __REFMAX__;

const raw = new Float32Array(Uint8Array.from(atob("__I__"), c => c.charCodeAt(0)).buffer);
const IMR = new Float32Array(N0 * N1), IMI = new Float32Array(N0 * N1), IMA = new Float32Array(N0 * N1);
for (let i = 0; i < N0 * N1; i++) { IMR[i] = raw[2 * i]; IMI[i] = raw[2 * i + 1]; IMA[i] = Math.hypot(IMR[i], IMI[i]); }

function table(N, C) {
  const c = new Float32Array(N * N), s = new Float32Array(N * N);
  for (let a = 0; a < N; a++) for (let b = 0; b < N; b++) {
    const ph = 2 * Math.PI * (((a - C) * (b - C)) % N) / N;
    c[a * N + b] = Math.cos(ph); s[a * N + b] = Math.sin(ph);
  }
  return [c, s];
}
const [C0t, S0t] = table(N0, C0), [C1t, S1t] = table(N1, C1);

// rotation bilinéaire autour du centre (= scipy.ndimage.rotate, order=1)
const RC0 = (N0 - 1) / 2, RC1 = (N1 - 1) / 2;
function rotateInto(src, deg, out) {
  const t = deg * Math.PI / 180, c = Math.cos(t), s = Math.sin(t);
  for (let i = 0; i < N0; i++) for (let j = 0; j < N1; j++) {
    const y = i - RC0, x = j - RC1;
    const ys = c * y + s * x + RC0, xs = -s * y + c * x + RC1;
    let v = 0;
    if (ys >= 0 && ys <= N0 - 1 && xs >= 0 && xs <= N1 - 1) {
      const y0 = Math.min(Math.floor(ys), N0 - 2), x0 = Math.min(Math.floor(xs), N1 - 2);
      const fy = ys - y0, fx = xs - x0, k = y0 * N1 + x0;
      v = (1 - fy) * ((1 - fx) * src[k] + fx * src[k + 1])
        + fy * ((1 - fx) * src[k + N1] + fx * src[k + N1 + 1]);
    }
    out[i * N1 + j] = v;
  }
}

let centre = 0;                               // centre du hochement asymétrique
function theta(t, prof, amp) {
  if (prof === "soudain") {                   // la tête tourne en ~0,2 s autour de t = T/2
    const x = Math.min(1, Math.max(0, (t - (T / 2 - 0.1)) / 0.2));
    return amp * x * x * (3 - 2 * x);
  }
  if (prof === "derive") return amp * t / T;             // tourne doucement tout du long
  const osc = amp * Math.sin(2 * Math.PI * t / 1.1);     // ~1 aller-retour par seconde
  if (prof === "oscill") return osc;
  return Math.max(-amp, Math.min(amp, centre + osc));
}
function newCentre() {
  const amp = +sth.value;
  centre = Math.round((Math.random() - 0.5) * amp);      // entre -amp/2 et +amp/2
}

// ligne b : on tourne l'image, on calcule la colonne b de K et sa contribution G_b à l'image
const HKR = new Float32Array(N0 * N1), HKI = new Float32Array(N0 * N1);
const GR = new Float32Array(N1 * N0), GI = new Float32Array(N1 * N0);
const IR = new Float32Array(N0 * N1), II = new Float32Array(N0 * N1);
const RR = new Float32Array(N0 * N1), RI = new Float32Array(N0 * N1);
const sR = new Float32Array(N0), sI = new Float32Array(N0), kR = new Float32Array(N0), kI = new Float32Array(N0);
let nDone = 0, lastAngle = null;

function rebuild() {
  const p = prof.value, amp = +sth.value;
  lastAngle = null;
  for (let b = 0; b < N1; b++) {
    const th = theta(b * TR, p, amp);
    if (th !== lastAngle) { rotateInto(IMR, th, RR); rotateInto(IMI, th, RI); lastAngle = th; }
    for (let i = 0; i < N0; i++) {
      let ar = 0, ai = 0;
      for (let j = 0; j < N1; j++) {
        const cr = C1t[b * N1 + j], ci = -S1t[b * N1 + j];      // exp(-i ...)
        const xr = RR[i * N1 + j], xi = RI[i * N1 + j];
        ar += xr * cr - xi * ci; ai += xr * ci + xi * cr;
      }
      sR[i] = ar; sI[i] = ai;
    }
    for (let a = 0; a < N0; a++) {
      let ar = 0, ai = 0;
      for (let i = 0; i < N0; i++) {
        const cr = C0t[a * N0 + i], ci = -S0t[a * N0 + i];
        ar += sR[i] * cr - sI[i] * ci; ai += sR[i] * ci + sI[i] * cr;
      }
      kR[a] = ar; kI[a] = ai; HKR[a * N1 + b] = ar; HKI[a * N1 + b] = ai;
    }
    for (let q = 0; q < N0; q++) {
      let ar = 0, ai = 0;
      for (let a = 0; a < N0; a++) {
        const cr = C0t[a * N0 + q], ci = S0t[a * N0 + q];
        ar += kR[a] * cr - kI[a] * ci; ai += kR[a] * ci + kI[a] * cr;
      }
      GR[b * N0 + q] = ar; GI[b * N0 + q] = ai;
    }
  }
  IR.fill(0); II.fill(0); nDone = 0;
}
function addColumn(b, sign) {
  for (let p = 0; p < N0; p++) {
    const gr = GR[b * N0 + p], gi = GI[b * N0 + p];
    for (let q = 0; q < N1; q++) {
      const cr = C1t[b * N1 + q], ci = S1t[b * N1 + q];
      IR[p * N1 + q] += sign * (gr * cr - gi * ci);
      II[p * N1 + q] += sign * (gr * ci + gi * cr);
    }
  }
}
function goTo(n) {                           // on ajoute ou retire des lignes jusqu'à n
  while (nDone < n) addColumn(nDone++, 1);
  while (nDone > n) addColumn(--nDone, -1);
}
""" + _JS_COMMON + r"""
const sn = document.getElementById("sn"), sth = document.getElementById("sth"),
      prof = document.getElementById("prof"), play = document.getElementById("play"),
      dice = document.getElementById("dice");
const HEAD = new Float32Array(N0 * N1);

function draw() {
  const n = +sn.value;
  goTo(n);
  const t = n * TR, th = theta(Math.max(0, n - 1) * TR, prof.value, +sth.value);
  document.getElementById("vth").textContent = sth.value + "°";
  document.getElementById("vn").textContent = n + " / " + N1;
  document.getElementById("state").textContent =
    (prof.value === "asym" ? "centre " + centre + "° · " : "") +
    "t = " + t.toFixed(2).replace(".", ",") + " s · θ = " + Math.round(th) + "°";

  rotateInto(IMA, th, HEAD);
  const head = new Array(N0), lk = new Array(N0), img = new Array(N0);
  for (let a = 0; a < N0; a++) {
    head[a] = new Array(N1); lk[a] = new Array(N1); img[a] = new Array(N1);
    for (let b = 0; b < N1; b++) {
      head[a][b] = HEAD[a * N1 + b];
      lk[a][b] = b < n ? Math.log(Math.hypot(HKR[a * N1 + b], HKI[a * N1 + b]) + Math.exp(LOGEPS)) : LOGEPS;
      img[a][b] = Math.hypot(IR[a * N1 + b], II[a * N1 + b]) / (N0 * N1);
    }
  }
  const line = n > 0 && n < N1 ? [{type: "line", x0: n - 0.5, x1: n - 0.5, y0: -0.5, y1: N0 - 0.5,
                                  line: {color: "rgb(220,50,47)", width: 2}}] : [];
  const how = first ? "newPlot" : "react";
  Plotly[how]("pk", [hm(head, GRAY, [0, REFMAX])], layout(), CFG);
  Plotly[how]("pi", [hm(lk, GRAY, [LOGEPS, LKMAX])], layout(line), CFG);
  Plotly[how]("pp", [hm(img, GRAY, [0, REFMAX])], layout(), CFG);
  first = false;
}

let pending = false;
function request() {
  if (pending) return;
  pending = true;
  requestAnimationFrame(() => { pending = false; draw(); });
}
function reset() { rebuild(); request(); }
prof.addEventListener("change", () => {
  dice.style.display = prof.value === "asym" ? "" : "none";
  if (prof.value === "asym") newCentre();
  reset();
});
sth.addEventListener("input", () => { if (prof.value === "asym") newCentre(); reset(); });
dice.addEventListener("click", () => { newCentre(); reset(); });
sn.addEventListener("input", request);

let timer = null;
function stop() { clearInterval(timer); timer = null; play.textContent = "▶ Lancer l'acquisition"; play.classList.remove("on"); }
play.addEventListener("click", () => {
  if (timer) { stop(); return; }
  if (+sn.value >= N1) sn.value = 0;
  play.textContent = "⏸ Pause"; play.classList.add("on");
  timer = setInterval(() => {
    if (+sn.value >= N1) { stop(); return; }
    sn.value = +sn.value + 1;
    request();
  }, 50);
});
rebuild();
draw();
</script>
</body>
</html>
"""


def write_motion_anim(path, K):
    I = ifft2c(K)
    i32 = np.empty(I.size * 2, dtype=np.float32)
    i32[0::2] = I.real.ravel()
    i32[1::2] = I.imag.ravel()
    m = np.abs(K)
    html = (
        _HTML_ANIM.replace("__N0__", str(K.shape[0]))
        .replace("__N1__", str(K.shape[1]))
        .replace("__TR__", repr(TR_MS / 1000))
        .replace("__LOGEPS__", repr(float(np.log(m[m > 0].min()))))
        .replace("__LKMAX__", repr(float(np.log(m.max()))))
        .replace("__REFMAX__", repr(float(np.abs(I).max())))
        .replace("__I__", base64.b64encode(i32.tobytes()).decode("ascii"))
    )
    return _write(path, html)


def write_static(path, panels):
    """Vignette PNG pour le PDF : une ligne log|K| / |image| / phase par (titre, K)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(panels)
    fig, axs = plt.subplots(n, 3, figsize=(7.5, 3.6 * n), squeeze=False)
    for r, (title, Km) in enumerate(panels):
        I = ifft2c(Km)
        axs[r, 0].imshow(log_mag(Km), cmap="gray")
        axs[r, 1].imshow(np.abs(I), cmap="gray")
        im = axs[r, 2].imshow(np.angle(I), cmap="RdBu_r", vmin=-np.pi, vmax=np.pi)
        cb = fig.colorbar(im, ax=axs[r, 2], fraction=0.07, pad=0.03)
        cb.set_ticks([-np.pi, 0, np.pi])
        cb.set_ticklabels(["−π", "0", "π"])
        for c, t in enumerate(["log|K|", "|image|", "phase"]):
            axs[r, c].set_title(f"{title} — {t}" if c == 0 and title else t, fontsize=9)
            axs[r, c].axis("off")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
