"""Zespolona teoria fal sprzężonych Kogelnika (dwie fale, siatka skośna, geometria 3D, bez strat).

Pole w płytce: E = R(z)·exp(−jρ·r) + S(z)·exp(−jσ·r), σ = ρ − G, konwencja exp(−jk·r) jak w rcwa.py.
Równania (Kogelnik 1969, α = 0):  cR·R' = −jκ·S,  cS·S' + jϑ·S = −jκ·R,  z — w głąb płytki wzdłuż kierunku R.
Rozwiązanie macierzowe v(d) = exp(M·d)·v(0), M = [[0, −jκ/cR], [−jκ/cS, −jϑ/cS]]; dla 2×2
exp(M·d) = e^{tr·d/2}·[cosh(q·d)·I + sinh(q·d)/q·(M − tr/2·I)], q² = tr²/4 − det M.
Odbicie (cS < 0): R(0) = 1, S(d) = 0 → S(0) = −E21/E22, R(d) = E11 + E12·S(0).
Zwraca amplitudy znormalizowane mocowo: r = S(0)·√(|cS|/cR) (odniesione do płaszczyzny wejścia, z = 0),
t = R(d) (bez fazy swobodnej propagacji exp(−jρz·d), którą niesie fala płaska). |r|² + |t|² = 1.
Wszystkie argumenty mogą być tablicami (wektoryzacja po kierunkach i długościach fali).
"""
import numpy as np


def kogc(rh, G, lam, L, n1, n0=1.5, pol="p"):
    """rh: kierunki fali padającej (..., 3), jednostkowe; G: wektor siatki (3,) [1/m]; lam [m] (skalar lub tablica).
    Fala ugięta σ = ρ − G. Oś z w dół; dla fali biegnącej w górę cR = |ρ̂z| i znak σz odwrócony jak w iteracja19.kog."""
    rh = np.asarray(rh, float)
    lam = np.asarray(lam, float)
    beta = 2 * np.pi * n0 / lam
    rho = beta[..., None] * rh
    sig = rho - np.asarray(G, float)
    nz = np.sign(rh[..., 2])
    cR = np.abs(rh[..., 2])
    cS = sig[..., 2] * nz / beta
    s2 = (sig**2).sum(-1)
    pf = np.abs((rh * sig).sum(-1)) / np.sqrt(s2) if pol == "p" else 1.0
    vt = (beta**2 - s2) / (2 * beta)
    kap = np.pi * n1 * pf / lam
    a = vt / (2 * cS)
    q = np.sqrt((-(a**2) - kap**2 / (cR * cS)).astype(complex))
    qL = q * L
    small = np.abs(qL) < 1e-9
    shq = np.where(small, L, np.sinh(qL) / np.where(small, 1.0, q))
    ch = np.cosh(qL)
    S0 = (1j * kap / cS) * shq / (ch - 1j * a * shq)
    Rd = np.exp(-1j * a * L) * (ch + 1j * a * shq - 1j * (kap / cR) * shq * S0)
    r = S0 * np.sqrt(np.abs(cS) / cR)
    return r, Rd
