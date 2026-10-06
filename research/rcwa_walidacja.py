"""Walidacja research/rcwa.py: (1) profil tylko w z vs macierz przejścia (TE i TM),
(2) siatka skośna: zachowanie energii i porównanie z Kogelnikiem, (3) zbieżność."""
import numpy as np, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rcwa import solve

lam, n0 = 532e-9, 1.5

# --- 1. profil tylko w z: siatka odbiciowa niesłantowana 10 µm, n1 = 0,008, 20° wewnątrz
th = 20.0
Lam = lam / (2 * n0 * np.cos(np.radians(th)))
n_per = int(round(10e-6 / Lam)); sub = 32
eps = [(n0 + 0.008 * np.cos((j + 0.5) / sub * 2 * np.pi)) ** 2 for j in range(n_per * sub)]
lay = [{"kind": "zonly", "eps_slices": eps, "h": Lam / sub}]


def r_tmm(st, b, pol):
    k = 2 * np.pi / lam
    def adm(n):
        kz = np.sqrt(n**2 - b**2 + 0j)
        return kz, (kz if pol == "s" else n**2 / kz)
    _, ei = adm(n0); _, eo = adm(n0)
    M = np.eye(2, dtype=complex)
    for n, d in st:
        kz, e = adm(n); dl = k * kz * d
        M = M @ np.array([[np.cos(dl), -1j * np.sin(dl) / e], [-1j * e * np.sin(dl), np.cos(dl)]])
    num = ei * M[0, 0] + ei * eo * M[0, 1] - M[1, 0] - eo * M[1, 1]
    den = ei * M[0, 0] + ei * eo * M[0, 1] + M[1, 0] + eo * M[1, 1]
    return abs(num / den) ** 2

st = [(np.sqrt(e), Lam / sub) for e in eps]
for pol in ("s", "p"):
    _, DEr, DEt = solve(lam, th, n0, n0, "s" if pol == "s" else "p", lay, M=0)
    print(f"1. profil z, pol {pol}: RCWA R = {DEr.sum():.5f}, T = {DEt.sum():.5f}, R+T = {DEr.sum() + DEt.sum():.5f}; "
          f"TMM R = {r_tmm(st, n0 * np.sin(np.radians(th)), pol):.5f}")

# --- 2. siatka skośna: wejście 20° wewnątrz, wyjście wzdłuż normalnej (w górę)
beta = 2 * np.pi * n0 / lam


def slanted(theta_in, n1, L, spp=16):
    t = np.radians(theta_in)
    Kx, Kz = beta * np.sin(t), beta * (1 + np.cos(t))
    Lz = 2 * np.pi / Kz
    ns = int(round(L / Lz)) * spp
    return [{"kind": "slanted", "eps0": n0**2, "e1": n0 * n1, "Kz": Kz, "L": ns / spp * Lz, "slices": ns}], 2 * np.pi / Kx


def kogelnik_eta(theta_in, n1, L, pol):
    c = np.cos(np.radians(theta_in))
    pf = c if pol == "p" else 1.0
    nu = np.pi * n1 * pf * L / (lam * np.sqrt(c * 1.0))
    return np.tanh(nu) ** 2

for pol in ("s", "p"):
    for (n1, L) in ((0.02, 10e-6), (0.002, 100e-6)):
        lay, Lx = slanted(20.0, n1, L)
        kx, DEr, DEt = solve(lam, 20.0, n0, n0, pol, lay, M=5, Lx=Lx)
        i_norm = np.argmin(np.abs(kx))
        print(f"2. skośna pol {pol}, n1 = {n1}, L = {L * 1e6:.0f} µm: η(rząd do normalnej) = {DEr[i_norm]:.4f}, "
              f"Kogelnik = {kogelnik_eta(20.0, n1, L, pol):.4f}, suma R+T = {DEr.sum() + DEt.sum():.6f}, "
              f"inne rzędy odbite = {DEr.sum() - DEr[i_norm]:.2e}")

# --- 3. zbieżność (pol p, n1 = 0,002, L = 100 µm)
for M in (3, 5, 7):
    for spp in (8, 16, 32):
        lay, Lx = slanted(20.0, 0.002, 100e-6, spp)
        kx, DEr, DEt = solve(lam, 20.0, n0, n0, "p", lay, M=M, Lx=Lx)
        print(f"3. M = {M}, plastry/okres = {spp}: η = {DEr[np.argmin(np.abs(kx))]:.5f}, R+T = {DEr.sum() + DEt.sum():.6f}")
