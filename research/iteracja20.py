"""Iteracja 20: woksel anamorficzny, bezpieczeństwo oka przy skanowaniu, kompensacja błędu okresu kątem wejścia.

Stos z iteracji 19: siatki skośne L = 1 mm, n1 = 2e-4, λ0 = 532 nm, pol. p, wejścia 20–28° wewn.,
wyjścia −0,24 … +0,24°. Rachunek kątowy przez rozkład wiązki na fale płaskie: η_śr = ∫ η(θ)·I(θ) dθ,
η(θ) z Kogelnika 3D (zgodny z RCWA co do 0,0012, iteracja 19).
Uruchomienie: python3 research/iteracja20.py
"""
import numpy as np, sys, pathlib
from math import erf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from iteracja19 import kog, K_of, dir_down, to_int, grating, run, pick, lam0, n0, L1, N1
from rcwa import solve

D_EYE, PUPIL = 300e-3, 3.5e-3
A_IN = np.degrees(np.arcsin(n0 * np.sin(np.radians(20.0))))  # 30,87° w powietrzu


def gauss_avg(f, theta0_deg, n=81):
    """Średnia f(θ) po rozkładzie natężenia exp(−2θ²/θ0²) (θ0 — półkąt 1/e² w powietrzu)."""
    t = np.linspace(-2.5 * theta0_deg, 2.5 * theta0_deg, n)
    w = np.exp(-2 * t**2 / theta0_deg**2)
    return float((np.array([f(x) for x in t]) * w).sum() / w.sum())


def theta0(w0):
    return np.degrees(lam0 / (np.pi * w0))


def in_cone(w0, half=0.5):
    """Ułamek mocy wiązki gaussowskiej (1D) w półkącie `half` stopni."""
    return erf(np.sqrt(2) * half / theta0(w0))


if __name__ == "__main__":
    K = K_of(20.0, 0.0)
    eta0 = kog(dir_down(A_IN), K, lam0)
    print("== 1. Woksel anamorficzny: η w funkcji talii sondy ==")
    print(f"η dla fali płaskiej = {eta0:.4f}")
    print("oś x (płaszczyzna padania), oś y skolimowana:")
    for w0x in (25e-6, 50e-6, 100e-6, 150e-6, 250e-6, 330e-6, 500e-6):
        e = gauss_avg(lambda x: kog(dir_down(A_IN + x), K, lam0), theta0(w0x))
        print(f"  w0x = {w0x * 1e6:5.0f} µm (2w0 = {2 * w0x * 1e3:.2f} mm, θ0 = {theta0(w0x):.3f}°): "
              f"η = {e:.4f} ({e / eta0:.0%} fali płaskiej)")
    print("oś y przy w0x = 330 µm (siatka 2D kątów):")
    tx0 = theta0(330e-6)
    for w0y in (7.5e-6, 10e-6, 19.4e-6, 25e-6, 29e-6, 50e-6):
        ty0 = theta0(w0y)
        e = gauss_avg(lambda y: gauss_avg(lambda x: kog(dir_down(A_IN + x, y), K, lam0), tx0, n=21), ty0, n=41)
        print(f"  w0y = {w0y * 1e6:5.1f} µm (2w0 = {2 * w0y * 1e6:.0f} µm, θ0 = {ty0:.2f}°): η = {e:.4f}; "
              f"moc w stożku ±0,5° w y = {in_cone(w0y):.3f}; stożek 1/e² = {2 * ty0:.2f}° "
              f"({'wypełnia' if 2 * ty0 >= np.degrees(PUPIL / D_EYE) else 'nie wypełnia'} źrenicy 0,67°)")
    w_cone = lam0 / (np.pi * np.radians(0.5))
    w_pupil = lam0 / (np.pi * np.radians(np.degrees(PUPIL / D_EYE) / 2))
    print(f"warunek 1 (półkąt 1/e² ≤ 0,5°): w0y ≥ {w_cone * 1e6:.1f} µm; wypełnienie źrenicy (stożek ≥ 0,67°): "
          f"w0y ≤ {w_pupil * 1e6:.1f} µm")
    for name, (wx, wy) in (("propozycja 2w0 = 300 × 15 µm", (150e-6, 7.5e-6)),
                           ("dopuszczalny 2w0 = 660 × 50 µm", (330e-6, 25e-6))):
        fx = (PUPIL + 2 * wx) / D_EYE + 2 * np.radians(min(theta0(wx), 0.5))
        fy = PUPIL / D_EYE + 2 * np.radians(min(theta0(wy), 0.5))
        nx, ny = fx * D_EYE / (2 * wx), fy * D_EYE / (2 * wy)
        print(f"  {name}: pole widzenia jednego oka {np.degrees(fx):.2f}° × {np.degrees(fy):.2f}° "
              f"({fx * D_EYE * 1e3:.1f} × {fy * D_EYE * 1e3:.1f} mm), woksli {nx:.0f} × {ny:.0f} = {nx * ny:.0f} na warstwę")
    dkx = n0 * (np.sin(np.radians(22.0)) - np.sin(np.radians(20.0)))
    print(f"rzędy SLM: kanały wejścia co Δkx = {dkx:.4f}; rząd m modulatora o skoku p trafia w sąsiedni kanał, "
          f"gdy m·λ/p = Δkx, czyli p = m·{lam0 / dkx * 1e6:.1f} µm (wymagany filtr w płaszczyźnie Fouriera)")

    print("\n== 2. Bezpieczeństwo oka: trzy kryteria ICNIRP 2013 (Tabela 5, apertura 7 mm, 400–700 nm) ==")
    P_eye = 0.60e-3  # moc kanału w źrenicy przy sondzie 1 mW (iteracja 19: 0,586–0,623 mW)

    def el_single(t, CE=1.0):
        """EL dla pojedynczego impulsu [J] (siatkówka, termicznie)."""
        if t < 5e-6:
            return 7.7e-8 * CE
        return 7e-4 * CE * t**0.75

    def el_cw(alpha_mrad):
        """EL dla ekspozycji ≥ T2 [W]: 0,39 mW dla α ≤ 1,5 mrad, inaczej 7e-4·C_E·T2^−0,25."""
        if alpha_mrad <= 1.5:
            return 3.9e-4
        CE = alpha_mrad / 1.5
        T2 = 10 * 10 ** ((alpha_mrad - 1.5) / 98.5)
        return 7e-4 * CE * T2**-0.25

    print(f"moc w źrenicy (kanał, sonda 1 mW): {P_eye * 1e3:.2f} mW; ramka 60 Hz, 5 warstw sekwencyjnie")
    for N in (100, 1000):
        t = 1 / (60 * 5 * N)
        E = P_eye * t
        print(f"  N = {N} woksli/warstwę: impuls {t * 1e6:.2f} µs (T_i = 5 µs), energia {E * 1e9:.1f} nJ; "
              f"kryterium 1: EL = {el_single(t) * 1e9:.0f} nJ → zapas {el_single(t) / E:.0f}×")
        n_spot = 60 * N * 10  # oko ogniskuje na ∞: wszystkie woksle warstwy w jednym miejscu siatkówki
        Cp = max(0.2, 5 * n_spot**-0.25) if t <= 5e-6 else 1.0
        print(f"    kryterium 3 (oko na ∞, {n_spot:.0e} impulsów w T2 = 10 s na jedno miejsce): Cp = {Cp:.2f} "
              f"→ EL·Cp = {el_single(t) * Cp * 1e9:.0f} nJ, zapas {el_single(t) * Cp / E:.1f}×")
    for share, label in ((1.0, "cała treść w jednej warstwie"), (0.2, "treść równo w 5 warstwach")):
        P = P_eye * share
        print(f"  kryterium 2 (średnia w T2 = 10 s na jedno miejsce siatkówki, α ≤ 1,5 mrad), {label}: "
              f"{P * 1e3:.2f} mW wobec {el_cw(1.0) * 1e3:.2f} mW → {P / el_cw(1.0):.2f} AEL")
    a_line = (1.5 + PUPIL / D_EYE * 1e3) / 2
    print(f"  ten sam rachunek dla źródła pozornego w kształcie linii (stożek y w źrenicy, α = (1,5 + "
          f"{PUPIL / D_EYE * 1e3:.1f})/2 = {a_line:.1f} mrad): EL = {el_cw(a_line) * 1e3:.2f} mW → "
          f"{P_eye / el_cw(a_line):.2f} AEL")
    print(f"  sonda, przy której kanał w źrenicy = 0,39 mW: {3.9e-4 / P_eye:.2f} mW")

    print("\n== 3. Kompensacja błędu okresu (δΛ/Λ) i skosu kątem wejścia ==")
    t = np.radians(20.0)
    psi = np.degrees(np.arctan2(np.sin(t), 1 + np.cos(t)))
    print(f"płaszczyzny siatki nachylone o {psi:.1f}°; kąt fali do wektora K: ψ = {20 - psi:.1f}° "
          f"(dψ = ε·cot ψ = {1 / np.tan(np.radians(20 - psi)):.2f}·ε rad)")
    rows = []
    for eps in (-1e-3, -3e-4, -1e-4, 1e-4, 3e-4, 1e-3):
        Ke = K * (1 + eps)
        sc = np.linspace(-1.0, 1.0, 4001)
        e = np.array([kog(dir_down(A_IN + x), Ke, lam0) for x in sc])
        i = np.argmax(e)
        kx_in = np.sin(np.radians(A_IN + sc[i]))
        out = np.degrees(np.arcsin(kx_in - Ke[0] / (2 * np.pi / lam0)))
        e_fix = kog(dir_down(A_IN), Ke, lam0)
        rows.append((eps, sc[i], e[i], out))
        print(f"  δΛ/Λ = {-eps:+.0e}: bez korekty η = {e_fix:.3f}; korekta wejścia {sc[i]:+.3f}° → η = {e[i]:.4f}, "
              f"wyjście przesunięte o {out:+.3f}° ({D_EYE * 1e3 * np.tan(np.radians(out)):+.2f} mm w 30 cm)")
    for dphi in (-0.05, -0.01, 0.01, 0.05):
        r = np.radians(dphi)
        Kr = np.array([K[0] * np.cos(r) - K[2] * np.sin(r), 0.0, K[0] * np.sin(r) + K[2] * np.cos(r)])
        sc = np.linspace(-1.0, 1.0, 4001)
        e = np.array([kog(dir_down(A_IN + x), Kr, lam0) for x in sc])
        i = np.argmax(e)
        kx_in = np.sin(np.radians(A_IN + sc[i]))
        out = np.degrees(np.arcsin(kx_in - Kr[0] / (2 * np.pi / lam0)))
        print(f"  błąd skosu {dphi:+.2f}°: bez korekty η = {kog(dir_down(A_IN), Kr, lam0):.3f}; korekta wejścia "
              f"{sc[i]:+.3f}° → η = {e[i]:.4f}, wyjście przesunięte o {out:+.3f}°")
    # kontrola RCWA dla δΛ/Λ = −1e-4 (K większe o 1e-4): siatka zapisana dla λ_d = λ0/(1+ε)
    eps, da, ek, _ = rows[3]
    import iteracja19 as m19
    m19.lam0 = lam0 / (1 + eps)
    g = grating(20.0, 0.0)
    m19.lam0 = lam0
    kx, DEr, DEt = run(g, np.sin(np.radians(A_IN + da)), lam0)
    print(f"  kontrola RCWA (δΛ/Λ = −1e-4, wejście {da:+.3f}°): η = {DEr.max():.4f} (Kogelnik {ek:.4f})")
