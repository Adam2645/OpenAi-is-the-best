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

## Iteracja 14 — trzeci audyt zewnętrzny

**Zmiana werdyktów:** ODRZUCONE pozostaje tylko tam, gdzie jest górne ograniczenie
(strukturalne, z definicji albo ze zmierzonej mocy całkowitej): B, C1, D, J, K.
A, E, F, H przechodzą do NIEROZSTRZYGNIĘTE (szacunek albo brak pomiaru).
Stan: 5 ODRZUCONE, 8 NIEROZSTRZYGNIĘTE, 0 POTWIERDZONE.

**Ujawnione założenie:** dosłownie zapisane warunki 1–5 spełnia lustro na stoliku piezo;
wykluczamy mechaniczny przesuw stałego reflektora, dopuszczamy przesuw materii polami.

**Spójność kąta:** wszędzie pełny kąt wierzchołkowy 1° (półkąt 0,5°). T2: NA ≤ 0,0087,
DOF ≥ 14 mm (pierwsze wydania: 3,5 mm dla półkąta 1°).

**Rachunki (`research/tmm_audyt3_c2.py`, wektoryzacja po kątach, ~40 s):**
- Zbieżność 8/16/32/64 podwarstw: R 0,209→0,219 (kanał 0), między 32 a 64 ≤ 0,5%;
  kroki μ, FWHM, z_gd, udziały H stałe do ≤ 0,05 µm.
- Przemiatanie n₁ = 0,004 / 0,008 / 0,012 / 0,02 / 0,03: R = 0,06–0,09 / 0,22–0,29 /
  0,41–0,52 / 0,72–0,83 / 0,91–0,96; kroki μ zawsze 9,3–10,1 µm; maks. R poza kanałami
  / najsłabszy kanał = 9,0 / 9,4 / 9,7 / 19,1 / 49,3%.
- Geometria: warstwy po 55/53/51/48/46 okresów, grubości 9,90–10,05 µm, kroki środków
  9,97 / 10,02 / 9,97 / 9,92 µm — materia też leży na progu 10 µm.
- Interfejsy (pol. s, bez AR): R_s = 0,045 / 0,059 / 0,078 / 0,111 / 0,167 przy
  17,7–58,9°; sygnał (1−R_s)²R = 0,20–0,23; tło z powierzchni / sygnał = 23–84%;
  koherentnie dla swobodnej warstwy 50 µm R = 0,19–0,40.

**Źródła sprawdzone w pełnych tekstach w tej iteracji:** Rui i in. (arXiv 2001.00795):
„R = 0.58(3)”, „η≃0.92 per lattice site on ≃200 lattice sites”, poszerzenie „beyond
70 photons per lattice site”, reflektancja liczona w kącie zbierania obiektywu.
Michine & Yoneda (PDF): „96% at 63 mJ/cm2 of the UV writing beam”, okno „about 10 ns”,
ozon 1–10%. Schilke 2011 nie znaleziono na arXiv — liczby oznaczone jako niesprawdzone
powtórnie.

## Iteracja 15 — hipotezy wdrożeniowe po audytach (`research/iteracja15.py`)

**H1. Rezygnacja z „materii w z” (woksel ogniskowy, VHOE/SLM).** Przy stożku pełnym 1°:
NA = 0,0087, woksel 1,22λ/NA = 74 µm szerokości i 2λ/NA² = 14 mm głębokości. Przy 12°
(dwoje oczu w 30 cm): 6,2 µm i 0,097 mm. Étendue: obraz 1 cm przy 12° wymaga ~3930²
≈ 1,5·10⁷ pikseli o skoku ≤ 2,54 µm w płaszczyźnie obrazu. Wiążącym ograniczeniem jest
warunek 1, nie definicja materii. NIEROZSTRZYGNIĘTE — decyzja definicyjna należy do autora.

**H2. C2: laminat + polaryzacja p + SLM.** Centrowanie na Brewsterze nie jest potrzebne:
przy pierwotnych kątach i pol. p R_p ≤ 3,5% (17,7–58,9°), ale sprzężenie maleje jak
|cos 2θ|, więc trzeba n₁ ≈ 0,02. Kandydat modelowy (laminat 51 µm, n = 1,48 zał., pol. p,
n₁ = 0,02): sygnał 0,24–0,67, tło z powierzchni 0,4–5,3% sygnału, kroki μ 59–60 µm,
FWHM 7,7–9,2 µm, C = 0,009–0,012, moc innych warstw 1,2–8,1% sygnału. Wachlarz
Brewstera o skoku 0,03 w cosθ: kanały się zlewają (poza kanałami 62–103%); o skoku 0,04
(4 kanały): sygnał 0,15–0,49, tło 0–11,5%, poza kanałami 21%.
Tolerancja kątowa (SLM): rozbieżność 1/e² 0,25° / 0,5° / 1° → sprawność Bragga 99–100% /
96–99% / 89–96% szczytu i ułamek mocy w stożku 0,5° = ~100% / 86,5% / 39,3%. Szczegół
na warstwie ≥ λ/(2 sin 0,5°) = 30,5 µm; ~1,1·10⁵ woksli na 1 cm².
NIEROZSTRZYGNIĘTE (model): brak pomiaru, warunki 3–4, wykonalność laminatu.

**H3. F z subradiacją.** Γ_kol/Γ ≈ (3/4π)(λ/a)²: 0,51 (a = 532 nm), 0,91 (400 nm),
2,05 (266 nm). Jeśli bilans skaluje się z Γ_kol, subradiacja go pogarsza (N ≈ 1,6·10⁸),
a gęstsza sieć poprawia ~2× (N ≈ 4·10⁷). Kierunek proponowanej dźwigni jest odwrotny.
NIEROZSTRZYGNIĘTE (szacunek).

**H4. Plazma w powietrzu.** n_c(532 nm) = 3,9·10²¹ cm⁻³. R ≥ 0,1 przy L = 100 µm wymaga
n_e = 4,4·10¹⁸ cm⁻³ (17,5% cząsteczek), przy L = 10 µm 175% (wielokrotna jonizacja).
Siatka wsteczna Λ = 266 nm: czas życia ~0,2–1,8 ps przy D_a = 10–100 cm²/s (założenie)
albo ~21 fs przy skalowaniu zmierzonych 68 ps (Λ = 15,3 µm) jak Λ². T3 da się przekroczyć,
ale warunki 1 (średnia czasowa) i 4 padają o rzędy wielkości. NIEROZSTRZYGNIĘTE (szacunek).

## Iteracja 16 — przekładki, kierunek wyjścia, siatki skośne, podwójna źrenica (`research/iteracja16.py`)

**Kluczowe:** siatki niesłantowane odbijają każdą warstwę pod innym kątem (−17,4 … −59,2°
w powietrzu, rozrzut 41,8°), więc widz w stożku 1° widzi jedną warstwę — C2 w tej geometrii
(także kandydat z iteracji 15) nie jest wyświetlaczem 3D.

- Przekładki 51/200/500/1000 µm (pol. p, n₁ = 0,02): R średnie po λ 0,21–0,71; zafalowanie
  przy stałej λ 36–64% (51 µm) i 42–62% (1 mm) — niezależne od grubości, zmienia się tylko
  okres prążków (2,1 nm → 0,11 nm); moc innych warstw 1–8% sygnału; brak modów falowodowych
  (TIR 1,5→1,48 dopiero > 80,6°). Winietowanie przy 1 mm: przesunięcie 5,6 mm, 44% pola 10 mm.
- Siatki skośne (Kogelnik, wyjście wzdłuż normalnej): η = 0,62–0,68 (p, n₁ = 0,02), czynnik
  |cosθ| = 0,82–0,98; światło z sąsiedniej siatki wychodzi pod 5,3–12,3°; akceptacja kątowa
  10,6° / 3,5° / 1,0° (powietrze) dla L = 10 / 30 / 100 µm przy stałym n₁·L.
- Podwójna źrenica ±6°: Δn 0,03 → 2 × 0,015: łącznie 0,70 (10 µm) / 0,92 (16 µm), na oko
  0,35 / 0,46 (pol. p); pole głowy: dwie plamki 5,2 mm w 30 cm.
- Bilans AOD 0,8 × SLM 0,6 × R 0,4 / 5 warstw: 38,4 µW/warstwę, 33,2 µW w stożku, SNR śrutowy
  ~10⁷ w 1 s; ograniczają tempo SLM (300 wzorów/s), étendue AOD, bezpieczeństwo oka.
- Przekaźnik 4f: M_z = 500 → półkąt 0,022°, plamka 0,23 mm ≪ źrenica → brak akomodacji;
  przy stożku 1° i źrenicy ~3,5 mm akomodacja przetrwa M_z ≲ 2. ODRZUCONE (Lagrange).
- Superradiacja: Rui i in. zmierzyli Γ = 4,04 MHz < Γ₀ = 6,06 MHz (lustro subradiacyjne);
  superradiacja w warstwie wymaga a < 0,49λ ≈ 381 nm, zysk ~2× przy a = 266 nm.

**Następne pytanie:** RCWA dla dwóch skośnych warstw ~100 µm (n₁ ≈ 0,002) z przekładką ~1 cm —
czy oba kanały wychodzą wzdłuż normalnej z ≥ 10% mocy w stożku 1° i przesłuchem ≤ 1%?

## Iteracja 17 — RCWA dwóch skośnych warstw (`research/rcwa.py`, `rcwa_walidacja.py`, `iteracja17.py`, `iteracja17b.py`)

**Metoda:** własny solver RCWA (Moharam i in., JOSA A 12, 1068, 1995; „enhanced transmittance”,
TM z regułą odwrotności Li). Walidacja: profil zależny tylko od z = TMM (s 0,21502; p 0,13444);
siatka skośna 20° → normalna zgodna z Kogelnikiem (p: 0,6654 vs 0,6659); R + T = 1,000000;
wynik niezależny od M = 3/5/7; 32 plastry na okres z (zbieżność 2. rzędu, błąd ~0,1%).
Parametry: L = 100 µm, n₁ = 0,002, n₀ = 1,5, λ₀ = 532 nm, pol. p; A: 20° wewn. (30,87° pow.),
B: 22° wewn. (34,19° pow.); warstwy łączone niekoherentnie (przekładka 10 mm, różnica dróg
2·1,48·10 mm ≈ 29,6 mm ≫ L_c).

- η do zadanego wyjścia: A 0,6650, B 0,6603; wszystkie wyższe rzędy ≤ 3·10⁻⁷ (jeden uwięziony TIR).
- **Cieniowanie (nowe):** z wzajemności górna siatka jest dopasowana Bragga do wiązki biegnącej w górę
  wzdłuż normalnej — odbija w dół 66,5% wyjścia B. Akceptacja tego portu: T = 0,34 / 0,40 / 0,64 /
  0,96 / 0,97 przy odchyleniu 0 / 0,25 / 0,5 / 0,75 / 1,0° (pow.). Przy N warstwach z wyjściem
  na normalnej dolny kanał dostaje ~0,62·0,335^(N−1): N = 3 → 0,07 < 10%.
- Bilans w stożku 1° (Fresnel pol. p na wejściu, 4% na wyjściu; linia wąska / źródło gaussowskie 1,5 nm):

  | stos (wyjścia w powietrzu) | kanał 1 | kanał 2 | kanał 3 | obce światło w stożku ±0,5° |
  |---|---|---|---|---|
  | 0° / 0° (polecenie) | 0,623 / 0,391 | 0,206 / 0,172 | — | 0 (najbliższe 2,8°, 0,96%) |
  | 0° / 1° | 0,623 / 0,391 | 0,597 / 0,359 | — | 0 (najbliższe 1,7–1,8°) |
  | 0° / 2° | 0,623 / 0,391 | 0,599 / 0,381 | — | 0 (najbliższe 0,7–0,8°) |
  | 0° / 3° | 0,623 / 0,391 | 0,608 / 0,381 | — | 0,39–0,72% mocy sondy (rząd z A 0,1–0,2° od wyjścia B) |
  | 0° / 2° / 4° | 0,623 / 0,391 | 0,599 / 0,381 | 0,602 / 0,376 | 0 (najbliższe 0,68–0,76°) |
  | 0° / 3° / 6° | 0,623 / 0,391 | 0,608 / 0,381 | 0,594 / 0,374 | 0,59–0,72% mocy sondy (jak 0°/3°) |

- Widmo A: FWHM 1,20 nm (oszacowanie λ²/(2nL) = 0,94 nm). Źródło gaussowskie 0,5/1,0/1,5/2,0 nm:
  η = 0,630/0,524/0,417/0,340 (95/79/63/51% szczytu). Argument „L < L_c ⇒ brak strat” jest
  błędny: o stratach decyduje szerokość widma siatki (1,2 nm), nie L wobec L_c.
- Prążki przekładki: widoczność V = exp(−(π·OPD·Δλ/λ²)²/(4 ln 2)) przy OPD = 29,6 mm:
  0,02 (Δλ = 0,01 nm), 2·10⁻⁷ (0,02 nm), ~0 (1,5 nm). Do zgaszenia prążków wystarcza
  0,02–0,05 nm; 1,5 nm gasi je, ale kosztuje 37% η. W geometrii skośnej wiązki kanałów są
  rozdzielone kątowo (≥ 0,7°) i bocznie (walk-off 10 mm·tan 22,3° = 4,1 mm), więc prążki
  przekładki w stożku sygnału wymagają ścieżek z dwoma odbiciami Fresnela (górna i dolna
  powierzchnia, 4% każda): ≲ 2·10⁻⁴ sygnału bez AR, czyli zafalowanie ≤ 3% przy pełnej
  koherencji i ~0 przy Δλ ≥ 0,02 nm.
- Śledzenie źrenicy zmianą kąta wejścia: η = 0,62 / 0,45 / 0,0002 / 0,004 / 0,002 przy
  +0,25 / 0,5 / 1 / 2 / 5° (pow.); użyteczne ±0,5° → plamka ±2,2 mm w 30 cm, nie „kilka cm”.
- Bezpieczeństwo oka: wyjście skolimowane (C6 = 1), więc cała moc kanału (0,39–0,62 mW przy
  sondzie 1 mW) może wejść w źrenicę 7 mm. AEL klasy 1 dla 532 nm przy T2 = 10 s z wzoru
  7·10⁻⁴·C6·T2^(−0,25) W = 0,39 mW (wzór z pamięci, tekstu normy IEC 60825-1:2014 nie
  zweryfikowano — płatny). Margines 6× wymaga, by sonda oświetlała woksele widoczne z jednej
  źrenicy ≤ 10–17% czasu; dla obrazu statycznego w polu ~9 mm jest 1,0–1,6× ponad AEL.

**Werdykt iteracji: NIEROZSTRZYGNIĘTE.** W modelu RCWA dwa (i trzy) kanały skośne dają
≥ 0,36 mocy sondy w stożku 1° przy źródle 1,5 nm, bez obcego światła w stożku, pod warunkiem
odchylenia wyjść o 1–2° między kolejnymi warstwami (wyjścia na wspólnej normalnej: drugi
kanał 0,17; trzeci z oszacowania ~0,07–0,08 < 0,10).
To rachunek, nie pomiar; warunek 4 (trwałość materiału) i realna modulacja n₁ = 0,002 przy
L = 100 µm w skośnej geometrii pozostają niezmierzone.

**Następne pytanie:** jak liczba kanałów skaluje się z odchyleniem wyjść (każdy kanał zużywa
≥ 1° pola wyjścia i ~2° pola wejścia) — ile warstw mieści się w polu wejścia, zanim przesłuch
w stożku przekroczy 1%?

## Iteracja 18 — źrenica widza kontra odchylone wyjścia (`research/iteracja18.py`)

**Korekta iteracji 17:** „okno 1–2° na warstwę” usuwa cieniowanie, ale w 30 cm wiązki z jednego
punktu płyty rozchodzą się o 300·tan(1,5°) = 7,9 mm na warstwę, a źrenica ma ~3,5 mm. Nieruchome
oko widzi jedną warstwę na pozycję (5 warstw 0/1,5/3/4,5/6°: plamki 0/7,9/15,7/23,6/31,5 mm,
w źrenicy 1 z 5). Wniosek iteracji 17 o trzech kanałach dotyczył mocy w stożku, nie wspólnej źrenicy.

- **H1 soczewka polowa f = 300 mm: ODRZUCONE.** W płaszczyźnie ogniskowej x_p = f·tanα — te same
  7,9 mm na 1,5°. Ogólnie (paraksjalnie) x_p = A·x + B·α, więc wszystkie warstwy z pola W w źrenicy
  p wymagają |A|·W + |B|·Θ ≤ p, czyli pozorna odległość obrazu D_app ≤ p/Θ: 33 mm dla Θ = 6°,
  401 mm dla 0,5°. Przy D_app = 300 mm: Θ ≤ 0,67° (0,48° z wiązką 1 mm). Soczewka leży poza stosem,
  więc RCWA się nie zmienia; stożek po soczewce w/f = 0,19° < 1°, ale to nie pomaga.
- **RCWA 5 warstw z polecenia** (wejścia 20–28° co 2°, linia wąska / źródło 0,15 nm):
  wyjścia +1,5°: 0,623 / 0,607 / 0,605 / 0,582 / 0,584 (0,15 nm: 0,580–0,620); przesłuch w stożku
  innego kanału 0,72% mocy sondy (1,2% sygnału; rząd z A 0,2° od wyjścia kanału 3).
  Wyjścia −1,5°: 0,597–0,624, przesłuch 0,99% mocy sondy. Wszystkie wyjścia 0°: 0,623 / 0,206 /
  0,071 / 0,024 / 0,008 (cieniowanie).
- **Stosy mieszczące się w źrenicy** (wachlarz 0,45°, plamki w 30 cm ≤ 2,36 mm, wiązki 1 mm w źrenicy):
  2 warstwy 0 / 0,45°: 0,623 / 0,356; 3 warstwy co 0,225°: 0,623 / 0,239 / 0,146;
  4 warstwy co 0,15°: 0,623 / 0,221 / 0,099 / 0,063. Obce światło w stożku: 0.
  Przy L = 100 µm jedno oko w 30 cm widzi najwyżej 3 warstwy po ≥ 10%.
- **H2 16 warstw: ODRZUCONE.** Wejście 8–38° wewn = 12,0–67,4° w powietrzu (od strony powietrza nie
  ma TIR, granicę daje Fresnel i czynnik p cosθ). Bez odchylenia: dolny kanał ~0,62·0,335¹⁵ = 5·10⁻⁸;
  z odchyleniem ≥ 0,75°/warstwę wachlarz 11° ≫ 0,67°. Przekładki 1 mm: OPD = 2,96 mm, V = 0,86 /
  0,38 / 0,009 / 1,6·10⁻⁴ przy Δλ = 0,02 / 0,05 / 0,11 / 0,15 nm — źródło 0,02–0,05 nm nie gasi
  prążków; 0,15 nm gasi przy η = 99,5% szczytu. Głębia 16 mm w 30 cm to Δ(1/z) = 0,169 D
  (rozmycie 2,0′ przy źrenicy 3,5 mm) i ≈ 1 głębia ostrości woksela w stożku 1° (T2: 14 mm);
  wiązka skolimowana nie daje bodźca akomodacji (najostrzejszy obraz przy ogniskowaniu na ∞).
- **H3 multipleksowanie azymutalne: ODRZUCONE.** Kogelnik 3D zgodny z RCWA dla odchylenia w płaszczyźnie
  siatki (T = 0,334 / 0,401 / 0,643 / 0,960 / 0,974 wobec 0,335 / 0,402 / 0,644 / 0,962 / 0,973).
  Odchylenie prostopadłe (y): T = 0,30 / 0,31 / 0,38 / 0,62 / 0,98 przy 1 / 2 / 3 / 4 / 5° — rozstrojenie
  Bragga jest tu drugiego rzędu, więc potrzeba ≥ 5° zamiast 0,75°. Warstwa obrócona o 90° z wyjściem
  na normalnej: jej pol. p jest dla górnej warstwy pol. s → T = 0,296 (gorzej niż 0,335).
  Dwa kierunki we wspólnym oknie 0,67° są zawsze bliżej niż 0,75°, więc żaden układ 2D nie daje
  T ≥ 0,96 przy L = 100 µm.

**Werdykt iteracji: ODRZUCONE** (H1, H2, H3 — każde na podstawie górnego ograniczenia: Lagrange,
cieniowanie RCWA, rozstrojenie Bragga). C2 ze skośnymi siatkami pozostaje NIEROZSTRZYGNIĘTE z limitem
3 warstw na jedno oko przy L = 100 µm.

**Następne pytanie:** siatki grubsze (L ~ 1 mm, n₁ ~ 2·10⁻⁴) mają port węższy ~10× (akceptacja ∝ 1/L) —
ile warstw zmieści się w wachlarzu 0,48° i czy wiązka woksela wypełniająca źrenicę (≥ 0,67°, potrzebna
do akomodacji) nie zostanie wycięta przez porty warstw wyżej?

## Iteracja 19 — siatki skośne 1 mm w jednej źrenicy; kompensacja translacyjna (`research/iteracja19.py`)

**Tor 1: L = 1 mm, n₁ = 2·10⁻⁴** (n₁·L jak przy 100 µm), n₀ = 1,5, λ₀ = 532 nm, pol. p, wejście 20° wewn.
Kogelnik 3D sprawdzony RCWA (32 plastry/okres, ~175 tys. plastrów, 11 s/rozwiązanie): wejście +0,05°
0,4540 vs 0,4552; λ₀ + 0,06 nm 0,3479 vs 0,3491; port 0,12° 0,9428 vs 0,9427; port 0° 0,3351 vs 0,3341.
- η szczyt 0,665; akceptacja kątowa wejścia FWHM 0,122° w powietrzu (0,075° wewn.); widmo FWHM 0,122 nm.
  Tolerancje dla η ≥ 90% szczytu: ±0,030 nm i ±0,030° (pow.).
- Źródło gaussowskie 0,01 / 0,05 / 0,11 / 0,15 / 1,5 nm: η = 100 / 95 / 75 / 63 / 8% szczytu.
- Port (wiązka z warstwy niżej): T = 0,334 / 0,630 / 0,982 / 0,943 / 0,981 / 0,997 przy odchyleniu
  0 / 0,05 / 0,10 / 0,12 / 0,15 / 0,24° — 0,12° trafia w listek boczny (minimum T 0,943); 0,10° i 0,15° dają 0,98.
- **RCWA stosu 5 warstw** (wejścia 20–28° co 2°, wyjścia −0,24 / −0,12 / 0 / +0,12 / +0,24°): moc w stożku
  0,623 / 0,586 / 0,586 / 0,596 / 0,603 przy λ₀; 0,40–0,43 przy λ₀ ± 0,05 nm. Obce światło w stożkach ±0,5°: 0
  (najbliższy obcy rząd 2,19° od wyjść, 6,6·10⁻⁵ mocy sondy). Plamki w 30 cm: −1,26 … +1,26 mm; wiązka 1 mm
  w źrenicy 3,5 mm w 99,3–100%. **Pierwszy model, w którym 5 warstw trafia w jedno nieruchome oko z ≥ 10%.**
- Stożek woksela: wyjście = wejście przesunięte w kx, więc w osi x stożek ≤ akceptacja 0,12° ≪ 0,67°
  (wypełnienie źrenicy). W osi y akceptacja wejścia ±1,26°; stożek y ±0,33° przechodzi przez porty 4 warstw
  wyżej w 98%. Bodziec akomodacji możliwy tylko w jednym południku — czy oko na niego reaguje, nie sprawdzono.
- Prążki przy przekładkach 1 mm (OPD 2,96 mm, okres 0,096 nm): V = 0,96 / 0,38 / 0,009 przy 0,01 / 0,05 / 0,11 nm.
  Tło koherentne ≤ R₁R₂: bez AR (R = 4%) ≤ 1,6·10⁻³ sygnału, zafalowanie ≤ ±8%; z AR (R = 0,25%) ≤ ±0,5%.
- Pole widzenia jednego oka przy stożku 1°: ≤ p/D + 1° = 1,67° (≈ 8,7 mm płyty w 30 cm); przy stożku x 0,12°
  w osi x ≈ 0,79°. To skutek samego warunku 1.

**Materiał (podagent, pełne teksty [FT] lub abstrakty [Abs]):** odbiciowe VBG w szkle PTR mają zmierzone
L = 5,5 mm, Δn = 230 ppm, R > 99%, FWHM 215 pm przy 1064 nm, a w wersji multipleksowanej L = 6,5 mm,
Δn = 130 ppm na siatkę, > 98% (Ott i in. 2013, Opt. Express 21, 29620 [FT]); L = 8,3 mm, Δn = 63 ppm,
FWHM 35 pm przy 633 nm, 98 ± 1% (Mhibik i in. 2016, Light Sci. Appl. 5, e16026 [FT]); maks. Δn ~10⁻³ [FT].
Δn = 2·10⁻⁴ jest więc typowe. Cztery odbiciowe VBG w szeregu po ~99,7%, łącznie > 750 W CW (Sevian i in. 2008,
Opt. Lett. 33, 384 [FT]); 420 W przy kilku kW/cm² (Ott 2013 [FT]) — warunek 4 przy 1 mW ma zapas rzędów
wielkości, ale zmierzono to przy 1064 nm, nie 532 nm. Odbiciowej VBG w PTR przy 532 nm z podanym L i Δn
w recenzowanej literaturze nie znaleziono (tylko karta producenta, słabe źródło). PQ:PMMA w bloku:
Δn do 1,16·10⁻⁴, skurcz 0,09–0,4% (Hu i in. 2022, ACS AMI 14, 21544 [FT]); skurcz przesuwa λ Bragga
o 0,5–2 nm, czyli 16–70 × poza tolerancją ±0,03 nm.

**Tor 2, kompensacja translacyjna: ODRZUCONE.** Start w x = −D·tanθ (−5,2 / −7,9 / −10,5 mm dla 1 / 1,5 / 2°)
kieruje wiązki w źrenicę, ale kierunek widzenia warstwy = kierunek jej wiązki, więc warstwy widać przesunięte
o Δθ. Łatka jednej warstwy ma ±0,43° (wiązki skolimowane), więc łatki nakładają się tylko przy Δθ < 0,86°.
Walk-off 4,1 mm w przekładce dotyczy wiązki sondy (gdzie wchodzi), nie kierunku wyjścia.

**Werdykt iteracji: NIEROZSTRZYGNIĘTE.** W modelu RCWA stos 5 warstw skośnych 1 mm spełnia warunek 1
(0,59–0,62 w stożku) i warunek 2 (warstwy co ≥ 1 mm, przełączanie kątem wejścia przy stałej λ) dla jednego
nieruchomego oka, bez przesłuchu w stożku. Brak pomiaru; warunki 3–4 i adresowanie x–y niewykazane;
bodziec głębi tylko w jednym południku.

**Następne pytanie:** pomiar dwóch skośnych siatek odbiciowych 1 mm (np. PTR) w szeregu przy 532 nm,
jednoczęstotliwościowym źródle i odchyleniu wyjść 0,10°: moc z każdej warstwy w aperturze 3,5 mm w 30 cm
(model: 0,62 i ~0,61) oraz przepuszczalność portu górnej siatki (model: 0,98).

## Iteracja 20 — woksel anamorficzny, bezpieczeństwo oka, kompensacja błędu okresu (`research/iteracja20.py`)

Rachunek kątowy przez rozkład wiązki na fale płaskie: η_śr = ∫ η(θ)·I(θ) dθ, η(θ) z Kogelnika 3D (zgodny z RCWA,
iteracja 19); wiązka gaussowska, półkąt 1/e² θ₀ = λ/(π w₀).

- **H1 woksel anamorficzny: NIEROZSTRZYGNIĘTE (model).** Oś x: η = 0,31 / 0,49 / 0,58 / 0,64 / 0,65 / 0,66 przy
  w₀x = 50 / 100 / 150 / 250 / 330 / 500 µm (2w₀ = 0,3 mm daje 87% fali płaskiej). Oś y przy w₀x = 330 µm:
  2w₀y = 15 µm daje stożek 2,59° i tylko 56% mocy w ±0,5°; warunek 1 (θ₀ ≤ 0,5°) wymaga 2w₀y ≥ 39 µm,
  wypełnienie źrenicy (≥ 0,67°) 2w₀y ≤ 58 µm, η = 0,648–0,650 w tym oknie. Pole widzenia jednego oka
  0,86° × 1,67° (4,5 × 8,7 mm), nie 8,7 × 8,7 mm, bo stożek w x ma ~0,1°. Woksli na warstwę na oko:
  ~8,7 tys. dla 300 × 15 µm (propozycja), ~2,3 tys. dla 300 × 50 µm, ~1 tys. dla 660 × 50 µm.
  Rzędy modulatora SLM (≥ 1,5° przy skoku ≤ 20 µm) nie są odbijane (strata), chyba że m·λ/p = Δkx = 0,0489
  (p = 10,9·m µm) — wtedy trafiają w kanał sąsiedniej warstwy; potrzebny filtr w płaszczyźnie Fouriera.
- **H2 bezpieczeństwo oka** (ICNIRP 2013, Health Phys. 105(3):271–295, Tabela 5, apertura 7 mm, tekst pierwotny
  przeczytany przez podagenta): kryterium 1 — impuls 33 µs (N = 100) ma 20 nJ wobec 307 nJ (zapas 15×),
  3,3 µs (N = 1000) 2 nJ wobec 77 nJ (39×); kryterium 3 — Cp = 1 (α ≤ 5 mrad, impuls > T_i = 5 µs) albo 0,2
  (impulsy ≤ T_i, ekspozycja zamierzona, 6·10⁵ impulsów na jedno miejsce) → zapas 7,7×; **kryterium 2
  (średnia w T2 = 10 s)**: skanowanie nie zmniejsza mocy średniej wchodzącej do źrenicy. Przy oku
  zogniskowanym na ∞ wiązki skolimowane jednej warstwy trafiają w jedno miejsce siatkówki: treść w jednej
  warstwie → 0,60 mW wobec 0,39 mW = 1,54 AEL; treść równo w 5 warstwach → 0,31 AEL; źródło pozorne liniowe
  (α = 6,6 mrad) → 0,36 AEL. Teza „skanowanie daje Klasę 1 z zapasem przy 1 mW”: ODRZUCONE (kontrprzykład).
  Przy sondzie ≤ 0,65 mW wszystkie trzy kryteria spełnione. Wartości IEC 60825-1:2014 tylko wtórnie
  (zgodne z kolumną W/J ICNIRP).
- **H3 kompensacja błędu okresu kątem wejścia: NIEROZSTRZYGNIĘTE (w modelu tak dla |δΛ/Λ| ≤ 1·10⁻⁴).**
  δΛ/Λ = 1·10⁻⁴: bez korekty η = 0,42; korekta wejścia 0,054° → η = 0,666 (RCWA 0,6652). Zakres ±0,5° deflektora
  pokrywa |δΛ/Λ| do ~1·10⁻³ (0,53°), ale wyjście przesuwa się o ~0,9 × korekta: 0,049° / 0,15° / 0,48° dla
  1·10⁻⁴ / 3·10⁻⁴ / 1·10⁻³ (0,26 / 0,77 / 2,5 mm w 30 cm). Port przy kroku 0,12° i przesunięciu ±0,05°:
  T = 0,90–1,0 (0,898 przy 0,07°). Błąd skosu ±0,01° / ±0,05°: korekta 0,016° / 0,082°, wyjście 0,015° / 0,075°.
  Praktyczna tolerancja: |δΛ/Λ| ≲ 1·10⁻⁴, skos ≲ 0,03°.

**Werdykt iteracji: NIEROZSTRZYGNIĘTE.** Woksel 2w₀ ≈ (0,3–0,66 mm) × (39–58 µm) zachowuje η ≥ 0,58 i stożek < 1°;
bezpieczeństwo oka przy 1 mW zależy od treści (do 1,54 AEL), przy ≤ 0,65 mW spełnione; błąd okresu ≤ 1·10⁻⁴
kompensowalny kątem wejścia.

**Następne pytanie:** jak oko widzi obraz z woksli skolimowanych w x: rozdzielczość w x przy ogniskowaniu na płytę
(w/D ≈ 2,2 mrad ≈ 7,6′ dla 0,66 mm) i zanik struktury x przy ogniskowaniu na ∞ — PSF siatkówkowe wiązki anamorficznej.

## Iteracja 21 — obraz woksla na siatkówce, faza cylindryczna, SNR warunku 3 (`research/iteracja21.py`)

Model: wiązka gaussowska z taliami w₀x, w₀y w warstwie, oglądana z 300 mm; oko zredukowane f = 17 mm, źrenica 3,5 mm;
pole na siatkówce = transformata Fouriera pola w źrenicy z fazą akomodacji (FFT 2D). Filtr Bragga: amplituda √η(θ)
z Kogelnika 3D (faza odbicia pominięta). Commity tej iteracji tylko lokalnie (polecenie użytkownika).

- Wiązka w źrenicy: x, w₀ = 150 µm: R(300 mm) = 359 mm (2,79 D), średnica 0,74 mm; x, w₀ = 330 µm: 1679 mm (0,60 D);
  y, w₀ = 25 µm: 300 mm (3,33 D), średnica 4,06 mm (wypełnia źrenicę). Teza audytu „R ≈ 500 mm dla 0,3 mm” — błędna.
- **Siatkówka, woksel 300 × 50 µm:** akomodacja na warstwę (3,33 D): FWHM x = 2,03′ (10,1 µm), y = 0,52′ (2,6 µm);
  kontrast sąsiednich woksli (skok 2w₀) x = 0,56, y = 0,08. Akomodacja na ∞: x = 4,23′, y = 22′, kontrast 0 i 0.
  Woksel 660 × 50 µm: na warstwę x = 4,43′, y = 0,52′; na ∞ kontrast 0. **„Kreska Sturma zamazująca x”: ODRZUCONE** —
  oko zogniskowane na warstwie odwzorowuje talię (elipsa 2′ × 0,5′, proporcja jak woksel); przy ∞ znika cały obraz
  (oba kierunki), bo położenie woksla nie zmienia kierunku wiązki. Skok 50 µm w y (0,57′) jest poniżej rozdzielczości
  źrenicy 1,22λ/p = 0,64′ (kontrast 0,08): rozróżnialny skok w y ≈ 1′ ≈ 90 µm → ~15 × 75 ≈ 1,1 tys. woksli na warstwę na oko.
- **Faza cylindryczna na wejściu: ODRZUCONE jako naprawa.** Talia 0,3 mm w warstwie: η = 0,581, wergencja x przy oku
  2,47 D, obraz x 2,51′. Propozycja (1 mm, f = −300 mm w warstwie): η = 0,491 (< 0,50), wergencja x 1,67 D (źródło pozorne
  600 mm od oka, nie 300 mm), obraz x 4,63′. f = −150 mm: η = 0,311, 2,18 D, 2,34′. Wergencja 3,33 D wymaga źródła
  pozornego w warstwie, czyli talii w warstwie, a jej rozmiar ogranicza akceptacja Bragga (w₀·θ ≥ λ/π).
- **Warunek 3 (sonda 0,50 mW, sygnał 0,30 mW = 8,0·10¹⁴ fotonów/s):** Si, wydajność kwantowa 0,70 (0,30 A/W), 1 cm²,
  filtr 10 nm, 1 s: SNR śrutowy 2,4·10⁷ (ciemnia), 2,3·10⁷ (500 lx, tło 6,7 µW), 2,0·10⁷ (10 klx, tło 133 µW);
  z niestabilnością lasera 0,1% / 1% rms: ~10³ / ~10². Spełnia w modelu; brak pomiaru.
- Jasność: 0,18 lm w stożku; luminancja woksla ~4·10¹¹ cd/m² chwilowo, ~1,7·10⁸ cd/m² średnio po polu 4,5 × 7,6 mm —
  nie „kilkanaście tysięcy nitów”. Wyświetlacz potrzebuje mocy o kilka rzędów mniejszej.

**Werdykt iteracji: NIEROZSTRZYGNIĘTE.** Obraz na siatkówce przy akomodacji na warstwę: woksel 2′ × 0,5′, x rozdzielone
przy skoku 0,3 mm; teza o astygmatycznej kresce i naprawa fazą cylindryczną odrzucone; warunek 3 spełniony w modelu.

**Następne pytanie:** czy oko faktycznie akomoduje na warstwę (3,33 D), gdy bodziec niesie tylko oś y — czyli czy
astygmatyczny bodziec akomodacji jest skuteczny (pomiar optometryczny), i czy przy jego braku obraz nie znika (∞ → kontrast 0)?

## Iteracja 22 — akomodacja kompromisowa, projekcja warstwowa, test laboratoryjny (`research/iteracja22.py`)

Commity tej iteracji tylko lokalnie (polecenie użytkownika). Model siatkówki jak w iteracji 21 (f = 17 mm, źrenica 3,5 mm);
woksel 300 × 50 µm (w₀x = 150, w₀y = 25 µm); skoki: x 300 µm, y 90 µm. Kontrast: woksle zapalane kolejno (suma natężeń)
albo jednocześnie przez SLM przy koherentnym laserze (suma pól, w fazie / w przeciwfazie).

| A [D] | FWHM x | FWHM y | kontrast x: kolejno / w fazie / przeciwfaza | kontrast y: kolejno / w fazie |
|---|---|---|---|---|
| 2,79 | 1,83′ | 4,24′ | 0,48 / 0,18 / 1 | 0,04 / 0 |
| 3,06 | 1,91′ | 1,79′ | 0,55 / 0,28 / 1 | 0,00 / 0 |
| 3,20 | 1,96′ | 0,65′ | 0,57 / 0,31 / 1 | 0,29 / 0 |
| 3,33 | 2,03′ | 0,52′ | 0,56 / 0,30 / 1 | 0,90 / 0,80 |
| 3,45 | 2,09′ | 0,60′ | 0,57 / 0,31 / 1 | 0,44 / 0,12 |

- **H1 akomodacja kompromisowa 3,06 D: ODRZUCONE (rachunek falowy).** Wiązka y wypełnia źrenicę, więc błąd 0,27 D
  rozmywa ją o p·ΔA = 0,95 mrad (3,2′): kontrast y przy skoku 90 µm spada z 0,90 do 0,00. Oś x jest wąska (0,74 mm
  w źrenicy) i prawie niewrażliwa na A (0,38–0,57 w 2,6–3,6 D). Optimum to akomodacja na warstwę (3,33 D) z tolerancją
  ok. ±0,1 D dla osi y. „Fizjologiczna głębia ostrości ±0,3–0,5 D” — nie sprawdzono; optycznie obraz y się rozmywa.
- **H2 projekcja warstwowa SLM/DMD: NIEROZSTRZYGNIĘTE.** Sonda 0,50 mW, T_SLM = 0,65, η = 0,60, 1100 woksli, 5 warstw:
  295 nW na woksel w czasie warstwy, 35,5 nW średnio w stożku; luminancja ~2,5·10⁷ cd/m² (równoważna z obrazu
  na siatkówce) — 1000 cd/m² daje już sonda ~20 nW. Bezpieczeństwo (ICNIRP 2013): pełna warstwa 0,195 mW w źrenicy →
  0,50 / 0,19 / 0,04 granicy (źródło punktowe / plama 4 mrad / obraz 22 mrad). **Nowe:** woksle zapalane jednocześnie
  koherentnym laserem (Δλ ≤ 0,03 nm) interferują: kontrast x spada z 0,56 do 0,30 (w fazie). Deflektor: wejścia
  30,87–44,77° w powietrzu (zakres 13,9° przy skoku 2° wewn.), iloczyn z polem 8,7 mm = 121 °·mm — do porównania
  z kartą urządzenia (nie sprawdzono).
- **Próba laboratoryjna (kryteria przed pomiarem):** płytka A: wejście 20,0° wewn. (30,87° pow.) → 0°, Λ = 180,07 nm,
  płaszczyzny nachylone 10,00°; płytka B: wejście 22,0° (34,19°) → +0,10°, Λ = 180,67 nm, 10,97° (dla +0,12°:
  180,68 nm, 10,96°). RCWA: wyjścia 0/0,10°: A 0,623, B 0,609 (port 0,982); 0/0,12°: B 0,585 (port 0,943) — zalecane 0,10°.
  Stożek 1°: soczewka f = 200 mm + przesłona 3,49 mm w ognisku. Warunek 2: warstwa B 2 mm głębiej → punkt wyjścia
  przesunięty o ~0,77 mm na powierzchni (10 µm głębi ↔ 3,8 µm), przy tej samej λ (miernik długości fali).

**Werdykt iteracji: NIEROZSTRZYGNIĘTE.** Akomodacja kompromisowa odrzucona; projekcja warstwowa ma ogromny zapas
jasności i spełnia Klasę 1, ale koherencja obniża kontrast x do 0,30; kryteria testu laboratoryjnego zapisane.

**Następne pytanie:** czy dekoherencja sąsiednich woksli w osi y (gdzie akceptacja Bragga jest szeroka, ±1,26°),
np. ruchomy dyfuzor lub wzór fazowy SLM, przywróci kontrast x ≥ 0,5 bez spadku η i bez wyjścia poza stożek 1°?

## Iteracja 23 — kontrast koherentny, faza 0/π, podramki, adresowanie kątowe (`research/iteracja23.py`)

Commity tej iteracji tylko lokalnie (polecenie użytkownika). Oś x, oko na warstwie: obraz woksla ≈ |pole odbite w warstwie|²
(wiązka x ≪ źrenica), pole odbite = wejście przefiltrowane amplitudą √η(θ) siatki 1 mm (Kogelnik 3D, faza pominięta).

- **Korekta iteracji 21–22:** kontrast w osi x liczyłem tam bez filtru Bragga. Filtr poszerza woksel (w₀x = 150 µm:
  FWHM 177 → 217 µm), więc przy skoku 300 µm kontrast zapalania kolejnego to **0,30** (nie 0,56), a jednoczesnego
  w fazie **0,02** (nie 0,30). Kontrast kolejny w funkcji talii i skoku (300 / 400 / 500 / 660 µm):
  w₀x = 100 µm (η 0,49): 0,56 / 0,89 / 1,00 / 1,00; 150 µm (η 0,58): 0,30 / 0,70 / 0,93 / 1,00;
  250 µm (η 0,64): 0,02 / 0,22 / 0,50 / 0,84; 330 µm (η 0,65): 0,00 / 0,04 / 0,20 / 0,54.
- Para woksli (w₀x = 150 µm, skok 300 µm), kontrast / η / moc średnia względem zapalania kolejnego:
  kolejno 0,30 / 0,581 / 100%; jednocześnie w fazie 0,02 / 0,624 / 107%; **przeciwfaza 0/π 1,00 / 0,525 / 90%**;
  **podramki nieparzyste/parzyste (DMD) 0,30 / 0,581 / 50%**; **dwie podramki z fazą względną 0 i π (modulator fazy)
  0,30 / 0,575 / 99%**. Rząd trzech woksli: kolejno 0,30, w fazie 0,03, 0/π/0 1,00, podramki (0,0,0)+(0,π,0) 0,30.
- **2A faza 0/π: ODRZUCONE jako naprawa.** Wzór 0/π o skoku 300 µm ma składowe ±λ/(2·skok) = ±0,051° przy połowie
  akceptacji 0,061°, więc η pary spada o 10%. Kontrast 1,00 bierze się z wymuszonego ciemnego prążka między każdymi
  dwoma zapalonymi sąsiadami — linia ciągła staje się przerywana; to zmiana obrazu, nie odtworzenie obrazu niekoherentnego.
- **2B podramki DMD: działa, ale nie „bez strat”** — kontrast jak kolejno (0,30), średnia moc 50% (połowa światła
  odrzucona). Przy zapasie jasności ~2,5·10⁴ (iteracja 22) strata nieistotna. Wariant z modulatorem fazy (0, potem π)
  daje ten sam kontrast przy 99% mocy, ale tylko dla najbliższych sąsiadów.
- **2C losowa faza w osi y: ODRZUCONE.** Maska wspólna dla sąsiadów w x nie zmienia członu interferencyjnego
  (I = |E1 + E2|²·|g(y)|²). Osobne maski muszą mieć komórki mniejsze od obrazu y na warstwie (45 µm): komórka 25 µm
  daje rozrzut 1,22° (poza stożkiem 1°), komórka 50 µm (0,61°, w stożku) to tylko 0,9 komórki na element rozdzielczości.
- **Deflektor:** TBP = D·Δθ/λ = 3967 (8,7 mm, 13,9°: 281 MHz, τ = 14,1 µs). **Teleskop 8,7×: ODRZUCONE** — iloczyn D·Δθ
  jest niezmiennikiem; deflektor 1 mm przed teleskopem rozszerzającym musiałby dać 121° (2448 MHz). Gęstsze kanały
  (siatki 1 mm): skok 1,0 / 0,5 / 0,38 / 0,25° wewn. → zakres 6,7 / 3,3 / 2,5 / 1,7°, pasmo 136 / 67 / 51 / 33 MHz,
  TBP 1921 / 948 / 719 / 471; odbicie sąsiedniej siatki ≤ 6,1·10⁻⁴ / 2,5·10⁻³ / 4,7·10⁻³ / 5,1·10⁻³ sygnału.
  Dyskretne źródła (jeden laser + przełącznik 1×5 do pięciu kolimatorów pod stałymi kątami) nie mają ograniczenia TBP
  i zachowują jedną λ (warunek 2); pięć osobnych laserów musiałoby trzymać λ w ±0,03 nm. Wspólna dla wszystkich strata
  oświetlenia pola wiązką gaussowską: 58 / 25 / 13% mocy w polu przy natężeniu brzegu ≥ 50 / 80 / 90% szczytu.
  Parametrów rynkowych deflektorów nie sprawdzono.

**Werdykt iteracji: NIEROZSTRZYGNIĘTE.** Teleskop i faza losowa w y odrzucone; faza 0/π zmienia obraz; podramki
odtwarzają kontrast niekoherentny (DMD kosztem 50% mocy, modulator fazy bez strat). Po uwzględnieniu filtru Bragga
kontrast w x wymaga skoku ≥ 400 µm (0,70 przy w₀x = 150 µm, 0,89 przy 100 µm).

**Następne pytanie:** jaka grubość siatki (0,5–1 mm) daje najlepszy kompromis: mniejszy woksel x po filtrze Bragga
(szersza akceptacja) kontra szerszy port (więcej cieniowania) i mniej warstw w wachlarzu 0,48°?
