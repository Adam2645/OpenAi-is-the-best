"""Iteracja 17b: bilans kanałów w stosie skośnych warstw ze źródłem szerokopasmowym.

Iteracja 17 (iteracja17.py) pokazała, że wyjście dolnej warstwy wzdłuż normalnej jest
w 66,5% odbijane z powrotem przez górną warstwę (jej „port wyjściowy” jest dopasowany
Bragga do wiązki biegnącej w górę wzdłuż normalnej). Tu liczymy:
  (a) dwie warstwy, oba wyjścia wzdłuż normalnej (konfiguracja z polecenia),
  (b) dwie warstwy, wyjście B odchylone o δ = 1°, 2°, 3° w powietrzu,
  (c) trzy warstwy z wyjściami 0°, δ, 2δ,
dla linii wąskiej (λ0) i źródła gaussowskiego FWHM 1,5 nm (całkowanie po widmie z
krokiem 0,1 nm, ±3 nm). Kanały łączone niekoherentnie (różnica dróg ~30 mm ≫ L_c).
Uruchomienie: python3 research/iteracja17b.py
"""
import numpy as np, sys, pathlib
from multiprocessing import Pool
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rcwa import solve

lam0, n0, L, n1 = 532e-9, 1.5, 100e-6, 0.002
M = 3
LAMS = lam0 + np.linspace(-3e-9, 3e-9, 61)
FWHM = 1.5e-9


def grating(theta_in, out_air=0.0, flip=False, spp=32):
    """Jak w iteracja17.py; wyjście podane jako kąt w powietrzu."""
    beta = 2 * np.pi * n0 / lam0
    o = np.arcsin(np.sin(np.radians(out_air)) / n0)
    t = np.radians(theta_in)
    Kx = beta * (np.sin(t) - np.sin(o))
    Kz = beta * (np.cos(t) + np.cos(o))
    Lz = 2 * np.pi / Kz
    ns = int(round(L / Lz)) * spp
    lay = [{"kind": "slanted", "eps0": n0**2, "e1": n0 * n1, "Kz": -Kz if flip else Kz,
            "L": ns / spp * Lz, "slices": ns}]
    return lay, 2 * np.pi / abs(Kx), np.sign(Kx)


def run(g, kx_in, lam):
    """g = (lay, Lx, sgn); kx_in = n0·sinθ (= sinθ_powietrze). Zwraca kx (ze znakiem), DEr, DEt."""
    lay, Lx, sgn = g
    th = np.degrees(np.arcsin(sgn * kx_in / n0))
    kx, DEr, DEt = solve(lam, th, n0, n0, "p", lay, M=M, Lx=Lx)
    return sgn * kx, DEr, DEt


def pick(kx, D, target):
    return D[np.argmin(np.abs(kx - target))]


def Rp_air(th_air):
    ti = np.radians(th_air); tt = np.arcsin(np.sin(ti) / n0)
    return ((n0 * np.cos(ti) - np.cos(tt)) / (n0 * np.cos(ti) + np.cos(tt))) ** 2


T_OUT = 1 - ((n0 - 1) / (n0 + 1)) ** 2


def channel(args):
    """Moc kanału k u widza (w kierunku jego wyjścia) przy długości fali lam.
    stack: lista (θ_wewn, wyjście_powietrze) od góry; zwraca (sygnał, η_k, ΠT_w_dół, ΠT_portów)."""
    stack, k, lam = args
    th_k, out_k = stack[k]
    kx_in = n0 * np.sin(np.radians(th_k))
    t_down = 1.0
    for th_j, out_j in stack[:k]:
        kx, DEr, DEt = run(grating(th_j, out_j), kx_in, lam)
        t_down *= pick(kx, DEt, kx_in)
    kx, DEr, DEt = run(grating(th_k, out_k), kx_in, lam)
    kx_out = np.sin(np.radians(out_k))
    i = np.argmin(np.abs(kx - kx_out))
    eta, kx_out = DEr[i], kx[i]          # rzeczywisty kierunek wyjścia przy tej λ
    t_up = 1.0
    for th_j, out_j in stack[:k]:
        kx, DEr, DEt = run(grating(th_j, out_j, flip=True), kx_out, lam)
        t_up *= pick(kx, DEt, kx_out)
    t_in = 1 - Rp_air(np.degrees(np.arcsin(kx_in)))
    return t_in * t_down * eta * t_up * T_OUT, eta, t_down, t_up


def crosstalk(stack, lam=lam0, cone_half=0.5):
    """Górne oszacowania (pełna transmisja warstw nad warstwą odbijającą), przy sondzie kanału m:
    zła_głębia — moc odbita przez warstwy j ≠ m w stożek ±cone_half° wokół wyjścia kanału m;
    inny_stożek — moc odbita przez dowolną warstwę w stożek kanału k o innym kierunku wyjścia;
    najbliższe — (odległość kątowa, moc) najbliższego obcego rzędu > 10⁻⁶ od dowolnego wyjścia."""
    wrong_depth = other_cone = 0.0
    nearest = (np.inf, 0.0)
    for m, (th_m, out_m) in enumerate(stack):
        kx_in = n0 * np.sin(np.radians(th_m))
        for j, (th_j, out_j) in enumerate(stack):
            kx, DEr, DEt = run(grating(th_j, out_j), kx_in, lam)
            ang = np.degrees(np.arcsin(np.clip(kx, -1, 1)))
            ok = np.abs(kx) < 1
            if j != m:
                wrong_depth = max(wrong_depth, DEr[ok & (np.abs(ang - out_m) < cone_half)].sum())
            for k, (_, out_k) in enumerate(stack):
                if abs(out_k - out_m) > 1e-9:
                    other_cone = max(other_cone, DEr[ok & (np.abs(ang - out_k) < cone_half)].sum())
                for i in np.flatnonzero(ok & (DEr > 1e-6)):
                    if j == m and abs(kx[i] - np.sin(np.radians(out_m))) < 0.01:
                        continue  # sygnał własny kanału
                    if abs(ang[i] - out_k) < nearest[0]:
                        nearest = (abs(ang[i] - out_k), DEr[i])
    return wrong_depth, other_cone, nearest


def spectral(pool, stack):
    w = np.exp(-0.5 * ((LAMS - lam0) / (FWHM / (2 * np.sqrt(2 * np.log(2))))) ** 2)
    w /= w.sum()
    out = []
    for k in range(len(stack)):
        res = pool.map(channel, [(stack, k, lm) for lm in LAMS])
        sig = np.array([r[0] for r in res])
        narrow = channel((stack, k, lam0))
        out.append((narrow, (sig * w).sum(), sig))
    return out


def report(pool, title, stack):
    print(f"\n== {title} ==")
    for k, (narrow, wide, sig) in enumerate(spectral(pool, stack)):
        th, o = stack[k]
        print(f"kanał {k + 1} (wejście {th}° wewn → wyjście {o:+.1f}° w powietrzu): "
              f"linia wąska: sygnał {narrow[0]:.4f} (η {narrow[1]:.4f}, T w dół {narrow[2]:.4f}, "
              f"T portów {narrow[3]:.4f}); źródło 1,5 nm: sygnał {wide:.4f}")
    for lm, tag in ((lam0, "λ0"), (lam0 - 1.5e-9, "λ0 − 1,5 nm"), (lam0 + 1.5e-9, "λ0 + 1,5 nm")):
        wd, oc, (dist, pw) = crosstalk(stack, lm)
        print(f"przesłuch przy {tag} (moc sondy, stożek ±0,5°): zła głębia {wd:.1e}, "
              f"stożek innego kanału {oc:.1e}; najbliższy obcy rząd {dist:.2f}° od wyjścia, moc {pw:.1e}")


if __name__ == "__main__":
    with Pool(4) as pool:
        report(pool, "(a) dwie warstwy, oba wyjścia wzdłuż normalnej", [(20.0, 0.0), (22.0, 0.0)])
        for d in (1.0, 2.0, 3.0):
            report(pool, f"(b) dwie warstwy, wyjście B odchylone o {d:.0f}°", [(20.0, 0.0), (22.0, d)])
        for d in (2.0, 3.0):
            report(pool, f"(c) trzy warstwy, wyjścia 0°, {d:.0f}°, {2 * d:.0f}°",
                   [(20.0, 0.0), (22.0, d), (24.0, 2 * d)])
