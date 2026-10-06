"""Iteracja 21: obraz woksla anamorficznego na siatkówce, faza cylindryczna na wejściu, SNR warunku 3.

Woksel: wiązka gaussowska z taliami w0x (płaszczyzna padania) i w0y w warstwie, oglądana z D = 300 mm.
Oko zredukowane: soczewka cienka, f = 17 mm, źrenica 3,5 mm. Pole na siatkówce (we współrzędnych kątowych)
= transformata Fouriera pola w źrenicy pomnożonego przez fazę akomodacji exp(+ik·A·r²/2) i przez źrenicę.
Akomodacja A = 1/D ogniskuje płaszczyznę warstwy (talii), A = 0 — nieskończoność.
Filtr Bragga: amplituda √η(θ) z Kogelnika 3D (iteracja 19; faza odbicia pominięta).
Uruchomienie: python3 research/iteracja21.py
"""
import numpy as np, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from iteracja19 import kog, K_of, dir_down, lam0, n0

D, F_EYE, PUPIL = 0.300, 0.017, 3.5e-3
k = 2 * np.pi / lam0
A_IN = np.degrees(np.arcsin(n0 * np.sin(np.radians(20.0))))
K = K_of(20.0, 0.0)
ARCMIN = np.degrees(1) * 60


def q_field(u, w0, z):
    """Pole 1D wiązki gaussowskiej z talią w0 w z = 0, w odległości z (bez fazy Gouya)."""
    q = z + 1j * np.pi * w0**2 / lam0
    return np.exp(-1j * k * u**2 / (2 * q))


def retina(Ex_fn, Ey_fn, A, x0=0.0, y0=0.0, Ns=700, Npad=4096, win=4.2e-3):
    """Natężenie na siatkówce (kąty) dla pola w źrenicy E(u,v) = Ex(u − x0)·Ey(v − y0)."""
    u = (np.arange(Ns) - Ns / 2) * win / Ns
    U, V = np.meshgrid(u, u, indexing="ij")
    E = Ex_fn(U - x0) * Ey_fn(V - y0)
    E *= np.exp(1j * k * A * (U**2 + V**2) / 2) * ((U**2 + V**2) <= (PUPIL / 2) ** 2)
    G = np.zeros((Npad, Npad), complex)
    G[:Ns, :Ns] = E
    I = np.abs(np.fft.fftshift(np.fft.fft2(G))) ** 2
    th = (np.arange(Npad) - Npad / 2) * lam0 / (Npad * win / Ns)
    return th, I


def fwhm_1d(th, prof):
    p = prof / prof.max()
    i = np.argmax(p)
    l, r = i, i
    while l > 0 and p[l] > 0.5: l -= 1
    while r < len(p) - 1 and p[r] > 0.5: r += 1
    xl = th[l] + (0.5 - p[l]) * (th[l + 1] - th[l]) / (p[l + 1] - p[l])
    xr = th[r - 1] + (0.5 - p[r - 1]) * (th[r] - th[r - 1]) / (p[r] - p[r - 1])
    return xr - xl


def contrast(prof_sum):
    """Kontrast dwóch woksli: (I_max − I_min między nimi)/(I_max + I_min)."""
    i1 = np.argmax(prof_sum)
    p = prof_sum.copy()
    # drugi maksimum poza otoczeniem pierwszego
    j = np.argsort(p)[::-1]
    i2 = next((x for x in j if abs(x - i1) > 2), i1)
    a, b = sorted((i1, i2))
    lo = p[a:b + 1].min() if b > a else p[a]
    hi = min(p[a], p[b])
    return (hi - lo) / (hi + lo)


if __name__ == "__main__":
    print("== 1. Wiązka woksla w źrenicy (300 mm od warstwy) ==")
    for name, w0 in (("x", 150e-6), ("x", 330e-6), ("y", 25e-6)):
        zR = np.pi * w0**2 / lam0
        R = D * (1 + (zR / D) ** 2)
        wz = w0 * np.sqrt(1 + (D / zR) ** 2)
        print(f"  oś {name}, w0 = {w0 * 1e6:.0f} µm: z_R = {zR * 1e3:.1f} mm, R(300 mm) = {R * 1e3:.0f} mm "
              f"(wergencja {1 / R:.2f} D), średnica 1/e² w źrenicy {2 * wz * 1e3:.2f} mm")

    print("\n== 2. Obraz na siatkówce (oko f = 17 mm, źrenica 3,5 mm) ==")
    for w0x in (150e-6, 330e-6):
        w0y = 25e-6
        Ex = lambda u, w=w0x: q_field(u, w, D)
        Ey = lambda v: q_field(v, w0y, D)
        for A, lab in ((1 / D, "+3,33 D (warstwa)"), (0.0, "0 D (nieskończoność)")):
            th, I = retina(Ex, Ey, A)
            i, j = np.unravel_index(np.argmax(I), I.shape)
            fx, fy = fwhm_1d(th, I[:, j]), fwhm_1d(th, I[i, :])
            # dwa sąsiednie woksle (skok 2w0) zapalane kolejno: suma natężeń
            th, Ia = retina(Ex, Ey, A, x0=-w0x)
            th, Ib = retina(Ex, Ey, A, x0=+w0x)
            cx = contrast((Ia + Ib)[:, np.argmax((Ia + Ib).max(axis=0))])
            th, Ia = retina(Ex, Ey, A, y0=-w0y)
            th, Ib = retina(Ex, Ey, A, y0=+w0y)
            cy = contrast((Ia + Ib)[np.argmax((Ia + Ib).max(axis=1)), :])
            print(f"  woksel 2w0 = {2 * w0x * 1e6:.0f} × {2 * w0y * 1e6:.0f} µm, akomodacja {lab}: FWHM x = "
                  f"{fx * ARCMIN:.2f}′ ({fx * F_EYE * 1e6:.1f} µm), y = {fy * ARCMIN:.2f}′ ({fy * F_EYE * 1e6:.1f} µm); "
                  f"kontrast sąsiednich woksli x = {cx:.2f}, y = {cy:.2f}")
    print(f"  dla porównania: granica dyfrakcyjna źrenicy 1,22λ/p = {1.22 * lam0 / PUPIL * ARCMIN:.2f}′, ostrość 1′")

    print("\n== 3. Faza cylindryczna na wejściu (oś x), filtr Bragga, krzywizna przy oku ==")
    eta_c = lambda t: kog(dir_down(A_IN + t), K, lam0)
    eta0 = eta_c(0.0)
    N1d, L1d = 2**15, 40e-3
    x = (np.arange(N1d) - N1d / 2) * L1d / N1d
    fx_ = np.fft.fftfreq(N1d, L1d / N1d)
    th_deg = np.degrees(np.arcsin(np.clip(lam0 * fx_, -1, 1)))
    filt = np.sqrt(np.array([eta_c(t) if abs(t) < 0.6 else 0.0 for t in th_deg]))
    for lab, w_in, R_in in (("talia w warstwie, 2w0 = 0,30 mm", 150e-6, np.inf),
                            ("propozycja: 1 mm, f = −300 mm w warstwie", 0.5e-3, 0.300),
                            ("1 mm, f = −150 mm w warstwie", 0.5e-3, 0.150)):
        E0 = np.exp(-x**2 / w_in**2) * (np.exp(-1j * k * x**2 / (2 * R_in)) if np.isfinite(R_in) else 1)
        S = np.fft.fft(E0)
        P_in = (np.abs(S) ** 2).sum()
        Sr = S * filt
        eta = (np.abs(Sr) ** 2).sum() / P_in
        kz = np.sqrt(np.maximum(k**2 - (2 * np.pi * fx_) ** 2, 0))
        Eeye = np.fft.ifft(Sr * np.exp(-1j * kz * D))
        Ie = np.abs(Eeye) ** 2
        m = Ie > 0.1 * Ie.max()
        ph = np.unwrap(np.angle(Eeye[m]))
        c2 = np.polyfit(x[m], ph, 2, w=np.sqrt(Ie[m]))[0]
        V = -2 * c2 / k  # wergencja [D], dodatnia = rozbieżna
        wd = 2 * np.sqrt((Ie * x**2).sum() / Ie.sum()) * 2
        # obraz w osi x przy akomodacji 3,33 D (1D, szczelina = źrenica)
        Ep = Eeye * np.exp(1j * k * x**2 / (2 * D)) * (np.abs(x) <= PUPIL / 2)
        Ir = np.abs(np.fft.fftshift(np.fft.fft(Ep))) ** 2
        thr = np.fft.fftshift(fx_) * lam0
        print(f"  {lab}: kąty wejścia ±{np.degrees(w_in / R_in) if np.isfinite(R_in) else np.degrees(lam0 / (np.pi * w_in)):.3f}° "
              f"(1/e²) → η = {eta:.3f} ({eta / eta0:.0%}); przy oku: wergencja x = {V:.2f} D (y: 3,33 D), "
              f"szerokość 1/e² ≈ {wd * 1e3:.2f} mm; obraz x przy 3,33 D: FWHM {fwhm_1d(thr, Ir) * ARCMIN:.2f}′")

    print("\n== 4. Warunek 3: SNR detektora przy sondzie 0,50 mW ==")
    h, c, q = 6.626e-34, 2.998e8, 1.602e-19
    P_sig = 0.50e-3 * 0.60  # moc w stożku (η ≈ 0,60 z iteracji 19)
    Rsp = 0.70 * q * lam0 / (h * c)  # krzem, wydajność kwantowa 0,70
    T = 1.0
    print(f"  sygnał {P_sig * 1e3:.2f} mW = {P_sig / (h * c / lam0):.2e} fotonów/s; czułość Si {Rsp:.2f} A/W, "
          f"prąd {Rsp * P_sig * 1e6:.0f} µA")
    for lux, lab in ((0, "ciemnia"), (500, "biuro 500 lx"), (10000, "dzień 10 klx")):
        # tło: światło białe ~ 250 lm/W w zakresie widzialnym, płaskie w 400–700 nm, filtr 10 nm, pole 1 cm²
        P_bg = lux / 250 / 300 * 10 * 1e-4
        i_s, i_b = Rsp * P_sig, Rsp * P_bg
        noise = np.sqrt(2 * q * (i_s + i_b) / (2 * T))
        print(f"  {lab}: tło {P_bg * 1e6:.2f} µW; SNR (szum śrutowy, 1 s) = {i_s / noise:.1e}")
    for rin in (1e-3, 1e-2):
        print(f"  z niestabilnością lasera {rin:.1%} rms w paśmie pomiaru: SNR ≈ {1 / rin:.0f}")
    V532 = 0.8832
    Phi = P_sig * 683 * V532
    Om = (2 * lam0 / (np.pi * 150e-6)) * (2 * lam0 / (np.pi * 25e-6))
    print(f"  jasność: {Phi:.3f} lm w stożku; luminancja woksla 300 × 50 µm ≈ "
          f"{Phi / (300e-6 * 50e-6 * Om):.1e} cd/m² (chwilowo), średnio po polu 4,5 × 7,6 mm ≈ "
          f"{Phi / (4.5e-3 * 7.6e-3 * Om):.1e} cd/m²")
