"""Drugi audyt C2: formalne metryki rozdzielenia płaszczyzn.

Definicje (dla kanału k, kąt θ_k stały):
  r_k(λ)      zespolony współczynnik odbicia stosu (macierz przejścia, pol. s),
  h_k(z)      osiowa odpowiedź impulsowa w paśmie kanału:
              h_k(z) = Σ_λ W(λ) r_k(λ) exp(-i 2 k0 n0 cosθ_k z),  W = okno Hanna,
              pasmo ±B wokół λ0 = 532 nm (B dobrane tak, by nie objąć pasm
              sąsiednich kanałów, które przy θ_k leżą ~20–26 nm dalej),
  I_k(z)      = |h_k(z)|²,
  μ_k         centroid I_k, FWHM_k szerokość połówkowa I_k,
  C_ij        = ∫I_i I_j dz / √(∫I_i² dz ∫I_j² dz)  (nakładanie),
  H_ij        = R samej warstwy i przy kącie θ_j (rozkład niekoherentny; suma
              koherentna różni się o interferencję, por. tmm_audyt_c2.py).
Rozdzielenie płaszczyzn i, i+1 wymaga: |μ_{i+1} − μ_i| ≥ 10 µm (warunek 2),
a dodatkowo, jako kryterium jakości spoza pięciu warunków: FWHM < |Δμ| i C małe.
Szerokość I_k zależy od pasma ±B: sonda monochromatyczna nie ma bramkowania osiowego.

Uruchomienie: python3 research/tmm_audyt2_c2.py
"""
import numpy as np

lam0, n0, n1, L, sub = 532e-9, 1.5, 0.008, 10e-6, 16
theta_design = np.array([11.5, 19.9, 25.8, 30.7, 34.9])
q = np.cos(np.radians(theta_design))
periods = lam0 / (2 * n0 * q)
N = len(periods)


def stack(layers, spacer=0.0, n_sp=1.48, sub=sub):
    out = []
    for k, Lam in enumerate(periods):
        n_per = int(round(L / Lam))
        if k in layers:
            ph = (np.arange(n_per * sub) + 0.5) / sub * 2 * np.pi
            out.extend((n0 + n1 * np.cos(p), Lam / sub) for p in ph)
        else:
            out.append((n0, n_per * Lam))
        if spacer and k < N - 1:
            out.append((n_sp, spacer))
    return out


def r_vec(st, theta_deg, lams):
    """Zespolone r dla wektora długości fal przy stałym kącie."""
    th = np.radians(theta_deg)
    k = 2 * np.pi / np.asarray(lams)
    beta = n0 * np.sin(th)
    eta0 = n0 * np.cos(th)
    M11 = np.ones_like(k, dtype=complex); M12 = np.zeros_like(M11)
    M21 = np.zeros_like(M11); M22 = np.ones_like(M11)
    for n, d in st:
        eta = np.sqrt(n**2 - beta**2 + 0j)
        dl = k * eta * d
        c, s = np.cos(dl), np.sin(dl)
        a11, a12, a21, a22 = c, -1j * s / eta, -1j * eta * s, c
        M11, M12, M21, M22 = (M11 * a11 + M12 * a21, M11 * a12 + M12 * a22,
                              M21 * a11 + M22 * a21, M21 * a12 + M22 * a22)
    num = eta0 * M11 + eta0 * eta0 * M12 - M21 - eta0 * M22
    den = eta0 * M11 + eta0 * eta0 * M12 + M21 + eta0 * M22
    return num / den


def peak_angles(st):
    out = []
    for t in np.degrees(np.arccos(q)):
        sc = np.linspace(t - 2, t + 2, 801)
        R = np.array([abs(r_vec(st, a, [lam0])[0]) ** 2 for a in sc])
        out.append((sc[np.argmax(R)], R.max()))
    return out


def z_gd(st, theta, dl=0.005e-9):
    r1, r2 = r_vec(st, theta, [lam0 - dl, lam0 + dl])
    dk = 2 * np.pi / (lam0 + dl) - 2 * np.pi / (lam0 - dl)
    return abs(np.angle(r2 / r1) / dk) / (2 * n0 * np.cos(np.radians(theta)))


def psf(st, theta, B, zmax, nl=301, nz=1200):
    k = np.linspace(2 * np.pi / (lam0 + B), 2 * np.pi / (lam0 - B), nl)
    r = r_vec(st, theta, 2 * np.pi / k)
    W = np.hanning(nl)
    z = np.linspace(0, zmax, nz)
    kz = 2 * n0 * np.cos(np.radians(theta))
    h = (W * r) @ np.exp(-1j * kz * np.outer(k, z))
    I = np.abs(h) ** 2
    mu = (z * I).sum() / I.sum()
    above = z[I >= I.max() / 2]
    return z, I, mu, above.max() - above.min()


def report(label, st, zmax, B=10e-9):
    pk = peak_angles(st)
    print(f"\n### {label}")
    print("R stosu przy θ_k:", np.round([R for _, R in pk], 4))
    zg = np.array([z_gd(st, t) for t, _ in pk]) * 1e6
    print("z_gd [µm]:", np.round(zg, 2), "kroki:", np.round(np.diff(zg), 2))
    Is, mus = [], []
    for k, (t, _) in enumerate(pk):
        z, I, mu, fw = psf(st, t, B, zmax)
        Is.append(I); mus.append(mu)
        print(f"kanał {k}: μ = {mu * 1e6:6.2f} µm, FWHM = {fw * 1e6:5.2f} µm")
    print("kroki μ [µm]:", np.round(np.diff(mus) * 1e6, 2))
    for i in range(N - 1):
        a, b = Is[i], Is[i + 1]
        print(f"C_{i}{i + 1} = {(a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()):.3f}")
    return pk


print(f"Pasmo PSF: ±10 nm wokół {lam0 * 1e9:.0f} nm, okno Hanna.")
pk = report("Stos ciągły, L = 10 µm, sub = 16", stack(set(range(N))), 60e-6)

print("\n### Czułość numeryczna z_gd (stos ciągły)")
for s in (16, 32):
    st = stack(set(range(N)), sub=s)
    for dl in (0.005e-9, 0.05e-9):
        zg = np.array([z_gd(st, t, dl) for t, _ in pk]) * 1e6
        print(f"sub={s}, Δλ={dl * 1e9:.3f} nm: kroki {np.round(np.diff(zg), 2)}")

print("\n### Macierz H_ij = R samej warstwy i przy kącie θ_j (stos ciągły)")
H = np.array([[abs(r_vec(stack({i}), t, [lam0])[0]) ** 2 for t, _ in pk] for i in range(N)])
np.set_printoptions(precision=4, suppress=True)
print(H)
print("udział warstwy j w Σ_i H_ij przy θ_j:", np.round(np.diag(H) / H.sum(axis=0), 3))

full = stack(set(range(N)))
grid = np.linspace(0, 41, 2051)
Rg = np.array([abs(r_vec(full, a, [lam0])[0]) ** 2 for a in grid])
qg = np.cos(np.radians(grid))
mask = np.ones_like(grid, bool)
for t, _ in pk:
    mask &= np.abs(qg - np.cos(np.radians(t))) > lam0 / (2 * n0 * L)
Rmin = min(R for _, R in pk)
print(f"\nmaks. R poza listkami = {Rg[mask].max():.4f}; najsłabszy kanał R = {Rmin:.4f}; "
      f"stosunek = {Rg[mask].max() / Rmin:.1%}")

report("Scenariusz laminatu: przekładki 51 µm, n = 1,48 (założenie)",
       stack(set(range(N)), spacer=51e-6), 280e-6)

print("\n### E: górna granica mocy koherentnej piksela 10 × 10 µm (atomy niezależne)")
h, c = 6.62607015e-34, 2.99792458e8
lam_rb, Gam = 780.241e-9, 2 * np.pi * 6.0666e6
sigma0 = 3 * lam_rb**2 / (2 * np.pi)
Npix = 1e-10 / sigma0
P = Npix * h * c / lam_rb * Gam / 8
print(f"N = A/σ0 = 1e-10 / {sigma0:.3e} = {Npix:.0f}; P ≤ N·ħω·Γ/8 = {P * 1e9:.2f} nW "
      f"(całość w 4π, więc też górna granica dla stożka < 1°); stosunek do 1 mW = {P / 1e-3:.1e}")
print(f"odstęp atomów przy OD = 1: √σ0 = {np.sqrt(sigma0) * 1e6:.2f} µm = {np.sqrt(sigma0) / lam_rb:.2f} λ "
      f"(< λ, czyli reżim kolektywny: dla takiej gęstości bilans niezależnych atomów jest tylko szacunkiem)")
