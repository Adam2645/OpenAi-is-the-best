"""Audyt C2: metryki, o które prosi recenzja zewnętrzna.

Na tym samym modelu co tmm_stos_siatek.py liczy:
  1. kroki z50 między kanałami (arytmetyka tabeli),
  2. rozkład osiowy odbicia p_k(z) = dR_k/dz stosu obciętego do głębokości z,
     jego centroid, szerokość 10–90% i nakładanie C_ij sąsiednich kanałów,
  3. przesłuch względem sygnału (nie względem mocy wejściowej),
  4. wariant laminatu: przekładki 51 µm o n = 1,48 między warstwami.
Uruchomienie: python3 research/tmm_audyt_c2.py
"""
import numpy as np
import importlib.util, pathlib

spec = importlib.util.spec_from_file_location(
    "tmm", pathlib.Path(__file__).with_name("tmm_stos_siatek.py"))
src = pathlib.Path(spec.origin).read_text().split("\nN = len(periods)")[0]
ns = {}
exec(src, ns)  # tylko definicje: parametry, build_stack, reflectance
lam, n0, n1, L, periods, sub = (ns[k] for k in ("lam", "n0", "n1", "L", "periods", "sub"))
reflectance = ns["reflectance"]
N = len(periods)


def stack(layers, spacer=0.0, n_sp=None):
    out = []
    for k, Lam in enumerate(periods):
        n_per = int(round(L / Lam))
        d = Lam / sub
        if k in layers:
            ph = (np.arange(n_per * sub) + 0.5) / sub * 2 * np.pi
            out.extend((n0 + n1 * np.cos(p), d) for p in ph)
        else:
            out.append((n0, n_per * Lam))
        if spacer and k < N - 1:
            out.append((n_sp, spacer))
    return out


def peaks(st):
    res = []
    for t in np.degrees(np.arccos(lam / (2 * n0 * periods))):
        sc = np.linspace(t - 2, t + 2, 801)
        R = reflectance(st, sc)
        res.append((sc[np.argmax(R)], R.max()))
    return res


def axial(st, theta):
    zs, Rs, acc, z = [0.0], [0.0], [], 0.0
    for n, d in st:
        acc.append((n, d)); z += d
        if len(acc) % sub == 0 or len(acc) == len(st):
            zs.append(z); Rs.append(reflectance(acc, theta)[0])
    zs, Rs = np.array(zs), np.array(Rs)
    p = np.gradient(Rs, zs)
    return zs, Rs, p


full = stack(set(range(N)))
pk = peaks(full)

print("== 1. Kroki z50 (połowa końcowego R) ==")
z50 = []
for t, R in pk:
    zs, Rs, _ = axial(full, t)
    z50.append(zs[np.argmax(Rs >= 0.5 * Rs[-1])])
z50 = np.array(z50) * 1e6
print("z50 [µm]:", np.round(z50, 1), " kroki:", np.round(np.diff(z50), 1))

print("\n== 2. Rozkład osiowy p_k(z) = dR/dz ==")
P = []
for k, (t, R) in enumerate(pk):
    zs, Rs, p = axial(full, t)
    w = np.clip(p, 0, None)
    cdf = np.cumsum(w) / w.sum()
    zc = (zs * w).sum() / w.sum()
    z10, z90 = zs[np.searchsorted(cdf, 0.1)], zs[np.searchsorted(cdf, 0.9)]
    neg = -np.clip(p, None, 0).sum() / w.sum()
    P.append((zs, p))
    print(f"kanał {k}: centroid {zc * 1e6:5.1f} µm, 10–90%: {z10 * 1e6:5.1f}–{z90 * 1e6:5.1f} µm "
          f"(szer. {(z90 - z10) * 1e6:4.1f} µm), ujemne dR/dz: {neg:.1%}")
cent = []
for zs, p in P:
    w = np.clip(p, 0, None); cent.append((zs * w).sum() / w.sum())
print("kroki centroidów [µm]:", np.round(np.diff(np.array(cent)) * 1e6, 2))
for i in range(N - 1):
    a, b = np.clip(P[i][1], 0, None), np.clip(P[i + 1][1], 0, None)
    print(f"C_{i}{i + 1} = ∫p_i p_j / √(∫p_i² ∫p_j²) = {(a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()):.3f}")

print("\n== 3. Przesłuch względem sygnału przy kącie kanału ==")
for k, (t, R) in enumerate(pk):
    alone = reflectance(stack({k}), t)[0]
    wrong = reflectance(stack(set(range(N)) - {k}), t)[0]
    print(f"kanał {k}: R_stos={R:.3f}, R_tylko_k={alone:.3f}, R_inne_warstwy={wrong:.4f} "
          f"→ P_inne/P_sygnał={wrong / alone:.1%}, |R_stos−R_k|/R_k={abs(R - alone) / alone:.1%}")
grid = np.linspace(0, 41, 4101)
Rg = reflectance(full, grid)
qg = np.cos(np.radians(grid))
mask = np.ones_like(grid, bool)
for t, _ in pk:
    mask &= np.abs(qg - np.cos(np.radians(t))) > lam / (2 * n0 * L)
Rmin = min(R for _, R in pk)
print(f"maks. R poza listkami = {Rg[mask].max():.3f} → {Rg[mask].max() / Rmin:.1%} najsłabszego kanału")

print("\n== 4. Laminat: przekładki 51 µm, n = 1,48 (założenie) ==")
lam_st = stack(set(range(N)), spacer=51e-6, n_sp=1.48)
for k, (t, R) in enumerate(peaks(lam_st)):
    print(f"kanał {k}: θ={t:.2f}°, R={R:.3f}")

print("\n== 5. Laminat: rozkład osiowy i przesłuch ==")
pkl = peaks(lam_st)
cl, Pl = [], []
for k, (t, R) in enumerate(pkl):
    zs, Rs, p = axial(lam_st, t)
    w = np.clip(p, 0, None)
    cdf = np.cumsum(w) / w.sum()
    z10, z90 = zs[np.searchsorted(cdf, 0.1)], zs[np.searchsorted(cdf, 0.9)]
    cl.append((zs * w).sum() / w.sum()); Pl.append(w)
    alone = reflectance(stack({k}, spacer=51e-6, n_sp=1.48), t)[0]
    wrong = reflectance(stack(set(range(N)) - {k}, spacer=51e-6, n_sp=1.48), t)[0]
    print(f"kanał {k}: centroid {cl[-1] * 1e6:6.1f} µm, 10–90% {z10 * 1e6:6.1f}–{z90 * 1e6:6.1f} µm, "
          f"ujemne dR/dz {-np.clip(p, None, 0).sum() / w.sum():.1%}, P_inne/P_sygnał={wrong / alone:.1%}, "
          f"|R_stos−R_k|/R_k={abs(R - alone) / alone:.1%}")
print("kroki centroidów [µm]:", np.round(np.diff(np.array(cl)) * 1e6, 1))
for i in range(N - 1):
    a, b = Pl[i], Pl[i + 1]
    print(f"C_{i}{i + 1} = {(a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()):.3f}")

print("\n== 6. Głębokość z opóźnienia grupowego (to, co zmierzy OCT) ==")
# z_gd = |dφ/dk0| / (2 n0 cosθ): dla odbicia z głębokości z faza rośnie jak 2 k0 n0 cosθ z.


def r_amp(st, theta_deg, lam_probe):
    th = np.radians(theta_deg)
    k = 2 * np.pi / lam_probe
    beta = n0 * np.sin(th); eta0 = n0 * np.cos(th)
    M = np.eye(2, dtype=complex)
    for n, d in st:
        eta = np.sqrt(n**2 - beta**2 + 0j); dl = k * eta * d
        M = M @ np.array([[np.cos(dl), -1j * np.sin(dl) / eta], [-1j * eta * np.sin(dl), np.cos(dl)]])
    num = eta0 * M[0, 0] + eta0 * eta0 * M[0, 1] - M[1, 0] - eta0 * M[1, 1]
    den = eta0 * M[0, 0] + eta0 * eta0 * M[0, 1] + M[1, 0] + eta0 * M[1, 1]
    return num / den


def z_gd(st, theta):
    dl = 0.005e-9
    r1, r2 = r_amp(st, theta, lam - dl), r_amp(st, theta, lam + dl)
    k1, k2 = 2 * np.pi / (lam - dl), 2 * np.pi / (lam + dl)
    dphi = np.angle(r2 / r1)
    return abs(dphi / (k2 - k1)) / (2 * n0 * np.cos(np.radians(theta)))


for lab, st, P_ in (("ciągły stos L=10 µm", full, pk), ("laminat, przekładki 51 µm", lam_st, pkl)):
    zg = np.array([z_gd(st, t) for t, _ in P_]) * 1e6
    zk = np.array([z_gd(stack({k}, *(() if st is full else (51e-6, 1.48))), t) for k, (t, _) in enumerate(P_)]) * 1e6
    print(f"{lab}: z_gd stosu [µm] = {np.round(zg, 1)}, kroki = {np.round(np.diff(zg), 1)}")
    print(f"{' ' * len(lab)}  z_gd samej warstwy k [µm] = {np.round(zk, 1)}")
