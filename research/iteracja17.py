"""Iteracja 17: RCWA (TM, pol. p) dla dwóch skośnych warstw L = 100 µm, n1 = 0,002.

Warstwa A (górna): wejście 20,0° wewnątrz, wyjście wzdłuż normalnej (w górę).
Warstwa B (dolna, 10 mm niżej): wejście 22,0° wewnątrz, wyjście wzdłuż normalnej.
Warstwy liczone osobno RCWA i łączone niekoherentnie: przy źródle o długości koherencji
~0,1–0,2 mm różnica dróg przez przekładkę 10 mm (~30 mm) wyklucza interferencję.
Przekładka n = 1,48 pominięta (odbicie na granicy 1,5/1,48 ~ 5·10⁻⁵).
Uruchomienie: python3 research/iteracja17.py
"""
import numpy as np, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rcwa import solve

lam0, n0, L, n1 = 532e-9, 1.5, 100e-6, 0.002
M = 3


def grating(theta_in, lam_design=lam0, spp=32, flip=False, out_tilt_int=0.0):
    """Siatka skośna zapisana dla (wejście θ_in w dół) → (wyjście w górę, odchylone o out_tilt_int)."""
    beta = 2 * np.pi * n0 / lam_design
    t, o = np.radians(theta_in), np.radians(out_tilt_int)
    Kx = beta * (np.sin(t) - np.sin(o))
    Kz = beta * (np.cos(t) + np.cos(o))
    Lz = 2 * np.pi / Kz
    ns = int(round(L / Lz)) * spp
    lay = [{"kind": "slanted", "eps0": n0**2, "e1": n0 * n1, "Kz": -Kz if flip else Kz,
            "L": ns / spp * Lz, "slices": ns}]
    return lay, 2 * np.pi / abs(Kx), np.sign(Kx)


def air(kx):
    s = np.clip(kx, -1, 1)
    return np.degrees(np.arcsin(s))


def Rp_air(th_air):
    ti = np.radians(th_air); tt = np.arcsin(np.sin(ti) / n0)
    return ((n0 * np.cos(ti) - np.cos(tt)) / (n0 * np.cos(ti) + np.cos(tt))) ** 2


def run(lay, Lx, sgn, theta, lam=lam0):
    # znak Kx: przy ujemnym Kx odwracamy kierunek x (kąt padania ze znakiem minus)
    kx, DEr, DEt = solve(lam, sgn * theta, n0, n0, "p", lay, M=M, Lx=Lx)
    return sgn * kx, DEr, DEt


thA, thB = 20.0, 22.0
A, LxA, sA = grating(thA)
B, LxB, sB = grating(thB)
Af, _, _ = grating(thA, flip=True)

print("== 1. Sprawność projektowa i wyższe rzędy ==")
for name, (lay, Lx, sg), th in (("A", (A, LxA, sA), thA), ("B", (B, LxB, sB), thB)):
    kx, DEr, DEt = run(lay, Lx, sg, th)
    i0 = np.argmin(np.abs(kx))
    others = [(air(kx[i]), DEr[i]) for i in range(len(kx)) if i != i0 and DEr[i] > 1e-9]
    print(f"warstwa {name}: wejście {th}° wewn ({air(n0 * np.sin(np.radians(th))):.2f}° w powietrzu), "
          f"η do normalnej = {DEr[i0]:.4f}, transmisja zerowa = {DEt[np.argmin(np.abs(kx - n0 * np.sin(np.radians(th))))]:.4f}, "
          f"suma = {DEr.sum() + DEt.sum():.6f}, inne odbite rzędy: " +
          ", ".join(f"{a:.1f}° → {e:.1e}" for a, e in others))

print("\n== 2. Przesłuch między kanałami ==")
for name, (lay, Lx, sg), th in (("A przy kącie kanału B", (A, LxA, sA), thB), ("B przy kącie kanału A", (B, LxB, sB), thA)):
    kx, DEr, DEt = run(lay, Lx, sg, th)
    t0 = DEt[np.argmin(np.abs(kx - n0 * np.sin(np.radians(th))))]
    refl = sorted([(air(kx[i]), DEr[i]) for i in range(len(kx)) if DEr[i] > 1e-9], key=lambda x: -x[1])
    print(f"{name}: transmisja zerowa {t0:.4f}; odbite rzędy (kąt w powietrzu → moc): " +
          ", ".join(f"{a:.2f}° → {e:.2e}" for a, e in refl[:3]))

print("\n== 3. Cieniowanie: wyjście warstwy B (w górę, wzdłuż normalnej) przechodzi przez A ==")
kx, DEr, DEt = solve(lam0, 0.0, n0, n0, "p", Af, M=M, Lx=LxA)
t0 = DEt[np.argmin(np.abs(kx))]
print(f"A odbija z powrotem w dół {DEr.sum():.4f}, przepuszcza do widza {t0:.4f}")
print("akceptacja tego „portu wyjściowego” A (wiązka w górę odchylona o δ):")
for d_air in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0):
    d_int = np.degrees(np.arcsin(np.sin(np.radians(d_air)) / n0))
    kx, DEr, DEt = solve(lam0, d_int, n0, n0, "p", Af, M=M, Lx=LxA)
    print(f"  δ = {d_air:4.2f}° w powietrzu: przepuszcza {DEt[np.argmin(np.abs(kx - n0 * np.sin(np.radians(d_int))))]:.4f}")

print("\n== 4. Bilans kanałów z interfejsami powietrza (pol. p) ==")
ToutN = 1 - ((n0 - 1) / (n0 + 1)) ** 2
for name, th in (("A", thA), ("B", thB)):
    ta = air(n0 * np.sin(np.radians(th)))
    Tin = 1 - Rp_air(ta)
    if name == "A":
        kx, DEr, DEt = run(A, LxA, sA, thA)
        sig = Tin * DEr[np.argmin(np.abs(kx))] * ToutN
    else:
        kxa, DEra, DEta = run(A, LxA, sA, thB)
        tA = DEta[np.argmin(np.abs(kxa - n0 * np.sin(np.radians(thB))))]
        kxb, DErb, DEtb = run(B, LxB, sB, thB)
        kxf, DErf, DEtf = solve(lam0, 0.0, n0, n0, "p", Af, M=M, Lx=LxA)
        sig = Tin * tA * DErb[np.argmin(np.abs(kxb))] * DEtf[np.argmin(np.abs(kxf))] * ToutN
    print(f"kanał {name}: wejście {ta:.2f}° (T_Fresnel = {Tin:.4f}), moc w kierunku normalnym u widza = {sig:.4f} mocy sondy")

print("\n== 5. Widmo odbicia warstwy A i źródło szerokopasmowe ==")
lams = lam0 + np.linspace(-3e-9, 3e-9, 121)
eta = []
for lm in lams:
    kx, DEr, DEt = run(A, LxA, sA, thA, lam=lm)
    eta.append(DEr.max())
eta = np.array(eta)
above = lams[eta >= 0.5 * eta.max()]
print(f"szczyt η = {eta.max():.4f}; FWHM widma = {(above.max() - above.min()) * 1e9:.3f} nm "
      f"(oszacowanie λ²/(2nL) = {lam0**2 / (2 * n0 * L) * 1e9:.3f} nm)")
for fw in (0.5e-9, 1.0e-9, 1.5e-9, 2.0e-9):
    sig = fw / (2 * np.sqrt(2 * np.log(2)))
    w = np.exp(-0.5 * ((lams - lam0) / sig) ** 2)
    Lc = 2 * np.log(2) / np.pi * lam0**2 / fw
    print(f"źródło gaussowskie FWHM {fw * 1e9:.1f} nm (L_c = {Lc * 1e6:.0f} µm): η średnie = {(eta * w).sum() / w.sum():.4f} "
          f"({(eta * w).sum() / w.sum() / eta.max():.0%} szczytu)")
print(f"różnica dróg przez przekładkę 10 mm (tam i z powrotem, n = 1,48): ~{2 * 1.48 * 10:.0f} mm; "
      f"droga w obrębie warstwy 2nL = {2 * n0 * L * 1e6:.0f} µm")

print("\n== 6. Śledzenie źrenicy zmianą kąta wejścia ==")
for d_air in (0.0, 0.25, 0.5, 1.0, 2.0, 5.0):
    ta = air(n0 * np.sin(np.radians(thA))) + d_air
    ti = np.degrees(np.arcsin(np.sin(np.radians(ta)) / n0))
    kx, DEr, DEt = run(A, LxA, sA, ti)
    i0 = np.argmin(np.abs(kx))
    out = air(kx[i0])
    print(f"wejście +{d_air:.2f}° w powietrzu: η = {DEr[i0]:.4f}, wyjście {out:+.2f}° w powietrzu "
          f"(przesunięcie plamki w 30 cm: {300 * np.tan(np.radians(out)):+.1f} mm)")
