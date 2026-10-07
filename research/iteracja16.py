"""Iteracja 16: przekładki makroskopowe, geometria widza, siatki skośne, podwójna źrenica.

1. TMM (pol. p, n1 = 0,02): przekładki 51 / 200 / 500 / 1000 µm; zafalowanie R przy
   zmianie λ (prążki Fabry'ego–Pérota) i moc z innych warstw.
2. Geometria: kierunek wyjścia każdego kanału, przesunięcie boczne i winietowanie.
3. Siatki skośne (Kogelnik 1969, siatka odbiciowa bez strat): każdy kanał kierowany
   w tę samą stronę (wzdłuż normalnej), selektywność kątowa i przesłuch.
4. Podwójna źrenica (±6° w powietrzu): podział Δn = 0,03 na dwie siatki.
5. Bilans czasowy AOD + SLM i przekaźnik osiowy 4f (M_z = M_x²).
Uruchomienie: python3 research/iteracja16.py
"""
import numpy as np

lam0, n0, L = 532e-9, 1.5, 10e-6
beta = 2 * np.pi * n0 / lam0
orig = np.degrees(np.arccos(np.array([0.98, 0.94, 0.90, 0.86, 0.82])))
per = lam0 / (2 * n0 * np.cos(np.radians(orig)))


def r_tmm(st, b, lam, pol, n_in=n0, n_out=n0):
    b = np.atleast_1d(np.asarray(b, float))
    lam = np.broadcast_to(np.asarray(lam, float), b.shape)
    k = 2 * np.pi / lam

    def adm(n):
        kz = np.sqrt(n**2 - b**2 + 0j)
        return kz, (kz if pol == "s" else n**2 / kz)

    _, ei = adm(n_in); _, eo = adm(n_out)
    M11 = np.ones_like(b, dtype=complex); M12 = np.zeros_like(M11)
    M21 = np.zeros_like(M11); M22 = np.ones_like(M11)
    for n, d in st:
        kz, e = adm(n)
        dl = k * kz * d
        c, s = np.cos(dl), np.sin(dl)
        a11, a12, a21, a22 = c, -1j * s / e, -1j * e * s, c
        M11, M12, M21, M22 = (M11 * a11 + M12 * a21, M11 * a12 + M12 * a22,
                              M21 * a11 + M22 * a21, M21 * a12 + M22 * a22)
    num = ei * M11 + ei * eo * M12 - M21 - eo * M22
    den = ei * M11 + ei * eo * M12 + M21 + eo * M22
    return num / den


def laminate(n1, sp, n_sp=1.48, sub=32, only=None):
    out = []
    for k, Lam in enumerate(per):
        n_per = int(round(L / Lam))
        if only is None or k in only:
            ph = (np.arange(n_per * sub) + 0.5) / sub * 2 * np.pi
            out.extend((n0 + n1 * np.cos(p), Lam / sub) for p in ph)
        else:
            out.append((n0, n_per * Lam))
        if k < len(per) - 1:
            out.append((n_sp, sp))
    return out


print("== 1. Przekładki makroskopowe (pol. p, n1 = 0,02, n_przekładki = 1,48) ==")
print("TIR na granicy 1,5 → 1,48 dopiero powyżej", f"{np.degrees(np.arcsin(1.48 / 1.5)):.1f}° wewnątrz; "
      "kanały mają 11,7–34,8°, więc przekładka nie prowadzi światła.")
for sp in (51e-6, 200e-6, 500e-6, 1000e-6):
    st = laminate(0.02, sp)
    res = []
    for k, t in enumerate(orig):
        sc = np.linspace(t - 1, t + 1, 401)
        b = n0 * np.sin(np.radians(sc))
        R = np.abs(r_tmm(st, b, lam0, "p")) ** 2
        tpk = sc[np.argmax(R)]
        bp = n0 * np.sin(np.radians(tpk))
        lams = lam0 + np.linspace(-0.2e-9, 0.2e-9, 801)
        Rl = np.abs(r_tmm(st, np.full(lams.shape, bp), lams, "p")) ** 2
        alone = np.abs(r_tmm(laminate(0.02, sp, only={k}), bp, lam0, "p")[0]) ** 2
        wrong = np.abs(r_tmm(laminate(0.02, sp, only=set(range(5)) - {k}), bp, lam0, "p")[0]) ** 2
        res.append((Rl.mean(), Rl.min(), Rl.max(), alone, wrong / alone))
    fsr = lam0**2 / (2 * 1.48 * sp * np.cos(np.radians(25))) * 1e12
    print(f"\nprzekładka {sp * 1e6:5.0f} µm (okres prążków w λ ~{fsr:.0f} pm):")
    for k, (mean, mn, mx, alone, xt) in enumerate(res):
        print(f"  kanał {k}: R średnie (λ0 ± 0,2 nm) {mean:.3f}, zakres {mn:.3f}–{mx:.3f}, "
              f"sama warstwa {alone:.3f}, moc innych warstw / sygnał {xt:.1%}")

print("\n== 2. Geometria siatek niesłantowanych: kierunek wyjścia i winietowanie ==")
th_air = np.degrees(np.arcsin(n0 * np.sin(np.radians(orig))))
print("kanał k wychodzi pod kątem zwierciadlanym −θ_pow,k:", np.round(-th_air, 1), "°")
print("rozrzut kierunków wyjścia między kanałami:", f"{th_air.max() - th_air.min():.1f}° "
      "wobec stożka 1°: widz w jednym miejscu widzi jedną warstwę.")
for sp in (51e-6, 1000e-6):
    z = np.array([k * (L + sp) + L / 2 for k in range(5)])
    dx = 2 * z * np.tan(np.radians(orig))
    print(f"przekładka {sp * 1e6:.0f} µm: przesunięcie boczne wiązki po odbiciu od warstwy k "
          f"[mm] = {np.round(dx * 1e3, 3)}; przy aperturze 10 mm użyteczna część = "
          f"{np.round(np.clip(1 - dx / 10e-3, 0, 1), 2)}")


def kogelnik(n1, L_, r_hat, s_hat, theta_read, pol):
    """Sprawność odbiciowej siatki Kogelnika zapisanej dla (r_hat → s_hat), czytanej pod theta_read."""
    K = beta * (r_hat - s_hat)
    Kmag = np.linalg.norm(K)
    phi = np.arctan2(K[0], K[1])
    th = np.radians(np.atleast_1d(theta_read))
    cR = np.cos(th)
    cS = np.cos(th) - Kmag / beta * np.cos(phi)
    pf = abs(np.dot(r_hat, s_hat)) if pol == "p" else 1.0
    nu = np.pi * n1 * pf * L_ / (lam0 * np.sqrt(np.abs(cR * cS)))
    vt = Kmag * np.cos(phi - th) - Kmag**2 * lam0 / (4 * np.pi * n0)
    xi = -vt * L_ / (2 * cS)
    root = np.sqrt(nu**2 - xi**2 + 0j)
    with np.errstate(divide="ignore", invalid="ignore"):
        eta = 1 / (1 + (1 - xi**2 / nu**2) / np.sinh(root) ** 2)
    eta = np.where(np.abs(root) < 1e-9, nu**2 / (1 + nu**2), eta)
    out_x = np.sin(th) - K[0] / beta  # kierunek wiązki ugiętej (składowa x / β)
    return np.real(eta), out_x


print("\n== 3. Siatki skośne: każdy kanał odbijany wzdłuż normalnej (Kogelnik) ==")
s_norm = np.array([0.0, -1.0])
for pol, n1 in (("p", 0.02), ("s", 0.008)):
    print(f"\npol {pol}, n1 = {n1}, L = 10 µm:")
    H = np.zeros((5, 5))
    for j, tj in enumerate(orig):
        r_hat = np.array([np.sin(np.radians(tj)), np.cos(np.radians(tj))])
        for k, tk in enumerate(orig):
            e, ox = kogelnik(n1, L, r_hat, s_hat=s_norm, theta_read=tk, pol=pol)
            H[j, k] = e[0]
        sc = np.linspace(tj - 3, tj + 3, 3001)
        e, ox = kogelnik(n1, L, r_hat, s_norm, sc, pol)
        above = sc[e >= 0.5 * e.max()]
        fac = n0 * np.cos(np.radians(tj)) / np.cos(np.radians(th_air[j]))
        Rf_p = 0.0
        print(f"  kanał {j}: θ_wewn {tj:5.2f}°, Λ = {lam0 / (2 * n0 * np.cos(np.radians(tj / 2))) * 1e9:6.1f} nm, "
              f"skos φ = {tj / 2:5.2f}°, η = {e.max():.3f} (współczynnik p |cosθ| = {np.cos(np.radians(tj)):.3f}), "
              f"FWHM kątowe {above.max() - above.min():.2f}° wewn = {(above.max() - above.min()) * fac:.2f}° z pow.")
    print("  macierz H (wiersz: siatka j, kolumna: kąt odczytu k):")
    print(np.array2string(H, precision=4, suppress_small=True))
    ox_x = [np.degrees(np.arcsin(np.clip(n0 * (np.sin(np.radians(orig[k])) - np.sin(np.radians(orig[j]))), -1, 1)))
            for j, k in ((0, 1), (1, 2), (2, 3), (3, 4))]
    print("  światło z niewłaściwej (sąsiedniej) siatki wychodzi w powietrzu pod kątem [°]:",
          np.round(ox_x, 1), "względem normalnej, czyli poza stożkiem 1° widza")

print("\n== 4. Podwójna źrenica: dwie siatki ±6° (powietrze) w jednej warstwie ==")
th_eye_int = np.degrees(np.arcsin(np.sin(np.radians(6)) / n0))
print(f"±6° w powietrzu = ±{th_eye_int:.2f}° wewnątrz")
for L_ in (10e-6, 16e-6):
    for pol in ("p", "s"):
        tin = 20.0
        r_hat = np.array([np.sin(np.radians(tin)), np.cos(np.radians(tin))])
        nus = []
        for sgn in (+1, -1):
            a = np.radians(180 + sgn * th_eye_int)
            s_hat = np.array([np.sin(a), np.cos(a)])
            pf = abs(np.dot(r_hat, s_hat)) if pol == "p" else 1.0
            cS = s_hat[1]
            nus.append(np.pi * 0.015 * pf * L_ / (lam0 * np.sqrt(abs(np.cos(np.radians(tin)) * cS))))
        nu1 = np.pi * 0.03 * (abs(np.cos(np.radians(tin))) if pol == "p" else 1) * L_ / (
            lam0 * np.sqrt(abs(np.cos(np.radians(tin)))))
        total = np.tanh(np.sqrt(nus[0] ** 2 + nus[1] ** 2)) ** 2
        print(f"L = {L_ * 1e6:.0f} µm, pol {pol}, wejście 20° wewn: jedna siatka n1 = 0,03 → η = {np.tanh(nu1) ** 2:.3f}; "
              f"dwie siatki po 0,015 → łącznie {total:.3f}, na oko {total / 2:.3f} "
              f"(słabe sprzężenie, każda osobno: {np.tanh(nus[0]) ** 2:.3f})")

print("\n== 5a. Bilans czasowy: AOD + SLM, 5 warstw sekwencyjnie ==")
P = 1e-3 * 0.8 * 0.6 * 0.4 / 5
cone = 1 - np.exp(-2 * 0.5**2 / 0.5**2)
Eph = 6.62607015e-34 * 2.99792458e8 / lam0
print(f"moc średnia na warstwę: 1 mW × 0,8 × 0,6 × 0,4 / 5 = {P * 1e6:.1f} µW; w stożku (θ0 = 0,5°): {P * cone * 1e6:.1f} µW")
print(f"fotony/s: {P * cone / Eph:.2e}; granica szumu śrutowego SNR w 1 s ≈ {np.sqrt(P * cone / Eph):.1e}")
for Nv in (1, 1e3, 1e4):
    print(f"  {Nv:.0e} woksli na warstwie (SLM fazowy dzieli moc): {P * cone / Nv * 1e9:.2f} nW na woksel")
print("przełączanie: 5 warstw × 60 Hz = 300 wzorów SLM na sekundę")

print("\n== 5b. Przekaźnik osiowy 4f: M_z = M_x², kąt maleje jak 1/M_x ==")
for Mz in (100, 500):
    Mx = np.sqrt(Mz)
    half = 0.5 / Mx
    spot = 2 * 0.3 * np.tan(np.radians(half)) * 1e3
    print(f"M_z = {Mz}: M_x = {Mx:.1f}; skok 60 µm → {60e-6 * Mz * 1e3:.0f} mm; półkąt stożka 0,5° → {half:.3f}°; "
          f"plamka w 30 cm {spot:.2f} mm wobec źrenicy ~3–4 mm; szczegół 30 µm → {30 * Mx:.0f} µm")

print("\n== 6a. Pełna amplituda prążków (okno ±1,2 nm obejmuje okres dla przekładki 51 µm) ==")
for sp in (51e-6, 1000e-6):
    st = laminate(0.02, sp)
    amps = []
    for k, t in enumerate(orig):
        sc = np.linspace(t - 1, t + 1, 401)
        R = np.abs(r_tmm(st, n0 * np.sin(np.radians(sc)), lam0, "p")) ** 2
        bp = n0 * np.sin(np.radians(sc[np.argmax(R)]))
        lams = lam0 + np.linspace(-1.2e-9, 1.2e-9, 2401)
        Rl = np.abs(r_tmm(st, np.full(lams.shape, bp), lams, "p")) ** 2
        amps.append((Rl.max() - Rl.min()) / Rl.mean())
    print(f"przekładka {sp * 1e6:.0f} µm: zafalowanie międzyszczytowe / średnia = {np.round(np.array(amps) * 100, 0)} %")

print("\n== 6b. Siatki skośne: szerokość akceptacji kątowej a grubość warstwy (pol p, R ≈ 0,5) ==")
for L_ in (10e-6, 30e-6, 100e-6):
    tj = orig[2]
    r_hat = np.array([np.sin(np.radians(tj)), np.cos(np.radians(tj))])
    n1 = 0.02 * 10e-6 / L_  # stałe n1·L, czyli podobne η w szczycie
    sc = np.linspace(tj - 8, tj + 8, 8001)
    e, _ = kogelnik(n1, L_, r_hat, s_norm, sc, "p")
    above = sc[e >= 0.5 * e.max()]
    fac = n0 * np.cos(np.radians(tj)) / np.cos(np.radians(th_air[2]))
    print(f"L = {L_ * 1e6:5.0f} µm (n1 = {n1:.4f}): η = {e.max():.3f}, FWHM {above.max() - above.min():.2f}° wewn "
          f"= {(above.max() - above.min()) * fac:.2f}° z powietrza")
