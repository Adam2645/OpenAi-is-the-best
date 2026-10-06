"""Jawne rachunki do recenzji „kierunkowe odbicie od materii w odległości z”.

Każda liczba w recenzji, która nie jest cytatem z pracy, pochodzi z tego pliku.
Uruchomienie: python3 research/obliczenia.py
"""
import math as m

h = 6.62607015e-34
hbar = h / (2 * m.pi)
c = 2.99792458e8
kB = 1.380649e-23

# --- 87Rb D2 (Steck, "Rubidium 87 D Line Data") ---
lam_rb = 780.241e-9
Gamma = 2 * m.pi * 6.0666e6
M_rb = 1.443160e-25
Isat_cyc = 1.669  # mW/cm^2, przejście cykliczne sigma±

sigma0 = 3 * lam_rb**2 / (2 * m.pi)
E_ph = h * c / lam_rb


def sekcja(t):
    print(f"\n== {t} ==")


sekcja("T0. Przekrój i OD (punkt startowy)")
print(f"sigma0(780 nm) = 3λ²/2π = {sigma0:.3e} m²")
print(f"N dla OD=1 na 1 mm² = A/sigma0 = {1e-6 / sigma0:.2e}  (w punkcie startowym podano 3e9 – błąd ~1000x)")

sekcja("T1. Budżet fotonów dowolnego reflektora atomowego (Rb D2)")
P_sat = E_ph * Gamma / 2
P_el = E_ph * Gamma / 8  # maks. moc rozproszona elastycznie (koherentnie), przy s=1
print(f"maks. moc rozpraszana na atom (s→∞)  ħωΓ/2 = {P_sat:.3e} W")
print(f"maks. moc koherentna na atom (s=1)   ħωΓ/8 = {P_el:.3e} W")
print(f"N ≥ 0.1 mW / (ħωΓ/8) = {1e-4 / P_el:.2e} atomów")
A_s01 = 1.0 / (0.1 * Isat_cyc)  # cm^2, P=1 mW, s=0.1
print(f"pole wiązki dla s≤0.1 przy 1 mW = {A_s01:.2f} cm²")
a = 532e-9
print(f"atomy w warstwie 2D a=532 nm na tym polu = {A_s01 * 1e-4 / a**2:.2e}")
print(f"sigma0/a² dla a=532 nm = {sigma0 / a**2:.2f}  (pojedyncza warstwa ma OD~1)")
s = 0.1
R_sc = Gamma / 2 * s / (1 + s)
k = 2 * m.pi / lam_rb
E_r = (hbar * k) ** 2 / (2 * M_rb)
heat = R_sc * 2 * E_r / kB
print(f"szybkość rozpraszania przy s=0.1 = {R_sc:.3e} 1/s")
print(f"grzanie odrzutem ≈ {heat:.2f} K/s → 1 mK w {1e-3 / heat * 1e3:.2f} ms")
print(f"liczba fotonów/atom w 1 s przy s=0.1 = {R_sc:.2e}  (Rui 2020: degradacja od ~70)")

sekcja("T2. Ognisko w powietrzu: stożek < 1° kontra głębia ostrości")
lam_g = 532e-9
for half_deg in (0.5, 1.0):
    NA = m.sin(m.radians(half_deg))
    print(f"półkąt {half_deg}° → NA={NA:.4f} → DOF=2λ/NA² = {2 * lam_g / NA**2 * 1e3:.1f} mm")
NA_10um = m.sqrt(2 * lam_g / 10e-6)
print(f"DOF=10 µm wymaga NA={NA_10um:.3f} → półkąt {m.degrees(m.asin(NA_10um)):.1f}°")

sekcja("T3. Kryterium sprzężenia warstwy Bragga: R=tanh²(πΔn L/λ)")
for lam in (532e-9, 589e-9, 780e-9):
    dnL = m.atanh(m.sqrt(0.1)) * lam / m.pi
    print(f"λ={lam * 1e9:.0f} nm: R≥0.1 wymaga Δn·L ≥ {dnL * 1e9:.1f} nm; "
          f"dla L=10 µm Δn ≥ {dnL / 10e-6:.2e}")
dn_air = 2.8e-4  # (n-1) powietrza, ~532 nm, 1 atm
print(f"powietrze: n-1≈{dn_air:.1e}; nawet przy 100% modulacji L ≥ "
      f"{m.atanh(m.sqrt(0.1)) * lam_g / m.pi / dn_air * 1e6:.0f} µm")
for dn, lab in ((1e-3, "PTR"), (0.03, "fotopolimer, Δn~0.03")):
    for R in (0.1, 0.8):
        L = m.atanh(m.sqrt(R)) * lam_g / (m.pi * dn)
        print(f"{lab}: R={R} → L={L * 1e6:.1f} µm")

sekcja("T4. Multipleksowanie: η=(M/#/M)², η≥0.1 → M ≤ 3.16·M/#")
for Mn in (0.1, 1, 3, 10, 30, 40):
    print(f"M/#={Mn:>5}: M_max={Mn / m.sqrt(0.1):.1f}")

sekcja("T5. Widzialność: CIE 1924 V(λ)")
V = {532: 0.8849624, 555: 1.0, 589: 0.7691547, 633: 0.2353344,
     780: 1.499e-05, 795: 5.2578e-06, 852: 4.5181e-07}
for l, v in V.items():
    print(f"{l} nm: V={v:.3e}; 1 mW → {683 * v * 1e-3:.2e} lm")

sekcja("T6. Wariant warstwowy C: ile płaszczyzn adresowanych kątem przy jednej λ")
# Niesłantowana siatka odbiciowa grubości L, kąt wewnętrzny θ, q = cosθ.
# Niedopasowanie Bragga Δβ = 2kn·Δq; pierwsze zero sinc: Δβ·L/2 = π → Δq = λ/(2nL).
# Dostępny zakres q: od θ=0 do θ_max (sinθ_max = 1/n przy padaniu ślizgowym z powietrza).
lam, n = 532e-9, 1.5
q_range = 1 - m.sqrt(1 - 1 / n**2)
print(f"dostępny zakres q=cosθ wewnątrz (n={n}): {q_range:.3f}")
for L in (2e-6, 8e-6, 10e-6, 100e-6):
    dq = lam / (2 * n * L)
    N_ch = q_range / dq
    dn_min = m.atanh(m.sqrt(0.1)) * lam / (m.pi * L)
    print(f"L={L * 1e6:5.0f} µm: Δq={dq:.4f}, kanały ≈ {N_ch:5.1f}, "
          f"łączna głębokość ≈ {N_ch * L * 1e3:.2f} mm, Δn_min(R=0.1)={dn_min:.1e}")
# szerokość kątowa przy θ=30°: Δθ ≈ λ/(2nL sinθ)
for L in (8e-6,):
    print(f"L={L * 1e6:.0f} µm, θ=30°: Δθ(pierwsze zero) ≈ {m.degrees(lam / (2 * n * L * 0.5)):.2f}°")

sekcja("T7. Cząstka w pułapce fotoforetycznej (J): dyfrakcja i ułamek w stożku")
d, lam = 10e-6, 532e-9
print(f"pierwsze zero płata dyfrakcyjnego 1.22λ/d = {m.degrees(1.22 * lam / d):.2f}°")
print(f"d potrzebne, by płat zmieścił się w półkącie 0.5°: {1.22 * lam / m.radians(0.5) * 1e6:.0f} µm")
w0 = 10e-6
frac_int = 1 - m.exp(-2 * (d / 2) ** 2 / w0**2)
cone = 2 * m.pi * (1 - m.cos(m.radians(0.5)))
print(f"ułamek przechwycony (w0=10 µm): {frac_int:.3f}; stożek 1° = {cone:.3e} sr")
print(f"izotropowo do stożka: {frac_int * cone / (4 * m.pi):.1e} mocy sondy (wymagane 0.1)")
print(f"detektor 1 cm² w 30 cm, izotropowo: {frac_int * 1e-3 * 1e-4 / (4 * m.pi * 0.3**2) * 1e9:.1f} nW")

sekcja("T8. Siatka gazowa w powietrzu (H): średnia czasowa i koszt podtrzymania")
lam = 532e-9
dn_gas = 2.3e-5  # z η=0.96 na 10 mm (Michine & Yoneda 2020)
print(f"κL dla η=0.96: asin(√0.96)={m.asin(m.sqrt(0.96)):.3f}; Δn={m.asin(m.sqrt(0.96)) * lam / (m.pi * 10e-3):.2e}")
for tau, f, eta, lab in ((10e-9, 10, 0.96, "okno 10 ns, 10 Hz"), (500e-9, 10, 0.5, "500 ns, 10 Hz, η=0.5")):
    print(f"{lab}: wypełnienie {tau * f:.0e} → średnio {1e-3 * eta * tau * f * 1e9:.2f} nW z 1 mW")
print(f"L(η=0.1) dla Δn={dn_gas:.1e}: {m.asin(m.sqrt(0.1)) * lam / (m.pi * dn_gas) * 1e3:.2f} mm")
print(f"ciągłe podtrzymanie: 50 mJ × 1/(10 ns) = {50e-3 / 10e-9 / 1e6:.0f} MW")

sekcja("T9. Stożek < 1° kontra widzenie obuoczne")
D = 0.30
spot = 2 * D * m.tan(m.radians(0.5))
print(f"plamka stożka 1° (pełny) w odległości 30 cm: {spot * 1e3:.1f} mm; rozstaw oczu ~63 mm "
      f"→ potrzebny kąt pełny {m.degrees(2 * m.atan(0.0315 / D)):.1f}°")
th_int = [11.69, 20.03, 25.51, 30.60, 34.81]
print("kąty zewnętrzne (z powietrza) dla kanałów TMM:",
      [round(m.degrees(m.asin(1.5 * m.sin(m.radians(t)))), 1) for t in th_int])
I_probe = 1e-3 / (m.pi * 0.05**2)  # 1 mW na kole o średnicy 1 mm, W/cm²
print(f"1 mW na Ø1 mm: {I_probe * 1e3:.0f} mW/cm², dawka w 1 s {I_probe:.3f} J/cm² "
      f"wobec 3 mW/cm²·100 h = {3e-3 * 3.6e5:.0f} J/cm² (Curtis & Psaltis 1994)")
print(f"moment od sondy na krawędzi płatka 150 µm: {2e-3 / c * 75e-6:.1e} N·m; "
      f"sztywność dla 0,15°: {2e-3 / c * 75e-6 / m.radians(0.15):.1e} N·m/rad")
