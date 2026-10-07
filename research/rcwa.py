"""Rygorystyczna analiza fal sprzężonych (RCWA) dla siatek 2D, TE i TM.

Formulacja: Moharam, Grann, Pommet, Gaylord, JOSA A 12, 1068 (1995), metoda
„enhanced transmittance” (stabilna dla grubych struktur). Dla TM reguła
odwrotności Li (macierz A = Toeplitz(1/ε)). Konwencja pól exp(−j k·r).

Siatka skośna: ε(x, z) = ε0 + 2·e1·cos(Kx·x + Kz·z), cięta na cienkie plastry.
Plaster j ma fazę ψ_j = Kz·z_j; dzięki temu W(ψ) = D(ψ)·W(0), V(ψ) = D(ψ)·V(0),
gdzie D = diag(exp(j·i·ψ)), więc wystarcza jedno rozwiązanie zagadnienia własnego.
Wszystkie długości w jednostkach 1/k0 wewnątrz funkcji.
"""
import numpy as np


def _kz(n, kx):
    v = n**2 - kx**2
    return np.where(v >= 0, np.sqrt(np.abs(v)) + 0j, -1j * np.sqrt(np.abs(v)))


def _sqrt_branch(lmb):
    q = np.sqrt(lmb.astype(complex))
    flip = (q.real < -1e-15) | ((np.abs(q.real) <= 1e-12) & (q.imag < 0))
    return np.where(flip, -q, q)


def _toeplitz(coef, N):
    """coef: słownik h -> ε_h; macierz E[i,p] = ε_{i-p} dla rzędów -M..M."""
    E = np.zeros((N, N), complex)
    for i in range(N):
        for p in range(N):
            E[i, p] = coef.get(i - p, 0.0)
    return E


def solve(lam, theta_deg, n_I, n_II, pol, layers, M=5, Lx=None, amps=False):
    """layers: lista słowników, każdy opisuje jednorodnie cięty blok:
         {'kind': 'slanted', 'eps0', 'e1', 'Kz', 'L', 'slices'} — siatka skośna
         {'kind': 'zonly', 'eps_slices': [ε_j], 'h'} — profil zależny tylko od z
         {'kind': 'homog', 'eps', 'L'} — warstwa jednorodna
       Lx: okres boczny [m] (wspólny dla wszystkich warstw); None = brak siatki bocznej.
       Zwraca (kx, DE_r, DE_t) — kx/k0 rzędów, sprawności odbicia i transmisji.
       amps=True: dodatkowo zespolone amplitudy (R, T) i kz/k0 obu ośrodków; R odniesione do górnej
       granicy (z = 0), T do dolnej (z = d), dla TM — amplitudy Hy przy fali padającej Hy = 1.
    """
    k0 = 2 * np.pi / lam
    orders = np.arange(-M, M + 1)
    N = len(orders)
    th = np.radians(theta_deg)
    G = 0.0 if Lx is None else lam / Lx
    kx = n_I * np.sin(th) - orders * G
    Kx = np.diag(kx)
    I = np.eye(N)
    kzI, kzII = _kz(n_I, kx), _kz(n_II, kx)
    if pol == "s":
        YI, YII = np.diag(kzI), np.diag(kzII)
        inc2 = 1j * n_I * np.cos(th)
    else:
        YI, YII = np.diag(kzI / n_I**2), np.diag(kzII / n_II**2)
        inc2 = 1j * np.cos(th) / n_I

    def eig_layer(E, A):
        if pol == "s":
            Om = Kx @ Kx - E
            lmb, W = np.linalg.eig(Om)
            q = _sqrt_branch(lmb)
            V = W @ np.diag(q)
        else:
            B = Kx @ np.linalg.solve(E, Kx) - I
            Om = np.linalg.solve(A, B)
            lmb, W = np.linalg.eig(Om)
            q = _sqrt_branch(lmb)
            V = A @ W @ np.diag(q)
        return W, V, q

    # lista plastrów: (W, V, q, h) z góry na dół
    slices = []
    for lay in layers:
        if lay["kind"] == "slanted":
            e0, e1, Kz = lay["eps0"], lay["e1"], lay["Kz"]
            ns = lay["slices"]
            h = lay["L"] / ns
            E0 = _toeplitz({0: e0, 1: e1, -1: e1}, N)
            xs = np.linspace(0, 1, 256, endpoint=False)
            inv = 1 / (e0 + 2 * e1 * np.cos(2 * np.pi * xs))
            c = np.fft.fft(inv) / len(xs)
            A0 = _toeplitz({hh: (c[hh % len(xs)]) for hh in range(-2 * M, 2 * M + 1)}, N)
            W0, V0, q = eig_layer(E0, A0)
            for j in range(ns):
                psi = Kz * (j + 0.5) * h
                D = np.diag(np.exp(1j * orders * psi))
                slices.append((D @ W0, D @ V0, q, h * k0))
        elif lay["kind"] == "zonly":
            for eps in lay["eps_slices"]:
                W, V, q = eig_layer(eps * I, (1 / eps) * I)
                slices.append((W, V, q, lay["h"] * k0))
        else:
            W, V, q = eig_layer(lay["eps"] * I, (1 / lay["eps"]) * I)
            slices.append((W, V, q, lay["L"] * k0))

    f, g = I.copy(), 1j * YII
    stack = []
    for W, V, q, hk in reversed(slices):
        X = np.diag(np.exp(-q * hk))
        Wi, Vi = np.linalg.inv(W), np.linalg.inv(V)
        a = 0.5 * (Wi @ f + Vi @ g)
        b = 0.5 * (Wi @ f - Vi @ g)
        ai = np.linalg.inv(a)
        XbaX = X @ b @ ai @ X
        f, g = W @ (I + XbaX), V @ (I - XbaX)
        stack.append(ai @ X)
    # górna granica
    delta = (orders == 0).astype(complex)
    Mtop = np.block([[-I, f], [1j * YI, g]])
    rhs = np.concatenate([delta, inc2 * delta])
    sol = np.linalg.solve(Mtop, rhs)
    R, T = sol[:N], sol[N:]
    for m in reversed(stack):  # stack[-1] odpowiada warstwie najwyższej
        T = m @ T
    if pol == "s":
        DEr = np.abs(R) ** 2 * np.real(kzI / (n_I * np.cos(th)))
        DEt = np.abs(T) ** 2 * np.real(kzII / (n_I * np.cos(th)))
    else:
        DEr = np.abs(R) ** 2 * np.real(kzI / (n_I * np.cos(th)))
        DEt = np.abs(T) ** 2 * np.real(kzII / n_II**2) / (np.cos(th) / n_I)
    if amps:
        return kx, DEr, DEt, R, T, kzI, kzII
    return kx, DEr, DEt
