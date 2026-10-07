"""Iteracja 25 — audyt iteracji 19–24: pełna odpowiedź zespolona, wspólna źrenica, tolerancje, przesłuch, grubość.

Model: każda siatka to zespolona funkcja przenoszenia widma kątowego (Kogelnik 3D, kogelnik_zesp.kogc,
sprawdzony z RCWA — sekcja `rcwa`). Pole wejściowe zadane w płaszczyźnie warstwy k (talie w0x, w0y),
rozkład na fale płaskie (κx, κy) wokół nośnej ρx0 = β·sinθ_k; odbicie r_k(κx, κy), w drodze w górę
przepuszczalności t_j(κx, κy) warstw j < k (porty), w drodze w dół t_j warstw j < k (wejście), propagacja
w szkle (n0) do powierzchni i w powietrzu do źrenicy (D = 300 mm), oko zredukowane: źrenica 3,5 mm,
akomodacja na warstwę, obraz siatkówkowy = transformata pola w źrenicy.
Warianty (to samo pole wejściowe, ta sama normalizacja mocy = 1):
  A — filtr amplitudowy |r_k| (jak iteracje 21–24),
  B — zespolone r_k pojedynczej siatki (bez warstw wyżej),
  C — pełny stos: t_dół warstw wyżej · r_k · t_góra warstw wyżej + propagacja (opcjonalnie skończone apertury).
Sekcje (python3 research/iteracja25.py [sekcja ...]): rcwa, warianty, zrenica, tolerancje, przesluch, grubosc,
zbieznosc. Wyniki: research/wyniki_it25/*.txt, *.csv, *.npz, *.png.
"""
import numpy as np, sys, pathlib, time, json
from multiprocessing import Pool
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kogelnik_zesp import kogc
from iteracja19 import lam0, n0, K_of, to_int, grating
from rcwa import solve

OUT = pathlib.Path(__file__).parent / "wyniki_it25"
OUT.mkdir(exist_ok=True)
D, PUPIL = 0.300, 3.5e-3
W0X, W0Y = 150e-6, 25e-6
PY = 90e-6            # skok woksli w y (iteracja 22)
SPACER = 1e-3         # przekładka między płytkami
NL = 0.2e-6           # n1·L (iteracja 24)
T_OUT = 1 - ((n0 - 1) / (n0 + 1)) ** 2
k0 = 2 * np.pi / lam0
BETA = k0 * n0
ARCMIN = np.degrees(1) * 60
L0, STEP0 = 0.85e-3, 0.110   # konfiguracja „optymalna” z iteracji 24 (krok w powietrzu, stopnie)


class Log:
    def __init__(self, name):
        self.f = open(OUT / f"{name}.txt", "w")

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        self.f.write(s + "\n"); self.f.flush()


# ---------------------------------------------------------------- geometria stosu
def design(L=L0, step=STEP0, N=5, spacer=SPACER, th0=20.0, dth=2.0, outs=None):
    """Warstwa k = 0 na górze. Wyjścia w powietrzu (k − (N−1)/2)·krok, wejścia th0 + k·dth wewnątrz."""
    lay = []
    for k in range(N):
        o = outs[k] if outs is not None else (k - (N - 1) / 2) * step
        th = th0 + k * dth
        lay.append(dict(k=k, th=th, out=o, K=K_of(th, o), z=k * (L + spacer), L=L, n1=NL / L))
    return lay


def out_dir_air(K, th_int, lam=lam0, ay=0.0):
    """Kierunek wyjścia (kąt x w powietrzu) dla fali wejściowej θ (wewn.) i siatki K: σ = ρ − K (składowe styczne)."""
    b = 2 * np.pi * n0 / lam
    sx = b * np.sin(np.radians(th_int)) - K[0]
    return np.degrees(np.arcsin(sx / (2 * np.pi / lam)))


# ---------------------------------------------------------------- siatka widma kątowego
class Grid:
    def __init__(self, nx=1024, ny=1024, wx=12e-3, wy=12e-3):
        self.nx, self.ny, self.wx, self.wy = nx, ny, wx, wy
        self.dx, self.dy = wx / nx, wy / ny
        self.x = (np.arange(nx) - nx // 2) * self.dx
        self.y = (np.arange(ny) - ny // 2) * self.dy
        self.kx = -2 * np.pi * np.fft.fftfreq(nx, self.dx)   # pole ∝ exp(−jκx·x)
        self.ky = -2 * np.pi * np.fft.fftfreq(ny, self.dy)
        self.KX, self.KY = np.meshgrid(self.kx, self.ky, indexing="ij")

    def fft(self, E):   # pole wyśrodkowane → widmo
        return np.fft.fft2(np.fft.ifftshift(E), norm="ortho")

    def ifft(self, A):  # widmo → pole wyśrodkowane
        return np.fft.fftshift(np.fft.ifft2(A, norm="ortho"))


def gauss_in(g, x0=0.0, y0=0.0, w0x=W0X, w0y=W0Y):
    E = np.exp(-((g.x[:, None] - x0) / w0x) ** 2 - ((g.y[None, :] - y0) / w0y) ** 2).astype(complex)
    A = g.fft(E)
    return A / np.sqrt((np.abs(A) ** 2).sum())


def unit(kx, ky, b, down=True):
    kz = np.sqrt(np.maximum(b**2 - kx**2 - ky**2, 0.0))
    v = np.stack([kx, ky, kz if down else -kz], -1) / b
    return v


def stack_response(lay, k, g, variant="C", lam=lam0, Kerr=None, upper=None):
    """Zespolone funkcje przenoszenia dla kanału k na siatce (κx, κy).
    Zwraca dict: r (odbicie warstwy k), tup (iloczyn portów), tdn (iloczyn przejść wejścia),
    H (całkowita funkcja: wariant A/B/C), sx (σx bezwzględne), ky.
    Kerr: lista wektorów siatek z błędami (domyślnie nominalne); upper: indeksy warstw nad k (domyślnie 0..k−1)."""
    b = 2 * np.pi * n0 / lam
    Ks = Kerr if Kerr is not None else [l["K"] for l in lay]
    L, n1 = lay[k]["L"], lay[k]["n1"]
    rx0 = BETA * np.sin(np.radians(lay[k]["th"]))  # nośna wejścia (λ0) — przy innym λ te same kierunki wejścia
    rx0 = b * np.sin(np.radians(lay[k]["th"])) if lam == lam0 else rx0
    kx = rx0 + g.KX
    rho = unit(kx, g.KY, b, True)
    r, _ = kogc(rho, Ks[k], lam, L, n1)
    sx = kx - Ks[k][0]
    sig = unit(sx, g.KY - Ks[k][1], b, False)
    up = range(k) if upper is None else upper
    tup = np.ones_like(r); tdn = np.ones_like(r)
    if variant == "C":
        for j in up:
            tup *= kogc(sig, -Ks[j], lam, lay[j]["L"], lay[j]["n1"])[1]
            tdn *= kogc(rho, Ks[j], lam, lay[j]["L"], lay[j]["n1"])[1]
    H = np.abs(r) if variant == "A" else r * tup * tdn
    return dict(r=r, tup=tup, tdn=tdn, H=H, sx=sx, sy=g.KY - Ks[k][1], b=b)


def to_pupil(resp, lay, k, g, A_in, lam=lam0, D_=D):
    """Widmo przy oku (ramka przesunięta o X tak, by środek wiązki nominalnej był w x = 0)."""
    b = resp["b"]; kv = 2 * np.pi / lam
    sx, sy = resp["sx"], resp["sy"]
    kzg = np.sqrt(np.maximum(b**2 - sx**2 - sy**2, 0))
    kza = np.sqrt(np.maximum(kv**2 - sx**2 - sy**2, 0))
    o = np.radians(lay[k]["out"])
    X = lay[k]["z"] * np.tan(np.arcsin(np.sin(o) / n0)) + D_ * np.tan(o)
    A = A_in * resp["H"] * np.exp(-1j * (kzg * lay[k]["z"] + kza * D_)) * np.exp(-1j * g.KX * X) * np.sqrt(T_OUT)
    # stała faza nośnej nieistotna; usuwamy fazę środka widma, by pola były porównywalne
    return A, X


def cone_fraction(A, resp, lay, k, half=0.5, lam=lam0):
    """Moc w stożku o pełnym kącie 2·half (stopnie) wokół nominalnego kierunku wyjścia (w powietrzu)."""
    kv = 2 * np.pi / lam
    ax = np.degrees(np.arcsin(np.clip(resp["sx"] / kv, -1, 1)))
    ay = np.degrees(np.arcsin(np.clip(resp["sy"] / kv, -1, 1)))
    m = (ax - lay[k]["out"]) ** 2 + ay**2 <= half**2
    return float((np.abs(A[m]) ** 2).sum())


# ---------------------------------------------------------------- oko
class Eye:
    """Obraz siatkówkowy (kąty) przez DFT pola w źrenicy; źrenica przesuwana o całkowitą liczbę próbek."""

    def __init__(self, g, th_half_x=14 / ARCMIN, th_half_y=4 / ARCMIN, dthx=0.05 / ARCMIN, dthy=0.04 / ARCMIN):
        self.g = g
        self.r = int(np.ceil(PUPIL / 2 / g.dx)) + 1
        self.u = np.arange(-self.r, self.r + 1) * g.dx
        self.v = np.arange(-self.r, self.r + 1) * g.dy
        U, V = np.meshgrid(self.u, self.v, indexing="ij")
        self.P = (U**2 + V**2) <= (PUPIL / 2) ** 2
        self.R2 = U**2 + V**2
        self.tx = np.arange(-th_half_x, th_half_x + 1e-12, dthx)
        self.ty = np.arange(-th_half_y, th_half_y + 1e-12, dthy)

    def crop(self, E, iu, iv):
        """Wycinek pola E (pole wyśrodkowane) wokół indeksów (iu, iv) środka źrenicy."""
        return E[iu - self.r:iu + self.r + 1, iv - self.r:iv + self.r + 1]

    def capture(self, E, iu, iv):
        return float((np.abs(self.crop(E, iu, iv)) ** 2 * self.P).sum())

    def image(self, E, iu, iv, Acc, cx=0.0, cy=0.0, field=False):
        """Pole/natężenie na siatkówce w kątach (cx + tx, cy + ty) przy akomodacji Acc [D]."""
        Ep = self.crop(E, iu, iv) * self.P * np.exp(1j * k0 * Acc * self.R2 / 2)
        Ax = np.exp(1j * k0 * np.outer(cx + self.tx, self.u))
        Ay = np.exp(1j * k0 * np.outer(cy + self.ty, self.v))
        F = Ax @ Ep @ Ay.T * np.sqrt(self.g.dx * self.g.dy)   # pole „ortho” → gęstość: E/√(dx·dy)
        return F if field else np.abs(F) ** 2


def fwhm_1d(t, p):
    p = p / p.max(); i = int(np.argmax(p)); l, r = i, i
    while l > 0 and p[l] > 0.5: l -= 1
    while r < len(p) - 1 and p[r] > 0.5: r += 1
    if l == 0 or r == len(p) - 1:
        return np.nan
    xl = t[l] + (0.5 - p[l]) * (t[l + 1] - t[l]) / (p[l + 1] - p[l])
    xr = t[r - 1] + (0.5 - p[r - 1]) * (t[r] - t[r - 1]) / (p[r] - p[r - 1])
    return xr - xl


def peak_pos(t, p):
    i = int(np.argmax(p))
    if 0 < i < len(p) - 1:
        a, b, c = p[i - 1], p[i], p[i + 1]
        den = a - 2 * b + c
        return t[i] + (0.5 * (a - c) / den if den != 0 else 0.0) * (t[1] - t[0])
    return t[i]


def michelson(t, prof, t1, t2):
    """Kontrast pary: (min(I(t1), I(t2)) − I(środek))/(min + I(środek)); t1, t2 — położenia nominalne
    (z poprawką na przesunięcie pojedynczego woksla). Ujemny → brak przerwy między wokslami (zapisywany jako 0)."""
    a, b = np.interp(t1, t, prof), np.interp(t2, t, prof)
    m = np.interp(0.5 * (t1 + t2), t, prof)
    return max(0.0, (min(a, b) - m) / (min(a, b) + m))


# ---------------------------------------------------------------- sekcja 1: RCWA (amplituda i faza)
def _rcwa_point(args):
    kind, L, n1, val, lam = args
    if kind == "r":
        lay, Lx, sgn = grating(20.0, 0.0, L=L, n1=n1)
        a_in = np.degrees(np.arcsin(n0 * np.sin(np.radians(20.0))))
        kx_in = np.sin(np.radians(a_in + val))
    else:
        lay, Lx, sgn = grating(20.0, 0.0, L=L, n1=n1, flip=True)
        kx_in = np.sin(np.radians(val))
    th = np.degrees(np.arcsin(sgn * kx_in / n0))
    kx, DEr, DEt, R, T, kzI, kzII = solve(lam, th, n0, n0, "p", lay, M=3, Lx=Lx, amps=True)
    kx = sgn * kx
    d = lay[0]["L"]
    if kind == "r":
        i = int(np.argmin(np.abs(kx - (kx_in - np.sin(np.radians(a_in)) + 0.0))))
        return DEr[i], complex(R[i]), d
    i0 = int(np.argmin(np.abs(kx - kx_in)))
    return DEt[i0], complex(T[i0] * np.exp(1j * kzII[i0] * (2 * np.pi / lam) * d)), d


def sec_rcwa():
    log = Log("rcwa")
    L, n1 = L0, NL / L0
    K = K_of(20.0, 0.0)
    a_in = np.degrees(np.arcsin(n0 * np.sin(np.radians(20.0))))
    dr = [-0.12, -0.08, -0.05, -0.02, 0.0, 0.02, 0.05, 0.08, 0.12]
    dt = [0.0, 0.03, 0.06, 0.09, 0.11, 0.14, 0.18, 0.22, 0.33]
    tasks = [("r", L, n1, d, lam0) for d in dr] + [("t", L, n1, d, lam0) for d in dt]
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(_rcwa_point, tasks)
    log(f"== 1. Kogelnik zespolony vs RCWA (L = {L * 1e3:.2f} mm, n1 = {n1:.3e}, TM, M = 3, 32 plastry/okres; "
        f"{time.time() - t0:.0f} s) ==")
    log("odbicie: faza względem punktu Bragga (RCWA: amplituda Hy w z = 0; Kogelnik: S(0)·√(|cS|/cR))")
    rows = []
    rk0 = None; rr0 = None
    for d, (de, Rr, Leff) in zip(dr, res[:len(dr)]):
        rk, tk = kogc(dirs(a_in + d), K, lam0, Leff, n1)
        if d == 0.0:
            rk0, rr0 = rk, Rr
        rows.append((d, de, Rr, rk))
    for d, de, Rr, rk in rows:
        dphr = np.angle(Rr / rr0); dphk = np.angle(rk / rk0)
        log(f"  wejście {d:+.2f}°: η RCWA {de:.4f} / Kogelnik {abs(rk) ** 2:.4f}; Δφ RCWA {dphr:+.3f} / Kogelnik "
            f"{dphk:+.3f} rad (różnica {np.angle(np.exp(1j * (dphr - dphk))):+.3f})")
    log("port (fala w górę odchylona o δ): t = R(d) bez fazy swobodnej propagacji; RCWA: T·exp(+j·kz·d)")
    up = lambda dd: dirs(dd) * np.array([1, 1, -1])
    for d, (de, Tr, Leff) in zip(dt, res[len(dr):]):
        rk, tk = kogc(up(d), -K, lam0, Leff, n1)
        log(f"  δ = {d:.2f}°: |t|² RCWA {de:.4f} / Kogelnik {abs(tk) ** 2:.4f}; φ RCWA {np.angle(Tr):+.4f} / "
            f"Kogelnik {np.angle(tk):+.4f} rad; |r|²+|t|² Kogelnik = {abs(rk) ** 2 + abs(tk) ** 2:.6f}")
    np.savez(OUT / "rcwa.npz", dr=dr, dt=dt, res=np.array([(a, b) for a, b, _ in res], dtype=object), allow_pickle=True)



# ---------------------------------------------------------------- pola kanału
def channel_fields(lay, k, g, variant, A_in, lam=lam0, Kerr=None):
    resp = stack_response(lay, k, g, variant, lam=lam, Kerr=Kerr)
    A_v = A_in * resp["H"]                      # widmo „pozorne” w płaszczyźnie warstwy (po wszystkich filtrach)
    A_p, X = to_pupil(resp, lay, k, g, A_in, lam=lam)
    P = dict(refl=float((np.abs(A_in * resp["r"] * (resp["tdn"] if variant == "C" else 1)) ** 2).sum()),
             top=float((np.abs(A_v) ** 2).sum()))
    P["air"] = P["top"] * T_OUT
    P["cone"] = cone_fraction(A_p, resp, lay, k, lam=lam)
    return dict(resp=resp, A_v=A_v, A_p=A_p, X=X, P=P,
                Deff=D + lay[k]["z"] / n0,
                # kąty siatkówkowe liczone względem nośnej σx0/k0 (obwiednia); woksel w x = 0, oko w środku ramki X
                th_nom=X / (D + lay[k]["z"] / n0) - np.sin(np.radians(lay[k]["out"])))


def shift_spec(g, A, s):
    """Widmo pola przesuniętego o s w x (woksel w x = s)."""
    return A * np.exp(1j * g.KX * s)


def layer_profile(g, A_v):
    E = g.ifft(A_v)
    I = np.abs(E) ** 2
    j = int(np.argmax(I.max(axis=0)))
    return E[:, j], I[:, j]


def retina_metrics(g, eye, cf, p_list=(300e-6, 330e-6, 400e-6), Acc=None, off=(0, 0), coh=True):
    """Obraz woksla na siatkówce i kontrast par (kolejno; jednocześnie w fazie) dla skoków p_list.
    off: przesunięcie źrenicy względem środka wiązki (w próbkach)."""
    Deff = cf["Deff"]
    Acc = 1 / Deff if Acc is None else Acc
    iu, iv = g.nx // 2 + off[0], g.ny // 2 + off[1]
    cx = cf["th_nom"] + off[0] * g.dx / Deff
    E0 = g.ifft(cf["A_p"])
    F0 = eye.image(E0, iu, iv, Acc, cx=cx, field=True)
    I0 = np.abs(F0) ** 2
    ii, jj = np.unravel_index(np.argmax(I0), I0.shape)
    tx = cx + eye.tx
    pk = peak_pos(tx, I0[:, jj])
    out = dict(cap=eye.capture(E0, iu, iv), fw=fwhm_1d(eye.tx, I0[:, jj]), fwy=fwhm_1d(eye.ty, I0[ii, :]),
               shift=pk - cx, peak=I0.max())
    # moc „użyteczna”: w komórce woksla (skok x 330 µm, y 90 µm) wokół położenia szczytu
    norm = (k0 / (2 * np.pi)) ** 2 * (eye.tx[1] - eye.tx[0]) * (eye.ty[1] - eye.ty[0])
    hx, hy = 330e-6 / 2 / Deff, PY / 2 / Deff
    mx = np.abs(tx - pk) <= hx; my = np.abs(eye.ty - eye.ty[jj]) <= hy
    out["useful"] = float(I0[np.ix_(mx, my)].sum() * norm)
    out["ret_tot"] = float(I0.sum() * norm)
    for p in p_list:
        Fa = eye.image(g.ifft(shift_spec(g, cf["A_p"], -p / 2)), iu, iv, Acc, cx=cx, field=True)
        Fb = eye.image(g.ifft(shift_spec(g, cf["A_p"], +p / 2)), iu, iv, Acc, cx=cx, field=True)
        t1, t2 = pk + p / 2 / Deff, pk - p / 2 / Deff
        Is = np.abs(Fa[:, jj]) ** 2 + np.abs(Fb[:, jj]) ** 2
        out[f"c{p * 1e6:.0f}"] = michelson(tx, Is, t1, t2)
        if coh:
            out[f"h{p * 1e6:.0f}"] = michelson(tx, np.abs(Fa[:, jj] + Fb[:, jj]) ** 2, t1, t2)
    return out


def pattern_metrics(g, eye, cf, p, Acc=None):
    """Obrazy złożone na siatkówce (oko na środku wzoru), kolejno (suma natężeń) i jednocześnie w fazie (suma pól).
    linia: 9 woksli co p → zafalowanie (max−min)/(max+min) w |x| ≤ 2p;
    naprzemienne: zapalone 2i·p, zgaszone (2i+1)·p → M = (min jasnych − max ciemnych)/(suma);
    grupy: zapalone ±1..±3·p, przerwa w 0 → V = (min I(±p) − I(0))/(suma)."""
    Deff = cf["Deff"]; Acc = 1 / Deff if Acc is None else Acc
    iu, iv = g.nx // 2, g.ny // 2
    cx = cf["th_nom"]
    F = lambda s: eye.image(g.ifft(shift_spec(g, cf["A_p"], s)), iu, iv, Acc, cx=cx, field=True)
    F0 = F(0.0); I0 = np.abs(F0) ** 2
    ii, jj = np.unravel_index(np.argmax(I0), I0.shape)
    tx = cx + eye.tx
    pk = peak_pos(tx, I0[:, jj])
    pos = lambda s: pk - s / Deff
    fields = {i: F(i * p)[:, jj] for i in range(-4, 5)}
    res = {}
    for mode in ("kolejno", "w fazie"):
        comb = (lambda idx: sum(np.abs(fields[i]) ** 2 for i in idx)) if mode == "kolejno" else \
               (lambda idx: np.abs(sum(fields[i] for i in idx)) ** 2)
        I = comb(range(-4, 5))
        m = (tx >= pos(2 * p)) & (tx <= pos(-2 * p))
        rip = (I[m].max() - I[m].min()) / (I[m].max() + I[m].min())
        I = comb([-4, -2, 0, 2, 4])
        lit = min(np.interp(pos(s * p), tx, I) for s in (-2, 0, 2))
        dark = max(np.interp(pos(s * p), tx, I) for s in (-1, 1))
        M = (lit - dark) / (lit + dark)
        I = comb([-3, -2, -1, 1, 2, 3])
        a = min(np.interp(pos(-p), tx, I), np.interp(pos(p), tx, I)); b = np.interp(pos(0), tx, I)
        V = (a - b) / (a + b)
        res[mode] = (rip, M, V)
    return res


def pmin_retina(g, eye, cf, lo=200e-6, hi=900e-6, target=0.5, coh=False):
    """Najmniejszy skok pary woksli z kontrastem Michelsona ≥ target na siatkówce (bisekcja, 5 µm)."""
    key = lambda p: retina_metrics(g, eye, cf, p_list=(p,), coh=coh)[f"{'h' if coh else 'c'}{p * 1e6:.0f}"]
    if key(hi) < target:
        return np.nan
    while hi - lo > 5e-6:
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if key(mid) >= target else (mid, hi)
    return hi


def best_focus(g, eye, cf, span=0.4, n=17):
    A0 = 1 / cf["Deff"]
    E0 = g.ifft(cf["A_p"])
    pk = [eye.image(E0, g.nx // 2, g.ny // 2, A0 + a, cx=cf["th_nom"]).max() for a in np.linspace(-span, span, n)]
    i = int(np.argmax(pk))
    return np.linspace(-span, span, n)[i], pk[i] / pk[n // 2]


def sec_warianty():
    log = Log("warianty")
    lay = design()
    g = Grid(); eye = Eye(g)
    A_in = gauss_in(g)
    log(f"== 2. Trzy warianty odpowiedzi (L = {L0 * 1e3:.2f} mm, krok {STEP0}°, w0x = {W0X * 1e6:.0f} µm, w0y = "
        f"{W0Y * 1e6:.0f} µm, siatka {g.nx}×{g.ny}, okno {g.wx * 1e3:.0f}×{g.wy * 1e3:.0f} mm) ==")
    log("A — |r| (model iteracji 21–24), B — zespolone r pojedynczej siatki, C — pełny stos (porty i wejście zespolone, propagacja)")
    log("kontrast: Michelson w położeniach nominalnych (z poprawką na przesunięcie pojedynczego woksla): "
        "(min(I1, I2) − I_środek)/(min + I_środek), 0 gdy brak przerwy; 'stary' — funkcja contrast() z iteracji 21–24")
    from iteracja21 import contrast as old_contrast
    rows = []
    for k in range(5):
        for var in "ABC":
            cf = channel_fields(lay, k, g, var, A_in)
            E, I = layer_profile(g, cf["A_v"])
            fwl, pkl = fwhm_1d(g.x, I), peak_pos(g.x, I)
            prof = lambda s: layer_profile(g, shift_spec(g, cf["A_v"], s))[0]
            lc = {}
            for p in (300e-6, 400e-6):
                a, b = prof(-p / 2), prof(p / 2)
                Is = np.abs(a) ** 2 + np.abs(b) ** 2
                lc[p] = (old_contrast(Is), michelson(g.x, Is, pkl - p / 2, pkl + p / 2),
                         michelson(g.x, np.abs(a + b) ** 2, pkl - p / 2, pkl + p / 2))
            m = retina_metrics(g, eye, cf)
            pm = pmin_retina(g, eye, cf)
            dA, gain = best_focus(g, eye, cf)
            row = dict(k=k, var=var, refl=cf["P"]["refl"], top=cf["P"]["top"], cone=cf["P"]["cone"], cap=m["cap"],
                       useful=m["useful"], fwl=fwl * 1e6, pkl=pkl * 1e6, old300=lc[300e-6][0], old400=lc[400e-6][0],
                       l300=lc[300e-6][1], l400=lc[400e-6][1], lh300=lc[300e-6][2], lh400=lc[400e-6][2],
                       fw=m["fw"] * ARCMIN, fwy=m["fwy"] * ARCMIN, sh=m["shift"] * ARCMIN,
                       shum=-m["shift"] * cf["Deff"] * 1e6, c300=m["c300"], c400=m["c400"], h300=m["h300"],
                       h400=m["h400"], pmin=pm * 1e6, dA=dA, gain=gain)
            rows.append(row)
            log(f"k={k} ({lay[k]['th']:.0f}° → {lay[k]['out']:+.2f}°, z = {lay[k]['z'] * 1e3:.2f} mm) {var}: "
                f"η odbicia {row['refl']:.3f}, przy powierzchni {row['top']:.3f}, w stożku 1° {row['cone']:.3f}, w źrenicy "
                f"{row['cap']:.3f}, w komórce woksla {row['useful']:.3f} | warstwa: FWHM {row['fwl']:.0f} µm, szczyt "
                f"{row['pkl']:+.0f} µm, kontrast 300/400 µm (stary) {row['old300']:.2f}/{row['old400']:.2f}, "
                f"Michelson kolejno {row['l300']:.2f}/{row['l400']:.2f}, w fazie {row['lh300']:.2f}/{row['lh400']:.2f}")
            log(f"      siatkówka: FWHM x {row['fw']:.2f}′ y {row['fwy']:.2f}′, przesunięcie {row['sh']:+.2f}′ "
                f"(≙ {row['shum']:+.0f} µm w warstwie), kontrast 300/400 µm kolejno {row['c300']:.2f}/{row['c400']:.2f}, "
                f"w fazie {row['h300']:.2f}/{row['h400']:.2f}; skok dla kontrastu 0,5: {row['pmin']:.0f} µm; "
                f"najlepsza akomodacja {row['dA']:+.2f} D od 1/D_eff (szczyt ×{row['gain']:.2f})")
    keys = list(rows[0].keys())
    with open(OUT / "warianty.csv", "w") as f:
        f.write(",".join(keys) + "\n")
        for r in rows:
            f.write(",".join(str(r[k]) for k in keys) + "\n")
    log("\n== obrazy złożone (oko na środku wzoru), skok 400 µm i 500 µm ==")
    log("linia: zafalowanie (niżej = ciągła); naprzemienne: M; grupy 3+3 z przerwą: V")
    for k in (0, 4):
        for var in "ABC":
            cf = channel_fields(lay, k, g, var, A_in)
            for p in (400e-6, 500e-6):
                pm = pattern_metrics(g, eye, cf, p)
                log(f"  k={k} {var}, skok {p * 1e6:.0f} µm: " + "; ".join(
                    f"{mode}: linia {v[0]:.2f}, naprzemienne {v[1]:.2f}, przerwa {v[2]:.2f}" for mode, v in pm.items()))


# ---------------------------------------------------------------- sekcja 3: źrenica, wspólny obszar
P_LIST = (330e-6, 400e-6, 500e-6)


def pupil_scan(g, eye, cf, offs_x, offs_y, p_list=P_LIST, axis="x"):
    """Przemiatanie położenia oka względem środka wiązki (w próbkach). Pola w źrenicy liczone raz.
    axis='x': para woksli w x (skoki p_list); axis='y': para w y (skok PY)."""
    Deff = cf["Deff"]
    E0 = g.ifft(cf["A_p"])
    if axis == "x":
        pairs = {p: (g.ifft(shift_spec(g, cf["A_p"], -p / 2)), g.ifft(shift_spec(g, cf["A_p"], p / 2))) for p in p_list}
    else:
        sh = lambda s: cf["A_p"] * np.exp(1j * g.KY * s)
        pairs = {PY: (g.ifft(sh(-PY / 2)), g.ifft(sh(PY / 2)))}
    out = []
    for ox, oy in zip(offs_x, offs_y):
        iu, iv = g.nx // 2 + ox, g.ny // 2 + oy
        cx = cf["th_nom"] + ox * g.dx / Deff
        cy = oy * g.dy / Deff
        F = eye.image(E0, iu, iv, 1 / Deff, cx=cx, cy=cy)
        ii, jj = np.unravel_index(np.argmax(F), F.shape)
        tx, ty = cx + eye.tx, cy + eye.ty
        rec = dict(ox=ox * g.dx, oy=oy * g.dy, cap=eye.capture(E0, iu, iv))
        if axis == "x":
            pk = peak_pos(tx, F[:, jj]); rec.update(fw=fwhm_1d(tx, F[:, jj]), sh=pk - cx)
            for p, (Ea, Eb) in pairs.items():
                I = eye.image(Ea, iu, iv, 1 / Deff, cx=cx, cy=cy) + eye.image(Eb, iu, iv, 1 / Deff, cx=cx, cy=cy)
                j2 = np.unravel_index(np.argmax(I), I.shape)[1]
                rec[f"c{p * 1e6:.0f}"] = michelson(tx, I[:, j2], pk + p / 2 / Deff, pk - p / 2 / Deff)
        else:
            pk = peak_pos(ty, F[ii, :]); rec.update(fw=fwhm_1d(ty, F[ii, :]), sh=pk - cy)
            Ea, Eb = pairs[PY]
            I = eye.image(Ea, iu, iv, 1 / Deff, cx=cx, cy=cy) + eye.image(Eb, iu, iv, 1 / Deff, cx=cx, cy=cy)
            i2 = np.unravel_index(np.argmax(I), I.shape)[0]
            rec["cy"] = michelson(ty, I[i2, :], pk + PY / 2 / Deff, pk - PY / 2 / Deff)
        out.append(rec)
    return out


def capture_map(g, E):
    disk = ((g.x[:, None] ** 2 + g.y[None, :] ** 2) <= (PUPIL / 2) ** 2).astype(float)
    Ip = np.abs(E) ** 2
    C = np.fft.fftshift(np.fft.ifft2(np.fft.fft2(np.fft.ifftshift(Ip)) * np.fft.fft2(np.fft.ifftshift(disk)))).real
    return C   # C[i, j] = moc w źrenicy o środku (x[i], y[j]) względem środka wiązki


def interval(mask, x):
    """Najdłuższy ciągły przedział, w którym mask = True."""
    best, cur = (np.nan, np.nan, 0.0), None
    for i, m in enumerate(mask):
        if m and cur is None:
            cur = i
        if (not m or i == len(mask) - 1) and cur is not None:
            j = i if m else i - 1
            if x[j] - x[cur] > best[2]:
                best = (x[cur], x[j], x[j] - x[cur])
            cur = None
    return best


def count_grid(mask, dx, dy, px, py):
    """Największa liczba węzłów siatki (px, py) mieszczących się w masce (przesunięcia siatki próbkowane co dx, dy)."""
    sx, sy = max(1, int(round(px / dx))), max(1, int(round(py / dy)))
    best = 0
    for a in range(sx):
        for b in range(0, sy, max(1, sy // 8)):
            best = max(best, int(mask[a::sx, b::sy].sum()))
    return best


def region_analysis(g, lay, ks, scans, cmaps, cmax, p, thr, crit_c=0.5):
    """Wspólny obszar woksli warstw ks widziany z oka w x_e = 0: maska w (x_v, y_v) na siatce g.
    Warstwa k widoczna, gdy C_k ≥ thr·C_max,k oraz (w x) kontrast pary ≥ crit_c i |przesunięcie| ≤ p/4."""
    mask = np.ones((g.nx, g.ny), bool)
    per = {}
    for k in ks:
        sc = scans[k]
        ox = np.array([r["ox"] for r in sc])
        sh0 = np.interp(0.0, ox, np.array([r["sh"] for r in sc]))
        okx = np.array([(r[f"c{p * 1e6:.0f}"] >= crit_c) and abs(r["sh"] - sh0) * (D + lay[k]["z"] / n0) <= p / 4
                        for r in sc])
        # warunek x na siatce przesunięć oka: Δx = x_e − x_in − X_k, woksel wyświetlany w x_d = x_in + s_k
        # (s_k — stałe przesunięcie boczne odbicia, skompensowane adresowaniem), oko w x_e = 0
        Xe = lay[k]["X"] - lay[k]["s"]
        dx_grid = -g.x - Xe
        okg = np.interp(dx_grid, ox, okx.astype(float), left=0, right=0) > 0.5
        # moc: C_k(Δx, Δy), Δy = −y_v
        sx = int(round(-Xe / g.dx))
        Ck = np.roll(np.roll(cmaps[k][::-1, ::-1], (1, 1), axis=(0, 1)), sx, axis=0)   # C_k(−x_v − X_k, −y_v)
        mk = (Ck >= thr * cmax[k]) & okg[:, None]
        per[k] = mk
        mask &= mk
    return mask, per


def sec_zrenica():
    log = Log("zrenica")
    lay = design()
    g = Grid(); eye = Eye(g)
    A_in = gauss_in(g)
    log(f"== 3. Najgłębszy woksel, źrenica i wspólny obszar (wariant C, L = {L0 * 1e3:.2f} mm, krok {STEP0}°) ==")
    cfs, scans, yscans, cmaps, cmax = {}, {}, {}, {}, {}
    step = 4
    offs = np.arange(-int(3.6e-3 / g.dx), int(3.6e-3 / g.dx) + 1, step)
    for k in range(5):
        cf = channel_fields(lay, k, g, "C", A_in)
        lay[k]["X"] = cf["X"]
        lay[k]["s"] = peak_pos(g.x, layer_profile(g, cf["A_v"])[1])
        cfs[k] = cf
        E0 = g.ifft(cf["A_p"])
        cmaps[k] = capture_map(g, E0)
        cmax[k] = cmaps[k].max()
        scans[k] = pupil_scan(g, eye, cf, offs, np.zeros_like(offs))
        yscans[k] = pupil_scan(g, eye, cf, np.zeros_like(offs), offs, axis="y")
        log(f"  k={k}: X = {cf['X'] * 1e3:+.3f} mm (środek wiązki nominalnej przy oku względem wejścia), stałe przesunięcie "
            f"odbicia s = {lay[k]['s'] * 1e6:+.0f} µm (kompensowane adresowaniem), C_max = {cmax[k]:.3f}")
    rowsy = {}
    for oy in (1.0e-3, 1.5e-3):
        rowsy[oy] = pupil_scan(g, eye, cfs[4], offs, np.full_like(offs, int(round(oy / g.dy))))
    np.savez(OUT / "zrenica_scan.npz", offs=offs * g.dx,
             **{f"x{k}_{key}": np.array([r[key] for r in scans[k]], float) for k in range(5) for key in scans[k][0]},
             **{f"y{k}_{key}": np.array([r[key] for r in yscans[k]], float) for k in range(5) for key in yscans[k][0]})

    # --- najgłębszy woksel: hierarchia mocy przy oku na osi wiązki
    k = 4; cf = cfs[k]
    s0 = scans[k][len(offs) // 2]
    m = retina_metrics(g, eye, cf, p_list=())
    log(f"\n-- najgłębsza warstwa k = 4: moce (sonda = 1) --")
    log(f"  odbita przez siatkę 4 (wiązka): {cf['P']['refl']:.3f}; przy powierzchni po 4 portach i wejściu: {cf['P']['top']:.3f}; "
        f"w powietrzu (Fresnel): {cf['P']['air']:.3f}; w stożku o pełnym kącie 1°: {cf['P']['cone']:.3f}")
    log(f"  w źrenicy 3,5 mm na osi wiązki: {s0['cap']:.3f}; w komórce woksla 330 × 90 µm na siatkówce: {m['useful']:.3f} "
        f"(całość obrazu w oknie siatkówki {m['ret_tot']:.3f})")
    for k2 in range(5):
        sc = scans[k2]
        cap = np.array([r["cap"] for r in sc]); ox = np.array([r["ox"] for r in sc])
        log(f"  k={k2}: przedział położeń oka z mocą ≥ 50% / 80% C_max (oś x, Δy = 0): "
            f"{interval(cap >= 0.5 * cmax[k2], ox)[2] * 1e3:.2f} / {interval(cap >= 0.8 * cmax[k2], ox)[2] * 1e3:.2f} mm; "
            f"kontrast ≥ 0,5 przy skoku 330/400/500 µm: " + " / ".join(
                f"{interval(np.array([r[f'c{p * 1e6:.0f}'] >= 0.5 for r in sc]), ox)[2] * 1e3:.2f}" for p in P_LIST) + " mm")
        capy = np.array([r["cap"] for r in yscans[k2]])
        log(f"        oś y (Δx = 0): moc ≥ 50% / 80%: {interval(capy >= 0.5 * cmax[k2], ox)[2] * 1e3:.2f} / "
            f"{interval(capy >= 0.8 * cmax[k2], ox)[2] * 1e3:.2f} mm; kontrast y (skok 90 µm) ≥ 0,5: "
            f"{interval(np.array([r['cy'] >= 0.5 for r in yscans[k2]]), ox)[2] * 1e3:.2f} mm")
    for oy, rr in rowsy.items():
        cap = np.array([r["cap"] for r in rr]); ox = np.array([r["ox"] for r in rr])
        log(f"  k=4 przy Δy = {oy * 1e3:.1f} mm: moc ≥ 50% C_max w x: {interval(cap >= 0.5 * cmax[4], ox)[2] * 1e3:.2f} mm; "
            f"kontrast ≥ 0,5 (400 µm): {interval(np.array([r['c400'] >= 0.5 for r in rr]), ox)[2] * 1e3:.2f} mm")

    # --- wspólny obszar
    log("\n-- wspólny obszar woksli widoczny z jednego położenia oka (pola różnych położeń oka nie są sumowane) --")
    log("kryteria: moc w źrenicy ≥ thr·C_max warstwy; kontrast pary w x ≥ 0,5 przy skoku p; zmiana położenia obrazu "
        "względem oka na osi wiązki ≤ p/4; "
        "liczone w siatce woksli p × 90 µm")
    res = []
    for thr in (0.5, 0.8):
        for p in P_LIST:
            per_layer = []
            for N in range(1, 6):
                best = (0, None)
                for s in range(0, 6 - N):
                    ks = list(range(s, s + N))
                    mask, per = region_analysis(g, lay, ks, scans, cmaps, cmax, p, thr)
                    cnt = count_grid(mask, g.dx, g.dy, p, PY)
                    wx = mask.any(axis=1).sum() * g.dx; wy = mask.any(axis=0).sum() * g.dy
                    if cnt > best[0] or best[1] is None:
                        best = (cnt, ks, wx, wy, count_grid(mask.any(axis=1)[:, None], g.dx, g.dy, p, 1e9))
                per_layer.append(best)
                res.append(dict(thr=thr, p=p * 1e6, N=N, ks=best[1], wx=best[2] * 1e3, wy=best[3] * 1e3, nx=best[4],
                                per_layer=best[0], total=best[0] * N))
            log(f"  thr {thr:.0%}, skok {p * 1e6:.0f} µm: " + "; ".join(
                f"N={N}: szer. x {b[2] * 1e3:.2f} mm, y {b[3] * 1e3:.2f} mm, kolumn {b[4]}, woksli/warstwę {b[0]}, "
                f"razem {b[0] * N}" for N, b in zip(range(1, 6), per_layer)))
    with open(OUT / "wspolny_obszar.json", "w") as f:
        json.dump(res, f, indent=1)
    # mapa wspólnego obszaru i rysunki
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        mask, per = region_analysis(g, lay, range(5), scans, cmaps, cmax, 400e-6, 0.5)
        fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
        ext = [g.y[0] * 1e3, g.y[-1] * 1e3, g.x[-1] * 1e3, g.x[0] * 1e3]
        col = np.zeros((g.nx, g.ny))
        for kk in range(5):
            col += per[kk]
        im = ax[0].imshow(col, extent=ext, aspect="auto", cmap="viridis")
        ax[0].contour(g.y * 1e3, g.x * 1e3, mask.astype(float), [0.5], colors="r")
        ax[0].set_xlim(-4, 4); ax[0].set_ylim(-4, 4)
        ax[0].set_xlabel("y woksla [mm]"); ax[0].set_ylabel("x woksla [mm]")
        ax[0].set_title("liczba warstw spełniających kryteria\n(oko w x = 0; czerwony: wszystkie 5, skok 400 µm)")
        plt.colorbar(im, ax=ax[0])
        E0 = g.ifft(cfs[4]["A_p"])
        r = eye.r; c = (g.nx // 2, g.ny // 2)
        Ep = eye.crop(E0, *c)
        ph = np.angle(Ep * np.exp(1j * k0 * eye.R2 / (2 * cfs[4]["Deff"])))
        I = np.abs(Ep) ** 2
        ax[1].imshow(np.where(eye.P, I / I.max(), np.nan).T, extent=[eye.u[0] * 1e3, eye.u[-1] * 1e3, eye.v[0] * 1e3,
                     eye.v[-1] * 1e3], origin="lower", cmap="magma")
        ax[1].contour(eye.u * 1e3, eye.v * 1e3, (np.where(eye.P, ph, np.nan) * (I > 0.05 * I.max())).T, 12,
                      colors="c", linewidths=0.6)
        ax[1].set_title("k = 4: natężenie w źrenicy (oko na osi)\nkontury: faza po odjęciu sfery 1/D_eff")
        ax[1].set_xlabel("u [mm]"); ax[1].set_ylabel("v [mm]")
        F = eye.image(E0, *c, 1 / cfs[4]["Deff"], cx=cfs[4]["th_nom"])
        ax[2].imshow(F.T / F.max(), extent=[eye.tx[0] * ARCMIN, eye.tx[-1] * ARCMIN, eye.ty[0] * ARCMIN,
                     eye.ty[-1] * ARCMIN], origin="lower", aspect="auto", cmap="gray")
        ax[2].set_xlim(-6, 6); ax[2].set_title("k = 4: obraz na siatkówce (akomodacja 1/D_eff)")
        ax[2].set_xlabel("θx [′]"); ax[2].set_ylabel("θy [′]")
        fig.tight_layout(); fig.savefig(OUT / "zrenica_k4.png", dpi=110)
        np.savez(OUT / "zrenica_k4_pole.npz", u=eye.u, v=eye.v, Ep=Ep, F=F, tx=eye.tx, ty=eye.ty)
    except ImportError:
        log("(matplotlib niedostępny — rysunki pominięte)")


# ---------------------------------------------------------------- sekcja 4: budżet tolerancji
def rotK(K, phi=0.0, tx=0.0, psi=0.0, eps=0.0):
    """Wektor siatki z błędami: skala okresu (1+ε), obrót wokół y (skos / pochylenie płytki w x–z) o φ,
    wokół x (pochylenie płytki w y–z) o τx, wokół z (obrót w płaszczyźnie płytki) o ψ — kąty w stopniach."""
    a, b, c = np.radians([phi, tx, psi])
    Ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    Rz = np.array([[np.cos(c), -np.sin(c), 0], [np.sin(c), np.cos(c), 0], [0, 0, 1]])
    return Rz @ Rx @ Ry @ (np.asarray(K) / (1 + eps))


def grating_io(K, lam=lam0, n=n0, a_in=None, L=L0, n1=None, match=False):
    """Wejście w powietrzu (a_in = (ax, ay) w stopniach) → (wyjście x, wyjście y [°, powietrze], η, wejście).
    match=True: kąt wejścia dobrany tak, by spełnić warunek Bragga i wyjście y = 0 (kalibracja C1)."""
    n1 = NL / L if n1 is None else n1
    kv = 2 * np.pi / lam; b = kv * n
    if match:
        ky = K[1]
        f = lambda kx: (kx - K[0]) ** 2 + (ky - K[1]) ** 2 + (np.sqrt(b**2 - kx**2 - ky**2) - K[2]) ** 2 - b**2
        x0 = kv * np.sin(np.radians(a_in[0]))
        lo, hi = x0 - 0.01 * kv, x0 + 0.01 * kv
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if np.sign(f(mid)) == np.sign(f(lo)) else (lo, mid)
        kx = 0.5 * (lo + hi)
    else:
        kx, ky = kv * np.sin(np.radians(a_in[0])), kv * np.sin(np.radians(a_in[1]))
    rh = np.array([kx, ky, np.sqrt(b**2 - kx**2 - ky**2)]) / b
    r, _ = kogc(rh, K, lam, L, n1, n0=n)
    ox = np.degrees(np.arcsin((kx - K[0]) / kv)); oy = np.degrees(np.arcsin((ky - K[1]) / kv))
    return ox, oy, abs(r) ** 2, (np.degrees(np.arcsin(kx / kv)), np.degrees(np.arcsin(ky / kv)))


def kog_chirp(rh, G, lam, L, n1, dn_of_z, ns=200, n0_=n0):
    """Kogelnik z niejednorodnym współczynnikiem średnim n0 + δn(z) (plastry, iloczyn macierzy 2×2):
    dodatkowe człony −j·β·δn/n0 w obu równaniach (fala R i S). Zwraca (r, t) jak kogc (skalarnie)."""
    beta = 2 * np.pi * n0_ / lam
    rho = beta * np.asarray(rh); sig = rho - G
    nz = np.sign(rh[2]); cR = abs(rh[2]); cS = sig[2] * nz / beta
    pf = abs(rh @ sig) / np.linalg.norm(sig)
    vt = (beta**2 - sig @ sig) / (2 * beta)
    kap = np.pi * n1 * pf / lam
    h = L / ns
    Mt = np.eye(2, dtype=complex)
    for i in range(ns):
        z = (i + 0.5) * h
        p = beta * dn_of_z(z) / n0_
        M = np.array([[-1j * p / cR, -1j * kap / cR], [-1j * kap / cS, -1j * vt / cS - 1j * p / cS]])
        tr = np.trace(M); q = np.sqrt(tr**2 / 4 - np.linalg.det(M) + 0j)
        sh = np.sinh(q * h) / q if abs(q * h) > 1e-12 else h
        E = np.exp(tr * h / 2) * (np.cosh(q * h) * np.eye(2) + sh * (M - tr / 2 * np.eye(2)))
        Mt = E @ Mt
    S0 = -Mt[1, 0] / Mt[1, 1]
    return S0 * np.sqrt(abs(cS) / cR), Mt[0, 0] + Mt[0, 1] * S0


def port_curves(lay, g, A_in, us):
    """T_eff[j][k](u): przepuszczalność portu warstwy j dla wiązki odbitej przez warstwę k (widmo 2D wiązki),
    gdy środek wiązki leży o u (stopnie, powietrze) od kierunku wyjścia warstwy j (u > 0 — wiązka głębszej warstwy)."""
    out = {}
    for k in range(len(lay)):
        resp = stack_response(lay, k, g, "B")
        w = np.abs(A_in * resp["r"]) ** 2
        m = w > 1e-5 * w.max()
        sx0, sy = resp["sx"][m], resp["sy"][m]; ww = w[m] / w[m].sum()
        kv = k0; b = BETA
        base = sx0 - kv * np.sin(np.radians(lay[k]["out"]))   # odchylenie od środka wiązki
        for j in range(len(lay)):
            if j == k:
                continue
            T = []
            for u in us:
                sx = kv * np.sin(np.radians(lay[j]["out"] + u)) + base
                sig = unit(sx, sy, b, False)
                t = kogc(sig, -lay[j]["K"], lam0, lay[j]["L"], lay[j]["n1"])[1]
                T.append(float((ww * np.abs(t) ** 2).sum()))
            out[(j, k)] = np.array(T)
    return out


def robust_step(curves, us, N, E2, lo=0.03, hi=0.35, thr=0.95, pairs_from=None):
    """Najmniejszy krok δ, dla którego T_eff[j][k](u) ≥ thr w całym przedziale (k−j)·δ ± E2 dla wszystkich par j < k < N.
    E2 — względny błąd kierunku dwóch warstw (suma błędów pojedynczych)."""
    for d in np.arange(lo, hi, 0.0005):
        ok = True
        for k in range(1, N):
            for j in range(k):
                c = curves.get((j, k)) if pairs_from is None else curves[pairs_from(j, k)]
                u = np.linspace((k - j) * d - E2, (k - j) * d + E2, 41)
                if np.interp(u, us, c).min() < thr:
                    ok = False; break
            if not ok:
                break
        if ok:
            return d
    return np.nan


def sec_tolerancje():
    log = Log("tolerancje")
    lay = design()
    log(f"== 4. Budżet tolerancji (L = {L0 * 1e3:.2f} mm, krok {STEP0}°; kąty wyjścia w powietrzu) ==")
    log("Interpretacja „±0,02°” z iteracji 24: okno ±0,02° wokół k·δ w przepuszczalności portu = błąd WZGLĘDNY kierunku dwóch "
        "warstw. Przy niezależnym błędzie pojedynczej warstwy ±E błąd względny sięga ±2E; iteracja 24 przeliczyła ±0,02° na "
        "tolerancję jednej warstwy (okres 4·10⁻⁵, skos 0,013°) — niespójnie o czynnik 2.")
    # --- współczynniki wrażliwości
    steps = dict(eps=1e-5, phi=1e-3, tx=1e-3, psi=1e-2, dn=1e-5, lam=1e-12, ain=1e-3)
    units = dict(eps="°/1e-5", phi="°/0,001°", tx="°/0,001°", psi="°/0,01°", dn="°/1e-5", lam="°/1 pm", ain="°/0,001°")
    names = dict(eps="okres δΛ/Λ", phi="skos / pochylenie płytki w x–z", tx="pochylenie płytki w y–z",
                 psi="obrót w płaszczyźnie płytki", dn="średni n płytki", lam="długość fali (wspólna)",
                 ain="kąt wejścia kanału (x)")
    coef = {}
    log("\n-- współczynniki: zmiana kierunku wyjścia x (y) i względne η: C0 = bez kalibracji (wejście nominalne); "
        "C1 = kąt wejścia kanału (x, y) dobrany do maksimum Bragga i wyjścia y = 0 --")
    for k, l in enumerate(lay):
        a_in = (np.degrees(np.arcsin(n0 * np.sin(np.radians(l["th"])))), 0.0)
        ox0, oy0, e0, _ = grating_io(l["K"], a_in=a_in)
        for key, s in steps.items():
            K2 = l["K"]; lam = lam0; n = n0; ai = a_in
            if key in ("eps", "phi", "tx", "psi"):
                K2 = rotK(l["K"], **{key: s})
            elif key == "dn":
                n = n0 + s
            elif key == "lam":
                lam = lam0 + s
            elif key == "ain":
                ai = (a_in[0] + s, 0.0)
            ox, oy, e, _ = grating_io(K2, lam=lam, n=n, a_in=ai)
            oxm, oym, em, aim = grating_io(K2, lam=lam, n=n, a_in=ai, match=True)
            coef[(k, key)] = dict(c0x=ox - ox0, c0y=oy - oy0, c1x=oxm - ox0, c1y=oym - oy0, dain=aim[0] - a_in[0],
                                  ain_y=aim[1])
    for key in steps:
        log(f"  {names[key]} [{units[key]}]: " + "; ".join(
            f"k={k}: C0 x {coef[(k, key)]['c0x']:+.4f} y {coef[(k, key)]['c0y']:+.4f}, C1 x {coef[(k, key)]['c1x']:+.4f} "
            f"(wejście {coef[(k, key)]['dain']:+.4f}° x, {coef[(k, key)]['ain_y']:+.4f}° y)" for k in (0, 2, 4)))
    # η bez kalibracji: przykładowe wartości błędów
    log("\n-- C0: η/η0 i przesunięcie wyjścia x dla przykładowych błędów (warstwa 4) --")
    l = lay[4]; a_in = (np.degrees(np.arcsin(n0 * np.sin(np.radians(l["th"])))), 0.0)
    ox0, _, e0, _ = grating_io(l["K"], a_in=a_in)
    for key, val in (("eps", 1e-5), ("eps", 1e-4), ("eps", 5e-4), ("phi", 0.005), ("phi", 0.02), ("phi", 0.1),
                     ("tx", 0.02), ("tx", 0.1), ("psi", 0.1), ("psi", 1.0), ("dn", 1e-4)):
        K2 = rotK(l["K"], **{key: val}) if key != "dn" else l["K"]
        ox, oy, e, _ = grating_io(K2, n=n0 + (val if key == "dn" else 0), a_in=a_in)
        oxm, oym, em, aim = grating_io(K2, n=n0 + (val if key == "dn" else 0), a_in=a_in, match=True)
        log(f"  {names[key]} = {val:g}: C0 η/η0 = {e / e0:.3f}, wyjście x {ox - ox0:+.4f}°, y {oy:+.4f}°; "
            f"C1: η/η0 = {em / e0:.3f}, wyjście x {oxm - ox0:+.4f}°, wejście zmienione o {aim[0] - a_in[0]:+.4f}° (x), "
            f"{aim[1]:+.4f}° (y)")
    # --- krzywe portów (widmo wiązki) i liczba warstw w funkcji błędu
    g = Grid(512, 512, 12e-3, 12e-3)
    A_in = gauss_in(g)
    us = np.linspace(-0.6, 0.6, 1201)
    curves = port_curves(lay, g, A_in, us)
    np.savez(OUT / "porty.npz", us=us, **{f"T{j}{k}": v for (j, k), v in curves.items()})
    up_pairs = {key: v for key, v in curves.items() if key[0] < key[1]}
    gen = lambda j, k: (min(4, j), min(4, j + (k - j))) if (j, k) in curves else (0, min(4, k - j))
    log("\n-- przepuszczalność portu dla wiązki (widmo 2D woksla) przy odstępie u od wyjścia warstwy wyżej --")
    for (j, k), v in sorted(up_pairs.items()):
        if k - j == 1 or (j, k) == (0, 4):
            log(f"  port {j} dla wiązki {k}: T(u) = " + ", ".join(f"{u:.2f}°: {np.interp(u, us, v):.3f}"
                                                              for u in (0.0, 0.06, 0.09, 0.11, 0.14, 0.22, 0.33, 0.44)))
    # pary dla N > 5: krzywe pary (0, m) — przybliżenie (wiązka warstwy najgłębszej dostępnej)
    pf = lambda j, k: (j, k) if k < 5 else (min(j, 3), 4) if (min(j, 3), 4) in curves else (0, 4)
    log("\n-- najmniejszy krok δ (T_eff ≥ 0,95 w oknie ±2E wokół k·δ) i liczba warstw; E — błąd pojedynczej warstwy --")
    tab = []
    for E in (0.0, 0.005, 0.01, 0.015, 0.02, 0.03, 0.04):
        row = [robust_step(curves, us, N, 2 * E, pairs_from=pf) for N in range(2, 7)]
        tab.append((E, row))
        log(f"  E = ±{E:.3f}° (względny ±{2 * E:.3f}°): " + ", ".join(
            f"N={N}: δ = {d:.4f}° (wachlarz {(N - 1) * d:.3f}°)" if np.isfinite(d) else f"N={N}: brak"
            for N, d in zip(range(2, 7), row)))
    d5 = STEP0
    Emax = 0.0
    for E in np.arange(0, 0.05, 0.0005):
        ok = all(np.interp(np.linspace((k - j) * d5 - 2 * E, (k - j) * d5 + 2 * E, 41), us, curves[(j, k)]).min() >= 0.95
                 for k in range(1, 5) for j in range(k))
        if ok:
            Emax = E
        else:
            break
    log(f"  konfiguracja iteracji 24 (5 warstw, δ = 0,110°): dopuszczalny błąd pojedynczej warstwy E ≤ ±{Emax:.4f}° "
        f"(względny ±{2 * Emax:.4f}°); przy względnym ±0,04° — " + (
            "spełnione" if all(np.interp(np.linspace((k - j) * d5 - 0.04, (k - j) * d5 + 0.04, 41), us, curves[(j, k)]).min()
                               >= 0.95 for k in range(1, 5) for j in range(k)) else "NIESPEŁNIONE: " + ", ".join(
                f"port {j}/wiązka {k}: min T = {np.interp(np.linspace((k - j) * d5 - 0.04, (k - j) * d5 + 0.04, 81), us, curves[(j, k)]).min():.3f}"
                for k in range(1, 5) for j in range(k)
                if np.interp(np.linspace((k - j) * d5 - 0.04, (k - j) * d5 + 0.04, 81), us, curves[(j, k)]).min() < 0.95)))
    # --- C1': odstrojenie wejścia w akceptacji (η ≥ 0,9 maksimum)
    log("\n-- C1': kąt wejścia odstrojony od Bragga w granicy η ≥ 0,9·η_max (wyjście przesuwa się 1:1 w kx) --")
    for k in (0, 4):
        resp = stack_response(lay, k, g, "B")
        base_ain = np.degrees(np.arcsin(n0 * np.sin(np.radians(lay[k]["th"]))))
        def eta_d(dd):
            A = gauss_in(g) * 1.0
            ph = np.exp(1j * 0)
            kx_shift = k0 * (np.sin(np.radians(base_ain + dd)) - np.sin(np.radians(base_ain)))
            # przesunięcie widma wejścia o Δkx: przemnożenie pola przez exp(−jΔkx·x)
            E_ = g.ifft(A) * np.exp(-1j * kx_shift * g.x[:, None])
            A2 = g.fft(E_)
            r = stack_response(lay, k, g, "B")["r"]
            return float((np.abs(A2 * r) ** 2).sum()), kx_shift
        e0, _ = eta_d(0.0)
        dd = np.linspace(0, 0.08, 81)
        vals = [eta_d(x)[0] / e0 for x in dd]
        dmax = dd[np.argmax(np.array(vals) < 0.9) - 1] if min(vals) < 0.9 else dd[-1]
        out_shift = np.degrees(k0 * (np.sin(np.radians(base_ain + dmax)) - np.sin(np.radians(base_ain))) / k0
                               / np.cos(np.radians(lay[k]["out"])))
        log(f"  k={k}: odstrojenie wejścia ±{dmax:.3f}° (η wiązki ≥ 0,9) przesuwa wyjście o ±{out_shift:.3f}°")
    # --- jednorodność w grubości: gradient n0 (Lumeau i Glebov 2015: ~20–28 ppm/mm)
    log("\n-- jednorodność w grubości: liniowy gradient średniego n przez płytkę (model plastrowy, 200 plastrów) --")
    l = lay[0]; a_in = np.degrees(np.arcsin(n0 * np.sin(np.radians(l["th"]))))
    das = np.linspace(-0.2, 0.2, 401)
    for gr in (0.0, 10e-6, 25e-6, 50e-6):
        dnf = lambda z, gr=gr: gr * 1e3 * (z - L0 / 2)
        eta = np.array([abs(kog_chirp(dirs(a_in + d), l["K"], lam0, L0, NL / L0, dnf)[0]) ** 2 for d in das])
        Tp = np.array([abs(kog_chirp(dirs(d) * np.array([1, 1, -1]), -l["K"], lam0, L0, NL / L0, dnf)[1]) ** 2
                       for d in (0.11, 0.14, 0.22)])
        log(f"  gradient {gr * 1e6:.0f} ppm/mm (±{gr * 1e3 * L0 / 2 * 1e6:.1f} ppm w płytce): η max {eta.max():.4f} przy "
            f"{das[np.argmax(eta)]:+.4f}°, akceptacja FWHM {fwhm_1d(das, eta):.4f}°, port T(0,11/0,14/0,22°) = "
            + "/".join(f"{t:.3f}" for t in Tp))
    np.savez(OUT / "tolerancje.npz", coef=np.array([(k, key, v["c0x"], v["c0y"], v["c1x"], v["c1y"], v["dain"])
                                                   for (k, key), v in coef.items()], dtype=object), allow_pickle=True)
    json.dump({f"{E}": [None if not np.isfinite(d) else d for d in row] for E, row in tab},
              open(OUT / "tolerancje_kroki.json", "w"), indent=1)


# ---------------------------------------------------------------- sekcja 5: przesłuch
def ghost_pupil(lay, k, j, g, A_in, lam=lam0):
    """Odbicie warstwy j ≠ k przy sondzie kanału k (wejście θ_k, talia w płaszczyźnie k): widmo przy oku we własnej
    ramce, przesunięcie ramki X_g względem woksla k, kierunek, położenie pozornego źródła w warstwie j."""
    b = BETA
    rx0 = b * np.sin(np.radians(lay[k]["th"]))
    kx = rx0 + g.KX
    rho = unit(kx, g.KY, b, True)
    r = kogc(rho, lay[j]["K"], lam, lay[j]["L"], lay[j]["n1"])[0]
    sx = kx - lay[j]["K"][0]
    sig = unit(sx, g.KY, b, False)
    tdn = np.ones_like(r); tup = np.ones_like(r)
    for i in range(j):
        tdn *= kogc(rho, lay[i]["K"], lam, lay[i]["L"], lay[i]["n1"])[1]
        tup *= kogc(sig, -lay[i]["K"], lam, lay[i]["L"], lay[i]["n1"])[1]
    dz = lay[j]["z"] - lay[k]["z"]
    rz = np.sqrt(np.maximum(b**2 - kx**2 - g.KY**2, 0))
    o = np.arcsin((rx0 - lay[j]["K"][0]) / k0)
    x_src = dz * np.tan(np.radians(lay[k]["th"]))
    X = x_src + lay[j]["z"] * np.tan(np.arcsin(np.sin(o) / n0)) + D * np.tan(o)
    kzg = np.sqrt(np.maximum(b**2 - sx**2 - g.KY**2, 0)); kza = np.sqrt(np.maximum(k0**2 - sx**2 - g.KY**2, 0))
    lin = rz.ravel()[0] if False else 0
    # propagacja sondy z płaszczyzny k do j (Δz może być ujemne — pole zadane w płaszczyźnie k)
    A = A_in * np.exp(-1j * rz * dz) * tdn * r * tup * np.exp(-1j * (kzg * lay[j]["z"] + kza * D)) * np.sqrt(T_OUT)
    A = A * np.exp(-1j * g.KX * X)
    return A, X, np.degrees(o), x_src


def etalon_ghost(lay, k, g, A_in, Rs):
    """Duch powierzchniowy: sygnał kanału k odbity od górnej powierzchni (od środka), w dół przez cały stos, odbity od
    dolnej powierzchni, w górę przez cały stos. Zwraca widmo przy oku w ramce sygnału (ta sama nośna)."""
    resp = stack_response(lay, k, g, "C")
    b = BETA
    sx, sy = resp["sx"], resp["sy"]
    dn = unit(sx, sy, b, True); up = unit(sx, sy, b, False)
    H = lay[-1]["z"] + lay[-1]["L"]
    t2 = np.ones_like(resp["r"])
    for l in lay:
        t2 *= kogc(dn, l["K"], lam0, l["L"], l["n1"])[1] * kogc(up, -l["K"], lam0, l["L"], l["n1"])[1]
    kzg = np.sqrt(np.maximum(b**2 - sx**2 - sy**2, 0))
    A_s, X = to_pupil(resp, lay, k, g, A_in)
    return A_s, A_s * Rs * t2 * np.exp(-1j * kzg * 2 * H), H


def sec_przesluch():
    log = Log("przesluch")
    g = Grid(); eye = Eye(g); A_in = gauss_in(g)
    log("== 5. Przesłuch (oświetlenie koherentne; mianownik = moc sygnału woksla w tej samej źrenicy) ==")
    log("Źródła: (a) odbicia poza Braggiem innych warstw od wiązki sondy, (b) porty (odbicie sygnału w dół — strata),"
        " (c) duch etalonowy powierzchni. Duch trafia do źrenicy, gdy środek jego wiązki przy oku leży w zasięgu źrenicy "
        "dla położeń oka, z których widać woksel sygnału.")
    for dth, lab in ((2.0, "kanały co 2° (projekt)"), (0.38, "kanały gęste co 0,38°")):
        lay = design(dth=dth)
        log(f"\n-- {lab} --")
        for k in (0, 2, 4):
            cf = channel_fields(lay, k, g, "C", A_in)
            Es = g.ifft(cf["A_p"]); Cs = capture_map(g, Es)
            s_k = peak_pos(g.x, layer_profile(g, cf["A_v"])[1])
            Xs = cf["X"]
            # położenia oka, z których woksel widać (moc ≥ 50% C_max): przedział w ramce sygnału
            row = Cs[:, g.ny // 2]
            vis = g.x[row >= 0.5 * row.max()]
            tot_pupil, tot_cell = 0.0, 0.0
            for j in range(5):
                if j == k:
                    continue
                Ag, Xg, og, xsrc = ghost_pupil(lay, k, j, g, A_in)
                Pg = float((np.abs(Ag) ** 2).sum())
                Eg = g.ifft(Ag); Cg = capture_map(g, Eg)
                # oko w położeniu e (ramka sygnału) → w ramce ducha: e + Xs − Xg
                worst = 0.0
                for e in vis[::4]:
                    eg = e + Xs - Xg
                    if abs(eg) > g.wx / 2 - PUPIL:
                        continue
                    ig = int(round(eg / g.dx)) + g.nx // 2
                    cs = row[int(round(e / g.dx)) + g.nx // 2]
                    worst = max(worst, Cg[ig, g.ny // 2] / cs)
                # pozorne źródło ducha w warstwie j a woksel sygnału: odległość boczna i kątowa
                sep = (xsrc - s_k)
                tot_pupil += worst
                log(f"  sonda k={k}, warstwa j={j}: moc ducha {Pg:.1e} (sygnał przy powierzchni {cf['P']['air']:.3f}), "
                    f"kierunek {og:+.2f}° (sygnał {lay[k]['out']:+.2f}°), środek przy oku o {(Xg - Xs) * 1e3:+.2f} mm od "
                    f"sygnału; w źrenicy (najgorsze położenie oka): {worst:.1e} sygnału; pozorne źródło "
                    f"{sep * 1e6:+.0f} µm od woksla ({sep / D * ARCMIN:+.1f}′) w głębokości warstwy {j}"
                    + (" → poza komórką woksla" if abs(sep) > 165e-6 else " → W KOMÓRCE WOKSLA"))
            log(f"  sonda k={k}: suma duchów w źrenicy ≤ {tot_pupil:.1e} sygnału (suma natężeń; amplitudowo "
                f"≤ {(np.sqrt(tot_pupil) if tot_pupil > 0 else 0):.1e})")
            if dth == 2.0:
                resp = cf["resp"]
                ports = float((np.abs(A_in * resp["r"] * resp["tdn"]) ** 2 * (1 - np.abs(resp["tup"]) ** 2)).sum())
                log(f"  sonda k={k}: (b) moc odbita przez porty w dół {ports:.3f} (opuszcza stos dołem, nie trafia do oka)")
                for Rs in (0.04, 0.0025):
                    A_s, A_g, H = etalon_ghost(lay, k, g, A_in, Rs)
                    Fs = eye.image(g.ifft(A_s), g.nx // 2, g.ny // 2, 1 / cf["Deff"], cx=cf["th_nom"], field=True)
                    Fg = eye.image(g.ifft(A_g), g.nx // 2, g.ny // 2, 1 / cf["Deff"], cx=cf["th_nom"], field=True)
                    i, jj = np.unravel_index(np.argmax(np.abs(Fs)), Fs.shape)
                    mod = 2 * abs(Fg[i, jj]) / abs(Fs[i, jj])
                    log(f"  sonda k={k}: (c) duch etalonowy R = {Rs:.2%} na obu powierzchniach (stos {H * 1e3:.2f} mm): "
                        f"moc {float((np.abs(A_g) ** 2).sum()) / float((np.abs(A_s) ** 2).sum()):.1e} sygnału, "
                        f"modulacja interferencyjna w szczycie obrazu ±{mod:.1%}")


# ---------------------------------------------------------------- sekcja 6: grubość
def sec_grubosc():
    log = Log("grubosc")
    g = Grid(512, 512, 12e-3, 12e-3); eye = Eye(g); A_in = gauss_in(g)
    us = np.linspace(-0.6, 0.6, 601)
    Ls = np.round(np.arange(0.75e-3, 1.0001e-3, 0.025e-3), 6)
    log("== 6. Gęste przemiatanie grubości L (n1·L = 0,2 µm, wejścia 20–28°, w0x = 150 µm, w0y = 25 µm, siatka 512²) ==")
    log("Dla każdego L: krok δ (T_eff ≥ 0,95 w oknie ±2E), najmniejszy skok woksla z kontrastem ≥ 0,5 na siatkówce "
        "(warstwa 0 i 4, warianty A/B/C), wspólny obszar N warstw (mapa mocy 2D warstwy 4 + przedział kontrastu, "
        "przesunięcia warstw D·tan(o_k) i ±D·E), moc najsłabszego kanału w źrenicy.")
    rows = []
    for L in Ls:
        t0 = time.time()
        lay = design(L=L, step=0.11)
        curves = {}
        for k in range(5):
            resp = stack_response(lay, k, g, "B")
            w = np.abs(A_in * resp["r"]) ** 2; m = w > 1e-5 * w.max()
            ww = w[m] / w[m].sum(); base = resp["sx"][m] - k0 * np.sin(np.radians(lay[k]["out"]))
            for j in range(k):
                T = []
                for u in us:
                    sig = unit(k0 * np.sin(np.radians(lay[j]["out"] + u)) + base, resp["sy"][m], BETA, False)
                    T.append(float((ww * np.abs(kogc(sig, -lay[j]["K"], lam0, L, NL / L)[1]) ** 2).sum()))
                curves[(j, k)] = np.array(T)
        pf = lambda j, k: (j, k) if k < 5 else (min(j, 3), 4)
        steps = {E: [robust_step(curves, us, N, 2 * E, pairs_from=pf) for N in range(2, 7)] for E in (0.0, 0.01, 0.02)}
        # woksle
        pm = {}
        for k in (0, 4):
            for var in "ABC":
                pm[(k, var)] = pmin_retina(g, eye, channel_fields(lay, k, g, var, A_in)) * 1e6
        p0 = np.ceil(max(pm[(0, "C")], pm[(4, "C")]) / 10) * 10 * 1e-6
        pitches = [round(p0 + i * 20e-6, 7) for i in range(11)]
        cf4 = channel_fields(lay, 4, g, "C", A_in)
        E4 = g.ifft(cf4["A_p"]); C4 = capture_map(g, E4)
        offs = np.arange(-int(3.6e-3 / g.dx), int(3.6e-3 / g.dx) + 1, 2)
        sc = pupil_scan(g, eye, cf4, offs, np.zeros_like(offs), p_list=pitches)
        ox = np.array([r["ox"] for r in sc]); sh = np.array([r["sh"] for r in sc]); sh0 = np.interp(0, ox, sh)
        capmask = np.roll(C4[::-1, ::-1], (1, 1), axis=(0, 1)) >= 0.5 * C4.max()
        res = {}
        for p in pitches:
            okx = np.array([r[f"c{p * 1e6:.0f}"] >= 0.5 and abs(r["sh"] - sh0) * cf4["Deff"] <= p / 4 for r in sc])
            okg = np.interp(-g.x, ox, okx.astype(float), left=0, right=0) > 0.5
            base_mask = capmask & okg[:, None]
            for E in (0.0, 0.01, 0.02):
                for N in range(1, 7):
                    d = 0.0 if N == 1 else steps[E][N - 2]
                    if not np.isfinite(d):
                        continue
                    mask = np.ones_like(base_mask)
                    for i in range(N):
                        sx_ = int(round(D * np.tan(np.radians((i - (N - 1) / 2) * d)) / g.dx))
                        mask &= np.roll(base_mask, -sx_, axis=0)
                    # błędy bezwzględne ±E przesuwają łatki warstw skrajnych o ±D·E
                    ex = int(round(D * np.tan(np.radians(E)) / g.dx))
                    if ex:
                        mask &= np.roll(mask, ex, axis=0) & np.roll(mask, -ex, axis=0)
                    tot = count_grid(mask, g.dx, g.dy, p, PY) * N
                    if tot > res.get((E, N), (-1,))[0]:
                        res[(E, N)] = (tot, count_grid(mask.any(axis=1)[:, None], g.dx, g.dy, p, 1e9), p * 1e6,
                                       mask.any(axis=1).sum() * g.dx * 1e3)
        for E in (0.0, 0.01, 0.02):
            for N in range(1, 7):
                res.setdefault((E, N), (0, 0, np.nan, 0.0))
        p = p0
        Pw = cf4["P"]["air"] * C4.max() / max(cf4["P"]["air"], 1e-12)
        rows.append(dict(L=L * 1e3, steps={str(E): v for E, v in steps.items()}, pm={f"{k}{v}": x for (k, v), x in pm.items()},
                         p=p * 1e6, res={f"{E}|{N}": v for (E, N), v in res.items()}, P4=float(C4.max()),
                         eta4=cf4["P"]["refl"]))
        log(f"L = {L * 1e3:.3f} mm ({time.time() - t0:.0f} s): krok δ dla N = 2…6 przy E = 0 / 0,01 / 0,02°: " + " | ".join(
            "/".join(f"{x:.3f}" if np.isfinite(x) else "—" for x in steps[E]) for E in (0.0, 0.01, 0.02)))
        log(f"   skok woksla dla kontrastu 0,5 [µm] warstwa 0 A/B/C = {pm[(0, 'A')]:.0f}/{pm[(0, 'B')]:.0f}/{pm[(0, 'C')]:.0f}, "
            f"warstwa 4 A/B/C = {pm[(4, 'A')]:.0f}/{pm[(4, 'B')]:.0f}/{pm[(4, 'C')]:.0f} → skoki od {p * 1e6:.0f} µm co 20 µm; "
            f"moc kanału 4 w źrenicy {C4.max():.3f}")
        for E in (0.0, 0.01, 0.02):
            log(f"   E = ±{E:.2f}°: woksle we wspólnym obszarze — razem (kolumny x; szerokość x; skok) dla N = 1…6: " + ", ".join(
                f"{res[(E, N)][0]} ({res[(E, N)][1]}; {res[(E, N)][3]:.2f} mm; {res[(E, N)][2]:.0f} µm)" for N in range(1, 7)))
    json.dump(rows, open(OUT / "grubosc.json", "w"), indent=1, default=float)


# ---------------------------------------------------------------- sekcja 7: zbieżność, bilans, apertury
def split_step_C(lay, k, g, A_in, edge=None):
    """Wariant C z jawną propagacją między warstwami i skończoną aperturą siatek wyżej (siatka tylko dla x < edge
    w płaszczyźnie każdej z warstw; poza nią szkło jednorodne). Zwraca widmo przy powierzchni (płaszczyzna z = 0)."""
    b = BETA
    resp = stack_response(lay, k, g, "B")
    sx, sy = resp["sx"], resp["sy"]
    tdn = np.ones_like(resp["r"])
    rho = unit(BETA * np.sin(np.radians(lay[k]["th"])) + g.KX, g.KY, b, True)
    for j in range(k):
        tdn *= kogc(rho, lay[j]["K"], lam0, lay[j]["L"], lay[j]["n1"])[1]
    A = A_in * tdn * resp["r"]
    kzg = np.sqrt(np.maximum(b**2 - sx**2 - sy**2, 0))
    z = lay[k]["z"]
    for j in reversed(range(k)):
        zb = lay[j]["z"] + lay[j]["L"]
        A = A * np.exp(-1j * kzg * (z - zb))            # do dolnej granicy siatki j
        sig = unit(sx, sy, b, False)
        t = kogc(sig, -lay[j]["K"], lam0, lay[j]["L"], lay[j]["n1"])[1]
        if edge is None:
            A = A * t
        else:
            E_ = g.ifft(A)
            ins = (g.x < edge)[:, None]
            A = g.fft(g.ifft(g.fft(E_ * ins) * t)) + g.fft(E_ * (~ins))
        A = A * np.exp(-1j * kzg * lay[j]["L"])
        z = lay[j]["z"]
    return A * np.exp(-1j * kzg * z)


def sec_zbieznosc():
    log = Log("zbieznosc")
    lay = design()
    log("== 7. Zbieżność, bilans energii, apertury ==")
    log("-- siatka kątowa/przestrzenna (warstwa 4, wariant C) --")
    for nx, w in ((512, 12e-3), (1024, 12e-3), (1024, 16e-3), (2048, 24e-3)):
        g = Grid(nx, nx, w, w); eye = Eye(g); A_in = gauss_in(g)
        cf = channel_fields(lay, 4, g, "C", A_in)
        E, I = layer_profile(g, cf["A_v"])
        m = retina_metrics(g, eye, cf, p_list=(400e-6, 460e-6), coh=False)
        log(f"  {nx}² okno {w * 1e3:.0f} mm (dx = {g.dx * 1e6:.1f} µm, dθ = {lam0 / w * 1e3:.3f} mrad): η przy powierzchni "
            f"{cf['P']['top']:.4f}, FWHM warstwy {fwhm_1d(g.x, I) * 1e6:.1f} µm, szczyt {peak_pos(g.x, I) * 1e6:+.1f} µm, "
            f"w źrenicy {m['cap']:.4f}, FWHM siatk. {m['fw'] * ARCMIN:.3f}′, kontrast 400/460 µm {m['c400']:.3f}/{m['c460']:.3f}")
    g = Grid(); eye = Eye(g); A_in = gauss_in(g)
    log("-- widmo źródła (średnia natężeń po długościach fali, gauss FWHM Δλ), warstwa 4, wariant C --")
    for fw, n in ((0.0, 1), (0.01e-9, 5), (0.01e-9, 9), (0.05e-9, 9), (0.05e-9, 17)):
        lams = lam0 + (np.linspace(-1.5, 1.5, n) * fw if n > 1 else np.array([0.0]))
        wts = np.exp(-4 * np.log(2) * ((lams - lam0) / fw) ** 2) if n > 1 else np.array([1.0])
        wts = wts / wts.sum()
        Isum, eta = 0, 0
        for lm, wt in zip(lams, wts):
            cf = channel_fields(lay, 4, g, "C", A_in, lam=lm)
            Isum = Isum + wt * layer_profile(g, cf["A_v"])[1]
            eta += wt * cf["P"]["top"]
        pkl = peak_pos(g.x, Isum)
        a = np.interp(g.x + 200e-6, g.x, Isum)
        log(f"  Δλ = {fw * 1e9:.2f} nm, {n} próbek: η {eta:.4f}, FWHM warstwy {fwhm_1d(g.x, Isum) * 1e6:.1f} µm, "
            f"szczyt {pkl * 1e6:+.1f} µm")
    log("-- bilans energii kanału 4 (moc sondy = 1) --")
    resp = stack_response(lay, 4, g, "C")
    b = BETA; rho = unit(BETA * np.sin(np.radians(lay[4]["th"])) + g.KX, g.KY, b, True)
    P_dn_loss = float((np.abs(A_in) ** 2 * (1 - np.abs(resp["tdn"]) ** 2)).sum())
    A1 = A_in * resp["tdn"]
    r4, t4 = kogc(rho, lay[4]["K"], lam0, lay[4]["L"], lay[4]["n1"])
    P_trans = float((np.abs(A1 * t4) ** 2).sum())
    P_ref = float((np.abs(A1 * r4) ** 2).sum())
    P_top = float((np.abs(A1 * r4 * resp["tup"]) ** 2).sum())
    P_port = P_ref - P_top
    log(f"  straty wejścia (odbicia warstw 0–3 w drodze w dół) {P_dn_loss:.2e}; przejście przez warstwę 4 w dół {P_trans:.4f}; "
        f"odbicie warstwy 4 {P_ref:.4f} = do powierzchni {P_top:.4f} + porty w dół {P_port:.4f}; suma "
        f"{P_dn_loss + P_trans + P_ref:.6f}")
    log("-- propagacja jawna między warstwami i skończona apertura siatek wyżej (warstwa 4) --")
    for edge in (None, 1e-3, 0.4e-3, 0.2e-3, 0.0):
        A = split_step_C(lay, 4, g, A_in, edge)
        resp = stack_response(lay, 4, g, "C")
        kzg = np.sqrt(np.maximum(BETA**2 - resp["sx"]**2 - resp["sy"]**2, 0))
        Av = A * np.exp(1j * kzg * lay[4]["z"])  # wsteczna propagacja do płaszczyzny warstwy 4
        E, I = layer_profile(g, Av)
        lab = "brak krawędzi" if edge is None else f"krawędź siatek 0–3 w x = {edge * 1e3:+.1f} mm od woksla"
        log(f"  {lab}: moc {float((np.abs(A) ** 2).sum()):.4f}, FWHM {fwhm_1d(g.x, I) * 1e6:.1f} µm, szczyt "
            f"{peak_pos(g.x, I) * 1e6:+.1f} µm")
    cf = channel_fields(lay, 4, g, "C", A_in)
    E, I = layer_profile(g, cf["A_v"])
    log(f"  wariant C (iloczyn funkcji przenoszenia): moc {cf['P']['top']:.4f}, FWHM {fwhm_1d(g.x, I) * 1e6:.1f} µm, "
        f"szczyt {peak_pos(g.x, I) * 1e6:+.1f} µm")
    log("-- RCWA: zbieżność (punkt Bragga, L = 0,85 mm) --")
    with Pool(3) as pool:
        out = pool.map(_rcwa_conv, [(3, 32), (5, 32), (3, 16)])
    for (M, spp), (de, R) in zip([(3, 32), (5, 32), (3, 16)], out):
        log(f"  M = {M} (rzędów {2 * M + 1}), {spp} plastrów/okres: η = {de:.5f}, faza R = {np.angle(R):+.4f} rad")


def _rcwa_conv(args):
    M, spp = args
    lay, Lx, sgn = grating(20.0, 0.0, L=L0, n1=NL / L0, spp=spp)
    kx, DEr, DEt, R, T, kzI, kzII = solve(lam0, 20.0, n0, n0, "p", lay, M=M, Lx=Lx, amps=True)
    i = int(np.argmin(np.abs(sgn * kx)))
    return DEr[i], complex(R[i])


def dirs(ax_air, ay_air=0.0):
    ax, ay = np.radians(to_int(ax_air)), np.radians(to_int(ay_air))
    v = np.array([np.sin(ax), np.sin(ay), 0.0]); v[2] = np.sqrt(1 - v[0] ** 2 - v[1] ** 2)
    return v


if __name__ == "__main__":
    secs = sys.argv[1:] or ["rcwa", "warianty", "zrenica", "tolerancje", "przesluch", "grubosc", "zbieznosc"]
    for s in secs:
        globals()["sec_" + s]()
