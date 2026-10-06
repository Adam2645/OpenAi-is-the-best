# Recenzja: kierunkowe odbicie wiązki od materii w odległości z

Dziennik iteracji. Każda iteracja kończy się jednym werdyktem:
POTWIERDZONE, ODRZUCONE albo NIEROZSTRZYGNIĘTE. Liczby, które nie są cytatami,
pochodzą z `research/obliczenia.py` (sekcje T0–T5). „Odczyt z wykresu” oznacza
liczbę odczytaną z rysunku w pracy, a nie podaną w tekście. Takie liczby są
słabsze niż wartości z tekstu.

## Warunki sukcesu (wszystkie naraz)

1. Co najmniej 10% mocy wejściowej wraca w stożek mniejszy niż 1°.
2. Zmiana sterowania przesuwa płaszczyznę odbicia o ≥ 10 µm przy tej samej
   barwie źródła.
3. Przy sondzie 1 mW detektor w odległości 30 cm mierzy sygnał z podanym SNR.
4. Ośrodek przeżywa 1 s pracy (bez wygrzania atomów i bez wybielenia polimeru).
5. Cytat do pomiaru albo jawne równanie z podstawionymi liczbami.

---

## Iteracja 0 — punkt startowy (A, E) i korekta rachunkowa

Mechanizm A (lustro Bragga z zimnych atomów w sieci 1D) jest POTWIERDZONY
jako lustro, ale nie jako wyświetlacz. Weryfikacja źródła:
Schilke, Zimmermann, Courteille, Guerin, PRL 106, 223903 (2011),
doi:10.1103/PhysRevLett.106.223903. Podają „R_max ≃ 80%” przy N = 5·10⁷
atomów, L ∼ 3 mm (∼7700 warstw), ρ = 7·10¹¹ cm⁻³ i sondzie o przewężeniu
35 µm. Warunek 2 pada, bo z jest skwantowane okresem sieci.

**Korekta (T0).** W punkcie startowym zapisano, że 1 mm² przy OD = 1
wymaga około 3·10⁹ atomów. To błąd o czynnik ~1000. Poprawny rachunek:
N = A/σ₀ = 10⁻⁶ m² / 2,907·10⁻¹³ m² = **3,4·10⁶**. Wniosek dla E (pęsety
jako piksele) się nie zmienia, bo największe tablice mają kilka tysięcy
atomów, czyli brakuje czynnika ~500. Do protokołu trafia jednak poprawna
liczba.

**Uwaga o barwie (T5).** Linie Rb (780/795 nm) leżą na granicy widzialności.
Według CIE 1924 V(780 nm) = 1,5·10⁻⁵, więc 1 mW przy 780 nm daje
1,0·10⁻⁵ lm. Ta sama moc przy 532 nm daje 0,60 lm, czyli 6·10⁴ razy więcej.
Każdy mechanizm oparty na Rb D2 jest więc dla oka praktycznie ciemny,
niezależnie od R. Na D2 (589 nm, V = 0,77) jest wyjątkiem.

---

## Iteracja 1 — C. Multipleksowane siatki Bragga w jednym ośrodku

Pytanie: czy da się multipleksować wiele siatek Bragga w jednym ośrodku
tak, aby każda odbijała z innej głębokości przy tej samej λ, i jaki jest
limit liczby siatek, zanim sprawność spadnie poniżej 10%?

**Mechanizm:** Multipleksowanie kątowe objętościowych siatek fazowych.
Rozważono dwa warianty:
- **C1, wspólna objętość:** wszystkie siatki zajmują całą grubość
  i dzielą zakres dynamiczny Δn.
- **C2, warstwy:** każda siatka w osobnej cienkiej warstwie na innej
  głębokości, z własnym okresem Λ_k, dopasowana do innego kąta przy tej
  samej λ.

**Liczby:**
- Prawo M/#: η = (M/#/M)², więc η ≥ 0,1 daje M ≤ 3,16·M/# (T4).
- Zmierzone M/#:

  | Materiał | Grubość | M/# | M_max przy η ≥ 10% |
  |---|---|---|---|
  | Fe:LiNbO₃ (Mok 1996) | 1 cm | 1,37 | 4,3 |
  | DuPont HRF-150 (Pu & Psaltis 1996) | 100 µm | 6,5 | 20,6 |
  | fotopolimer Bell Labs (Dhar 1999) | 1 mm | 42 | 133 |
  | szkło PTR, Δn = 10⁻³, 532 nm (rachunek) | 5 mm | ~29,5 | ~93 |

- C2 (T3, T6): λ = 532 nm, n = 1,5. Warstwa L odbija R ≥ 0,1, gdy
  Δn ≥ 0,104·λ/L, czyli 5,5·10⁻³ dla L = 10 µm. Liczba kanałów
  rozdzielnych kątem to N_ch ≈ 0,255·2nL/λ:
  - L = 8 µm: ~11,5 kanału na 0,09 mm głębokości;
  - L = 10 µm: ~14 kanałów na 0,14 mm;
  - L = 100 µm: ~144 kanały na 14 mm, wtedy wystarcza Δn ≥ 5,5·10⁻⁴.
- Szerokość kątowa warstwy 8 µm przy θ = 30° to ~2,5° (do pierwszego zera).
- A, OD nie dotyczą (ośrodek ciągły). θ = 0–42° wewnątrz ośrodka.

**Dowód:**
- Mok, Burr, Psaltis, Opt. Lett. 21, 896 (1996), doi:10.1364/OL.21.000896:
  „M/# is the constant of proportionality between diffraction efficiency
  and the number of holograms squared”; równanie 1: η = (M/#/M)².
- Dhar i in., Opt. Lett. 24, 487 (1999), doi:10.1364/OL.24.000487:
  „M/# values as high as 42 in 1-mm-thick formats”.
- An, Psaltis, Burr, Appl. Opt. 38, 386 (1999): 10 000 hologramów
  w Fe:LiNbO₃ przy η ≈ 7·10⁻⁹ każdy. To ilustracja ceny dużego M.
- Ott i in., Opt. Express 21, 29620 (2013), doi:10.1364/OE.21.029620:
  - 2 siatki odbiciowe w PTR o grubości 5,5 mm, „exceeding 99% for each
    individual grating”, ale każda przy **innej λ**;
  - „90% of the power is localized within the first quarter of the
    grating”.
- Luo i in., J. Biomed. Opt. 16, 096015 (2011), doi:10.1117/1.3626211:
  2 siatki „sensitive to a specific depth”, Δz ∼ 50 µm, η ≈ 30%.
  Tu jednak głębokość dotyczy **obiektu** w obrazowaniu, a odczyt był
  w **różnych barwach** fluorescencji.
- Curtis & Psaltis, Appl. Opt. 33, 5396 (1994): utrwalony UV hologram
  DuPont odczytywany „for 100 h” przy 3 mW/cm². Warunek 4 dla polimeru
  utrwalonego jest więc spełniony.

**Test zabójczy:**
- **C1, warunek 2.** Każda siatka we wspólnej objętości zajmuje całą
  grubość. Silna siatka odbija głównie z przedniej ćwiartki (Ott 2013),
  więc głębokości nie da się wybrać. „Głębokość” można zakodować tylko
  w fazie (holograficzna soczewka z ogniskiem w z). Wtedy obowiązuje T2:
  przy stożku < 1° DOF ≥ 3,5 mm, czyli 350× więcej niż 10 µm.
- **C2, warunek 2.** Nie pada na papierze: ~14 płaszczyzn co 10 µm przy
  Δn ≥ 5,5·10⁻³, co mieści się w zasięgu fotopolimerów (Δn ~ 0,03).
  Nie ma jednak pomiaru takiego stosu przy jednej λ z adresowaniem
  kątowym.
- **CEL.** Płaszczyzna odbicia leży wewnątrz bryły materiału, nie
  w powietrzu.

**Werdykt: NIEROZSTRZYGNIĘTE.**
- Odpowiedź na pytanie startowe: przy wspólnej objętości limit to
  M ≤ 3,16·M/#, maksymalnie ~133 siatki (M/# = 42, 1 mm). Prawo
  POTWIERDZONE pomiarem (Mok 1996, Dhar 1999). Siatki te nie odbijają
  jednak z różnych głębokości, więc **C1 jako selektor głębokości jest
  ODRZUCONE** (warunek 2: DOF ≥ 3,5 mm wobec 10 µm, T2).
- C2 spełnia na papierze warunki 1, 3, 4 i 5:
  - kierunkowość jak lustro, stożek = rozbieżność wiązki;
  - 0,1 mW odbite daje SNR ≫ 10³;
  - utrwalony polimer jest stabilny 100 h;
  - jawne równania T3 i T6.
- Warunek 2 dla C2 nie jest zmierzony. Limitem nie jest tu M/#, tylko
  liczba kanałów kątowych: ~1,4 płaszczyzny na µm grubości warstwy.
- Nie wolno tego uogólniać na „obraz w powietrzu”: obraz siedzi w bloku
  materiału.

**Następne pytanie:** Czy istnieje pomiar stosu ≥ 3 warstw siatek
odbiciowych (lub mikrohologramów wielowarstwowych) przy jednej λ,
z R ≥ 0,1 na warstwę i adresowaniem kątowym, a nie ogniskowaniem
wysokiej NA? (Zlecone agentowi: iteracja 8.)

---

## Iteracja 2 — D. Metapowierzchnia jako cienki modulator fazy (ognisko w z)

**Mechanizm:** Przestrajalna metasoczewka (odbiciowa albo transmisyjna)
skupia światło w ognisku w powietrzu w odległości z. W punkcie z nie ma
materii. Materia odbijająca leży w płaszczyźnie metapowierzchni.

**Liczby:** λ = 532 nm, apertura D = 1 cm, z = 30 cm, NA = D/2z = 0,0167,
pełny kąt stożka 1,91°. Krążek Airy'ego 0,61λ/NA = 19,5 µm.
DOF = 2λ/NA² = 3,83 mm. Sprawność skupiania 40–86% (zob. Dowód).
N, A, OD nie dotyczą tego mechanizmu, bo nie ma atomów rozpraszających w z.

**Dowód:**
- Khorasaninejad i in., Science 352, 1190 (2016), doi:10.1126/science.aaf6644:
  sprawność „86, 73, and 66%” przy 405/532/660 nm.
- Arbabi E. i in., Nat. Commun. 9, 812 (2018), doi:10.1038/s41467-018-03155-6:
  MEMS, 915 nm, „>60 diopters (about 4%) change … upon a 1-µm movement”,
  sprawność 40–45%.
- Badloe i in., Adv. Sci. 8, 2102646 (2021), doi:10.1002/advs.202102646:
  ciekły kryształ, 633 nm, dwa dyskretne ogniska, „43.5% and 44.0%”.
- Smalley i in., Nature 553, 486 (2018), doi:10.1038/nature25176:
  „Clipping restricts … all technologies in which the light scattering
  surface and the image point are physically separate.”

**Test zabójczy (T2): warunek 1 wyklucza się z warunkiem 2.**
Dla każdego obrazu tworzonego przez ognisko:
- Stożek o półkącie < 1° wymusza NA ≤ 0,0175, czyli DOF ≥ 3,5 mm.
  Przy pełnym kącie < 1° DOF ≥ 14 mm.
- Rozróżnialny krok 10 µm wymaga DOF ≤ 10 µm, czyli NA ≥ 0,326,
  czyli półkąta 19°.
- Przesunięcie ogniska o 10 µm jest technicznie trywialne
  (Δf/f = 3,3·10⁻⁵ przy demonstrowanych > 60 D). Zmienia ono jednak
  natężenie na osi tylko o ~1,6% i nie tworzy nowego, adresowalnego woksla.
- Do tego w z nie ma materii, więc nie spełnia to CELU „odbicia od materii
  w z”. Obraz jest widoczny tylko z wnętrza stożka (Smalley 2018, „clipping”).

**Werdykt: ODRZUCONE** jako odbicie od materii w z. Warunek 2 w sensie
adresowalnym pada liczbowo: DOF 3,5–14 mm wobec wymaganych 10 µm.
Częściowo POTWIERDZONE, tylko jako rzeczywisty obraz lotniczy
(nie hologram, nie odbicie w z):
- warunek 1 przy półkącie 0,955° i sprawności 40–86%;
- warunek 3: ≥ 0,4 mW w ognisku, czyli ~10¹⁵ fotonów/s. Shot-noise SNR
  ~3·10⁷ w 1 s to górna granica, a obserwator musi być w stożku;
- warunek 4: dawka 1,27 mJ/cm² w 1 s wobec ns-LIDT TiO₂ ~0,5 J/cm²
  (Jung i in., Adv. Opt. Mater. 2025). Progu CW nie znaleziono;
- warunek 5.

**Wniosek ogólny (T2):** Jedyną drogą do spełnienia 1 i 2 naraz jest
materia fizycznie zlokalizowana w z. Rozdzielczość osiową daje wtedy
grubość warstwy L, a kąt stożka zależy od rozmiaru poprzecznego wiązki.

**Następne pytanie:** Jaka jest minimalna modulacja współczynnika
załamania Δn, przy której warstwa grubości L ≤ 10 µm odbija R ≥ 0,1?
(Rozstrzygnięcie rachunkiem: T3.)

**Odpowiedź (T3):** R = tanh²(πΔnL/λ) ≥ 0,1 wymaga Δn·L ≥ 0,1042·λ.
Przy 532 nm to 55,5 nm, czyli dla L = 10 µm Δn ≥ 5,5·10⁻³.
Powietrze ma n − 1 ≈ 2,8·10⁻⁴. Nawet przy 100% modulacji gęstości warstwa
musi mieć ≥ 198 µm. **Odbicie Bragga od samego powietrza nie może być
zlokalizowane lepiej niż ~0,2 mm**, a realne Δn ≪ n − 1 daje warstwy
milimetrowe. Fotopolimer (Δn ~ 0,03) potrzebuje L = 1,8 µm dla R = 0,1
i 8,1 µm dla R = 0,8.

---

## Iteracja 3 — B. Selektywne odbicie od par przy dielektryku

**Mechanizm:** Odbicie Fresnela na granicy okno–para atomowa z rezonansowym
współczynnikiem n_v: R = |(n_w − n_v)/(n_w + n_v)|²
(Bloch & Ducloy, Adv. At. Mol. Opt. Phys. 50, 91 (2005), równanie 10).
W przybliżeniu pierwszego rzędu ΔR/R₀ = −[4n_w/(n_w² − 1)]·Re(n_v − 1)
(równanie 11).

**Liczby:**
- λ = 780 nm (Rb).
- z = granica okna. Głębokość sondowania λ/2π = 124 nm
  (Laliotis i in., AVS Quantum Sci. 3, 043501 (2021)).
- θ = 64 mrad, okno YAG (n = 1,821), R₀ ≈ 8,5%.
- N = 1,2–3,6·10¹⁷ cm⁻³ przy T = 367–427 °C.
- Szczyt δR = (R − R₀)/R₀ ≈ +2,6, czyli R ≈ 30% (odczyt z wykresu).
  Rezonansowy wkład atomów ΔR ≈ 0,22.
- Przy zwykłej gęstości ~10¹³ cm⁻³ ΔR ~ 10⁻⁴ (Bloch & Ducloy 2005).

**Dowód:**
- Sautenkov, Saakyan, Bobrov, Zelener, JQSRT 328, 109153 (2024),
  doi:10.1016/j.jqsrt.2024.109153 (arXiv:2312.06243).
- Keaveney i in., PRL 109, 233001 (2012): „peak index n=1.26±0.02”
  przy 5·10¹⁶ cm⁻³ i warstwie 250 nm.
- Bloch & Ducloy: „increasing the length L (L≫λ) does not increase the
  reflected field”.
- Komórki klinowe: Keaveney i in. PRL 108, 173601 (2012), L = 30 nm–2 µm.
  Peyrot i in. PRL 120, 243401 (2018), L = 50 nm–1,5 µm.
- Sargsyan i in., Opt. Lett. 42, 1476 (2017): przesunięcie linii
  ≈ 240 MHz przy L = 40 nm, szerokość γ[MHz] ≈ 15000/L[nm].

**Test zabójczy: warunek 2.**
- Płaszczyzna odbicia jest przyklejona do granicy okna. Grubość warstwy
  odbijającej to ~0,12 µm.
- W komórce klinowej największy zakres zmiany L to 2 µm, czyli mniej
  niż wymagane 10 µm. Zmiana L dodatkowo przesuwa i poszerza linię,
  czyli zmienia rezonansową „barwę”.
- Warunek 1 jest spełniony tylko przy 3,6·10¹⁷ cm⁻³ i 427 °C.
  Z wartości R ≈ 30% aż 8,5 punktu to nierezonansowy Fresnel okna.
  Pasmo ma tylko 10–40 GHz. Rb jest niewidoczne (T5).

**Werdykt: ODRZUCONE.** Powód liczbowo: Δz_max ≈ 2 µm < 10 µm, a płaszczyzny
nie da się oderwać od okna. Warunek 4 jest spełniony (para się nie
niszczy, a nasycenie w gęstej parze I_sat ≥ 1,5 kW/cm²). To nie ratuje
warunku 2.

**Następne pytanie:** Czy mechanizm z sondą w objętości ośrodka
(uporządkowana warstwa atomów, którą da się przesunąć) przejdzie
budżet fotonów przy 1 mW? (Iteracja 4.)

---

## Iteracja 4 — F. Rozpraszanie kolektywne: gęsta chmura i warstwa 2D (lustro subradiacyjne)

**Mechanizm:** Kolektywne rozpraszanie zimnych atomów. W granicy
uporządkowanej jest to pojedyncza warstwa 2D w sieci o stałej a < λ,
która odbija spekularnie, bo dla a < λ istnieje tylko rząd zerowy
(Shahmoon i in., PRL 118, 113601 (2017); Bettles i in., PRL 116, 103602 (2016)).

**Liczby:**
- λ = 780,24 nm, a = 532 nm (a/λ = 0,68), θ = 0° (odbicie wstecz).
- N ≈ 200 (Rui 2020), do 1500 (Srakaew 2023).
- σ₀/a² = 1,03, czyli pojedyncza pełna warstwa ma OD ≈ 1. To jest
  powód, dla którego w ogóle działa.
- Zmierzone R = 0,58(3) przy s ≈ 3·10⁻⁴ (rachunek z liczby fotonów
  podanej w pracy).

**Dowód:**
- Rui i in., Nature 583, 369 (2020), doi:10.1038/s41586-020-2463-x:
  - „R ≃ 0.58(3)”; wypełnienie „η ≃ 0.92 … on ≃ 200 lattice sites”;
  - przy nieporządku pionowym R = 0,13, w płaszczyźnie R = 0,07;
  - poszerzenie linii powyżej „70 photons per lattice site”;
  - w sieci 40 E_r ubytek wypełnienia 0,114 na ms już przy s ~ 10⁻⁴.
- Srakaew i in., Nat. Phys. (2023), doi:10.1038/s41567-023-01959-y:
  do 1500 atomów, promień 12,5 µm, R_max = 0,37(2) z polem sterującym.
- Chmury nieuporządkowane: Corman i in. PRA 96, 053629 (2017),
  Jennewein i in. PRL 116, 233601 (2016), Pellegrino i in. PRL 113,
  133602 (2014). Żadna z tych prac nie zmierzyła odbicia spekularnego.
  Corman: OD nasyca się na ~3,5 (Beer–Lambert przewiduje 13).
- Koherentne rozpraszanie wsteczne: Labeyrie i in., PRL 83, 5266 (1999),
  wzmocnienie 1,06–1,11, szerokość stożka 0,57 mrad. Do stożka trafia
  ułamek procenta mocy, nie 10%.
- Transport w sieci: Schmid i in., NJP 8, 159 (2006), „up to 20 cm”,
  straty < 10%. Kuhr i in., Science 293, 278 (2001), ~1 cm.

**Test zabójczy (T1): budżet fotonów, warunki 1, 3, 4.**
- Maksymalna moc rozpraszana koherentnie przez atom to ħωΓ/8 = 1,21 pW
  (przy s = 1). 0,1 mW wymaga N ≥ 8,2·10⁷ atomów działających naraz.
- Żeby zostać w reżimie liniowym (s ≤ 0,1) przy 1 mW, potrzeba ≥ 6 cm²
  wiązki, czyli **2,1·10⁹ uporządkowanych atomów**. To 1,4·10⁶ razy
  więcej niż rekord (1500).
- Przy s = 0,1 każdy atom rozprasza 1,73·10⁶ fotonów/s. To 2,5·10⁴ razy
  powyżej zmierzonego progu degradacji (~70 fotonów na węzeł) już po 1 s.
  Grzanie odrzutem wynosi 0,63 K/s, więc sieć o głębokości 1 mK opróżnia
  się w ~1,6 ms, a nie w 1 s.

**Werdykt: ODRZUCONE** jako wyświetlacz przy 1 mW. Warunki 1 i 4 padają:
brakuje czynnika 10⁶ w liczbie atomów, a czas życia pod sondą to 1,6 ms
wobec 1 s. Warunek 2 pozostaje NIEROZSTRZYGNIĘTY: transport w sieci na cm
istnieje, ale nikt nie przesunął warstwy odbijającej (wymagany rozrzut
pionowy ≤ ~0,05a). POTWIERDZONE tylko jako mikroskopowe lustro atomowe:
R = 0,58 przy s ≈ 3·10⁻⁴, 200 atomów.

**Następne pytanie:** Czy ośrodek, który odnawia się sam (gorąca para,
atomy przelatują przez wiązkę w ~7 µs), omija limit grzania T1 i czy
siatka indukowana optycznie daje się przesuwać? (Iteracja 5.)

---

## Iteracja 5 — G (nowy). Siatka Bragga indukowana optycznie w parze (EIT / AC-Stark)

**Równanie rządzące:** Fala stojąca sprzęgająca moduluje χ pary z okresem
λ_c/2. Sonda przy stałej λ odbija się według R = tanh²(κL), κ = πΔn/λ
(teoria fal sprzężonych). Siatka istnieje tylko tam, gdzie nakładają się
wiązki sprzęgające.

**Liczby:**
- λ = 780/795 nm (Rb D2/D1), N = 10¹²–10¹³ cm⁻³ (90 °C).
- Na podstawie danych Little 2013 (R = 0,13 przy L = 1 mm) Δn ≥ 9,6·10⁻⁵,
  czyli L(R = 0,1) ≈ 0,87 mm i L(R = 0,8) ≈ 3,8 mm.
- Górna granica dla 2-poziomowego atomu bez Dopplera to Δn = Nσ₀λ/8π
  = 9·10⁻³. Absorpcja przy tym samym odstrojeniu daje jednak T = e⁻⁵·⁸
  na 40 µm, więc ta granica jest niefizyczna. Poszerzenie Dopplera
  (563 MHz) obcina Δn ~100×.

**Dowód:**
- Bajcsy, Zibrov, Lukin, Nature 426, 638 (2003), doi:10.1038/nature02176:
  - „peak reflection intensity is … (up to ∼80%) of the input signal
    beam”;
  - komórka 4 cm, sonda 250 µW, wiązki sprzęgające 8–40 mW, wiązka 2 mm,
    okno EIT „few 100 kHz-wide”.
- Zhang, Zhou, Wang, Zhu, PRA 83, 053841 (2011): Cs, 43%.
- Bae i in., Opt. Express 18, 1389 (2010): 11,5%.
- Little i in., PRA 87, 043815 (2013): siatka AC-Stark w komórce 1 mm,
  θ_Bragg = 11,2°, ~13–14% (odczyt z wykresu).

**Test zabójczy:**
- Warunek 1: nieudowodniony przy 1 mW, bo największa testowana sonda to
  250 µW. 1 mW w wiązce 2 mm to 19·I_sat. Zachowanie stosunku
  Ω_p/Ω_c ≤ 0,18 wymaga ≥ 32 mW na wiązkę sprzęgającą.
- Warunek 2: w geometrii współliniowej siatka wypełnia całą komórkę,
  więc lokalizacji brak. W geometrii skrzyżowanej długość nakładania
  wzdłuż sondy to ~5D ≈ 3 mm, a minimalny rozróżnialny krok ≈ L ≥ 0,87 mm.
  Przesunięcie o ≥ 10 µm jest więc możliwe tylko jako przesunięcie
  warstwy milimetrowej. Nikt tego nie zademonstrował.
- Warunek 4: atomy się odnawiają (v̄ ≈ 297 m/s, przelot 2 mm w ~7 µs),
  więc limit T1 nie obowiązuje. Ośrodek przeżywa 1 s. Ryzykiem jest
  pompowanie optyczne, nie grzanie.
- Barwa: Rb jest niewidoczne (V(780 nm) = 1,5·10⁻⁵). Ośrodek siedzi
  w szklanej komórce, nie w powietrzu.

**Werdykt: NIEROZSTRZYGNIĘTE.**
- POTWIERDZONE warunki 4 i 5 oraz kierunkowość (odbicie odtwarza mod
  sondy, rozbieżność 0,014° przy przewężeniu 1 mm).
- Warunek 1 nie jest zmierzony przy 1 mW.
- Warunek 2 nie jest zademonstrowany, a jego realna rozdzielczość to
  ~1 mm, nie 10 µm.

**Następne pytanie (do pomiaru):** W układzie Bajcsy (komórka Rb, 90 °C)
zmierzyć R(P_sondy) dla P_sondy = 0,25 → 1 mW przy P_c = 40 mW na wiązkę.
Czy R ≥ 0,1 przy 1 mW?

---

## Iteracja 6 — H (nowy). Siatka zapisana laserem w samym powietrzu

_W toku: agent zbiera pomiary siatek gazowych i plazmowych._

---

## Iteracja 7 — J (nowy). Pojedyncza cząstka w pułapce fotoforetycznej

**Równanie rządzące:** Rozpraszanie Mie na kuli o średnicy d ≫ λ.
Q_ext → 2. Płat dyfrakcyjny do przodu ma pierwsze zero przy 1,22λ/d.
Reszta rozpraszania rozkłada się szeroko kątowo. Cząstka jest materią
w z, w powietrzu, przesuwaną mechanicznie (ruch soczewki pułapki).
Nie jest to hologram, tylko wolumetryczny wyświetlacz punktowy.

**Liczby:**
- λ = 532 nm, d = 10 µm, w₀ sondy = 10 µm.
- Ułamek przechwycony 1 − e^(−d²/2w₀²) = 0,39. Stożek 1° = 2,39·10⁻⁴ sr.
- Ułamek mocy w stożku (rozpraszanie ~izotropowe) = 7,5·10⁻⁶.
  Z ilorazem lidarowym 18,8 sr wychodzi ~1·10⁻⁵.
- Płat dyfrakcyjny zmieści się w półkącie 0,5° dopiero dla d ≥ 74 µm.
  Idealny retroreflektor 10 µm daje najwyżej 2,5% sondy w stożku.
- Rozdzielczość adresowania ~16 µm (1600 dpi; rachunek z objętości
  i liczby punktów).
- N, A, OD w sensie atomowym nie dotyczą (jedna cząstka).

**Dowód:**
- Smalley i in., Nature 553, 486 (2018), doi:10.1038/nature25176:
  - „1,600 dots per inch”, „16,700 points per second”;
  - „minimum hold power recorded was less than 24 mW (for 405-nm
    light)”;
  - „average hold time of 1.1 h”.
- Rogers, Laney, Peatross, Smalley, Appl. Opt. 58, G363 (2019),
  doi:10.1364/AO.58.00G363:
  - „The scattered optical power is estimated of the order of
    nanowatts”;
  - rozpraszanie jest „strongly diverging”;
  - „many trap attempts fail to hold even a few seconds”.
- Kuttler i in., JoVE 177, e63113 (2021): skuteczność złapania 1–14%
  na próbę.

**Test zabójczy: warunek 1.** Do stożka < 1° trafia ~10⁻⁵ mocy sondy
wobec wymaganych 10⁻¹, czyli 10⁴ razy za mało. Nawet idealna cząstka
10 µm nie przekracza 2,5% z samej dyfrakcji.

**Werdykt: ODRZUCONE.** Powód liczbowo: warunek 1, 7,5·10⁻⁶ (lub 10⁻⁵)
wobec 0,1. Inne warunki przy 1 mW:
- Warunek 2 POTWIERDZONY warunkowo: adresowanie ~16 µm, barwa stała,
  ale drgań osiowych nikt nie zmierzył.
- Warunek 3 POTWIERDZONY: 35 nW na 1 cm² w 30 cm, SNR ~3·10⁴ wobec
  szumu 1 pW (rachunek). Zgadza się z rzędem „nanowatts” u Rogersa 2019.
- Warunek 4 POTWIERDZONY warunkowo: pułapka ma własną wiązkę ≥ 24 mW,
  średni czas trzymania 1,1 h, ale wiele prób trwa tylko sekundy.
- Warunek 5 spełniony.

To jedyny jak dotąd mechanizm, który daje materię w z **w powietrzu**
i przesuwa ją o ≥ 10 µm. Pada wyłącznie na kierunkowości.

**Następne pytanie:** Czy w pułapce fotoforetycznej (lub innej pułapce
w powietrzu) da się utrzymać płaski odbijający płatek o średnicy
≥ 74 µm ze stabilnością orientacji ≤ 0,25°? Tyle wymaga skierowania
odbicia wstecz w stożek 1°. (Do rozstrzygnięcia pomiarem albo
cytatem z literatury pułapek optycznych i akustycznych.)

---
