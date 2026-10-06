"""Iteracja 9: rachunek macierzy przejścia (TMM) dla wariantu C2.

Stos N warstw siatek odbiciowych (niesłantowanych) w jednym bloku o n0 = 1,5.
Każda warstwa ma grubość L, amplitudę modulacji n1 i własny okres
Λ_k = λ / (2 n0 cos θ_k), więc przy jednej λ dopasowuje się do innego kąta
wewnętrznego θ_k. Polaryzacja s. Wejście i wyjście w ośrodku n0 (granice
zewnętrzne z powłoką AR, której tu nie modelujemy).

Sprawdzamy:
  1. R(θ_k) dla każdego kanału i przesłuch R poza kanałami,
  2. czy odbicie przy θ_k pochodzi z warstwy k: R stosu obciętego do głębokości z
     rośnie skokowo na głębokości warstwy k (z_50 = głębokość połowy końcowego R).

n1 = 0,008: górna granica zmierzona dla Bayfol HX w geometrii odbiciowej
(Bruder, Fäcke, Rölle, Polymers 9, 472 (2017), tab. 3: 0,0078–0,0090).
Uruchomienie: python3 research/tmm_stos_siatek.py
"""
import numpy as np

lam = 532e-9
n0 = 1.5
n1 = 0.008
L = 10e-6
theta_design_deg = np.array([11.5, 19.9, 25.8, 30.7, 34.9])
sub = 16  # podwarstw na okres

k0 = 2 * np.pi / lam
q_design = np.cos(np.radians(theta_design_deg))
periods = lam / (2 * n0 * q_design)


def build_stack(layers):
    """Lista (n, d) podwarstw; layers = indeksy warstw obecnych (inne = n0)."""
    out = []
    for k, Lam in enumerate(periods):
        n_per = int(round(L / Lam))
        d = Lam / sub
        if k in layers:
            phase = (np.arange(n_per * sub) + 0.5) / sub * 2 * np.pi
            out.extend((n0 + n1 * np.cos(p), d) for p in phase)
        else:
            out.append((n0, n_per * Lam))
    return out


def reflectance(stack, theta_deg):
    th = np.radians(np.atleast_1d(theta_deg))
    beta = n0 * np.sin(th)
    eta0 = n0 * np.cos(th)
    M11 = np.ones_like(th, dtype=complex)
    M12 = np.zeros_like(M11)
    M21 = np.zeros_like(M11)
    M22 = np.ones_like(M11)
    for n, d in stack:
        eta = np.sqrt(n**2 - beta**2 + 0j)
        delta = k0 * eta * d
        c, s = np.cos(delta), np.sin(delta)
        a11, a12, a21, a22 = c, -1j * s / eta, -1j * eta * s, c
        M11, M12, M21, M22 = (M11 * a11 + M12 * a21, M11 * a12 + M12 * a22,
                              M21 * a11 + M22 * a21, M21 * a12 + M22 * a22)
    num = eta0 * M11 + eta0 * eta0 * M12 - M21 - eta0 * M22
    den = eta0 * M11 + eta0 * eta0 * M12 + M21 + eta0 * M22
    return np.abs(num / den) ** 2


N = len(periods)
full = build_stack(set(range(N)))
print(f"λ={lam * 1e9:.0f} nm, n0={n0}, n1={n1}, L={L * 1e6:.0f} µm, N={N}, "
      f"okresy Λ_k = {np.round(periods * 1e9, 1)} nm")
print("R z teorii fal sprzężonych, pol. s: tanh²(π n1 L/(λ cosθ_k)) =",
      np.round(np.tanh(np.pi * n1 * L / (lam * q_design)) ** 2, 3))

R_peak = []
for k, t in enumerate(theta_design_deg):
    scan = np.linspace(t - 3, t + 3, 601)
    R = reflectance(full, scan)
    i = np.argmax(R)
    R_peak.append((scan[i], R[i]))
    alone = reflectance(build_stack({k}), scan[i])[0]
    without = reflectance(build_stack(set(range(N)) - {k}), scan[i])[0]
    print(f"kanał {k}: θ_proj={t:5.1f}°, szczyt przy θ={scan[i]:6.2f}°, R_stos={R[i]:.3f}, "
          f"R_tylko_k={alone:.3f}, R_bez_k={without:.4f}")

# przesłuch: maks. R poza głównymi listkami kanałów. Szerokość listka liczona
# w q = cosθ (pierwsze zero: Δq = λ/(2 n0 L)), bo blisko normalnej listek
# w kątach jest szeroki (dq/dθ = sinθ → 0).
grid = np.linspace(0, 41, 4101)
Rg = reflectance(full, grid)
qg = np.cos(np.radians(grid))
dq0 = lam / (2 * n0 * L)
mask = np.ones_like(grid, dtype=bool)
for t, _ in R_peak:
    mask &= np.abs(qg - np.cos(np.radians(t))) > dq0
print(f"pierwsze zero listka Δq = λ/(2 n0 L) = {dq0:.4f}")
print(f"maks. R poza głównymi listkami w 0–41°: {Rg[mask].max():.4f} "
      f"przy θ={grid[mask][np.argmax(Rg[mask])]:.2f}°")

# położenie płaszczyzny odbicia: R stosu obciętego do głębokości z
print("\nGłębokość, na której R(θ_k) osiąga 50% wartości końcowej (płaszczyzna odbicia):")
edges = np.cumsum([0] + [int(round(L / p)) * p for p in periods])
for k, (t, Rk) in enumerate(R_peak):
    zs, Rs = [], []
    acc, z = [], 0.0
    for n, d in full:
        acc.append((n, d))
        z += d
        if len(acc) % 64 == 0 or len(acc) == len(full):
            zs.append(z)
            Rs.append(reflectance(acc, t)[0])
    zs, Rs = np.array(zs), np.array(Rs)
    z50 = zs[np.argmax(Rs >= 0.5 * Rs[-1])]
    print(f"kanał {k} (θ={t:.2f}°): z_50 = {z50 * 1e6:5.1f} µm; "
          f"warstwa k leży w {edges[k] * 1e6:5.1f}–{edges[k + 1] * 1e6:5.1f} µm")
