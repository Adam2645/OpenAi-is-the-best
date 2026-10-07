"""Trzeci audyt C2: zbieżność, przemiatanie n1, geometria warstw, pełne interfejsy.

Te same definicje metryk co w tmm_audyt2_c2.py (h_k, I_k, μ_k, FWHM_k, C_ij, H_ij,
z_gd). Nowe:
  1. zbieżność względem liczby podwarstw na okres: 8, 16, 32, 64,
  2. przemiatanie amplitudy modulacji n1 = 0,004 … 0,03,
  3. geometryczne położenie warstw (gdzie naprawdę jest materia),
  4. układ z interfejsami powietrze | blok | powietrze (pol. s, bez powłoki AR):
     koherentnie dla swobodnej warstwy 50 µm oraz niekoherentnie dla grubego podłoża.
Uruchomienie: python3 research/tmm_audyt3_c2.py
"""
import numpy as np

lam0, n0, L = 532e-9, 1.5, 10e-6
theta_design = np.array([11.5, 19.9, 25.8, 30.7, 34.9])
q = np.cos(np.radians(theta_design))
periods = lam0 / (2 * n0 * q)
N = len(periods)
n_per = np.array([int(round(L / p)) for p in periods])


def stack(layers, n1, sub, outer=None):
    """Lista (n, d). outer = współczynnik ośrodka na zewnątrz (None = n0, czyli idealne AR)."""
    out = []
    for k, Lam in enumerate(periods):
        if k in layers:
            ph = (np.arange(n_per[k] * sub) + 0.5) / sub * 2 * np.pi
            out.extend((n0 + n1 * np.cos(p), Lam / sub) for p in ph)
        else:
            out.append((n0, n_per[k] * Lam))
    return out


def r_general(st, sin_beta_n, lams, n_in, n_out):
    """r dla wektorów (kąty lub λ); sin_beta_n = n·sinθ (niezmiennik), pol. s."""
    lams = np.broadcast_to(np.asarray(lams, float), np.shape(sin_beta_n)).astype(float)
    beta = np.asarray(sin_beta_n, float)
    k = 2 * np.pi / lams
    eta_in = np.sqrt(n_in**2 - beta**2 + 0j)
    eta_out = np.sqrt(n_out**2 - beta**2 + 0j)
    M11 = np.ones_like(beta, dtype=complex); M12 = np.zeros_like(M11)
    M21 = np.zeros_like(M11); M22 = np.ones_like(M11)
    for n, d in st:
        eta = np.sqrt(n**2 - beta**2 + 0j)
        dl = k * eta * d
        c, s = np.cos(dl), np.sin(dl)
        a11, a12, a21, a22 = c, -1j * s / eta, -1j * eta * s, c
        M11, M12, M21, M22 = (M11 * a11 + M12 * a21, M11 * a12 + M12 * a22,
                              M21 * a11 + M22 * a21, M21 * a12 + M22 * a22)
    num = eta_in * M11 + eta_in * eta_out * M12 - M21 - eta_out * M22
    den = eta_in * M11 + eta_in * eta_out * M12 + M21 + eta_out * M22
    return num / den


def R_int(st, th_deg):
    th = np.radians(np.atleast_1d(th_deg))
    return np.abs(r_general(st, n0 * np.sin(th), lam0, n0, n0)) ** 2


def peaks(st):
    out = []
    for t in np.degrees(np.arccos(q)):
        sc = np.linspace(t - 2, t + 2, 801)
        R = R_int(st, sc)
        i = np.argmax(R)
        out.append((sc[i], R[i]))
    return out


def z_gd(st, theta, dl=0.005e-9):
    b = n0 * np.sin(np.radians(theta))
    r1, r2 = r_general(st, np.array([b, b]), np.array([lam0 - dl, lam0 + dl]), n0, n0)
    dk = 2 * np.pi / (lam0 + dl) - 2 * np.pi / (lam0 - dl)
    return abs(np.angle(r2 / r1) / dk) / (2 * n0 * np.cos(np.radians(theta)))


def psf(st, theta, B=10e-9, zmax=60e-6, nl=301, nz=1200):
    k = np.linspace(2 * np.pi / (lam0 + B), 2 * np.pi / (lam0 - B), nl)
    b = n0 * np.sin(np.radians(theta))
    r = r_general(st, np.full(nl, b), 2 * np.pi / k, n0, n0)
    z = np.linspace(0, zmax, nz)
    h = (np.hanning(nl) * r) @ np.exp(-1j * 2 * n0 * np.cos(np.radians(theta)) * np.outer(k, z))
    I = np.abs(h) ** 2
    above = z[I >= I.max() / 2]
    return I, (z * I).sum() / I.sum(), above.max() - above.min()


def metrics(n1, sub):
    full = stack(set(range(N)), n1, sub)
    pk = peaks(full)
    res = {"R": [], "mu": [], "fw": [], "zgd": [], "diag": [], "C": []}
    Is = []
    for k, (t, R) in enumerate(pk):
        I, mu, fw = psf(full, t)
        Is.append(I)
        res["R"].append(R); res["mu"].append(mu * 1e6); res["fw"].append(fw * 1e6)
        res["zgd"].append(z_gd(full, t) * 1e6)
    H = np.array([[R_int(stack({i}, n1, sub), t)[0] for t, _ in pk] for i in range(N)])
    res["diag"] = list(np.diag(H) / H.sum(axis=0))
    for i in range(N - 1):
        a, b = Is[i], Is[i + 1]
        res["C"].append((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))
    grid = np.linspace(0, 41, 4101)
    Rg = R_int(full, grid)
    qg = np.cos(np.radians(grid))
    mask = np.ones_like(grid, bool)
    for t, _ in pk:
        mask &= np.abs(qg - np.cos(np.radians(t))) > lam0 / (2 * n0 * L)
    res["off"] = Rg[mask].max() / min(res["R"])
    res["pk"] = pk
    return res


f2 = lambda a: " / ".join(f"{x:.2f}" for x in a)
f3 = lambda a: " / ".join(f"{x:.3f}" for x in a)

print("== 1. Zbieżność (n1 = 0,008) ==")
for sub in (8, 16, 32, 64):
    m = metrics(0.008, sub)
    print(f"sub={sub:>2}: R = {f3(m['R'])}; kroki μ = {f2(np.diff(m['mu']))}; "
          f"FWHM = {f2(m['fw'])}; kroki z_gd = {f2(np.diff(m['zgd']))}; H_kk/ΣH = {f3(m['diag'])}")

print("\n== 2. Przemiatanie n1 (sub = 16) ==")
for n1 in (0.004, 0.008, 0.012, 0.02, 0.03):
    m = metrics(n1, 16)
    print(f"n1={n1:.3f}: R = {f3(m['R'])}; kroki μ = {f2(np.diff(m['mu']))}; FWHM = {f2(m['fw'])}; "
          f"C = {f3(m['C'])}; H_kk/ΣH = {f3(m['diag'])}; maks. R poza kanałami / min R = {m['off']:.1%}")

print("\n== 3. Geometria warstw (gdzie jest materia) ==")
edges = np.concatenate([[0], np.cumsum(n_per * periods)]) * 1e6
centers = (edges[:-1] + edges[1:]) / 2
print("liczba okresów:", n_per, "grubości [µm]:", np.round(np.diff(edges), 3))
print("środki [µm]:", np.round(centers, 2), "kroki środków [µm]:", np.round(np.diff(centers), 2))

print("\n== 4. Interfejsy powietrze | blok | powietrze, pol. s, bez AR ==")
m = metrics(0.008, 16)
grat = stack(set(range(N)), 0.008, 16)
bare = [(n0, sum(d for _, d in grat))]
for k, (t, Rin) in enumerate(m["pk"]):
    b = n0 * np.sin(np.radians(t))
    th_air = np.degrees(np.arcsin(b))
    ci, ct = np.cos(np.radians(th_air)), np.cos(np.radians(t))
    Rs = ((ci - n0 * ct) / (ci + n0 * ct)) ** 2
    Rcoh = np.abs(r_general(grat, np.array([b]), lam0, 1.0, 1.0)) ** 2
    Rbare = np.abs(r_general(bare, np.array([b]), lam0, 1.0, 1.0)) ** 2
    # niekoherentnie, grube podłoże: front Rs, potem siatka Rin, sumowanie natężeń (bez tylnej powierzchni)
    Rinc = Rs + (1 - Rs) ** 2 * Rin / (1 - Rs * Rin)
    print(f"kanał {k}: θ_powietrze = {th_air:5.1f}°, Fresnel R_s = {Rs:.3f}; "
          f"wewn. R = {Rin:.3f}; koherentnie (warstwa 50 µm w powietrzu) R = {Rcoh[0]:.3f} "
          f"(sam blok bez siatek {Rbare[0]:.3f}); niekoherentnie: sygnał (1−R_s)²·R = "
          f"{(1 - Rs) ** 2 * Rin:.3f}, tło z powierzchni = {Rs:.3f}")
