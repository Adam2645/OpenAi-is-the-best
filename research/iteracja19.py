"""Iteracja 19: grube siatki skośne (L = 1 mm, n1 = 2e-4) w jednej źrenicy; kompensacja translacyjna.

Tor 1: pojedyncza siatka L = 1 mm (akceptacja kątowa, widmo, port) — Kogelnik 3D sprawdzony punktowo
RCWA; stos 5 warstw z wyjściami −0,24 … +0,24° (wachlarz 0,48°) — RCWA; prążki przy wąskim źródle;
stożek woksela potrzebny do akomodacji kontra akceptacja grubej siatki.
Tor 2: wyjścia odchylone o 1–2° i punkty startu przesunięte o −D·tanθ, by wiązki trafiły w źrenicę.
Uruchomienie: python3 research/iteracja19.py
"""
import numpy as np, sys, pathlib
from multiprocessing import Pool
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rcwa import solve

lam0, n0 = 532e-9, 1.5
L1, N1 = 1e-3, 2e-4           # tor 1
D_EYE, PUPIL, BEAM = 300.0, 3.5, 1.0  # mm
M = 3


def to_int(a_air):
    return np.degrees(np.arcsin(np.sin(np.radians(a_air)) / n0))


def grating(theta_in, out_air, L=L1, n1=N1, flip=False, spp=32):
    beta = 2 * np.pi * n0 / lam0
    o, t = np.radians(to_int(out_air)), np.radians(theta_in)
    Kx = beta * (np.sin(t) - np.sin(o))
    Kz = beta * (np.cos(t) + np.cos(o))
    Lz = 2 * np.pi / Kz
    ns = int(round(L / Lz)) * spp
    lay = [{"kind": "slanted", "eps0": n0**2, "e1": n0 * n1, "Kz": -Kz if flip else Kz,
            "L": ns / spp * Lz, "slices": ns}]
    return lay, 2 * np.pi / abs(Kx), np.sign(Kx)


def run(g, kx_in, lam):
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
    """Moc kanału k u widza (jak iteracja17b.channel, z L i n1 jako parametrami)."""
    stack, k, lam, L, n1 = args
    th_k, out_k = stack[k]
    kx_in = n0 * np.sin(np.radians(th_k))
    t_down = 1.0
    for th_j, out_j in stack[:k]:
        kx, DEr, DEt = run(grating(th_j, out_j, L, n1), kx_in, lam)
        t_down *= pick(kx, DEt, kx_in)
    kx, DEr, DEt = run(grating(th_k, out_k, L, n1), kx_in, lam)
    i = np.argmin(np.abs(kx - np.sin(np.radians(out_k))))
    eta, kx_out = DEr[i], kx[i]
    t_up = 1.0
    for th_j, out_j in stack[:k]:
        kx, DEr, DEt = run(grating(th_j, out_j, L, n1, flip=True), kx_out, lam)
        t_up *= pick(kx, DEt, kx_out)
    t_in = 1 - Rp_air(np.degrees(np.arcsin(kx_in)))
    return t_in * t_down * eta * t_up * T_OUT, eta, t_down, t_up


def stray(args):
    """Odbicia warstwy j przy sondzie kanału m: lista (kąt w powietrzu, moc) bez sygnału własnego."""
    stack, m, j, lam, L, n1 = args
    th_m, out_m = stack[m]
    kx_in = n0 * np.sin(np.radians(th_m))
    kx, DEr, DEt = run(grating(*stack[j], L, n1), kx_in, lam)
    ok = (np.abs(kx) < 1) & (DEr > 1e-9)
    if j == m:
        ok &= np.abs(kx - np.sin(np.radians(out_m))) >= 1e-3
    return [(np.degrees(np.arcsin(x)), d) for x, d in zip(kx[ok], DEr[ok])]


def kog(rho_hat, G, lam, L=L1, n1=N1, pol="p"):
    """Kogelnik (odbicie) dla fali rho_hat na siatce G; fala ugięta σ = ρ − G; oś z w dół."""
    beta = 2 * np.pi * n0 / lam
    rho = beta * rho_hat
    sig = rho - G
    nz = np.sign(rho_hat[2])
    cR, cS = rho_hat[2] * nz, sig[2] * nz / beta
    pf = abs(rho_hat @ sig) / np.linalg.norm(sig) if pol == "p" else 1.0
    vt = (beta**2 - sig @ sig) / (2 * beta)
    nu = np.pi * n1 * pf * L / (lam * np.sqrt(abs(cR * cS)))
    xi = -vt * L / (2 * cS)
    root = np.sqrt(nu**2 - xi**2 + 0j)
    if abs(root) < 1e-9:
        return float(nu**2 / (1 + nu**2))
    return float(np.real(1 / (1 + (1 - xi**2 / nu**2) / np.sinh(root) ** 2)))


def K_of(theta_in, out_air):
    beta = 2 * np.pi * n0 / lam0
    t, o = np.radians(theta_in), np.radians(to_int(out_air))
    return beta * np.array([np.sin(t) - np.sin(o), 0.0, np.cos(t) + np.cos(o)])


def dir_down(ax_air, ay_air=0.0):
    ax, ay = np.radians(to_int(ax_air)), np.radians(to_int(ay_air))
    v = np.array([np.sin(ax), np.sin(ay), 0.0]); v[2] = np.sqrt(1 - v[0]**2 - v[1]**2)
    return v


def fwhm(x, y):
    a = x[y >= 0.5 * y.max()]
    return a.max() - a.min()


TH_A = 20.0
STACK = [(20.0 + 2 * k, -0.24 + 0.12 * k) for k in range(5)]

if __name__ == "__main__":
    K = K_of(TH_A, 0.0)
    a_in = np.degrees(np.arcsin(n0 * np.sin(np.radians(TH_A))))  # 30,87° w powietrzu
    print("== 1. Pojedyncza siatka L = 1 mm, n1 = 2·10⁻⁴ (Kogelnik 3D; kontrola RCWA niżej) ==")
    d = np.linspace(-0.3, 0.3, 1201)
    eta_a = np.array([kog(dir_down(a_in + x), K, lam0) for x in d])
    print(f"η szczyt = {eta_a.max():.4f}; akceptacja kątowa wejścia FWHM = {fwhm(d, eta_a):.3f}° w powietrzu "
          f"= {fwhm(to_int(a_in + d), eta_a):.3f}° wewnątrz")
    dl = np.linspace(-0.4e-9, 0.4e-9, 1601)
    eta_l = np.array([kog(dir_down(a_in), K, lam0 + x) for x in dl])
    print(f"widmo: FWHM = {fwhm(dl, eta_l) * 1e9:.3f} nm (L = 100 µm, RCWA: 1,20 nm)")
    for fw in (0.01e-9, 0.05e-9, 0.11e-9, 0.15e-9, 1.5e-9):
        lams = lam0 + np.linspace(-4 * fw, 4 * fw, 801)
        w = np.exp(-0.5 * ((lams - lam0) / (fw / 2.3548)) ** 2)
        e = np.array([kog(dir_down(a_in), K, lm) for lm in lams])
        print(f"  źródło gaussowskie {fw * 1e9:5.2f} nm: η średnie = {(e * w).sum() / w.sum():.4f} "
              f"({(e * w).sum() / w.sum() / eta_a.max():.0%} szczytu)")
    print("port (wiązka w górę z warstwy niżej, odchylona o δ w powietrzu): T = 1 − η")
    up = lambda ax, ay=0.0: dir_down(ax, ay) * np.array([1, 1, -1])
    for dd in (0.0, 0.05, 0.10, 0.12, 0.15, 0.24):
        print(f"  δx = {dd:4.2f}°: T = {1 - kog(up(dd), -K, lam0):.3f};  δx = −{dd:4.2f}°: "
              f"T = {1 - kog(up(-dd), -K, lam0):.3f}")

    with Pool(4) as pool:
        print("\nkontrola RCWA (32 plastry na okres, ~11 s na rozwiązanie):")
        gA, gAf = grating(TH_A, 0.0), grating(TH_A, 0.0, flip=True)
        checks = [("wejście +0,05°", gA, n0 * np.sin(np.radians(to_int(a_in + 0.05))), lam0,
                   kog(dir_down(a_in + 0.05), K, lam0), "r"),
                  ("λ0 + 0,06 nm", gA, n0 * np.sin(np.radians(TH_A)), lam0 + 0.06e-9,
                   kog(dir_down(a_in), K, lam0 + 0.06e-9), "r"),
                  ("port δx = 0,12°", gAf, np.sin(np.radians(0.12)), lam0, 1 - kog(up(0.12), -K, lam0), "t"),
                  ("port δx = 0", gAf, 0.0, lam0, 1 - kog(up(0.0), -K, lam0), "t")]
        res = pool.starmap(run, [(g, kx, lm) for _, g, kx, lm, _, _ in checks])
        for (name, g, kx_in, lm, kv, what), (kx, DEr, DEt) in zip(checks, res):
            if what == "r":
                v = DEr.max()
            else:
                v = pick(kx, DEt, kx_in)
            print(f"  {name}: RCWA {v:.4f}, Kogelnik {kv:.4f}")

        print("\n== 2. Stos 5 warstw L = 1 mm, wyjścia −0,24 / −0,12 / 0 / +0,12 / +0,24° (RCWA) ==")
        lams = [lam0, lam0 - 0.05e-9, lam0 + 0.05e-9]
        tasks = [(STACK, k, lm, L1, N1) for lm in lams for k in range(5)]
        out = pool.map(channel, tasks)
        for i, lm in enumerate(lams):
            row = out[5 * i:5 * i + 5]
            print(f"λ = λ0 {('%+.2f nm' % ((lm - lam0) * 1e9)) if lm != lam0 else ''}: moc w stożku = "
                  + " / ".join(f"{r[0]:.3f}" for r in row) + "  (T portów: "
                  + " / ".join(f"{r[3]:.3f}" for r in row) + ")")
        st = pool.map(stray, [(STACK, m, j, lam0, L1, N1) for m in range(5) for j in range(5)])
        sig = [r[0] for r in out[:5]]
        worst, near = 0.0, (np.inf, 0.0)
        for idx, lst in enumerate(st):
            m = idx // 5
            for ang, pw in lst:
                for _, o in STACK:
                    dist = abs(ang - o)
                    if dist < 0.5:
                        worst = max(worst, pw / sig[m])
                    if pw > 1e-6 and dist < near[0]:
                        near = (dist, pw)
        print(f"obce światło w stożkach ±0,5° wokół wyjść (górne oszacowanie, względem sygnału): {worst:.1e}; "
              f"najbliższy obcy rząd > 10⁻⁶ mocy sondy: {near[0]:.2f}° od wyjścia ({near[1]:.1e})")
        x = D_EYE * np.tan(np.radians([o for _, o in STACK]))
        c = 0.5 * (x.min() + x.max())
        frac = np.clip(np.minimum(x + BEAM / 2, c + PUPIL / 2) - np.maximum(x - BEAM / 2, c - PUPIL / 2), 0, None) / BEAM
        print(f"plamki w 30 cm: {np.round(x, 2)} mm; ułamek wiązki 1 mm w źrenicy 3,5 mm: {np.round(frac, 3)}")

    print("\n== 3. Stożek woksela (akomodacja) kontra gruba siatka ==")
    print(f"oś x: wyjście = wejście przesunięte w kx, więc stożek woksela w x ≤ akceptacja wejścia "
          f"≈ {fwhm(d, eta_a):.2f}° (FWHM) wobec ≥ {np.degrees(PUPIL / D_EYE):.2f}° potrzebnych do wypełnienia źrenicy")
    gy = np.linspace(0, 3, 301)
    eta_y = np.array([kog(dir_down(a_in, g), K, lam0) for g in gy])
    print(f"oś y: η spada do połowy przy {gy[eta_y >= 0.5 * eta_y[0]].max():.2f}° (pow.) — akceptacja wejścia ±"
          f"{gy[eta_y >= 0.5 * eta_y[0]].max():.2f}°")
    Ks = [K_of(th, o) for th, o in STACK]
    th5, o5 = STACK[4]
    cone = np.linspace(-np.degrees(PUPIL / D_EYE) / 2, np.degrees(PUPIL / D_EYE) / 2, 41)
    tr = []
    for g in cone:
        t = 1.0
        for Kj in Ks[:4]:
            t *= 1 - kog(up(o5, g), -Kj, lam0)
        tr.append(t)
    print(f"kanał 5 (+0,24°), stożek w y ±{cone[-1]:.2f}°: przez porty 4 warstw wyżej przechodzi średnio "
          f"{np.mean(tr):.3f} (min {np.min(tr):.3f}); na osi {tr[len(tr) // 2]:.3f}")

    print("\n== 4. Prążki przy wąskim źródle, przekładki 1 mm ==")
    opd = 2 * 1.48 * 1e-3
    for dlw in (0.01e-9, 0.05e-9, 0.11e-9):
        xx = np.pi * opd * dlw / lam0**2
        print(f"  Δλ = {dlw * 1e9:.2f} nm: V = {np.exp(-xx**2 / (4 * np.log(2))):.3f}")
    for R in (0.04, 0.0025):
        g = R * R
        print(f"  powierzchnie R = {R:.4f}: tło koherentne ≤ R² = {g:.1e} sygnału → zafalowanie ≤ ±{2 * np.sqrt(g):.1%}")
    print(f"  okres prążków w λ: λ²/OPD = {lam0**2 / opd * 1e9:.3f} nm")

    print("\n== 5. Tor 2: kompensacja translacyjna (wyjścia 0 / 1 / 1,5 / 2°) ==")
    for th in (1.0, 1.5, 2.0):
        print(f"  wyjście {th}°: start w x = {-D_EYE * np.tan(np.radians(th)):+.1f} mm, kierunek widzenia "
              f"tej warstwy przesunięty o {th}° względem warstwy 0°")
    half = np.degrees((PUPIL + BEAM) / D_EYE) / 2
    print(f"  łatka widoczna z jednej warstwy (wiązki skolimowane): ±{half:.2f}° wokół kierunku wyjścia; "
          f"łatki warstw nakładają się tylko przy Δθ < {2 * half:.2f}°")
    print(f"  pole widzenia jednego oka przy stożku 1°: ≤ p/D + 1° = {np.degrees(PUPIL / D_EYE) + 1:.2f}° "
          f"(≈ {D_EYE * np.radians(np.degrees(PUPIL / D_EYE) + 1):.1f} mm płyty w 30 cm)")
