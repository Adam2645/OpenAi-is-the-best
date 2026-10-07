"""Iteracja 26 — kontrola własnego odrzucenia z iteracji 25.

Rozstrzygane pytanie: czy w obecnej rodzinie modeli istnieje pięciowarstwowa konfiguracja, która po optymalizacji kierunków
wyjść i położenia oka daje wspólny obraz spełniający jawne kryteria — nominalnie i przy zdefiniowanych błędach?

Rodzina modeli (bez zmian względem iteracji 25): stos płytek PTR (n0 = 1,5), siatki skośne odbiciowe, L = 0,75–1,0 mm,
n1·L = 0,2 µm, wejścia wewnątrz 20/22/24/26/28°, przekładki 1 mm (ten sam n), sonda gaussowska w0x = 150 µm, w0y = 25 µm
zadana w płaszczyźnie warstwy, D = 300 mm, źrenica 3,5 mm, kalibracja C1 (kąt wejścia kanału). Wyjścia o_k — dowolne.
Model pola: widmo kątowe 2D, zespolone r i t (Kogelnik 3D zgodny z RCWA, iteracja 25), wariant C (pełny stos).

Sekcje (python3 research/iteracja26.py [sekcja ...]): kx, plaszczyzny, moc, progi, kierunki, bledy.
Wyniki: research/wyniki_it26/.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np, sys, pathlib, json, time, itertools
from multiprocessing import Pool
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import iteracja25 as it
from iteracja25 import (design, Grid, Eye, gauss_in, unit, stack_response, to_pupil, channel_fields, shift_spec,
                        layer_profile, capture_map, count_grid, pupil_scan, peak_pos, fwhm_1d, michelson, kogc,
                        grating_io, rotK, pmin_retina, D, PUPIL, PY, W0X, W0Y, NL, L0, BETA, k0, n0, lam0, ARCMIN,
                        T_OUT, SPACER)
from iteracja19 import kog, K_of, dir_down

OUT = pathlib.Path(__file__).parent / "wyniki_it26"
OUT.mkdir(exist_ok=True)
PITCHES = (250e-6, 300e-6, 350e-6, 400e-6, 450e-6, 500e-6, 550e-6, 600e-6, 700e-6)
XROWS = (0.0, 0.4e-3, 0.8e-3, 1.2e-3, 1.6e-3, 2.0e-3)   # |Δy| wierszy przemiatania x (układ symetryczny w y)
YROWS = (-1.6e-3, -0.8e-3, 0.0, 0.8e-3, 1.6e-3)          # Δx wierszy przemiatania y
POW = (("rel", 0.2), ("rel", 0.3), ("rel", 0.5), ("rel", 0.8), ("abs", 0.05), ("abs", 0.1), ("abs", 0.2), ("abs", 0.3))
CON = (0.15, 0.3, 0.5)


class Log(it.Log):
    def __init__(self, name):
        self.f = open(OUT / f"{name}.txt", "w")


def eye_fast(g):
    return FastEye(g)


class FastEye(Eye):
    """Ta sama optyka co Eye (iteracja 25), z buforowaniem fazy akomodacji i jąder DFT; pary woksli liczone jako profil
    w wierszu (kolumnie) szczytu pojedynczego woksla — oba woksle pary leżą na tej samej wysokości (szerokości)."""

    def __init__(self, g):
        super().__init__(g, th_half_x=8 / ARCMIN, th_half_y=2.5 / ARCMIN, dthx=0.08 / ARCMIN, dthy=0.06 / ARCMIN)
        self.Ax0 = np.exp(1j * k0 * np.outer(self.tx, self.u))
        self.Ay0 = np.exp(1j * k0 * np.outer(self.ty, self.v))
        self.sc = np.sqrt(g.dx * g.dy)
        self._acc = {}

    def _prep(self, E, iu, iv, Acc, cx, cy):
        if Acc not in self._acc:
            self._acc[Acc] = self.P * np.exp(1j * k0 * Acc * self.R2 / 2)
        return (self.crop(E, iu, iv) * self._acc[Acc] * np.exp(1j * k0 * cx * self.u)[:, None]
                * np.exp(1j * k0 * cy * self.v)[None, :])

    def image(self, E, iu, iv, Acc, cx=0.0, cy=0.0, field=False):
        F = self.Ax0 @ (self._prep(E, iu, iv, Acc, cx, cy) @ self.Ay0.T) * self.sc
        return F if field else np.abs(F) ** 2

    def row(self, E, iu, iv, Acc, cx, cy, j):
        return np.abs(self.Ax0 @ (self._prep(E, iu, iv, Acc, cx, cy) @ self.Ay0[j])) ** 2 * self.sc**2

    def col(self, E, iu, iv, Acc, cx, cy, i):
        return np.abs(self.Ax0[i] @ self._prep(E, iu, iv, Acc, cx, cy) @ self.Ay0.T) ** 2 * self.sc**2


def fast_scan(g, eye, cf, offs_x, offs_y, p_list=PITCHES, axis="x"):
    """Jak iteracja25.pupil_scan (te same definicje: moc w źrenicy, położenie szczytu, kontrast Michelsona par)."""
    Deff = cf["Deff"]; A = 1 / Deff
    E0 = g.ifft(cf["A_p"])
    if axis == "x":
        pairs = {p: (g.ifft(shift_spec(g, cf["A_p"], -p / 2)), g.ifft(shift_spec(g, cf["A_p"], p / 2))) for p in p_list}
    else:
        shy = lambda s: cf["A_p"] * np.exp(1j * g.KY * s)
        pairs = {PY: (g.ifft(shy(-PY / 2)), g.ifft(shy(PY / 2)))}
    out = {key: [] for key in (["ox", "oy", "cap", "sh"] + ([f"c{p * 1e6:.0f}" for p in p_list] if axis == "x" else ["cy"]))}
    for ox, oy in zip(offs_x, offs_y):
        iu, iv = g.nx // 2 + ox, g.ny // 2 + oy
        cx = cf["th_nom"] + ox * g.dx / Deff
        cy = oy * g.dy / Deff
        F = eye.image(E0, iu, iv, A, cx, cy)
        ii, jj = np.unravel_index(np.argmax(F), F.shape)
        tx, ty = cx + eye.tx, cy + eye.ty
        out["ox"].append(ox * g.dx); out["oy"].append(oy * g.dy); out["cap"].append(eye.capture(E0, iu, iv))
        if axis == "x":
            pk = peak_pos(tx, F[:, jj]); out["sh"].append(pk - cx)
            for p, (Ea, Eb) in pairs.items():
                I = eye.row(Ea, iu, iv, A, cx, cy, jj) + eye.row(Eb, iu, iv, A, cx, cy, jj)
                out[f"c{p * 1e6:.0f}"].append(michelson(tx, I, pk + p / 2 / Deff, pk - p / 2 / Deff))
        else:
            pk = peak_pos(ty, F[ii, :]); out["sh"].append(pk - cy)
            Ea, Eb = pairs[PY]
            I = eye.col(Ea, iu, iv, A, cx, cy, ii) + eye.col(Eb, iu, iv, A, cx, cy, ii)
            out["cy"].append(michelson(ty, I, pk + PY / 2 / Deff, pk - PY / 2 / Deff))
    return {k: np.array(v, float) for k, v in out.items()}


# ------------------------------------------------------------------ ocena jednej warstwy (pełny potok, wariant C)
def layer_eval(args):
    lay, k, nx, wx, step = args
    g = Grid(nx, nx, wx, wx); eye = eye_fast(g); A_in = gauss_in(g)
    cf = channel_fields(lay, k, g, "C", A_in)
    E0 = g.ifft(cf["A_p"])
    C = capture_map(g, E0)
    s = peak_pos(g.x, layer_profile(g, cf["A_v"])[1])
    n = int(3.6e-3 / g.dx)
    offs = np.arange(-n, n + 1, step)
    xs = {dy: fast_scan(g, eye, cf, offs, np.full_like(offs, int(round(dy / g.dy)))) for dy in XROWS}
    ys = {dxr: fast_scan(g, eye, cf, np.full_like(offs, int(round(dxr / g.dx))), offs, axis="y") for dxr in YROWS}
    return dict(k=k, X=cf["X"], s=s, Deff=cf["Deff"], P=cf["P"], Cmax=float(C.max()), C=C.astype(np.float32),
                xs=xs, ys=ys, out=lay[k]["out"], th=lay[k]["th"], nx=nx, wx=wx)


def eval_stack(lay, nx=512, wx=12e-3, step=None, pool=None):
    step = step or (3 if nx == 512 else 6)
    tasks = [(lay, k, nx, wx, step) for k in range(len(lay))]
    res = pool.map(layer_eval, tasks) if pool else [layer_eval(t) for t in tasks]
    global _UID
    _UID += 1
    _MASKS.clear()           # maski są potrzebne tylko w obrębie jednej konfiguracji
    for d in res:
        d["uid"] = _UID          # jednoznaczny klucz bufora masek (id() listy może być użyte ponownie)
    return res


def _interp_rows(rows, vals, q):
    """Liniowa interpolacja między wierszami (rows rosnące); poza zakresem — wiersz skrajny."""
    q = np.clip(q, rows[0], rows[-1])
    i = np.clip(np.searchsorted(rows, q) - 1, 0, len(rows) - 2)
    f = (q - rows[i]) / (rows[i + 1] - rows[i])
    return vals[i] * (1 - f)[..., None] + vals[i + 1] * f[..., None] if vals.ndim == 2 else vals[i] * (1 - f) + vals[i + 1] * f


def layer_mask(d, g, p, pkind, pthr, cthr, mode="pelny"):
    """Maska woksli warstwy (x_d, y_v) widocznych z oka w (0, 0): moc w źrenicy, kontrast par x i y, zmiana położenia
    obrazu ≤ skok/4 (x) i ≤ 90 µm/4 (y). Kontrast i położenie interpolowane liniowo między wierszami przemiatania."""
    Xe = d["X"] - d["s"]
    sx = int(round(-Xe / g.dx))
    Cv = np.roll(np.roll(d["C"][::-1, ::-1], (1, 1), axis=(0, 1)), sx, axis=0)
    pw = Cv >= (pthr * d["Cmax"] if pkind == "rel" else pthr)
    dxg = -g.x - Xe                      # Δx dla każdego x_d
    dyg = np.abs(g.y)                    # |Δy| dla każdego y_v
    key = f"c{p * 1e6:.0f}"
    r0 = d["xs"][XROWS[0]]
    sh0 = np.interp(0.0, r0["ox"], r0["sh"])
    cx = np.array([np.interp(dxg, d["xs"][dy]["ox"], d["xs"][dy][key], left=0, right=0) for dy in XROWS])   # (wiersze, nx)
    sx_ = np.array([np.interp(dxg, d["xs"][dy]["ox"], d["xs"][dy]["sh"]) for dy in XROWS])
    rows = np.array(XROWS)
    q = np.clip(dyg, rows[0], rows[-1])
    i = np.clip(np.searchsorted(rows, q) - 1, 0, len(rows) - 2)
    f = (q - rows[i]) / (rows[i + 1] - rows[i])
    C2 = cx[i, :].T * (1 - f)[None, :] + cx[i + 1, :].T * f[None, :]          # (nx, ny)
    S2 = sx_[i, :].T * (1 - f)[None, :] + sx_[i + 1, :].T * f[None, :]
    okx = (C2 >= cthr) & (np.abs(S2 - sh0) * d["Deff"] <= p / 4)
    if mode == "it25":   # kryteria iteracji 25: kontrast x z wiersza Δy = 0 dla każdego y, bez warunku w y
        ok0 = (cx[0] >= cthr) & (np.abs(sx_[0] - sh0) * d["Deff"] <= p / 4)
        return pw & ok0[:, None]
    ry0 = d["ys"][0.0]
    shy0 = np.interp(0.0, ry0["oy"], ry0["sh"])
    cy = np.array([np.interp(-g.y, d["ys"][dxr]["oy"], d["ys"][dxr]["cy"], left=0, right=0) for dxr in YROWS])  # (wiersze, ny)
    sy = np.array([np.interp(-g.y, d["ys"][dxr]["oy"], d["ys"][dxr]["sh"]) for dxr in YROWS])
    yr = np.array(YROWS)
    q = np.clip(dxg, yr[0], yr[-1])
    i = np.clip(np.searchsorted(yr, q) - 1, 0, len(yr) - 2)
    f = (q - yr[i]) / (yr[i + 1] - yr[i])
    Cy2 = cy[i, :] * (1 - f)[:, None] + cy[i + 1, :] * f[:, None]            # (nx, ny)
    Sy2 = sy[i, :] * (1 - f)[:, None] + sy[i + 1, :] * f[:, None]
    oky = (Cy2 >= cthr) & (np.abs(Sy2 - shy0) * d["Deff"] <= PY / 4)
    return pw & okx & oky


_MASKS = {}
_UID = 0


def count_1d(v, d, p):
    s = max(1, int(round(p / d)))
    return max(int(v[a::s].sum()) for a in range(s))


def common_count(data, ks, p, pkind, pthr, cthr, mode="pelny"):
    g = Grid(data[0]["nx"], data[0]["nx"], data[0]["wx"], data[0]["wx"])
    m = np.ones((g.nx, g.ny), bool)
    for k in ks:
        key = (data[0]["uid"], k, p, pkind, pthr, cthr, mode)
        if key not in _MASKS:
            _MASKS[key] = layer_mask(data[k], g, p, pkind, pthr, cthr, mode)
        m &= _MASKS[key]
    cnt = count_grid(m, g.dx, g.dy, p, PY)
    cols = count_1d(m.any(axis=1), g.dx, p)
    rows = count_1d(m.any(axis=0), g.dy, PY)
    return cnt, cols, rows, float(m.any(axis=1).sum() * g.dx), float(m.any(axis=0).sum() * g.dy)


def k1_ok(data):
    """Warunek 1 (pierwotny): ≥ 10% mocy wejściowej w stożku o pełnym kącie < 1° — dla każdego kanału."""
    return all(d["P"]["cone"] >= 0.10 for d in data), [d["P"]["cone"] for d in data]


def best_over_pitch(data, ks, pkind, pthr, cthr, pitches=PITCHES):
    best = (0, 0, 0, 0.0, 0.0, np.nan)
    for p in pitches:
        c = common_count(data, ks, p, pkind, pthr, cthr)
        if c[0] > best[0]:
            best = c + (p,)
    return best


# ------------------------------------------------------------------ sekcja kx: odwzorowanie i Jacobian
def sec_kx():
    log = Log("kx")
    log("== Odwzorowanie kx → kąt i Jacobian ==")
    log("kx — składowa wektora falowego równoległa do powierzchni płytki (oś x w płaszczyźnie padania). Zachowana na wszystkich "
        "granicach (płytki, przekładki, powierzchnia). Sonda zadana w płaszczyźnie warstwy: E(x, y) = exp(−x²/w0x² − y²/w0y²)·"
        "exp(−jρx0·x), więc jej widmo jest gaussem w kx wokół ρx0 = β·sinθ_k (β = 2πn0/λ).")
    log("Fala o kx: kąt wewnątrz θ, β·sinθ = kx; kąt w powietrzu a, k0·sin a = kx. Jacobiany: dθ/dkx = 1/(β·cosθ), "
        "da/dkx = 1/(k0·cos a).")
    log("Iteracje 20–24: przesunięcie kąta w powietrzu t = arcsin(λ·fx), czyli da/dfx = λ ⇒ Δkx = k0·cos a0·λ·fx = 2π·fx·cos a0 "
        "zamiast 2π·fx. Czynnik = cos a0 (kąt wejścia W POWIETRZU), nie cos θ (wewnątrz).")
    for th in (20.0, 22.0, 24.0, 26.0, 28.0):
        a = np.degrees(np.arcsin(n0 * np.sin(np.radians(th))))
        log(f"  θ = {th:.0f}° wewn. → a = {a:.2f}° w powietrzu: cos a = {np.cos(np.radians(a)):.3f} "
            f"(= √(1 − n0²·sin²θ)); cos θ = {np.cos(np.radians(th)):.3f}")
    # numeryczne potwierdzenie: η wiązki liczona trzema drogami (1D, warstwa 0 i 4, L = 0,85 mm)
    L = L0; n1 = NL / L
    N, LX = 2**14, 20e-3
    x = (np.arange(N) - N / 2) * LX / N; fx = np.fft.fftfreq(N, LX / N)
    log("\nsprawdzenie: η i FWHM odbitego woksla (1D, Kogelnik, L = 0,85 mm, w0x = 150 µm) dla trzech odwzorowań:")
    for th in (20.0, 28.0):
        K = K_of(th, 0.0); a0 = np.degrees(np.arcsin(n0 * np.sin(np.radians(th))))
        maps = {
            "(a) poprawne: kx = ρx0 + 2πfx, θ z β·sinθ = kx": None,
            "(b) iteracje 20–24: a = a0 + arcsin(λfx)": np.degrees(np.arcsin(np.clip(lam0 * fx, -1, 1))),
        }
        for lab, t in maps.items():
            if t is None:
                kx = BETA * np.sin(np.radians(th)) + 2 * np.pi * fx
                R = np.sqrt(np.array([kog(np.array([q / BETA, 0, np.sqrt(max(1 - (q / BETA) ** 2, 0))]), K, lam0, L, n1)
                                      if abs(q - BETA * np.sin(np.radians(th))) < 0.02 * BETA else 0.0 for q in kx]))
            else:
                R = np.sqrt(np.array([kog(dir_down(a0 + tt), K, lam0, L, n1) if abs(tt) < 1.5 else 0 for tt in t]))
            for wlab, w in (("w0x na warstwie = 150 µm", 150e-6), ("w⊥ = 150 µm (na warstwie 150/cosθ)", 150e-6 / np.cos(np.radians(th)))):
                E = np.exp(-(x / w) ** 2)
                I = np.abs(np.fft.ifft(np.fft.fft(E) * R)) ** 2
                a_ = x[I >= 0.5 * I.max()]
                log(f"  θ = {th:.0f}°, {lab}, {wlab}: η = {I.sum() / (E ** 2).sum():.4f}, FWHM {(a_.max() - a_.min()) * 1e6:.0f} µm")


# ------------------------------------------------------------------ sekcja plaszczyzny: płaszczyzny, niezmienniczość, faza
def sec_plaszczyzny():
    log = Log("plaszczyzny")
    lay = design()
    g = Grid(); eye = Eye(g); A_in = gauss_in(g)
    log("== Płaszczyzny odniesienia, test niezmienniczości, rozkład fazy (L = 0,85 mm, krok 0,110°, siatka 1024²) ==")
    log("Płaszczyzny odniesienia amplitud:")
    log("  RCWA: R w z = 0 (górna granica siatki), T w z = d (dolna) dla fali exp(−jkz·(z − d)).")
    log("  Kogelnik: r = S(0)·√(|cS|/cR) w z = 0 (płaszczyzna wejścia); t = R(d) BEZ fazy swobodnej exp(−jρz·d) — "
        "faza swobodna jest w fali płaskiej; porównanie z RCWA: T_RCWA·exp(+jkz·d) = R(d) (iteracja 25: zgodne do 0,0011 rad).")
    log("  Stos: r_k w górnej płaszczyźnie siatki k (z_k), porty t_j bez fazy swobodnej, propagacja exp(−j|σz|·z_k) od z_k "
        "do powierzchni raz (obejmuje grubości siatek wyżej), potem powietrze D.")
    log("Szerokości (FWHM w x) w tych samych płaszczyznach dla wszystkich wariantów:")
    rows = []
    for k in (0, 4):
        for var in "ABC":
            cf = channel_fields(lay, k, g, var, A_in)
            resp = cf["resp"]
            kzg = np.sqrt(np.maximum(BETA**2 - resp["sx"]**2 - resp["sy"]**2, 0))
            fw = {}
            # 1) płaszczyzna warstwy (pole pozorne: wszystkie filtry, cofnięte jednorodnie do z_k)
            E, I = layer_profile(g, cf["A_v"]); fw["warstwa z_k"] = (fwhm_1d(g.x, I), peak_pos(g.x, I))
            # 2) powierzchnia z = 0 (pole rzeczywiste)
            E, I = layer_profile(g, cf["A_v"] * np.exp(-1j * kzg * lay[k]["z"])); fw["powierzchnia z = 0"] = (fwhm_1d(g.x, I), peak_pos(g.x, I))
            # 3) źrenica (ramka X_k)
            E, I = layer_profile(g, cf["A_p"]); fw["źrenica"] = (fwhm_1d(g.x, I), peak_pos(g.x, I))
            log(f"  k={k} {var}: " + "; ".join(f"{p}: FWHM {v[0] * 1e6:.0f} µm, szczyt {v[1] * 1e6:+.0f} µm" for p, v in fw.items()))
    # --- test niezmienniczości: przesunięcie płaszczyzny odniesienia odbicia o Δ (w górę) i o L (dolna granica)
    log("\nTest niezmienniczości (warstwa 4, wariant C): odbicie odniesione do płaszczyzny z_k + Δ; wejście przeliczone do tej "
        "płaszczyzny A·exp(−jρz·Δ), odbicie r_Δ = r·exp(+j(ρz + |σz|)·Δ), propagacja w górę od z_k + Δ. Obraz w źrenicy i na "
        "siatkówce porównany z obliczeniem podstawowym:")
    k = 4
    cf = channel_fields(lay, k, g, "C", A_in)
    resp = cf["resp"]
    rx = BETA * np.sin(np.radians(lay[k]["th"])) + g.KX
    rz = np.sqrt(np.maximum(BETA**2 - rx**2 - g.KY**2, 0))
    kzg = np.sqrt(np.maximum(BETA**2 - resp["sx"]**2 - resp["sy"]**2, 0))
    kza = np.sqrt(np.maximum(k0**2 - resp["sx"]**2 - resp["sy"]**2, 0))
    Ap0 = cf["A_p"]
    F0 = eye.image(g.ifft(Ap0), g.nx // 2, g.ny // 2, 1 / cf["Deff"], cx=cf["th_nom"])
    for Dz in (0.5e-3, -0.5e-3, lay[k]["L"]):
        A_D = A_in * np.exp(-1j * rz * Dz)                       # wejście w płaszczyźnie z_k + Δ
        r_D = resp["r"] * np.exp(1j * (rz + kzg) * Dz)            # odbicie odniesione do z_k + Δ
        A = A_D * r_D * resp["tup"] * resp["tdn"] * np.exp(-1j * kzg * (lay[k]["z"] + Dz)) * np.exp(-1j * kza * D)
        o = np.radians(lay[k]["out"])
        A = A * np.exp(-1j * g.KX * cf["X"]) * np.sqrt(T_OUT)
        F = eye.image(g.ifft(A), g.nx // 2, g.ny // 2, 1 / cf["Deff"], cx=cf["th_nom"])
        log(f"  Δ = {Dz * 1e3:+.2f} mm: max|ΔE_źrenica|/max|E| = {np.abs(A - Ap0).max() / np.abs(Ap0).max():.1e}; "
            f"max|ΔI_siatkówka|/max I = {np.abs(F - F0).max() / F0.max():.1e}")
    # kontrola ujemna: podwójnie policzona grubość siatek wyżej
    Adbl = Ap0 * np.exp(-1j * kzg * 4 * lay[k]["L"])
    E, I = layer_profile(g, cf["A_v"]); E2, I2 = layer_profile(g, cf["A_v"] * np.exp(-1j * kzg * 4 * lay[k]["L"]))
    Fd = eye.image(g.ifft(Adbl), g.nx // 2, g.ny // 2, 1 / cf["Deff"], cx=cf["th_nom"])
    log(f"  kontrola ujemna — grubość 4 siatek liczona dwukrotnie (+3,4 mm szkła): w płaszczyźnie z_k FWHM "
        f"{fwhm_1d(g.x, I) * 1e6:.0f} → {fwhm_1d(g.x, I2) * 1e6:.0f} µm, szczyt {peak_pos(g.x, I) * 1e6:+.0f} → "
        f"{peak_pos(g.x, I2) * 1e6:+.0f} µm; obraz na siatkówce zmienia się o {np.abs(Fd - F0).max() / F0.max():.1e} maksimum "
        f"(test wykrywa podwójne liczenie, ale nie może ono dać przesunięcia ~180 µm)")
    # --- przesunięcie z nachylenia fazy r (bez propagacji): s = −dφ/dkx (konwencja exp(−jkx·x))
    log("\nPrzesunięcie z samego nachylenia fazy odbicia r(kx) w z = 0 (bez propagacji), s = +dφ/dκ przy pole ∝ exp(−jκx):")
    for kk in range(5):
        cf = channel_fields(lay, kk, g, "B", A_in)
        r = cf["resp"]["r"][:, 0]
        w = np.abs(cf["A_v"][:, 0]) ** 2
        m = w > 1e-3 * w.max()
        ph = np.unwrap(np.angle(r[m][np.argsort(g.kx[m])])); kxs = np.sort(g.kx[m])
        ww = w[m][np.argsort(g.kx[m])]
        c = np.polyfit(kxs, ph, 3, w=np.sqrt(ww))
        slope = np.polyfit(kxs, ph, 1, w=np.sqrt(ww))[0]
        thi = lay[kk]["th"]; oi = np.degrees(np.arcsin(np.sin(np.radians(lay[kk]["out"])) / n0))
        log(f"  k={kk}: dφ/dκ = {slope * 1e6:+.0f} µm (szczyt woksla B: patrz tabela), głębokość efektywna "
            f"s/(tanθ − tan o) = {slope / (np.tan(np.radians(thi)) - np.tan(np.radians(oi))) * 1e3:.3f} mm "
            f"(L = {L0 * 1e3:.2f} mm); człon sześcienny φ3 = {c[0]:.2e} rad·m³")
    # --- rozkład fazy H wariantu C: stała, liniowa, reszta
    log("\nRozkład fazy całkowitej funkcji przenoszenia H (wariant C) na część stałą, liniową (w κx, κy) i resztę; obrazy:")
    for kk in (0, 4):
        cf = channel_fields(lay, kk, g, "C", A_in)
        H = cf["resp"]["H"]
        w = np.abs(A_in * H) ** 2
        # część liniowa bez rozwijania fazy: średnie ważone przyrosty fazy między sąsiednimi próbkami κ
        Hs, ws_ = np.fft.fftshift(H), np.fft.fftshift(w)
        dkx = 2 * np.pi / g.wx; dky = 2 * np.pi / g.wy      # κ maleje o dk przy rosnącym indeksie (κ = −2πf)
        sx_ = np.angle((np.sqrt(ws_[1:, :] * ws_[:-1, :]) * Hs[1:, :] * np.conj(Hs[:-1, :])).sum()) / (-dkx)
        sy_ = np.angle((np.sqrt(ws_[:, 1:] * ws_[:, :-1]) * Hs[:, 1:] * np.conj(Hs[:, :-1])).sum()) / (-dky)
        c0 = np.angle((w * H * np.exp(-1j * (sx_ * g.KX + sy_ * g.KY))).sum())
        lin = c0 + sx_ * g.KX + sy_ * g.KY
        res_ph = np.angle(H * np.exp(-1j * lin))
        rms = np.sqrt((w * res_ph ** 2).sum() / w.sum())
        coef = (c0, sx_, sy_)
        variants = {"bez kompensacji": H, "usunięta tylko część liniowa": H * np.exp(-1j * lin),
                    "usunięta cała faza (|H|)": np.abs(H)}
        for lab, Hv in variants.items():
            cfv = dict(cf); cfv["A_v"] = A_in * Hv
            Ap, X = to_pupil(dict(cf["resp"], H=Hv), lay, kk, g, A_in)
            cfv["A_p"] = Ap
            E, I = layer_profile(g, cfv["A_v"])
            mtr = it.retina_metrics(g, eye, cfv, p_list=(400e-6, 500e-6), coh=False)
            pm = pmin_retina(g, eye, cfv)
            log(f"  k={kk}, {lab}: FWHM w z_k {fwhm_1d(g.x, I) * 1e6:.0f} µm, szczyt {peak_pos(g.x, I) * 1e6:+.0f} µm; "
                f"siatkówka FWHM {mtr['fw'] * ARCMIN:.2f}′, kontrast 400/500 µm {mtr['c400']:.2f}/{mtr['c500']:.2f}, "
                f"skok dla 0,5: {pm * 1e6:.0f} µm")
        log(f"     część liniowa: nachylenie {coef[1] * 1e6:+.0f} µm (x), {coef[2] * 1e6:+.1f} µm (y); "
            f"reszta fazy rms (ważona mocą) {rms:.2f} rad")


# ------------------------------------------------------------------ sekcja moc: komórka i rozlanie
def sec_moc():
    log = Log("moc")
    lay = design()
    g = Grid(); eye = Eye(g, th_half_x=20 / ARCMIN, th_half_y=6 / ARCMIN); A_in = gauss_in(g)
    log("== Moc na siatkówce: komórka woksla, całość, rozlanie (oko na osi wiązki, akomodacja 1/D_eff) ==")
    norm = (k0 / (2 * np.pi)) ** 2 * (eye.tx[1] - eye.tx[0]) * (eye.ty[1] - eye.ty[0])
    for k in (0, 2, 4):
        cf = channel_fields(lay, k, g, "C", A_in)
        E0 = g.ifft(cf["A_p"])
        cap = eye.capture(E0, g.nx // 2, g.ny // 2)
        F = eye.image(E0, g.nx // 2, g.ny // 2, 1 / cf["Deff"], cx=cf["th_nom"])
        ii, jj = np.unravel_index(np.argmax(F), F.shape)
        tx, ty = cf["th_nom"] + eye.tx, eye.ty
        pk = peak_pos(tx, F[:, jj])
        tot = F.sum() * norm
        for px in (330e-6, 500e-6):
            hx, hy = px / 2 / cf["Deff"], PY / 2 / cf["Deff"]
            def cell(nx_, ny_):
                mx = np.abs(tx - pk - nx_ * 2 * hx) <= hx
                my = np.abs(ty - ty[jj] - ny_ * 2 * hy) <= hy
                return F[np.ix_(mx, my)].sum() * norm
            c0 = cell(0, 0)
            nbx = cell(-1, 0) + cell(1, 0); nby = cell(0, -1) + cell(0, 1)
            log(f"  k={k}, komórka {px * 1e6:.0f} × {PY * 1e6:.0f} µm (kątowo ±{hx * ARCMIN:.2f}′ × ±{hy * ARCMIN:.2f}′, "
                f"D_eff = {cf['Deff'] * 1e3:.1f} mm): w źrenicy {cap:.3f}; na siatkówce w oknie ±20′ × ±6′ {tot:.3f}; "
                f"w komórce {c0:.3f}; w sąsiednich komórkach x {nbx:.3f}, y {nby:.3f}; dalej {tot - c0 - nbx - nby:.3f}; "
                f"poza oknem {cap - tot:.3f}")


# ------------------------------------------------------------------ sekcja progi: projekt nominalny, tabela uzgodniona
def table_rows(data, label, pitches_fixed=(500e-6,), Ns=range(1, 6)):
    rows = []
    for pk, pt in POW:
        for ct in CON:
            for N in Ns:
                best = None
                for s in range(0, len(data) - N + 1):
                    ks = list(range(s, s + N))
                    for mode in ("stały 500 µm", "optymalizowany"):
                        c = (common_count(data, ks, 500e-6, pk, pt, ct) + (500e-6,)) if mode.startswith("stały") \
                            else best_over_pitch(data, ks, pk, pt, ct)
                        key = (mode,)
                        if best is None:
                            best = {}
                        if key not in best or c[0] > best[key][0]:
                            best[key] = c + (ks,)
                for (mode,), c in best.items():
                    rows.append(dict(konfiguracja=label, prog_mocy=f"{pk} {pt:g}", kontrast=ct, N=N, skok=mode,
                                     skok_um=c[5] * 1e6 if np.isfinite(c[5]) else None, woksli=c[0], woksli_razem=c[0] * N, kolumny=c[1],
                                     wiersze=c[2], szer_x_mm=c[3] * 1e3, szer_y_mm=c[4] * 1e3, warstwy=c[6],
                                     bledy="nominalnie"))
    return rows


def sec_progi():
    log = Log("progi")
    lay = design()
    log("== Projekt nominalny iteracji 25 (L = 0,85 mm, krok 0,110°) — wspólny obszar w funkcji progów ==")
    t0 = time.time()
    with Pool(4) as pool:
        data = eval_stack(lay, 512, pool=pool)
        data1024 = eval_stack(lay, 1024, pool=pool)
    log(f"(obliczenia {time.time() - t0:.0f} s; siatka 512² i kontrola 1024²)")
    log("moc w stożku 1° (warunek 1, ≥ 0,10): " + " / ".join(f"{d['P']['cone']:.3f}" for d in data) +
        "; maks. moc w źrenicy: " + " / ".join(f"{d['Cmax']:.3f}" for d in data))
    # uzgodnienie z iteracją 25 (tamże: 208/328/306/248/150 przy rel 0,5, kontrast 0,5, skok 500 µm, siatka 1024²,
    # kontrast tylko w osi x przy Δy = 0, bez kontrastu y)
    log("Uzgodnienie z iteracją 25 (tam: na warstwę 208 / 164 / 102 / 62 / 30, razem 208 / 328 / 306 / 248 / 150; 1024², "
        "rel 0,5, kontrast 0,5 tylko w x przy Δy = 0, bez warunku w y, skok 500 µm). Liczby niżej: woksli NA WARSTWĘ / RAZEM.")
    for lab, dd in (("1024²", data1024), ("512²", data)):
        for mode, mlab in (("it25", "kryteria iteracji 25"), ("pelny", "kryteria pełne: kontrast x interpolowany w Δy, kontrast y")):
            row = []
            for N in range(1, 6):
                best = max(common_count(dd, list(range(s, s + N)), 500e-6, "rel", 0.5, 0.5, mode)[0] for s in range(6 - N))
                row.append(f"{best}/{best * N}")
            log(f"  {lab}, {mlab}: N = 1…5 → " + " | ".join(row))
    rows = table_rows(data, "L = 0,85 mm, krok 0,110°")
    json.dump(rows, open(OUT / "progi.json", "w"), indent=1, default=str)
    with open(OUT / "progi.csv", "w") as f:
        keys = list(rows[0].keys())
        f.write(";".join(keys) + "\n")
        for r in rows:
            f.write(";".join(str(r[k]) for k in keys) + "\n")
    log("\nN = 5: woksle NA WARSTWĘ (kolumny × wiersze; skok) dla progów mocy (wiersze) i kontrastu (kolumny), skok optymalizowany:")
    log("  próg mocy | " + " | ".join(f"kontrast ≥ {c}" for c in CON))
    for pk, pt in POW:
        cells = []
        for ct in CON:
            r = next(r for r in rows if r["prog_mocy"] == f"{pk} {pt:g}" and r["kontrast"] == ct and r["N"] == 5
                     and r["skok"] == "optymalizowany")
            cells.append(f"{r['woksli']} ({r['kolumny']}×{r['wiersze']}; {r['skok_um']:.0f} µm)" if r["woksli"] else "0")
        log(f"  {pk} {pt:g} | " + " | ".join(cells))
    log("\nN = 1…5 przy rel 0,5 i kontraście 0,5 — stały skok 500 µm / optymalizowany (woksli na warstwę; razem = ×N):")
    for mode in ("stały 500 µm", "optymalizowany"):
        r5 = [next(r for r in rows if r["prog_mocy"] == "rel 0.5" and r["kontrast"] == 0.5 and r["N"] == N and r["skok"] == mode)
              for N in range(1, 6)]
        log(f"  {mode}: " + "; ".join(f"N={r['N']}: {r['woksli']} ({r['kolumny']}×{r['wiersze']}, skok "
                                      f"{(r['skok_um'] or 0):.0f} µm, warstwy {r['warstwy']})" for r in r5))
    # łatki warstw we wspólnych współrzędnych
    g = Grid(512, 512, 12e-3, 12e-3)
    log("\nŁatki widoczności (oko w x = 0; rel 0,5; kontrast 0,5; skok 500 µm) we współrzędnych woksla wyświetlanego x_d:")
    for d in data:
        m = layer_mask(d, g, 500e-6, "rel", 0.5, 0.5)
        xs = g.x[m[:, g.ny // 2]]
        o = np.radians(d["out"])
        log(f"  k={d['k']}: x_d ∈ [{xs.min() * 1e3:+.2f}, {xs.max() * 1e3:+.2f}] mm (szer. {(xs.max() - xs.min()) * 1e3:.2f}); "
            f"X_k = {d['X'] * 1e3:+.3f} mm, D·tan o_k = {D * np.tan(o) * 1e3:+.3f} mm (różnica {(d['X'] - D * np.tan(o)) * 1e6:+.0f} µm), "
            f"przesunięcie odbicia s_k = {d['s'] * 1e6:+.0f} µm")
    np.save(OUT / "progi_nominal_meta.npy", np.array([dict(k=d["k"], X=d["X"], s=d["s"], P=d["P"], Cmax=d["Cmax"]) for d in data]),
            allow_pickle=True)


# ------------------------------------------------------------------ sekcja kierunki: optymalizacja wyjść
PRIMARY = (("rel", 0.5, 0.5), ("rel", 0.3, 0.5), ("abs", 0.1, 0.5), ("abs", 0.1, 0.3), ("rel", 0.5, 0.3), ("abs", 0.1, 0.15))


def summarize(data, ks=range(5)):
    ok1, cones = k1_ok(data)
    res = {}
    for pk, pt, ct in PRIMARY:
        res[f"{pk} {pt:g} / C {ct}"] = best_over_pitch(data, list(ks), pk, pt, ct)
    return ok1, cones, res


def outs_from_gaps(gaps):
    o = np.concatenate([[0.0], np.cumsum(gaps)])
    return list(o - o.mean())


def sec_kierunki():
    log = Log("kierunki")
    log("== Optymalizacja kierunków wyjść (pełny potok, wariant C, siatka 512²), kryteria na całym stosie ==")
    log("Kryteria: K1 (pierwotny warunek 1) — każdy kanał ≥ 0,10 mocy wejściowej w stożku 1°; obraz — moc w źrenicy ≥ próg "
        "(rel: ułamek maksimum warstwy, abs: ułamek mocy sondy), kontrast par x i y ≥ C, zniekształcenie ≤ skok/4. "
        "Brak progu 0,95 dla pojedynczego portu.")
    results = []
    with Pool(4) as pool:
        for L in (0.85e-3, 0.75e-3, 1.0e-3):
            steps = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12) if L == 0.85e-3 else (0.02, 0.03, 0.04, 0.06, 0.08, 0.11)
            for dlt in steps:
                t0 = time.time()
                lay = design(L=L, outs=outs_from_gaps([dlt] * 4))
                data = eval_stack(lay, 512, pool=pool)
                ok1, cones, res = summarize(data)
                results.append(dict(L=L * 1e3, gaps=[dlt] * 4, K1=ok1, cones=cones, res={k: list(v) for k, v in res.items()}))
                log(f"L = {L * 1e3:.2f} mm, krok {dlt:.3f}° ({time.time() - t0:.0f} s): K1 {'tak' if ok1 else 'NIE'} "
                    f"(stożek: {' / '.join(f'{c:.3f}' for c in cones)}); " + "; ".join(
                        f"{k}: {v[0]} ({v[1]}×{v[2]}, skok {v[5] * 1e6:.0f} µm)" if v[0] else f"{k}: 0" for k, v in res.items()))
                json.dump(results, open(OUT / "kierunki.json", "w"), indent=1, default=float)
        # wyjścia nierówne: przeszukiwanie współrzędnościowe wokół najlepszego kroku równego (L = 0,85 mm)
        for key in ("rel 0.5 / C 0.5", "abs 0.1 / C 0.3"):
            base = [r for r in results if r["L"] == 0.85 and r["K1"] and len(set(r["gaps"])) == 1]
            best = max(base, key=lambda r: r["res"][key][0])
            gaps = list(best["gaps"]); bval = best["res"][key][0]
            log(f"\nwyjścia nierówne ({key}): start od kroku {gaps[0]:.3f}° ({bval} woksli na warstwę), krok 0,01°")
            seen = {tuple(np.round(r["gaps"], 3)) for r in results if r["L"] == 0.85}
            improved = True
            while improved:
                improved = False
                cands = []
                for i in range(4):
                    for dd in (-0.01, 0.01):
                        gg = list(gaps); gg[i] = round(gg[i] + dd, 3)
                        if gg[i] < 0 or tuple(gg) in seen:
                            continue
                        seen.add(tuple(gg)); cands.append(gg)
                for gg in cands:
                    lay = design(L=0.85e-3, outs=outs_from_gaps(gg))
                    data = eval_stack(lay, 512, pool=pool)
                    ok1, cones, res = summarize(data)
                    results.append(dict(L=0.85, gaps=gg, K1=ok1, cones=cones, res={k: list(v) for k, v in res.items()}))
                    v = res[key]
                    log(f"  odstępy {gg}: K1 {'tak' if ok1 else 'NIE'} (min stożek {min(cones):.3f}), {key}: {v[0]} "
                        f"({v[1]}×{v[2]}, skok {v[5] * 1e6:.0f} µm)")
                    if ok1 and v[0] > bval:
                        bval, gaps, improved = v[0], gg, True
                json.dump(results, open(OUT / "kierunki.json", "w"), indent=1, default=float)
            log(f"najlepsze odstępy (L = 0,85 mm, {key}): {gaps} → {bval} woksli na warstwę ({bval * 5} razem)")


# ------------------------------------------------------------------ sekcja bledy: najgorszy wektor błędów
def perturbed(lay, eps, phi, calib="C1"):
    """Stos z błędami okresu ε_j i orientacji φ_j (obrót wektora siatki w x–z) — pełny model siatki (rezonans, η, faza).
    C1: kąt wejścia kanału dobrany do maksimum Bragga (x) i wyjścia y = 0; λ wspólna, materiał bez zmian."""
    out = []
    for l, e, p in zip(lay, eps, phi):
        K2 = rotK(l["K"], phi=p, eps=e)
        a_nom = np.degrees(np.arcsin(n0 * np.sin(np.radians(l["th"]))))
        if calib == "C1":
            ox, oy, eta, ain = grating_io(K2, a_in=(a_nom, 0.0), L=l["L"], match=True)
            th = np.degrees(np.arcsin(np.sin(np.radians(ain[0])) / n0))
        else:
            ox, oy, eta, ain = grating_io(K2, a_in=(a_nom, 0.0), L=l["L"])
            th = l["th"]
        out.append(dict(l, K=K2, th=th, out=ox))
    return out


def sec_bledy():
    log = Log("bledy")
    res_k = json.load(open(OUT / "kierunki.json"))
    done = set()
    for key in ("rel 0.5 / C 0.5", "abs 0.1 / C 0.3"):
        cands = [r for r in res_k if r["L"] == 0.85 and r["K1"] and r["res"][key][0] > 0]
        if not cands:
            log(f"== {key}: brak konfiguracji nominalnej z niezerowym obszarem — analiza błędów bezprzedmiotowa ==")
            continue
        best = max(cands, key=lambda r: r["res"][key][0])
        if tuple(best["gaps"]) in done:
            continue
        done.add(tuple(best["gaps"]))
        errors_for(log, best["gaps"], key, best["res"][key][0])


def sec_bledy_rowne():
    """Błędy dla konfiguracji z równym krokiem 0,03° i 0,04° (zapas warunku 1), L = 0,85 mm."""
    log = Log("bledy_rowne")
    res_k = json.load(open(OUT / "kierunki.json"))
    for dlt in (0.03, 0.04):
        r = next(r for r in res_k if r["L"] == 0.85 and r["gaps"] == [dlt] * 4)
        errors_for(log, [dlt] * 4, "rel 0.5 / C 0.5", r["res"]["rel 0.5 / C 0.5"][0])


def errors_for(log, gaps, key, nominal):
    log(f"\n== Błędy wykonania: konfiguracja L = 0,85 mm, odstępy wyjść {gaps}° (nominalnie {nominal} woksli na warstwę, "
        f"{key}) ==")
    lay = design(L=0.85e-3, outs=outs_from_gaps(gaps))
    # współczynniki liniowe (C1): przesunięcie wyjścia x na jednostkę ε i φ
    a_e, a_p = [], []
    for l in lay:
        a_nom = np.degrees(np.arcsin(n0 * np.sin(np.radians(l["th"]))))
        o0 = grating_io(l["K"], a_in=(a_nom, 0), match=True)[0]
        a_e.append((grating_io(rotK(l["K"], eps=1e-5), a_in=(a_nom, 0), match=True)[0] - o0) / 1e-5)
        a_p.append((grating_io(rotK(l["K"], phi=1e-3), a_in=(a_nom, 0), match=True)[0] - o0) / 1e-3)
    a_e, a_p = np.array(a_e), np.array(a_p)
    log("współczynniki C1: wyjście x [°] na ε = 10⁻⁵: " + " / ".join(f"{v * 1e-5:+.4f}" for v in a_e) +
        "; na φ = 0,001°: " + " / ".join(f"{v * 1e-3:+.4f}" for v in a_p))
    us = np.linspace(-0.6, 0.6, 601)
    g5 = Grid(512, 512, 12e-3, 12e-3); A5 = gauss_in(g5)
    curves = it.port_curves(lay, g5, A5, us)
    o_nom = np.array([l["out"] for l in lay])
    levels = ((1e-5, 0.002), (2e-5, 0.005), (5e-5, 0.01))
    log("Model zastępczy do wyboru wektora: po C1 błąd warstwy j przesuwa jej wyjście (i okrąg Bragga portu) o "
        "u_j = a_ε,j·ε_j + a_φ,j·φ_j ∈ [−U_j, U_j], U_j = |a_ε,j|·ε0 + |a_φ,j|·φ0; przeszukanie u_j ∈ {−U, −U/2, 0, U/2, U}⁵; "
        "porty T_eff(s_k − s_j) z widmem wiązki. Wybrane wektory sprawdzone pełnym modelem siatek (K' z błędami: rezonans, η, "
        "faza, porty, wachlarz, łatki).")
    with Pool(4) as pool:
        for e0, p0 in levels:
            U = np.abs(a_e) * e0 + np.abs(a_p) * p0
            vals = (-1.0, -0.5, 0.0, 0.5, 1.0)
            worst = []
            for ev in itertools.product(vals, repeat=5):
                ev = np.array(ev)
                s = o_nom + ev * U
                fan = s.max() - s.min()
                Tmin = min(np.prod([np.interp(s[k] - s[j], us, curves[(j, k)]) for j in range(k)]) for k in range(1, 5))
                eps = ev * e0 * np.sign(a_e); phi = ev * p0 * np.sign(a_p)
                worst.append((fan, Tmin, tuple(eps), tuple(phi)))
            wf = max(worst, key=lambda w: w[0]); wt = min(worst, key=lambda w: w[1])
            log(f"\nbudżet |ε| ≤ {e0:.0e}, |φ| ≤ {p0}° (każda warstwa niezależnie); przesunięcie wyjścia U_j = "
                + " / ".join(f"{u:.4f}" for u in U) + "°")
            for lab, w in (("największy wachlarz", wf), ("najmniejsza transmisja portów", wt)):
                for calib in ("C1", "C0"):
                    lay2 = perturbed(lay, w[2], w[3], calib=calib)
                    data = eval_stack(lay2, 512, pool=pool)
                    ok1, cones, res = summarize(data)
                    if calib == "C1":
                        log(f"  wektor ({lab}): ε = [{', '.join(f'{x:+.1e}' for x in w[2])}], "
                            f"φ = [{', '.join(f'{x:+.4f}' for x in w[3])}]°; model zastępczy: wachlarz {w[0]:.3f}° "
                            f"(nominalnie {o_nom.max() - o_nom.min():.3f}°), min iloczyn portów {w[1]:.3f}")
                    log(f"    pełny model, {calib}: wyjścia " + " / ".join(f"{d['out']:+.3f}" for d in data) + "°; wejścia "
                        + " / ".join(f"{d['th']:.4f}" for d in data) + "° wewn.; K1 " + ("tak" if ok1 else "NIE")
                        + " (stożek " + " / ".join(f"{c:.3f}" for c in cones) + "); " + "; ".join(
                            f"{k}: {v[0]} ({v[1]}×{v[2]})" for k, v in res.items()))


def sec_granica():
    """Ograniczenie geometryczne rodziny z wyjściami równoległymi w obrębie warstwy: woksel warstwy k widać tylko z położeń
    oka, w których źrenica nakłada się na ślad wiązki; przedział ten ma szerokość ≤ p + f_k (f_k — ślad wiązki przy oku),
    a ślady warstw są przesunięte o X_k ≈ D·tan o_k. Stąd W_N ≤ min_k(p + f_k) − (X_max − X_min) niezależnie od progów jasności."""
    log = Log("granica")
    log("== Ograniczenie geometryczne a progi jakości (N = 5, L = 0,85 mm, wyjścia równe co δ) ==")
    g = Grid(512, 512, 12e-3, 12e-3); A_in = gauss_in(g)
    with Pool(4) as pool:
        for dlt in (0.03, 0.06, 0.110, 0.1575):
            lay = design(outs=outs_from_gaps([dlt] * 4))
            data = eval_stack(lay, 512, pool=pool)
            f = []
            for k in range(5):
                cf = channel_fields(lay, k, g, "C", A_in)
                Ix = (np.abs(g.ifft(cf["A_p"])) ** 2).sum(axis=1)
                xs = g.x[Ix >= Ix.max() * np.exp(-2)]
                f.append(xs.max() - xs.min())
            X = np.array([d["X"] - d["s"] for d in data])
            bound = min(PUPIL + fk for fk in f) - (X.max() - X.min())
            parts = []
            for lab, pk, pt, ct in (("tylko geometria (moc > 1% maks.)", "rel", 0.01, -1.0),
                                    ("geometria + kontrast ≥ 0,5", "rel", 0.01, 0.5),
                                    ("moc ≥ 20% + kontrast ≥ 0,5", "rel", 0.2, 0.5),
                                    ("moc ≥ 50% + kontrast ≥ 0,5", "rel", 0.5, 0.5)):
                b = best_over_pitch(data, list(range(5)), pk, pt, ct)
                parts.append(f"{lab}: {b[0]} woksli ({b[1]} kol. × {b[2]} wierszy, szer. x {b[3] * 1e3:.2f} mm, skok "
                             f"{b[5] * 1e6:.0f} µm)" if b[0] else f"{lab}: 0")
            log(f"δ = {dlt:.4f}°: ślad wiązki przy oku f_k (1/e², x) = " + " / ".join(f"{v * 1e3:.2f}" for v in f)
                + f" mm; rozrzut łatek X_max − X_min = {(X.max() - X.min()) * 1e3:.2f} mm; granica W_5 ≤ {bound * 1e3:.2f} mm")
            log("   " + "; ".join(parts))


def dirs(ax_air, ay_air=0.0):
    return it.dirs(ax_air, ay_air)


if __name__ == "__main__":
    secs = sys.argv[1:] or ["kx", "plaszczyzny", "moc", "progi", "kierunki", "bledy"]
    for s_ in secs:
        globals()["sec_" + s_]()
