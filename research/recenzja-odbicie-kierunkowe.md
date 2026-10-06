# Recenzja: kierunkowe odbicie wiązki od materii w odległości z

Dziennik iteracji. Każda iteracja kończy się jednym werdyktem:
POTWIERDZONE, ODRZUCONE albo NIEROZSTRZYGNIĘTE. Liczby, które nie są cytatami,
pochodzą z `research/obliczenia.py` (sekcje T0–T8). „Odczyt z wykresu” oznacza
liczbę odczytaną z rysunku w pracy, a nie podaną w tekście. Takie liczby są
słabsze niż wartości z tekstu.

## Warunki sukcesu (wszystkie naraz)

1. Co najmniej 10% mocy wejściowej wraca w stożek mniejszy niż 1°.
2. Zmiana sterowania przesuwa płaszczyznę odbicia o ≥ 10 µm przy tej samej
   barwie źródła.
3. Przy sondzie 1 mW detektor w odległości 30 cm mierzy sygnał z podanym SNR.
4. Ośrodek przeżywa 1 s pracy (bez wygrzania atomów i bez wybielenia polimeru).
5. Cytat do pomiaru albo jawne równanie z podstawionymi liczbami.

**Odczyt warunku 2 (korekta recenzenta po iteracji 6).** Warunek mówi
o przesunięciu **płaszczyzny odbicia**, czyli miejsca, w którym materia
odbija, o **co najmniej** 10 µm. Nie wymaga woksla o głębokości 10 µm.
Dlatego:
- **(a)** przesunięcie warstwy o grubości L o krok ≥ max(10 µm, L)
  spełnia warunek 2;
- **(b)** ognisko w pustym powietrzu nie jest płaszczyzną odbicia.

W iteracjach 1–2 pierwotnie użyłem ostrzejszego odczytu („rozróżnialny
krok 10 µm”). Poprawiłem to poniżej. Werdykty C1 i D się nie zmieniają,
ale zmienia się ich uzasadnienie.

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
  więc płaszczyzna odbicia się nie przesuwa przy zmianie kanału.
  „Głębokość” można zakodować tylko w fazie (holograficzna soczewka
  z ogniskiem w z). Ognisko nie jest jednak płaszczyzną odbicia (zob.
  iteracja 2), a T2 daje mu przy stożku < 1° głębokość ≥ 3,5 mm.
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
  ODRZUCONE**. Warunek 2: płaszczyzna odbicia jest ta sama dla każdego
  kanału, czyli Δz = 0.
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

**Test zabójczy: warunek 2 z definicji.** Płaszczyzną odbicia jest
metapowierzchnia i ona się nie przesuwa (Δz = 0). Przesuwa się ognisko,
w którym nie ma materii, więc nie jest to „odbicie od materii w z”.
Obraz jest widoczny tylko z wnętrza stożka (Smalley 2018, „clipping”).

**Ograniczenie T2 (nie zabójcze dla warunku 2, ale dla obrazu 3D):**
Dla każdego woksla tworzonego przez ognisko:
- Stożek o półkącie < 1° wymusza NA ≤ 0,0175, czyli głębokość woksla
  DOF ≥ 3,5 mm. Przy pełnym kącie < 1° DOF ≥ 14 mm.
- Woksel o głębokości 10 µm wymaga NA ≥ 0,326, czyli półkąta 19°.
- Kroki ogniska rzędu ≥ DOF (np. 4 mm, Δf/f ≈ 1,3%) są osiągalne
  przestrajaniem (> 60 D zademonstrowane przy 915 nm). Obraz 3D
  z ogniska przy stożku < 1° ma więc woksle o głębokości milimetrowej.

**Werdykt: ODRZUCONE** jako odbicie od materii w z (warunek 2: Δz
płaszczyzny odbicia = 0).
Częściowo POTWIERDZONE, tylko jako rzeczywisty obraz lotniczy
(nie hologram, nie odbicie w z, woksel ≥ 3,5 mm głęboki):
- warunek 1 przy półkącie 0,955° i sprawności 40–86%;
- warunek 3: ≥ 0,4 mW w ognisku, czyli ~10¹⁵ fotonów/s. Shot-noise SNR
  ~3·10⁷ w 1 s to górna granica, a obserwator musi być w stożku;
- warunek 4: dawka 1,27 mJ/cm² w 1 s wobec ns-LIDT TiO₂ ~0,5 J/cm²
  (Jung i in., Adv. Opt. Mater. 2025). Progu CW nie znaleziono;
- warunek 5.

**Wniosek ogólny (T2):** Warunek 2 wymaga materii odbijającej w z.
Dla takiej materii głębokość woksla to grubość warstwy L, a kąt stożka
zależy od rozmiaru poprzecznego wiązki. Te dwie wielkości są od siebie
niezależne, w przeciwieństwie do ogniska.

**Następne pytanie:** Jaka jest minimalna modulacja współczynnika
załamania Δn, przy której warstwa grubości L odbija R ≥ 0,1,
i ile wynosi L dla samego powietrza? (Rozstrzygnięcie rachunkiem: T3.)

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
- Warunek 2 nie jest zademonstrowany. Krok musiałby wynosić ≥ L ≈ 1 mm.
  To jest zgodne z odczytem (a), ale nikt tego nie zmierzył.

**Następne pytanie (do pomiaru):** W układzie Bajcsy (komórka Rb, 90 °C)
zmierzyć R(P_sondy) dla P_sondy = 0,25 → 1 mW przy P_c = 40 mW na wiązkę.
Czy R ≥ 0,1 przy 1 mW?

---

## Iteracja 6 — H (nowy). Siatka zapisana laserem w samym powietrzu

**Równanie rządzące:** Interferujące impulsy UV fotolizują ozon i tworzą
modulację gęstości gazu (siatka gazowa). Alternatywnie siatkę tworzy
plazma z interferujących filamentów fs albo efekt Kerra, Δn = n₂I.
Siatka istnieje tylko w obszarze nakładania wiązek zapisujących,
więc z wybiera się kierowaniem wiązek. Sonda jest odchylana zgodnie
z η = sin²(πΔnL/λ) (siatka transmisyjna).

**Liczby:**
- λ_sondy = 532 nm; okres siatki Λ ≈ 40 µm (Michine) lub 9–32 µm (Ou).
- Kąt Bragga ~0,5°, wiązki rozdzielone o ~1°.
- Δn z danych: 2,3·10⁻⁵ (η = 0,96 na 10 mm). Ou 2026 podaje
  Δn = 10⁻⁵–10⁻⁴.
- L(η = 0,1) = 2,4 mm (T8). Zmierzone siatki mają L = 3,3–10 mm.
- Wypełnienie czasowe: okno ~10 ns przy 10 Hz daje 10⁻⁷.
- Kerr: n₂(powietrze) ≈ 7,9·10⁻²⁰ cm²/W, więc Δn = 10⁻⁶ wymaga
  1,3·10¹³ W/cm². Powyżej tego zaczyna się filamentacja i jonizacja.
- N, σ, OD w sensie atomowym nie dotyczą (ośrodek nierezonansowy).

**Dowód:**
- Michine & Yoneda, Commun. Phys. 3, 24 (2020),
  doi:10.1038/s42005-020-0286-6. Warunki:
  - ozon 1–10% w O₂ w rurze przepływowej, nie powietrze otoczenia;
  - zapis KrF 248 nm, 50–200 mJ, „5 to 20 Hz”;
  - wynik: „96% at 63 mJ/cm2 of the UV writing beam”, okno wysokiej
    sprawności „about 10 ns”.
- Ou i in., arXiv:2601.09963 (2026, **preprint, nierecenzowany**):
  „95.7% ± 3.6%” przez 7737 strzałów przy 10 Hz.
- Wahlstrand, Cheng, Milchberg, PRA 85, 043820 (2012): n₂(N₂) = 7,4·10⁻²⁰ cm²/W.
- Shi i in., PRL 107, 095004 (2011): siatka plazmowa w powietrzu,
  „~19%” (wartość z cytatu wtórnego, oryginału nie przeczytano).
- Schrödel i in., Nat. Photon. 18, 54 (2024): siatka ultradźwiękowa
  w powietrzu, Δn „only 10^-7”, > 50% po 7 przejściach, impulsy ~1 ms
  przy 5 Hz.

**Test zabójczy: warunek 1 (średnia czasowa) i T3 (powietrze).**
- Szczytowo 96% jest kierunkowe, ale dla sondy CW 1 mW średnia to
  0,1 nW (okno 10 ns, 10 Hz). W wariancie hojnym (500 ns, η = 0,5)
  wychodzi 2,5 nW, czyli 2,5·10⁻⁶ mocy sondy. Brakuje czynnika ≥ 4·10⁴.
- Ciągłe podtrzymanie wymagałoby ~5 MW mocy zapisu (50 mJ co 10 ns)
  i wymiany ozonu w ~0,5 µs, czyli przepływu ~2 km/s.
- W powietrzu otoczenia ozonu jest ≤ 70 ppb wobec 1–6% w doświadczeniach,
  czyli 10⁵–10⁶ razy mniej absorbentu.
- T3: warstwa 10 µm wymagałaby Δn = 5,5·10⁻³, więcej niż całe
  n − 1 powietrza (2,8·10⁻⁴). Warstwa w powietrzu ma zawsze ≥ 0,2 mm,
  realnie milimetry. To nie łamie warunku 2 w odczycie (a),
  ale przesunięcia siatki nikt nie zmierzył.

**Werdykt: ODRZUCONE.** Powód liczbowo: warunek 1, średnio ≤ 2,5·10⁻⁶
mocy sondy wobec 0,1. Warunek 4: impulsowa praca jest POTWIERDZONA
(> 2 h przy 10 Hz, preprint), ale praca ciągła wymaga ~MW. To jedyny
mechanizm odbijający od samego gazu w z. Pozostaje mechanizmem
impulsowym dla laserów dużej mocy (do tego go zaprojektowano), a nie
wyświetlaczem.

**Następne pytanie:** Czy jakikolwiek ośrodek w powietrzu ma Δn ≥ 10⁻³
podtrzymywane w sposób ciągły przy poborze < 1 W, czyli 10⁴ razy mniej
niż siatka gazowa? (Rachunek budżetu energii; kandydaci to aerozol
i warstwy cząstek. Patrz iteracja 9: płatek w pułapce.)

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

## Iteracja 8 — C2 w literaturze: warstwowe siatki odbiciowe i mikrohologramy

**Mechanizm:** Siatki odbiciowe zlokalizowane na różnych głębokościach
jednego bloku, przy jednej λ. Pytanie z iteracji 1 brzmiało: czy
istnieje pomiar z adresowaniem kątowym?

**Liczby:**
- Mikrohologramy wielowarstwowe:
  - McLeod: 12 warstw w 125 µm (skok ~10 µm), 532 nm;
  - Orlic: 39 warstw w 300 µm (skok < 8 µm);
  - GE: odbiciowość ≤ ~1% na mikrohologram (komunikat prasowy),
    0,03–0,26% (patent), NA odczytu 0,16.
- Laminat dwóch warstw Bayfol HX: warstwy 15,3 µm, przekładka 51,2 µm,
  n₁ = 2,1·10⁻², czyli skok płaszczyzn ~66 µm.

**Dowód:**
- McLeod, Daiber, McDonald, Robertson, Slagle, Sochava, Hesselink,
  Appl. Opt. 44, 3197 (2005), doi:10.1364/AO.44.003197:
  - zapis „at the focus of a high-numerical-aperture beam and its
    retroreflection”;
  - „12 layers of microholograms in a 125-µm photopolymer disk”.
- Ostroverkhov, Lawrence, Shi, Boden, Erben, Jpn. J. Appl. Phys. 48,
  03A035 (2009), doi:10.1143/JJAP.48.03A035: materiał progowy,
  stabilność odczytu CW 1000× lepsza niż w materiale liniowym.
- US 6,020,985 (patent McLeod i in.): w materiale liniowym „the maximum
  index change in each layer varies as 1/N, while the diffraction
  efficiency … varies as 1/N²”. Dotyczy zapisu przez pozostałe warstwy
  jednego bloku. Nie dotyczy warstw nagranych osobno i zlaminowanych.
- Shams Lahijani i in., Proc. SPIE 12574, 1257403 (2023) (arXiv:2304.03059):
  dwie warstwy Bayfol HX z przekładką, siatki transmisyjne. Warstwy
  interferują ze sobą („rapid oscillations” w odpowiedzi kątowej).
- **Korekta raportu agenta:** Zhou, Li, Liu, Su, Opt. Express 26, 22866
  (2018) to „Compact design for optical-see-through holographic displays
  employing holographic optical elements”. Dwa HOE pełnią tam różne
  funkcje (ekspander wiązki, okular i combiner). Nie są to dwie
  płaszczyzny głębokości adresowane kątem, więc praca **nie** jest
  dowodem dla C2.

**Test zabójczy:**
- Mikrohologramy adresowane ogniskiem padają na warunku 1:
  - R ≤ 0,01 wobec wymaganych 0,1;
  - odbicie wraca w stożek NA odczytu: NA 0,16 to półkąt 9,2° wobec 0,5°.
- Adresowanie kątowe w jednym bloku: zero pomiarów.

**Werdykt:**
- Mikrohologramy adresowane ogniskiem: **ODRZUCONE**
  (warunek 1: R ≤ 0,01; stożek 9,2°).
- C2 z adresowaniem kątowym pozostaje NIEROZSTRZYGNIĘTE z braku pomiaru.

**Następne pytanie:** Czy jawny rachunek (macierz przejścia, bez
przybliżenia fal sprzężonych) potwierdza C2 przy zmierzonym limicie
n₁ dla Bayfol HX w odbiciu? (Iteracja 9.)

---

## Iteracja 9 — C2 rachunkiem: stos 5 warstw, macierz przejścia

**Mechanizm:** Stos N = 5 niesłantowanych siatek odbiciowych w bloku
n₀ = 1,5. Każda warstwa ma grubość L = 10 µm i okres
Λ_k = λ/(2n₀cosθ_k). Wybór głębokości odbywa się przez kąt padania
przy stałej λ = 532 nm. Rachunek: `research/tmm_stos_siatek.py`
(pełna macierz przejścia, polaryzacja s, 16 podwarstw na okres).

**Liczby:**
- n₁ = 0,008 to zmierzona górna granica dla Bayfol HX w odbiciu,
  0,0078–0,0090 (Bruder, Fäcke, Rölle, Polymers 9, 472 (2017), tab. 3).
- Λ_k = 181, 189, 197, 206, 216 nm. Kąty wewnętrzne θ_k = 11,7–34,8°,
  zewnętrzne 17,7–58,9°.
- Wyniki TMM:

  | kanał | θ_wewn | R stosu | R bez warstwy k | z₅₀ (płaszczyzna odbicia) | warstwa k |
  |---|---|---|---|---|---|
  | 0 | 11,69° | 0,216 | 0,0017 | 7,2 µm | 0–10 µm |
  | 1 | 20,03° | 0,259 | 0,0098 | 16,9 µm | 10–20 µm |
  | 2 | 25,51° | 0,248 | 0,0048 | 27,0 µm | 20–30 µm |
  | 3 | 30,60° | 0,292 | 0,0120 | 37,6 µm | 30–40 µm |
  | 4 | 34,81° | 0,286 | 0,0020 | 47,0 µm | 40–50 µm |

- Maksymalne R poza głównymi listkami: 0,020.
- Kontrola: teoria fal sprzężonych tanh²(πn₁L/(λcosθ_k)) = 0,20–0,27.
  TMM dla pojedynczej warstwy daje 0,196–0,263, więc oba rachunki
  są zgodne.

**Dowód:** Jawne równanie: macierz charakterystyczna warstw (Born & Wolf,
rozdz. 1.6) z podstawionymi liczbami oraz kod powyżej. Limit n₁ to
pomiar (Bruder 2017). Pomiaru całego stosu nie ma (iteracja 8).

**Test zabójczy:**
- **Warunek 1:** R = 0,22–0,29 ≥ 0,1. Odbicie jest spekularne, a stożek
  równa się rozbieżności wiązki: 0,014° przy przewężeniu 1 mm.
- **Warunek 2:** płaszczyzna odbicia przeskakuje o 9,7–10,6 µm przy
  zmianie kąta, przy stałej λ.
- **Warunek 3:** ~0,2 mW odbite, ~5·10¹⁴ fotonów/s, SNR (szum śrutowy)
  ~2·10⁷ w 1 s. Detektor musi stać w kierunku zwierciadlanym dla θ_k.
- **Warunek 4:** dawka 0,127 J/cm² w 1 s (1 mW na Ø 1 mm) wobec
  1080 J/cm² bez degradacji dla utrwalonego DuPont (Curtis & Psaltis
  1994, 100 h przy 3 mW/cm²). Dla wybielonego Bayfol HX brak liczby.
- **Ograniczenia modelu:**
  - 1D, idealna sinusoida, bez absorpcji, rozpraszania i błędów
    laminacji;
  - zewnętrzny Fresnel powietrze/blok (~4%) leży na stałym z i musi
    być pokryty AR, bo inaczej daje kierunkowe tło;
  - realny laminat z podłożami daje skok ~66 µm (Shams Lahijani 2023),
    nie 10 µm. To nadal spełnia warunek 2.

**Werdykt (pierwotny, wycofany po audycie — patrz iteracja 12): POTWIERDZONE rachunkiem** dla warunków 1, 2, 3 i 5. Warunek 4
POTWIERDZONY dla utrwalonego polimeru typu DuPont (dawka 10⁴ razy
poniżej przetestowanej), a NIEROZSTRZYGNIĘTY dla Bayfol HX.
- Zakres: **wyłącznie w bloku stałym**. Płaszczyzny odbicia leżą
  wewnątrz polimeru, nie w powietrzu.
- Nie jest to wynalazek ani nowe zjawisko. To znana fizyka siatek
  objętościowych (Kogelnik 1969) w znanym układzie warstwowym.
- Nie jest to też „obraz 3D w powietrzu”: T9 daje plamkę 5,2 mm w 30 cm,
  więc woksel widzi jedno oko.

**Następne pytanie (do pomiaru):** Laminat 2–5 osobno nagranych warstw
Bayfol HX (lub DuPont) z okresami z tabeli, odczyt 532 nm, 1 mW,
powłoka AR. Zmierzyć:
- R(θ) każdego kanału, czy jest ≥ 0,1;
- położenie płaszczyzny odbicia, interferometrią niskokoherencyjną
  albo OCT.

---

## Iteracja 10 — J+ (nowy). Płaskie lustro lewitowane w powietrzu

**Mechanizm:** Zamiast kulki (iteracja 7) płaski reflektor w pułapce
w powietrzu (akustycznej, fotoforetycznej, diamagnetycznej). Odbicie
spekularne, więc kierunkowe, jeśli płat dyfrakcyjny i drgania kąta
mieszczą się w stożku.

**Liczby (wymagania):**
- d ≥ 150 µm, bo płat 1,22λ/d ≈ 0,25° przy 532 nm.
- Drgania przechyłu ≤ 0,15°, bo wiązka odchyla się o 2× przechył.
- Czas ≥ 1 s, przesuw w z ≥ 10 µm.
- Moment od sondy 1 mW na krawędzi płatka 150 µm to 5·10⁻¹⁶ N·m,
  więc potrzebna sztywność kątowa ≥ 1,9·10⁻¹³ N·m/rad (T9).
  W gazie silniejsze od ciśnienia promieniowania są siły fotoforetyczne
  z absorpcji (Pahi i in., arXiv:2512.09401, preprint).

**Dowód:**
- Liu, Huo, He, Ma, Opt. Express 34, 19811 (2026), doi:10.1364/OE.592104,
  sprawdzone w Crossref:
  - lusterko aluminiowe lewitowane ultradźwiękami w powietrzu;
  - „Five discrete and repeatable steering states spanning approximately
    ±8° optical deflection… settling times on the order of tens of
    milliseconds”;
  - wymiary lustra 6 mm × 0,2 mm, 40 kHz (Liu, Yang, Ma, Micromachines
    17, 879 (2026), symulacja).
- Winstone i in., PRL 129, 053604 (2022): płytki 2,5–5 µm, przechył rms
  0,27–0,97° (z ekwipartycji, nie pomiar bezpośredni).
- Perdriat i in., PRL 128, 117203 (2022): diament ~15 µm w pułapce
  Paula, błąd kąta „about 1 degree”.
- Koller i in., arXiv:2609.17787 (2026, **preprint**): mikrolustro
  lewitowane nadprzewodząco w 3,2 K w próżni. Sonda tylko „several
  nanowatts”, więc przy 1 mW odpada.

**Test zabójczy:** Liczba rozstrzygająca to drgania przechyłu lustra
z Liu 2026. **Nikt jej nie podał.**
- Dla tego lustra: R(Al) ≈ 0,9, płat dyfrakcyjny 0,006°, a siła sondy
  to 4·10⁻⁸ ciężaru lustra. Warunki 1, 3, 4 przechodzą, jeśli drgania
  ≤ 0,15°.
- Przesuwu w z o ≥ 10 µm nie raportowano.
- Najlepsze zmierzone kąty (0,27–1°) dotyczą obiektów µm i są powyżej
  0,15°.

**Werdykt: NIEROZSTRZYGNIĘTE.**
- To jedyny kandydat z materią **w powietrzu**, który nie pada na
  liczbie, tylko na braku liczby.
- Ograniczenie T9: lustro kierunkowe widzi jedno oko. Jedno lustro
  to jeden woksel, nie obraz.

**Następne pytanie (do pomiaru):** W układzie Liu 2026 zmierzyć dźwignią
optyczną (lustro → ekran 1 m) rms przechyłu w 1 s. Czy jest ≤ 0,15°?
Czy przesunięcie lustra w z o ≥ 10 µm (zmiana faz przetworników)
zachowuje ten przechył?

---

## Iteracja 12 — audyt zewnętrzny pierwszego wydania referatu

**Wynik:** C2 zmienia werdykt z POTWIERDZONE na **NIEROZSTRZYGNIĘTE (tylko model)**.
Żaden mechanizm nie został wykazany jako spełniający pięć warunków naraz.

**Zarzuty potwierdzone w pełnych tekstach źródeł:**
- Curtis & Psaltis, Appl. Opt. 33, 5396 (1994): „HRF-150 is designed by DuPont as
  a transmission film, and … it does not record reflection holograms effectively”;
  w 100-godzinnym odczycie „The initial increase … is caused by the bleaching of
  the material with light exposure”. Nie potwierdza warunku 4.
- Bruder, Fäcke, Rölle, Polymers 9, 472 (2017), tab. 3: Δn₁ 0,0065–0,0090 to
  „maximum refractive index modulation as obtained in holography recording” dla
  wariantów boranowego fotoinicjatora w żywicy, nie granica Bayfol HX w odbiciu.

**Zarzuty potwierdzone rachunkiem (`research/tmm_audyt_c2.py`):**
- Kroki z₅₀: 9,7 / 10,1 / 10,6 / 9,4 µm (pierwotny zakres „9,7–10,6” był błędny);
  przy innym próbkowaniu 9,7 / 9,7 / 10,4 / 9,4 µm.
- Rozkład dR/dz: centroidy co 5–6 µm, nakładanie 0,32–0,43, 30–63% ujemnej masy.
- Głębokość z opóźnienia grupowego (OCT): 5,7 / 14,3 / 23,8 / 34,2 / 42,9 µm,
  kroki 8,6 / 9,5 / 10,3 / 8,8 µm — warunek 2 pada w 3 z 4 przejść.
  Pojedyncza warstwa daje z_gd w swoim środku (4,6 … 44,4 µm): metryka poprawna.
- Przesłuch: moc z innych warstw 0,7–5,0% sygnału; interferencja zmienia R o
  9–22%; maks. R poza kanałami 0,020 = 9,4% najsłabszego kanału.
- Laminat (przekładki 51 µm, n = 1,48 założone): R = 0,25–0,31, kroki z_gd
  51–60 µm, przesłuch 0,8–4,4%, interferencja 14–27%. Nowa hipoteza modelowa.

**Zarzuty przyjęte bez zmiany werdyktu:** warunek 3 tylko jako limit szumu
śrutowego; R całkowite ≠ moc w stożku; brak adresowania x–y; T1/T2/T3 mają zakres
(T1: atomy niezależne, skala Γ_kol/Γ ≈ 0,5–0,7; T2: woksle ogniskowe; T3: obojętny
gaz bez rezonansu, nie plazma); E — pole 1 mm² pochodzi z punktu startowego,
argument przeniesiony na budżet mocy przy 1 mW (piksel 10×10 µm: ~340 atomów,
≤ 0,4 nW); F — 1500 atomów to stan techniki; H to dyfrakcja w transmisji;
J+ to jeden obiekt; liczba odrzuconych 9, nie 8; 12 iteracji dla 13 mechanizmów.

**Następne pytanie:** model C2 z rzeczywistym laminatem (indeksy i grubości z kart
materiałowych) i skokiem warstw z marginesem ponad 10 µm, z mocą w stożku < 1°
dla skończonej wiązki — czy R_stożek ≥ 0,1 i kroki z_gd ≥ 10 µm utrzymują się?

## Iteracja 13 — drugi audyt zewnętrzny

**Wynik:** werdykty bez zmian (9 ODRZUCONE, 4 NIEROZSTRZYGNIĘTE); zmienia się
precyzja twierdzeń. Rachunki: `research/tmm_audyt2_c2.py`.

**Nowe liczby dla C2 (stos ciągły L = 10 µm):**
- Osiowa odpowiedź impulsowa w paśmie ±10 nm (okno Hanna): centroidy μ_k
  5,3 / 14,7 / 24,5 / 34,6 / 44,4 µm, kroki 9,4 / 9,9 / 10,1 / 9,9 µm,
  FWHM 8,1–9,1 µm, nakładanie C = 0,12–0,17.
- z_gd: kroki 8,62 / 9,52 / 10,35 / 8,78 µm, stabilne do 0,01 µm przy 16 vs 32
  podwarstwach i Δλ 0,005 vs 0,05 nm. Metryki różnią się o ≤ 1,5 µm → brak marginesu.
- H_ij: przekątna 0,196–0,263, poza przekątną ≤ 0,0043, udział warstwy k 96,8–98,7%.
- Maks. R poza kanałami 0,0202 / 0,2164 = 9,3%.
- Scenariusz laminatu (51 µm, n = 1,48 założone): kroki μ 58–59 µm, FWHM 8,2–8,9 µm,
  C = 0,012–0,014.

**E:** P ≤ N·ħω·Γ/8 = 344 × 1,21 pW = 0,42 nW w 4π; przy OD = 1 odstęp √σ₀ = 0,54 µm
= 0,69 λ, więc reżim kolektywny i tylko szacunek.

**Źródła sprawdzone w pełnych tekstach:**
- Bajcsy, Zibrov, Lukin (arXiv quant-ph/0311092), rys. 2B, krzywa (ii), pomiar CW:
  „The peak reflection intensity is a substantial fraction (up to ∼80%) of the input
  signal beam”; sonda 250 µW; mechanizm: „periodic modulation of the absorptive rather
  than dispersive properties lays at the origin of the observed Bragg reflection”.
- Blanche, Mahamat, Buoye, Materials 13, 5498 (2020): Δn = 0,03 „per the manufacturer’s
  specifications” [Covestro, Bayfol HX200 Description and Application Information 2018;
  Technical Data Sheet 2020]; samych kart nie pobrano.

**Zmiany redakcyjne:** definicja „odbicia od materii w z” jako wybór definicji problemu;
T1 bez mnożnika Γ_kol; T9 — dwie wiązki mogą dać stereoskopię; H — brak pomiaru odbicia
wstecz; przesłuch ≤ 5% jako dodatkowe kryterium jakości; laminat jako scenariusz;
usunięte zdanie o „przełomie”; opis metody z ujawnieniem wsparcia AI.
