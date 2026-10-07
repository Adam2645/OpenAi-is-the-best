"""Iteracja 23: kontrast sąsiednich woksli przy oświetleniu koherentnym i adresowanie kątowe warstw.

1. Oś x, oko zogniskowane na warstwie: obraz woksla ≈ |pole odbite w warstwie|² (pole wiązki x ≪ źrenicy, iteracja 21).
   Pole odbite = pole wejściowe przefiltrowane amplitudą √η(θ) siatki 1 mm (Kogelnik 3D, faza odbicia pominięta).
   Para sąsiednich woksli (skok 300 µm, w0x = 150 µm): kolejno, jednocześnie w fazie, w przeciwfazie, podramki
   parzyste/nieparzyste (DMD), dwie podramki z fazą względną 0 i π (modulator fazy).
2. Faza losowa w osi y: warunek, by uśredniła człon interferencyjny w osi x, i koszt kątowy.
3. Adresowanie kątowe: iloczyn czas × pasmo deflektora (TBP = D·Δθ/λ), teleskop, gęstsze kanały
   (rozproszenie poza Braggiem z Kogelnika 3D), dyskretne źródła; strata oświetlenia prostokątnego pola.
Uruchomienie: python3 research/iteracja23.py
"""
import numpy as np, sys, pathlib
from math import erf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from iteracja19 import kog, K_of, dir_down, lam0, n0
from iteracja21 import contrast

A_IN = np.degrees(np.arcsin(n0 * np.sin(np.radians(20.0))))
K = K_of(20.0, 0.0)
W0X, PX = 150e-6, 300e-6

N, LX = 2**14, 20e-3
x = (np.arange(N) - N / 2) * LX / N
fx = np.fft.fftfreq(N, LX / N)
th = np.degrees(np.arcsin(np.clip(lam0 * fx, -1, 1)))
R = np.sqrt(np.array([kog(dir_down(A_IN + t), K, lam0) if abs(t) < 0.6 else 0.0 for t in th]))


def reflect(E):
    return np.fft.ifft(np.fft.fft(E) * R)


def vox(x0, phase=0.0):
    return np.exp(-((x - x0) / W0X) ** 2) * np.exp(1j * phase)


def eff(E):
    return (np.abs(reflect(E)) ** 2).sum() / (np.abs(E) ** 2).sum()


def prof_contrast(I):
    return contrast(I)


if __name__ == "__main__":
    print("== 1. Oś x: dwa sąsiednie woksle po filtrze Bragga (oko na warstwie) ==")
    e1, e2 = vox(-PX / 2), vox(+PX / 2)
    r1, r2 = reflect(e1), reflect(e2)
    eta1 = eff(e1)
    rp_in, rp_anti = reflect(e1 + e2), reflect(e1 - e2)
    eta_in, eta_anti = eff(e1 + e2), eff(e1 - e2)
    cases = [
        ("kolejno (niekoherentnie)", np.abs(r1) ** 2 + np.abs(r2) ** 2, eta1, 1.0),
        ("jednocześnie w fazie", np.abs(rp_in) ** 2, eta_in, 1.0),
        ("jednocześnie w przeciwfazie (0/π)", np.abs(rp_anti) ** 2, eta_anti, 1.0),
        ("podramki nieparzyste/parzyste (DMD)", np.abs(r1) ** 2 + np.abs(r2) ** 2, eta1, 0.5),
        ("dwie podramki: faza względna 0, potem π", (np.abs(rp_in) ** 2 + np.abs(rp_anti) ** 2) / 2,
         (eta_in + eta_anti) / 2, 1.0),
    ]
    print(f"  pojedynczy woksel: η = {eta1:.4f}")
    for lab, I, e, duty in cases:
        print(f"  {lab}: kontrast {prof_contrast(I):.2f}; η = {e:.4f}; czas świecenia woksla {duty:.0%} "
              f"→ moc średnia {e * duty / eta1:.0%} przypadku kolejnego")
    sb = lam0 / (2 * PX)
    print(f"  wzór 0/π o skoku {PX * 1e6:.0f} µm ma składowe kątowe ±λ/(2·skok) = ±{np.degrees(sb):.3f}° "
          f"(akceptacja FWHM 0,122°, połowa 0,061°)")
    # trzy woksle w rzędzie (W-W-W): sąsiedzi i następni sąsiedzi
    e3 = [vox(-PX), vox(0), vox(PX)]
    r3 = [reflect(e) for e in e3]
    inc = sum(np.abs(r) ** 2 for r in r3)
    coh = np.abs(sum(r3)) ** 2
    alt = np.abs(r3[0] - r3[1] + r3[2]) ** 2
    two = (coh + alt) / 2
    m = (np.abs(x) < 1.6 * PX)
    def mod(I):
        p = I[m]
        return (p.max() - p[np.argmin(np.abs(x[m] - PX / 2))]) / (p.max() + p[np.argmin(np.abs(x[m] - PX / 2))])
    print(f"  rząd 3 woksli, głębokość modulacji między sąsiadami: kolejno {mod(inc):.2f}, w fazie {mod(coh):.2f}, "
          f"0/π/0 {mod(alt):.2f}, dwie podramki (0,0,0)+(0,π,0) {mod(two):.2f}")

    print("  kontrast przy zapalaniu kolejnym (po filtrze Bragga) w funkcji talii i skoku:")
    for w in (100e-6, 150e-6, 250e-6, 330e-6):
        row = []
        for pitch in (300e-6, 400e-6, 500e-6, 660e-6):
            a = reflect(np.exp(-((x + pitch / 2) / w) ** 2)); b = reflect(np.exp(-((x - pitch / 2) / w) ** 2))
            row.append(f"{prof_contrast(np.abs(a) ** 2 + np.abs(b) ** 2):.2f}")
        ra = reflect(np.exp(-(x / w) ** 2)); I = np.abs(ra) ** 2
        half = x[I >= 0.5 * I.max()]
        print(f"    w0x = {w * 1e6:.0f} µm (η = {eff(np.exp(-(x / w) ** 2)):.3f}, FWHM odbitego woksla "
              f"{(half.max() - half.min()) * 1e6:.0f} µm wobec {1.177 * w * 1e6:.0f} µm na wejściu): kontrast przy "
              f"skoku 300 / 400 / 500 / 660 µm = " + " / ".join(row))

    print("\n== 2. Faza losowa w osi y ==")
    print("  maska φ(y) wspólna dla sąsiadów w osi x: I = |E1(x) + E2(x)|²·|g(y)|² — człon interferencyjny bez zmian")
    psf_y = 0.52 / 60 * np.pi / 180 * 0.300
    for ell in (50e-6, 25e-6, 15e-6, 5e-6):
        spread = np.degrees(lam0 / ell)
        print(f"  osobna maska dla każdego woksla, komórka {ell * 1e6:.0f} µm (obraz y na warstwie {psf_y * 1e6:.0f} µm): "
              f"komórek na element rozdzielczości {psf_y / ell:.1f}, rozrzut kątowy y ≈ λ/komórka = {spread:.2f}° "
              f"({'w' if spread <= 1.0 else 'poza'} stożku 1°)")

    print("\n== 3. Adresowanie kątowe warstw ==")
    v_a = 617.0
    for Dw, dth, lab in ((8.7e-3, 13.9, "deflektor o aperturze 8,7 mm, zakres 13,9°"),
                         (1e-3, 13.9 * 8.7, "deflektor 1 mm + teleskop 8,7× (zakres przed teleskopem)")):
        tbp = Dw * np.radians(dth) / lam0
        print(f"  {lab}: Δf = Δθ·v/λ = {np.radians(dth) * v_a / lam0 / 1e6:.0f} MHz, τ = {Dw / v_a * 1e6:.1f} µs, "
              f"TBP = D·Δθ/λ = {tbp:.0f}")
    print("  gęstsze kanały (siatki 1 mm): rozproszenie poza Braggiem i zakres deflektora")
    for s in (2.0, 1.0, 0.5, 0.38, 0.25):
        worst = 0.0
        for dm in (-1, 1):
            t = np.radians(20.0 + dm * s)
            a = np.degrees(np.arcsin(n0 * np.sin(t)))
            worst = max(worst, kog(dir_down(a), K, lam0))
        off = np.degrees(np.arcsin(n0 * np.sin(np.radians(20 + s))) - np.arcsin(n0 * np.sin(np.radians(20.0))))
        rng = np.degrees(np.arcsin(n0 * np.sin(np.radians(20 + 4 * s))) - np.arcsin(n0 * np.sin(np.radians(20.0))))
        kx_off = n0 * (np.sin(np.radians(20 + s)) - np.sin(np.radians(20.0)))
        stray = np.degrees(np.arcsin(kx_off))
        print(f"    skok {s:.2f}° wewn ({off:.2f}° pow.): odbicie sąsiedniej siatki ≤ {worst:.1e} "
              f"({worst / 0.665:.1e} sygnału), kierunek ±{stray:.2f}° od wyjścia; 5 kanałów: zakres {rng:.1f}° → "
              f"Δf = {np.radians(rng) * v_a / lam0 / 1e6:.0f} MHz, TBP = {8.7e-3 * np.radians(rng) / lam0:.0f}")
    print("  oświetlenie pola 4,5 × 8,7 mm wiązką gaussowską: jednorodność brzegu kontra wykorzystanie mocy")
    for edge in (0.5, 0.8, 0.9):
        r = np.sqrt(-np.log(edge) / 2)  # a/w dla natężenia brzegu = edge
        f1 = erf(np.sqrt(2) * r)
        print(f"    natężenie na brzegu ≥ {edge:.0%} szczytu: w każdej osi {f1:.2f}, łącznie {f1 * f1:.2f}")
