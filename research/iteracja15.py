"""Iteracja 15: hipotezy wdrożeniowe po trzech audytach.

1. C2 w polaryzacji p przy kącie Brewstera (TMM TE/TM, interfejsy z powietrzem).
2. Tolerancja kątowa: ile rozbieżności (np. po SLM) znosi kanał i warunek 1.
3. Szacunki dla hipotez: woksel ogniskowy (VHOE), kolektywna warstwa atomów, plazma.
Uruchomienie: python3 research/iteracja15.py
"""
import numpy as np

lam0, n0, L = 532e-9, 1.5, 10e-6


def grating_stack(periods, n1, sub=32):
    out = []
    for Lam in periods:
        n_per = int(round(L / Lam))
        ph = (np.arange(n_per * sub) + 0.5) / sub * 2 * np.pi
        out.extend((n0 + n1 * np.cos(p), Lam / sub) for p in ph)
    return out


def r_tmm(st, beta, lam, n_in, n_out, pol):
    """r dla wektora beta = n·sinθ; pol 's' (TE) albo 'p' (TM), admitancje Macleoda."""
    beta = np.atleast_1d(np.asarray(beta, float))
    k = 2 * np.pi / lam

    def adm(n):
        kz = np.sqrt(n**2 - beta**2 + 0j)
        return (kz, kz) if pol == "s" else (kz, n**2 / kz)

    _, e_in = adm(n_in)
    _, e_out = adm(n_out)
    M11 = np.ones_like(beta, dtype=complex); M12 = np.zeros_like(M11)
    M21 = np.zeros_like(M11); M22 = np.ones_like(M11)
    for n, d in st:
        kz, e = adm(n)
        dl = k * kz * d
        c, s = np.cos(dl), np.sin(dl)
        a11, a12, a21, a22 = c, -1j * s / e, -1j * e * s, c
        M11, M12, M21, M22 = (M11 * a11 + M12 * a21, M11 * a12 + M12 * a22,
                              M21 * a11 + M22 * a21, M21 * a12 + M22 * a22)
    num = e_in * M11 + e_in * e_out * M12 - M21 - e_out * M22
    den = e_in * M11 + e_in * e_out * M12 + M21 + e_out * M22
    return num / den


def fresnel(th_air_deg, pol):
    ti = np.radians(th_air_deg)
    tt = np.arcsin(np.sin(ti) / n0)
    if pol == "s":
        r = (np.cos(ti) - n0 * np.cos(tt)) / (np.cos(ti) + n0 * np.cos(tt))
    else:
        r = (n0 * np.cos(ti) - np.cos(tt)) / (n0 * np.cos(ti) + np.cos(tt))
    return r**2


def analyse(label, theta_int, n1, pol):
    q = np.cos(np.radians(theta_int))
    periods = lam0 / (2 * n0 * q)
    full = grating_stack(periods, n1)
    rows = []
    for k, t in enumerate(theta_int):
        sc = np.linspace(t - 2.5, t + 2.5, 1001)
        R = np.abs(r_tmm(full, n0 * np.sin(np.radians(sc)), lam0, n0, n0, pol)) ** 2
        i = np.argmax(R)
        tpk, Rpk = sc[i], R[i]
        th_air = np.degrees(np.arcsin(n0 * np.sin(np.radians(tpk))))
        Rf = fresnel(th_air, pol)
        sig = (1 - Rf) ** 2 * Rpk
        # akceptacja kątowa wokół szczytu (wewnątrz i z powietrza)
        above90 = sc[R >= 0.9 * Rpk]
        above50 = sc[R >= 0.5 * Rpk]
        w90 = above90.max() - above90.min()
        w50 = above50.max() - above50.min()
        fac = n0 * np.cos(np.radians(tpk)) / np.cos(np.radians(th_air))  # dθ_air/dθ_int
        rows.append((k, tpk, th_air, Rpk, Rf, sig, Rf / sig, w90, w50, w90 * fac, w50 * fac, sc, R))
    grid = np.linspace(max(0.5, theta_int.min() - 8), min(41.5, theta_int.max() + 6), 3001)
    Rg = np.abs(r_tmm(full, n0 * np.sin(np.radians(grid)), lam0, n0, n0, pol)) ** 2
    qg = np.cos(np.radians(grid))
    mask = np.ones_like(grid, bool)
    for r_ in rows:
        mask &= np.abs(qg - np.cos(np.radians(r_[1]))) > lam0 / (2 * n0 * L)
    off = Rg[mask].max() / min(r_[3] for r_ in rows)
    print(f"\n### {label}: pol {pol}, n1 = {n1}")
    for (k, tpk, ta, Rpk, Rf, sig, bgs, w90, w50, w90a, w50a, *_ ) in rows:
        print(f"kanał {k}: θ_wewn {tpk:5.2f}°, θ_pow {ta:5.1f}°, R_wewn {Rpk:.3f}, Fresnel {Rf:.4f}, "
              f"sygnał {sig:.3f}, tło/sygnał {bgs:.1%}, akceptacja 90%: {w90:.2f}° wewn = {w90a:.2f}° z pow., "
              f"50%: {w50:.2f}° wewn = {w50a:.2f}° z pow.")
    print(f"maks. R poza kanałami / najsłabszy kanał = {off:.1%}")
    return rows


print("== 1. Polaryzacja p przy kącie Brewstera ==")
thB = np.degrees(np.arctan(n0))
thB_int = 90 - thB
print(f"kąt Brewstera powietrze→polimer {thB:.2f}°, wewnątrz {thB_int:.2f}°; "
      f"czynnik sprzężenia p |cos 2θ| = {abs(np.cos(np.radians(2 * thB_int))):.3f}")
orig = np.degrees(np.arccos(np.array([0.98, 0.94, 0.90, 0.86, 0.82])))
qB = np.cos(np.radians(thB_int))
brew = np.degrees(np.arccos(qB + 0.03 * np.array([2, 1, 0, -1, -2])))
print("projekt Brewstera: kąty wewnętrzne", np.round(brew, 2))
analyse("Projekt pierwotny", orig, 0.008, "s")
analyse("Projekt pierwotny", orig, 0.008, "p")
for n1 in (0.008, 0.015, 0.03):
    analyse("Wachlarz wokół Brewstera", brew, n1, "p")
analyse("Wachlarz wokół Brewstera", brew, 0.03, "s")

print("\n== 2. Tolerancja kątowa wiązki (np. po SLM) ==")
alpha = np.radians(0.5)  # półkąt stożka warunku 1
print(f"Abbe: najmniejszy szczegół przy półkącie 0,5°: λ/(2 sin 0,5°) = {lam0 / (2 * np.sin(alpha)) * 1e6:.1f} µm")
w0 = lam0 / (np.pi * alpha)
print(f"wiązka Gaussa o rozbieżności 0,5°: w0 = λ/(π·θ) = {w0 * 1e6:.1f} µm (średnica 2w0 = {2 * w0 * 1e6:.1f} µm)")
for f in (0.5, 1, 2):
    th0 = alpha / f
    print(f"  w0 = {lam0 / (np.pi * th0) * 1e6:5.1f} µm (θ0 = {np.degrees(th0):.2f}°): "
          f"ułamek mocy w półkącie 0,5° = {1 - np.exp(-2 * alpha**2 / th0**2):.1%}")
print(f"woksele na warstwie o aperturze 1 cm przy szczególe 30,5 µm: ~{(1e-2 / 30.5e-6) ** 2:.1e}")

print("\n== 3a. Woksel ogniskowy (VHOE / hologram z SLM) ==")
for name, full_deg in (("stożek 1° (warunek 1)", 1.0), ("stożek 12° (dwoje oczu w 30 cm)", 12.0)):
    NA = np.sin(np.radians(full_deg / 2))
    print(f"{name}: NA = {NA:.4f}, szerokość woksla 1,22λ/NA = {1.22 * lam0 / NA * 1e6:.1f} µm, "
          f"głębokość 2λ/NA² = {2 * lam0 / NA**2 * 1e3:.3f} mm")

print("\n== 3b. Warstwa kolektywna (F): skala szerokości linii ==")
lam_rb = 780.241e-9
for a in (266e-9, 400e-9, 532e-9):
    g = 3 / (4 * np.pi) * (lam_rb / a) ** 2
    print(f"a = {a * 1e9:.0f} nm (a/λ = {a / lam_rb:.2f}): Γ_kol/Γ ≈ (3/4π)(λ/a)² = {g:.2f}; "
          f"szacunek N dla 0,1 mW, jeśli bilans skaluje się z Γ_kol: {8.24e7 / g:.1e}")

print("\n== 3c. Plazma w powietrzu (H/T3): gęstość i czas życia ==")
e, me, eps0, c = 1.602e-19, 9.109e-31, 8.854e-12, 2.998e8
w = 2 * np.pi * c / lam0
nc = eps0 * me * w**2 / e**2 * 1e-6  # cm^-3
print(f"gęstość krytyczna n_c(532 nm) = {nc:.2e} cm⁻³; powietrze: 2,5e19 cząsteczek/cm³")
for Lx in (10e-6, 100e-6, 1e-3):
    dn = np.arctanh(np.sqrt(0.1)) * lam0 / (np.pi * Lx)
    print(f"L = {Lx * 1e6:6.0f} µm: Δn = {dn:.1e} → n_e = 2·Δn·n_c = {2 * dn * nc:.1e} cm⁻³ "
          f"({2 * dn * nc / 2.5e19:.1%} cząsteczek powietrza)")
Lam_b = lam0 / 2
for Da in (10, 100):
    tau = (Lam_b * 1e2) ** 2 / (4 * np.pi**2 * Da)
    print(f"siatka wsteczna Λ = {Lam_b * 1e9:.0f} nm, dyfuzja ambipolarna D = {Da} cm²/s (założenie): "
          f"τ ≈ Λ²/(4π²D) = {tau * 1e12:.2f} ps")
print(f"skalowanie zmierzonego τ = 68 ps (Λ = 15,3 µm) jak Λ²: {68 * (Lam_b / 15.3e-6) ** 2 * 1e3:.0f} fs")


print("\n\n== 1b. Poprawka: okno szukania ±1° i wachlarz Brewstera o skoku 0,04 w cosθ ==")


def analyse2(label, theta_int, n1, pol, win=1.0):
    q = np.cos(np.radians(theta_int))
    full = grating_stack(lam0 / (2 * n0 * q), n1)
    out = []
    for k, t in enumerate(theta_int):
        sc = np.linspace(t - win, t + win, 401)
        R = np.abs(r_tmm(full, n0 * np.sin(np.radians(sc)), lam0, n0, n0, pol)) ** 2
        i = np.argmax(R)
        tpk, Rpk = sc[i], R[i]
        ta = np.degrees(np.arcsin(n0 * np.sin(np.radians(tpk))))
        Rf = fresnel(ta, pol)
        sig = (1 - Rf) ** 2 * Rpk
        out.append((tpk, ta, Rpk, Rf, sig))
    grid = np.linspace(max(0.5, theta_int.min() - 6), min(41.5, theta_int.max() + 4), 3001)
    Rg = np.abs(r_tmm(full, n0 * np.sin(np.radians(grid)), lam0, n0, n0, pol)) ** 2
    qg = np.cos(np.radians(grid))
    mask = np.ones_like(grid, bool)
    for o in out:
        mask &= np.abs(qg - np.cos(np.radians(o[0]))) > lam0 / (2 * n0 * L)
    off = Rg[mask].max() / min(o[2] for o in out)
    print(f"\n### {label}: pol {pol}, n1 = {n1}")
    for k, (tpk, ta, Rpk, Rf, sig) in enumerate(out):
        print(f"kanał {k}: θ_wewn {tpk:5.2f}°, θ_pow {ta:5.1f}°, R_wewn {Rpk:.3f}, Fresnel {Rf:.4f}, "
              f"sygnał {sig:.3f}, tło/sygnał {Rf / sig:.1%}")
    print(f"maks. R poza kanałami / najsłabszy kanał = {off:.1%}")
    return full, out


brew4 = np.degrees(np.arccos(qB + 0.04 * np.array([2, 1, 0, -1])))
print("wachlarz Brewstera, 4 kanały, kąty wewnętrzne:", np.round(brew4, 2))
for n1 in (0.015, 0.02, 0.03):
    analyse2("Wachlarz Brewstera 4 kanały", brew4, n1, "p")
for n1 in (0.015, 0.02):
    analyse2("Projekt pierwotny", orig, n1, "p")

print("\n== 2b. Sprawność uśredniona po gaussowskim widmie kątowym (płaszczyzna padania) ==")
full_s, out_s = analyse2("Projekt pierwotny (odniesienie)", orig, 0.008, "s")
for th0_ext in (0.25, 0.5, 1.0):
    effs = []
    for (tpk, ta, Rpk, Rf, sig) in out_s:
        d_ext = np.linspace(-3 * th0_ext, 3 * th0_ext, 241)
        ta_v = ta + d_ext
        ti_v = np.degrees(np.arcsin(np.sin(np.radians(ta_v)) / n0))
        R = np.abs(r_tmm(full_s, n0 * np.sin(np.radians(ti_v)), lam0, n0, n0, "s")) ** 2
        wgt = np.exp(-2 * d_ext**2 / th0_ext**2)
        effs.append((R * wgt).sum() / wgt.sum() / Rpk)
    cone = 1 - np.exp(-2 * 0.5**2 / th0_ext**2)
    print(f"rozbieżność wiązki θ0 = {th0_ext}° (z powietrza, 1/e²): sprawność Bragga / szczyt = "
          f"{' / '.join(f'{e:.2f}' for e in effs)}; ułamek mocy wiązki kołowej w półkącie 0,5° = {cone:.1%}")


print("\n== 4. Kandydat modelowy: laminat (przekładki 51 µm, n = 1,48) + pol p + n1 = 0,02 ==")


def laminate(periods, n1, sp=51e-6, n_sp=1.48, sub=32, only=None):
    out = []
    for k, Lam in enumerate(periods):
        n_per = int(round(L / Lam))
        if only is None or k in only:
            ph = (np.arange(n_per * sub) + 0.5) / sub * 2 * np.pi
            out.extend((n0 + n1 * np.cos(p), Lam / sub) for p in ph)
        else:
            out.append((n0, n_per * Lam))
        if k < len(periods) - 1:
            out.append((n_sp, sp))
    return out


def psf_pol(st, theta, pol, B=10e-9, zmax=280e-6, nl=301, nz=2400):
    k = np.linspace(2 * np.pi / (lam0 + B), 2 * np.pi / (lam0 - B), nl)
    b = n0 * np.sin(np.radians(theta))
    r = np.array([r_tmm(st, b, 2 * np.pi / kk, n0, n0, pol)[0] for kk in k])
    z = np.linspace(0, zmax, nz)
    h = (np.hanning(nl) * r) @ np.exp(-1j * 2 * n0 * np.cos(np.radians(theta)) * np.outer(k, z))
    I = np.abs(h) ** 2
    above = z[I >= I.max() / 2]
    return I, (z * I).sum() / I.sum(), above.max() - above.min()


per = lam0 / (2 * n0 * np.cos(np.radians(orig)))
for pol, n1 in (("s", 0.008), ("p", 0.02)):
    st = laminate(per, n1)
    rows, Is, mus = [], [], []
    for k, t in enumerate(orig):
        sc = np.linspace(t - 1, t + 1, 401)
        R = np.abs(r_tmm(st, n0 * np.sin(np.radians(sc)), lam0, n0, n0, pol)) ** 2
        i = np.argmax(R); tpk, Rpk = sc[i], R[i]
        ta = np.degrees(np.arcsin(n0 * np.sin(np.radians(tpk))))
        Rf = fresnel(ta, pol)
        I, mu, fw = psf_pol(st, tpk, pol)
        Is.append(I); mus.append(mu)
        alone = np.abs(r_tmm(laminate(per, n1, only={k}), n0 * np.sin(np.radians(tpk)), lam0, n0, n0, pol)[0]) ** 2
        wrong = np.abs(r_tmm(laminate(per, n1, only=set(range(5)) - {k}), n0 * np.sin(np.radians(tpk)), lam0, n0, n0, pol)[0]) ** 2
        rows.append((tpk, ta, Rpk, Rf, (1 - Rf) ** 2 * Rpk, mu, fw, wrong / alone))
    print(f"\npol {pol}, n1 = {n1}:")
    for k, (tpk, ta, Rpk, Rf, sig, mu, fw, xt) in enumerate(rows):
        print(f"kanał {k}: θ_pow {ta:5.1f}°, R_wewn {Rpk:.3f}, sygnał {sig:.3f}, tło/sygnał {Rf / sig:.1%}, "
              f"μ {mu * 1e6:6.1f} µm, FWHM {fw * 1e6:4.1f} µm, moc innych warstw / sygnał {xt:.1%}")
    print("kroki μ [µm]:", np.round(np.diff(mus) * 1e6, 1),
          " C sąsiadów:", [round(float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum())), 3)
                          for a, b in zip(Is[:-1], Is[1:])])

print("\n== 5. Étendue hologramu z SLM (obraz rzeczywisty w powietrzu) ==")
for size, full_deg in ((0.01, 1.0), (0.01, 12.0), (0.05, 12.0)):
    s = np.sin(np.radians(full_deg / 2))
    Np = 2 * size * s / lam0
    print(f"obraz {size * 100:.0f} cm, stożek {full_deg}°: ~{Np:.0f} pikseli na bok "
          f"({Np**2:.1e} łącznie) przy skoku ≤ {lam0 / (2 * s) * 1e6:.2f} µm w płaszczyźnie obrazu")
