"""Iteracja 18: źrenica widza kontra odchylone wyjścia warstw skośnych.

Sprawdzane hipotezy (z audytu po iteracji 17):
  H1 soczewka polowa f = 300 mm zbiera wyjścia 0/1,5/3/4,5/6° w jednej źrenicy 3,5 mm,
  H2 pojemność 16 warstw (wejście 6,6–38,8° wewn., skok 2°), przekładki 1 mm,
  H3 multipleksowanie azymutalne (obrót wektora K) usuwa cieniowanie bez odchylania wyjść,
  plus RCWA stosu 5 warstw z polecenia i stosów mieszczących się w jednej źrenicy.
Uruchomienie: python3 research/iteracja18.py
"""
import numpy as np, sys, pathlib
from multiprocessing import Pool
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from iteracja17b import channel, crosstalk, lam0, n0, L, n1

D_EYE, PUPIL, BEAM = 300.0, 3.5, 1.0  # mm: odległość widza, źrenica, szerokość wiązki woksela


def pupil_capture(outs):
    """Wiązki z jednego punktu płyty pod kątami outs [°]; źrenica ustawiona centralnie między skrajnymi.
    Zwraca położenia plamek [mm] i ułamek każdej wiązki (cylinder o szerokości BEAM) w źrenicy."""
    x = D_EYE * np.tan(np.radians(outs))
    c = 0.5 * (x.min() + x.max())
    lo = np.maximum(x - BEAM / 2, c - PUPIL / 2)
    hi = np.minimum(x + BEAM / 2, c + PUPIL / 2)
    return x, np.clip(hi - lo, 0, None) / BEAM


print("== 1. Soczewka polowa i niezmiennik Lagrange'a ==")
outs = np.array([0.0, 1.5, 3.0, 4.5, 6.0])
x, f = pupil_capture(outs)
print(f"bez soczewki, 30 cm: plamki {np.round(x, 1)} mm, w źrenicy {PUPIL} mm: {np.round(f, 2)}")
print(f"soczewka f = 300 mm, oko w ognisku: plamki f·tanα = {np.round(300 * np.tan(np.radians(outs)), 1)} mm "
      "(te same — soczewka zamienia kąt na położenie)")
print("układ paraksjalny płyta → źrenica: x_p = A·x + B·α; wszystkie warstwy z całego pola W w źrenicy p "
      "wymagają |A|·W + |B|·Θ ≤ p,\nwięc pozorna odległość obrazu D_app = W/Ω ≤ p/Θ "
      "(Ω — kąt, pod którym oko widzi pole W):")
for th in (0.5, 1.0, 6.0, 22.5):
    print(f"  wachlarz wyjść Θ = {th:4.1f}°: D_app ≤ {PUPIL / np.radians(th):6.1f} mm")
print(f"przy D_app = 300 mm i źrenicy {PUPIL} mm: Θ ≤ {np.degrees(PUPIL / D_EYE):.2f}° "
      f"(z wiązką {BEAM} mm: ≤ {np.degrees((PUPIL - BEAM) / D_EYE):.2f}°)")

# --- RCWA ---
STACKS = {
    "5 warstw, wyjścia +1,5° (polecenie)": [(20.0 + 2 * k, 1.5 * k) for k in range(5)],
    "5 warstw, wyjścia −1,5°": [(20.0 + 2 * k, -1.5 * k) for k in range(5)],
    "5 warstw, wszystkie wyjścia 0°": [(20.0 + 2 * k, 0.0) for k in range(5)],
    "2 warstwy w źrenicy, wyjścia 0 / 0,45°": [(20.0, 0.0), (22.0, 0.45)],
    "3 warstwy w źrenicy, wyjścia 0 / 0,225 / 0,45°": [(20.0, 0.0), (22.0, 0.225), (24.0, 0.45)],
    "4 warstwy w źrenicy, wyjścia 0 / 0,15 / 0,3 / 0,45°": [(20.0 + 2 * k, 0.15 * k) for k in range(4)],
}
FW = 0.15e-9  # źródło gaszące prążki przekładki 1 mm (patrz sekcja 4)
LAMS = lam0 + np.linspace(-0.3e-9, 0.3e-9, 13)
W = np.exp(-0.5 * ((LAMS - lam0) / (FW / (2 * np.sqrt(2 * np.log(2))))) ** 2)
W /= W.sum()


def kogelnik3d(rho_hat, K, pol_factor):
    """Sprawność odbiciowa (Kogelnik) dla fali padającej rho_hat na siatkę K (oś z w głąb warstwy
    wzdłuż kierunku padania); fala ugięta σ = ρ + K."""
    beta = 2 * np.pi * n0 / lam0
    rho = beta * rho_hat
    sig = rho + K
    cR = abs(rho_hat[2])
    cS = np.sign(rho_hat[2]) * sig[2] / beta  # składowa wzdłuż kierunku wnikania; ujemna dla odbicia
    vt = (beta**2 - sig @ sig) / (2 * beta)
    nu = np.pi * n1 * pol_factor * L / (lam0 * np.sqrt(abs(cR * cS)))
    xi = -vt * L / (2 * cS)
    root = np.sqrt(nu**2 - xi**2 + 0j)
    if abs(root) < 1e-9:
        return nu**2 / (1 + nu**2), sig
    return float(np.real(1 / (1 + (1 - xi**2 / nu**2) / np.sinh(root) ** 2))), sig


def pol_factors(rho_hat, sig):
    """Współczynnik sprzężenia dla polaryzacji ⊥ i ∥ do płaszczyzny (ρ, σ)."""
    c = abs(rho_hat @ sig) / np.linalg.norm(sig)
    return 1.0, c


if __name__ == "__main__":
    with Pool(4) as pool:
        print("\n== 2. RCWA: bilans kanałów (linia wąska / źródło gaussowskie 0,15 nm), przesłuch, źrenica ==")
        tasks = [(st, k, lm) for st in STACKS.values() for k in range(len(st)) for lm in [lam0, *LAMS]]
        res = iter(pool.map(channel, tasks))
        for name, st in STACKS.items():
            print(f"\n{name}:")
            for k, (th, o) in enumerate(st):
                narrow = next(res)
                wide = np.array([next(res)[0] for _ in LAMS])
                print(f"  kanał {k + 1}: wejście {th:.0f}° wewn → wyjście {o:+.3g}°: linia wąska {narrow[0]:.4f} "
                      f"(η {narrow[1]:.4f}, T w dół {narrow[2]:.4f}, T portów {narrow[3]:.4f}); "
                      f"źródło 0,15 nm {(wide * W).sum():.4f}")
            wd, oc, (dist, pw) = crosstalk(st)
            x, f = pupil_capture(np.array([o for _, o in st]))
            print(f"  przesłuch (λ0, stożek ±0,5°): zła głębia {wd:.1e}, stożek innego kanału {oc:.1e}; "
                  f"najbliższy obcy rząd {dist:.2f}° od wyjścia ({pw:.1e})")
            print(f"  źrenica {PUPIL} mm w 30 cm: plamki {np.round(x, 2)} mm, ułamek wiązki w źrenicy {np.round(f, 2)}")

    print("\n== 3. Multipleksowanie azymutalne (Kogelnik 3D, port warstwy A) ==")
    beta = 2 * np.pi * n0 / lam0
    t = np.radians(20.0)
    K = beta * np.array([np.sin(t), 0.0, np.cos(t) + 1.0])  # k_in − k_out, z w dół
    print("walidacja na odchyleniu w płaszczyźnie siatki (x) wobec RCWA z iteracji 17 "
          "(T = 0,335 / 0,402 / 0,644 / 0,962 / 0,973):")
    for d_air in (0.0, 0.25, 0.5, 0.75, 1.0):
        a = np.arcsin(np.sin(np.radians(d_air)) / n0)
        rho = np.array([np.sin(a), 0.0, -np.cos(a)])  # w górę
        e, sig = kogelnik3d(rho, K, 1.0)
        pf = pol_factors(rho, sig)[1]
        e, sig = kogelnik3d(rho, K, pf)
        print(f"  δx = {d_air:4.2f}° (pow.): T = {1 - e:.3f}")
    print("odchylenie wyjścia w płaszczyźnie prostopadłej (y), T dla polaryzacji ⊥ / ∥:")
    gam_ok = None
    for g_air in (0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0):
        g = np.arcsin(np.sin(np.radians(g_air)) / n0)
        rho = np.array([0.0, np.sin(g), -np.cos(g)])
        _, sig = kogelnik3d(rho, K, 1.0)
        Ts = [1 - kogelnik3d(rho, K, pf)[0] for pf in pol_factors(rho, sig)]
        if gam_ok is None and min(Ts) >= 0.96:
            gam_ok = g_air
        print(f"  δy = {g_air:4.1f}° (pow.): T = {Ts[0]:.3f} / {Ts[1]:.3f}")
    print(f"T ≥ 0,96 dla obu polaryzacji od δy ≈ {gam_ok}° (w płaszczyźnie siatki: 0,75°)")
    rho = np.array([0.0, 0.0, -1.0])
    e_s = kogelnik3d(rho, K, 1.0)[0]
    print(f"warstwa B obrócona o 90° w azymucie, wyjście wzdłuż normalnej: jej pol. p jest dla A pol. s → "
          f"A odbija {e_s:.3f}, przepuszcza {1 - e_s:.3f} (bez obrotu: 0,335)")

    print("\n== 4. Prążki przekładki 1 mm i głębia 16 mm ==")
    opd = 2 * 1.48 * 1e-3
    for dl in (0.02e-9, 0.05e-9, 0.11e-9, 0.15e-9):
        xx = np.pi * opd * dl / lam0**2
        print(f"  Δλ = {dl * 1e9:.2f} nm: widoczność prążków V = {np.exp(-xx**2 / (4 * np.log(2))):.2e}")
    z1, z2 = 0.300, 0.316
    dD = 1 / z1 - 1 / z2
    NA = np.sin(np.radians(0.5))
    print(f"  głębia 16 mm w 30 cm: Δ(1/z) = {dD:.3f} D; rozmycie przy źrenicy {PUPIL} mm: "
          f"{PUPIL * 1e-3 * dD * 1e3:.2f} mrad = {np.degrees(PUPIL * 1e-3 * dD) * 60:.1f}′")
    print(f"  głębia ostrości woksela w stożku 1° (T2): 2λ/NA² = {2 * lam0 / NA**2 * 1e3:.1f} mm; "
          f"wiązka skolimowana (NA → 0): brak bodźca akomodacji")
    th16 = 8.0 + 2 * np.arange(16)
    print(f"  16 kanałów co 2°: wejście {th16[0]:.0f}–{th16[-1]:.0f}° wewn = "
          f"{np.degrees(np.arcsin(n0 * np.sin(np.radians(th16[0])))):.1f}–"
          f"{np.degrees(np.arcsin(n0 * np.sin(np.radians(th16[-1])))):.1f}° w powietrzu; "
          f"bez odchylenia wyjść dolny kanał ~0,62·0,335^15 = {0.62 * 0.335**15:.1e}")
