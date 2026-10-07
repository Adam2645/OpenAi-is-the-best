"""Iteracja 22: akomodacja kompromisowa, projekcja warstwowa przez SLM, parametry testu laboratoryjnego.

1. Obraz woksla 300 × 50 µm (w0x = 150 µm, w0y = 25 µm) na siatkówce w funkcji akomodacji A (2,6–3,6 D);
   kontrast sąsiednich woksli: skok x 300 µm, y 90 µm; suma natężeń (woksle zapalane kolejno) albo suma pól
   (woksle zapalane jednocześnie przez SLM i oświetlane koherentnym laserem: fazy zgodne lub przeciwne).
2. Bilans fotometryczny projekcji warstwowej (SLM/DMD), bezpieczeństwo oka, zakres kątowy deflektora.
3. Parametry pierwszej próby z dwiema płytkami PTR 1 mm (RCWA kanału B dla wyjść 0,10° i 0,12°).
Uruchomienie: python3 research/iteracja22.py
"""
import numpy as np, sys, pathlib
from multiprocessing import Pool
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from iteracja21 import q_field, fwhm_1d, contrast, D, F_EYE, PUPIL, ARCMIN
from iteracja19 import channel, lam0, n0, L1, N1, to_int

k = 2 * np.pi / lam0
W0X, W0Y = 150e-6, 25e-6
PX, PY = 300e-6, 90e-6


def retina_field(A, x0=0.0, y0=0.0, Ns=700, Npad=4096, win=4.2e-3):
    u = (np.arange(Ns) - Ns / 2) * win / Ns
    U, V = np.meshgrid(u, u, indexing="ij")
    E = q_field(U - x0, W0X, D) * q_field(V - y0, W0Y, D)
    E = E * np.exp(1j * k * A * (U**2 + V**2) / 2) * ((U**2 + V**2) <= (PUPIL / 2) ** 2)
    G = np.zeros((Npad, Npad), complex)
    G[:Ns, :Ns] = E
    F = np.fft.fftshift(np.fft.fft2(G))
    th = (np.arange(Npad) - Npad / 2) * lam0 / (Npad * win / Ns)
    return th, F


def pair_contrast(A, axis):
    """Kontrast dwóch sąsiednich woksli wzdłuż osi: (niekoherentnie, koherentnie w fazie, w przeciwfazie)."""
    d = (PX if axis == 0 else PY) / 2
    sh = {"x0": d} if axis == 0 else {"y0": d}
    shm = {"x0": -d} if axis == 0 else {"y0": -d}
    th, F1 = retina_field(A, **shm)
    th, F2 = retina_field(A, **sh)
    out = []
    for I in (np.abs(F1) ** 2 + np.abs(F2) ** 2, np.abs(F1 + F2) ** 2, np.abs(F1 - F2) ** 2):
        i, j = np.unravel_index(np.argmax(I), I.shape)
        prof = I[:, j] if axis == 0 else I[i, :]
        out.append(contrast(prof))
    return out


if __name__ == "__main__":
    print("== 1. Akomodacja: obraz woksla 300 × 50 µm i kontrast sąsiadów (x co 300 µm, y co 90 µm) ==")
    for A in (2.6, 2.79, 3.06, 3.20, 3.33, 3.45, 3.6):
        th, F = retina_field(A)
        I = np.abs(F) ** 2
        i, j = np.unravel_index(np.argmax(I), I.shape)
        fx, fy = fwhm_1d(th, I[:, j]), fwhm_1d(th, I[i, :])
        cx, cy = pair_contrast(A, 0), pair_contrast(A, 1)
        print(f"  A = {A:.2f} D: FWHM x = {fx * ARCMIN:.2f}′, y = {fy * ARCMIN:.2f}′; kontrast x (kolejno / jednocz. "
              f"w fazie / w przeciwfazie) = {cx[0]:.2f} / {cx[1]:.2f} / {cx[2]:.2f}; y = {cy[0]:.2f} / {cy[1]:.2f} / {cy[2]:.2f}")
    print(f"  rozmycie geometryczne osi y przy błędzie akomodacji ΔA: p·ΔA = {PUPIL * 0.27 * 1e3:.2f} mrad "
          f"({PUPIL * 0.27 * ARCMIN:.1f}′) dla ΔA = 0,27 D")

    print("\n== 2. Projekcja warstwowa (SLM/DMD), 60 Hz × 5 warstw ==")
    P, T_slm, eta, Nv, nlay = 0.50e-3, 0.65, 0.60, 1100, 5
    Pv = P * T_slm / Nv
    print(f"  moc na woksel w czasie świecenia warstwy: {Pv * 1e9:.0f} nW (przed siatką), {Pv * eta * 1e9:.0f} nW w stożku;"
          f" średnio w czasie (1/{nlay}): {Pv * eta / nlay * 1e9:.1f} nW")
    V532 = 0.8832
    Phi = Pv * eta / nlay * 683 * V532
    Om = (2 * lam0 / (np.pi * W0X)) * (2 * lam0 / (np.pi * W0Y))
    L_vox = Phi / ((2 * W0X) * (2 * W0Y) * Om)
    img = (2.03 / ARCMIN) * (0.52 / ARCMIN)
    L_eq = Phi / (np.pi * (PUPIL / 2) ** 2 * img)
    print(f"  strumień {Phi:.1e} lm na woksel; luminancja woksla (pole 300 × 50 µm, stożek {Om:.1e} sr) "
          f"≈ {L_vox:.1e} cd/m²; równoważna z obrazu na siatkówce (2,03′ × 0,52′, źrenica 3,5 mm) ≈ {L_eq:.1e} cd/m²")
    print(f"  moc sondy dająca 1000 cd/m² (liniowo): {P * 1000 / L_eq * 1e9:.0f} nW")
    # bezpieczeństwo oka (ICNIRP 2013, iteracja 20): cała warstwa zapalona, P w źrenicy = P·T·η
    Pe = P * T_slm * eta

    def el_cw(a):
        if a <= 1.5:
            return 3.9e-4
        return 7e-4 * (min(a, 100) / 1.5) * (10 * 10 ** ((a - 1.5) / 98.5)) ** -0.25
    for a, lab in ((1.5, "oko na ∞, źródło punktowe (najgorzej)"), (4.0, "oko na ∞, plama 1,2 × 6,4 mrad"),
                   (22.0, "oko na warstwie, obraz 15 × 29 mrad")):
        print(f"  pełna warstwa w źrenicy {Pe * 1e3:.3f} mW, {lab}: α = {a} mrad → EL {el_cw(a) * 1e3:.2f} mW, "
              f"{Pe / el_cw(a):.2f} granicy")
    th_air = [np.degrees(np.arcsin(n0 * np.sin(np.radians(20 + 2 * kk)))) for kk in range(5)]
    span = th_air[-1] - th_air[0]
    print(f"  deflektor: kąty wejścia {th_air[0]:.2f}–{th_air[-1]:.2f}° w powietrzu (zakres {span:.1f}°); "
          f"iloczyn zakres × szerokość wiązki dla pola 8,7 mm: {span * 8.7:.0f} °·mm")

    print("\n== 3. Próba laboratoryjna: dwie płytki PTR 1 mm, n1 = 2·10⁻⁴ ==")
    beta = 2 * np.pi * n0 / lam0
    for th, o in ((20.0, 0.0), (22.0, 0.10), (22.0, 0.12)):
        oi = np.radians(to_int(o)); t = np.radians(th)
        K = beta * np.array([np.sin(t) - np.sin(oi), np.cos(t) + np.cos(oi)])
        Lam = 2 * np.pi / np.linalg.norm(K)
        tilt = np.degrees(np.arctan2(K[0], K[1]))
        print(f"  siatka: wejście {th}° wewn ({np.degrees(np.arcsin(n0 * np.sin(t))):.2f}° pow.) → wyjście {o}° pow.: "
              f"okres Λ = {Lam * 1e9:.2f} nm, płaszczyzny nachylone o {tilt:.2f}° do powierzchni")
    with Pool(4) as pool:
        stacks = [[(20.0, 0.0), (22.0, 0.10)], [(20.0, 0.0), (22.0, 0.12)]]
        res = pool.map(channel, [(st, kk, lam0, L1, N1) for st in stacks for kk in range(2)])
    for i, st in enumerate(stacks):
        a, b = res[2 * i], res[2 * i + 1]
        print(f"  wyjścia 0 / {st[1][1]}°: kanał A {a[0]:.3f}, kanał B {b[0]:.3f} (port A przepuszcza {b[3]:.3f})")
    f_lens = 0.200
    print(f"  stożek 1° (pełny): soczewka f = {f_lens * 1e3:.0f} mm + przesłona w ognisku o średnicy "
          f"{2 * f_lens * np.tan(np.radians(0.5)) * 1e3:.2f} mm")
    dz = 2.0e-3
    print(f"  warunek 2: warstwa B leży {dz * 1e3:.0f} mm głębiej (płytka 1 mm + przekładka 1 mm); wejście pod 20°/22° wewn "
          f"przesuwa punkt wyjścia o Δx = Δz·tanθ ≈ {dz * np.tan(np.radians(21)) * 1e3:.2f} mm na powierzchni — "
          f"Δz = Δx/tanθ; 10 µm odpowiada Δx = {10e-6 * np.tan(np.radians(21)) * 1e6:.1f} µm")
