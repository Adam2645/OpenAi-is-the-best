"""Iteracja 24: grubość siatki L ∈ {0,5; 0,7; 0,85; 1,0} mm przy stałym n1·L = 0,2 µm.

Dla każdego L (Kogelnik 3D, zgodny z RCWA; kontrola RCWA dla L = 0,5 mm):
- przepuszczalność portu T(δ) i najmniejszy krok wyjść δ_min, od którego T ≥ 0,95 dla wszystkich większych δ;
- liczba warstw w wachlarzu 0,48° i moc najsłabszego kanału (iloczyn portów warstw wyżej);
- woksel x po filtrze Bragga (w0x = 150 µm): FWHM, η, kontrast sąsiadów (zapalanie kolejne) przy skoku 300 / 400 µm
  i najmniejszy skok z kontrastem ≥ 0,5;
- szerokość widma, akceptacja kątowa, odbicie sąsiedniej siatki przy skoku kanałów 0,38° wewn.;
- funkcja celu: liczba rozróżnialnych woksli (kontrast ≥ 0,5) w objętości widzianej jednym okiem, także ważona η.
Uruchomienie: python3 research/iteracja24.py
"""
import numpy as np, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from iteracja19 import kog, K_of, dir_down, lam0, n0, grating, run, pick
from iteracja21 import contrast

A_IN = np.degrees(np.arcsin(n0 * np.sin(np.radians(20.0))))
K = K_of(20.0, 0.0)
NL1 = 0.2e-6
W0X = 150e-6
FAN, FOVX, NY = 0.48, 4.5e-3, 96
P_TOP = 0.623  # kanał najwyższy w stosie (RCWA, iteracja 19)
up = lambda ax: dir_down(ax) * np.array([1, 1, -1])

N, LX = 2**14, 20e-3
x = (np.arange(N) - N / 2) * LX / N
fx = np.fft.fftfreq(N, LX / N)
th = np.degrees(np.arcsin(np.clip(lam0 * fx, -1, 1)))


def fwhm(t, y):
    a = t[y >= 0.5 * y.max()]
    return a.max() - a.min()


def study(L):
    n1 = NL1 / L
    eta0 = kog(dir_down(A_IN), K, lam0, L, n1)
    # port
    ds = np.linspace(0, 0.6, 1201)
    T = np.array([1 - kog(up(d), -K, lam0, L, n1) for d in ds])
    bad = np.where(T < 0.95)[0]
    dmin = ds[bad[-1] + 1] if len(bad) else 0.0
    first = ds[np.argmax(T >= 0.95)]
    Tf = lambda d: 1 - kog(up(d), -K, lam0, L, n1)
    # krok wyjść: wszystkie porty warstw wyżej (odchylenia δ, 2δ, …, (N−1)δ) muszą mieć T ≥ 0,95
    dd = np.linspace(0, 0.75, 3001)
    Tg = np.array([Tf(d) for d in dd])
    Ti = lambda d: np.interp(d, dd, Tg)

    def pick_step(tol):
        for Nl in range(10, 1, -1):
            best = None
            for d in np.arange(0.03, FAN / (Nl - 1) + 1e-9, 0.0005):
                tm = min(Ti(np.linspace(k * d - tol, k * d + tol, 9)).min() for k in range(1, Nl))
                if tm >= 0.95 and (best is None or tm > best[1]):
                    best = (d, tm)
            if best:
                return Nl, best[0]
        return 1, None
    nlay, step = pick_step(0.0)
    nlay_r, step_r = pick_step(0.02)
    chans = [P_TOP * np.prod([Tf(k * step) for k in range(1, m + 1)]) for m in range(nlay)]
    # filtr Bragga i woksel x
    R = np.sqrt(np.array([kog(dir_down(A_IN + t), K, lam0, L, n1) if abs(t) < 1.5 else 0.0 for t in th]))
    refl = lambda E: np.fft.ifft(np.fft.fft(E) * R)
    E = np.exp(-(x / W0X) ** 2)
    rE = refl(E)
    I = np.abs(rE) ** 2
    eta_w = I.sum() / (E**2).sum()
    fw = fwhm(x, I)
    def c_at(p):
        a = np.abs(refl(np.exp(-((x + p / 2) / W0X) ** 2))) ** 2
        b = np.abs(refl(np.exp(-((x - p / 2) / W0X) ** 2))) ** 2
        return contrast(a + b)
    c300, c400 = c_at(300e-6), c_at(400e-6)
    pmin = next(p for p in np.arange(150e-6, 800e-6, 10e-6) if c_at(p) >= 0.5)
    # widmo i akceptacja
    dl = np.linspace(-0.6e-9, 0.6e-9, 1201) / (L / 1e-3)
    sp = np.array([kog(dir_down(A_IN), K, lam0 + d, L, n1) for d in dl])
    da = np.linspace(-0.6, 0.6, 1201) / (L / 1e-3)
    ac = np.array([kog(dir_down(A_IN + d), K, lam0, L, n1) for d in da])
    nb = kog(dir_down(np.degrees(np.arcsin(n0 * np.sin(np.radians(20.38))))), K, lam0, L, n1)
    return dict(L=L, n1=n1, eta0=eta0, dmin=dmin, first=first, nlay=nlay, step=step, nlay_r=nlay_r, step_r=step_r, chans=chans, fw=fw, eta_w=eta_w,
                c300=c300, c400=c400, pmin=pmin, spec=fwhm(dl, sp), acc=fwhm(da, ac), nb=nb)


if __name__ == "__main__":
    print("== Przemiatanie grubości siatki (n1·L = 0,2 µm, w0x = 150 µm, wachlarz ≤ 0,48°) ==")
    res = [study(L) for L in (0.5e-3, 0.7e-3, 0.85e-3, 1.0e-3, 1.2e-3)]
    for r in res:
        nx = int(FOVX / r["pmin"])
        vox = r["nlay"] * nx * NY
        r["nx"], r["vox"] = nx, vox
        r["F2"] = vox * min(r["chans"]) * r["eta_w"] / r["eta0"]
        r["F1r"] = r["nlay_r"] * nx * NY
        print(f"L = {r['L'] * 1e3:.2f} mm (n1 = {r['n1']:.2e}): η = {r['eta0']:.3f}; widmo FWHM {r['spec'] * 1e9:.3f} nm; "
              f"akceptacja {r['acc']:.3f}° (pow.)")
        print(f"   port: T ≥ 0,95 od δ = {r['first']:.3f}° (pierwsze przekroczenie), trwale od δ_min = {r['dmin']:.3f}°; "
              f"krok dobrany tak, by T(kδ) ≥ 0,95: δ = {r['step']:.4f}° → warstw w 0,48°: {r['nlay']} (wachlarz {(r['nlay'] - 1) * r['step']:.3f}°); kanały (od góry): " + " / ".join(f"{c:.3f}" for c in r["chans"]))
        print(f"   wariant odporny (T ≥ 0,95 w ±0,02° wokół kδ): δ = {r['step_r']:.4f}° → warstw {r['nlay_r']}")
        print(f"   woksel x: FWHM {r['fw'] * 1e6:.0f} µm (wejście 177 µm), η(w0x = 150 µm) = {r['eta_w']:.3f}; "
              f"kontrast 300 / 400 µm = {r['c300']:.2f} / {r['c400']:.2f}; skok dla kontrastu 0,5: {r['pmin'] * 1e6:.0f} µm "
              f"→ {nx} woksli w x")
        print(f"   odbicie sąsiedniej siatki przy skoku kanałów 0,38° wewn.: {r['nb']:.1e} ({r['nb'] / r['eta0']:.1e} sygnału)")
        print(f"   F1 = warstwy × woksle x × woksle y = {r['nlay']} × {nx} × {NY} = {vox}; "
              f"F2 = F1 × moc najsłabszego kanału × (η woksla / η fali płaskiej) = {r['F2']:.0f}")
    b1 = max(res, key=lambda r: r["vox"]); b2 = max(res, key=lambda r: r["F2"]); b3 = max(res, key=lambda r: r["F1r"])
    print(f"L_opt: według F1 {b1['L'] * 1e3:.2f} mm, według F2 {b2['L'] * 1e3:.2f} mm, według F1 w wariancie odpornym "
          f"{b3['L'] * 1e3:.2f} mm (F1 odporne: " + " / ".join(f"{r['F1r']}" for r in res) + ")")

    print("\n== Kontrola RCWA dla L = 0,5 mm ==")
    r = res[0]
    g = grating(20.0, 0.0, L=r["L"], n1=r["n1"])
    kx, DEr, DEt = run(g, n0 * np.sin(np.radians(20.0)), lam0)
    gf = grating(20.0, 0.0, L=r["L"], n1=r["n1"], flip=True)
    kxs, DErs, DEts = run(gf, np.sin(np.radians(r["dmin"])), lam0)
    print(f"  η: RCWA {DEr.max():.4f}, Kogelnik {r['eta0']:.4f}; port przy δ_min = {r['dmin']:.3f}°: "
          f"RCWA {pick(kxs, DEts, np.sin(np.radians(r['dmin']))):.4f}, Kogelnik "
          f"{1 - kog(up(r['dmin']), -K, lam0, r['L'], r['n1']):.4f}")
