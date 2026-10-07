# Kierunkowe odbicie światła od materii w wybranej odległości z

Oct 6, 2026 · @Adam Kowalczyk

Na podstawie dostępnych danych literaturowych i przedstawionych rachunków żaden z trzynastu mechanizmów nie został wykazany jako spełniający wszystkie pięć warunków jednocześnie. Najbliżej jest C2, model warstwowego stosu siatek odbiciowych. To interesująca hipoteza modelowa, która wymaga eksperymentalnego wykazania osiowej separacji, sprawności w stożku < 1°, SNR, trwałości i przede wszystkim niezależnego adresowania x–y. W wersji z warstwami co 10 µm leży dokładnie na progu warunku 2 i w trzech z czterech przejść go nie osiąga, także w modelu. To wydanie uwzględnia trzy audyty zewnętrzne.

## Cel i kryteria

Badane pytanie: czy wiązkę światła widzialnego można kierunkowo odbić od materii w wybranej odległości z, tak by powstał jasny, adresowalny obraz 3D w powietrzu. Mechanizm uznajemy za skuteczny tylko wtedy, gdy spełnia jednocześnie wszystkie pięć warunków.

| Nr | Warunek | Próg liczbowy |
| --- | --- | --- |
| 1 | Odbicie kierunkowe | ≥ 10% mocy wejściowej w stożku o pełnym kącie wierzchołkowym < 1° (półkąt 0,5°, 2,39·10⁻⁴ sr) |
| 2 | Wybór odległości z | płaszczyzna odbicia przesuwa się o ≥ 10 µm przy stałej barwie źródła |
| 3 | Jasność | sonda 1 mW, detektor w 30 cm, podany SNR |
| 4 | Trwałość ośrodka | 1 s pracy bez wygrzania atomów i bez wybielenia polimeru |
| 5 | Dowód | cytat do pomiaru albo jawne równanie z podstawionymi liczbami |

Przez „odbicie od materii w z” rozumiemy fizyczną interakcję pola z materią zlokalizowaną w pobliżu współrzędnej z. Samo ogniskowanie fali w pustej przestrzeni nie spełnia tej definicji. To wybór definicji problemu, a nie prawo fizyki: przy definicji „fala wychodząca z objętości” rozwiązania holograficzne i metapowierzchniowe wróciłyby do gry. Warunek 2 odczytujemy dosłownie: materia odbijająca ma się przesunąć o co najmniej 10 µm. Gdy odbicie jest rozłożone w grubej warstwie, podajemy położenie materii oraz efektywną głębokość odpowiedzi (definicje w sekcji o C2); to nie są te same wielkości.

Założenie dodatkowe, w pierwszych wydaniach niejawne: wykluczamy mechaniczny przesuw stałego reflektora. Dosłownie zapisane warunki 1–5 spełnia bowiem zwykłe lustro na stoliku piezo (R ≈ 0,9 w stożku, przesuw 10 µm, stała barwa). Pokazuje to, że pięć warunków nie koduje „adresowalnego obrazu 3D w powietrzu”. Dopuszczamy przesuw materii polami: pułapką optyczną, akustyczną albo siecią optyczną.

Doprecyzowanie sondy: 1 mW w wiązce o średnicy 1 mm, czyli średnio 127 mW/cm². Dla atomów Rb (I\_sat = 1,669 mW/cm²) daje to s ≈ 76. Inna średnica zmienia s jak 1/A, a wtedy także liczbę atomów potrzebnych do pokrycia wiązki.

Dla światła rezonansowego przyjęto przekrój czynny σ₀ = 3λ²/2π, czyli 2,907·10⁻¹³ m² dla linii D2 rubidu-87 (780 nm).

Rodzaje dowodu i werdyktów. Jawne równanie z parametrami niezmierzonymi w danym układzie daje tylko „spełnia w modelu”; POTWIERDZONE wymaga pomiaru. ODRZUCONE wymaga górnego ograniczenia: strukturalnego, wynikającego z przyjętej definicji albo ze zmierzonej mocy całkowitej, która ogranicza moc w stożku. Sam brak pomiaru albo szacunek daje NIEROZSTRZYGNIĘTE.

Warunki 3 i 4 są w oryginalnym brzmieniu nieoperacyjne. Proponowane doprecyzowanie, do ustalenia przed pomiarem:

- **Warunek 3:** SNR = średni sygnał / odchylenie standardowe w czasie integracji 1 s; detektor krzemowy o polu 1 cm² z filtrem 532 ± 5 nm; tło mierzone przy wyłączonym kanale i włączonym oświetleniu otoczenia.
- **Warunek 4:** dla polimeru zmiana R < 1% w ciągu 1 s ciągłego odczytu; dla atomów ubytek < 10% i spadek R < 10% w ciągu 1 s.

## Metoda

Recenzja przebiegła w dwunastu iteracjach (0–11) i objęła trzynaście mechanizmów. Iteracja 0 dotyczyła A i E, iteracja 1 wariantów C1 i C2, a iteracja 9 była rachunkiem dla C2. Każda iteracja kończyła się jednym werdyktem: POTWIERDZONE, ODRZUCONE albo NIEROZSTRZYGNIĘTE. Po pierwszym wydaniu referat przeszedł trzy audyty zewnętrzne; ich skutki opisuje sekcja Korekty.

1. Wybór mechanizmu z listy startowej (A–F) albo nowego, jeśli podano równanie rządzące.
2. Wielkości: λ, d lub z, θ, N, A, OD i oczekiwane R.
3. Porównanie z co najmniej jednym pomiarem z recenzowanej pracy: autorzy, rok i liczba.
4. Test zabójczy: który warunek pada i przy jakiej liczbie.
5. Werdykt i jedno następne pytanie rozstrzygalne pomiarem albo rachunkiem.

Literaturę przeszukiwano równolegle w kilku niezależnych ścieżkach, z pomocą narzędzi AI. Recenzent sprawdził sam w pełnych tekstach liczby z sześciu prac: Curtis & Psaltis 1994, Bruder i in. 2017, Bajcsy i in. 2003, Blanche i in. 2020, Rui i in. 2020 oraz Michine & Yoneda 2020. Pozostałe liczby pochodzą z pełnych tekstów lub abstraktów odczytanych w ścieżkach wyszukiwania i nie zostały powtórnie sprawdzone. Sprawdzenie w Crossref (22 DOI) potwierdza tylko dane bibliograficzne, nie liczby. Fora nie są dowodem; preprinty, patenty, komunikaty prasowe i karty producentów są oznaczone jako słabsze źródła.

Wszystkie liczby niecytowane pochodzą z pięciu skryptów w Pythonie: obliczenia.py (sekcje T0–T9), tmm\_stos\_siatek.py (macierz przejścia), tmm\_audyt\_c2.py, tmm\_audyt2\_c2.py i tmm\_audyt3\_c2.py (metryki osiowe, macierz H, zbieżność, przemiatanie n₁, interfejsy z powietrzem). Liczby odczytane z rysunku w pracy, a nie z jej tekstu, są oznaczone jako odczyt z wykresu.

## Wyniki

Pięć mechanizmów odrzucono na podstawie górnego ograniczenia: strukturalnego, z przyjętej definicji albo ze zmierzonej mocy całkowitej. Osiem pozostaje nierozstrzygniętych, bo brakuje pomiaru w wymaganych warunkach albo dostępny jest tylko szacunek. Żadnego nie potwierdzono. Wcześniejsze wydania odrzucały też A, E, F i H, ale te odrzucenia opierały się na szacunkach albo braku pomiaru, nie na ograniczeniu.

| Mechanizm | Werdykt | Podstawa werdyktu | Liczba rozstrzygająca | Główne źródło |
| --- | --- | --- | --- | --- |
| C2. Warstwy siatek odbiciowych adresowane kątem (tylko model) | NIEROZSTRZYGNIĘTE | model: warunek 2 na progu; 3 i 4 niewykazane; brak adresowania x–y | środki warstw przesuwają się o 9,92–10,02 µm, efektywna głębokość odpowiedzi o 8,6–10,4 µm; bez AR tło z powierzchni 23–84% sygnału | rachunek TMM po trzech audytach |
| G. Zwierciadło Bragga z modulacji absorpcji EIT w parze Rb (fala stojąca) | NIEROZSTRZYGNIĘTE | brak pomiaru przy 1 mW i brak przesuwu siatki | R do \~0,8 w pomiarze CW (rys. 2B, krzywa ii) przy sondzie 250 µW; w geometrii współliniowej siatka wypełnia całą komórkę | Bajcsy 2003 |
| J+. Płaskie lustro lewitowane akustycznie w powietrzu | NIEROZSTRZYGNIĘTE | brak pomiaru przechyłu; to jeden obiekt, nie obraz | drgań przechyłu nikt nie podał; wymagane ≤ 0,15° | Liu 2026 |
| N. Stos reflektorów przełączanych napięciem (ciekły kryształ cholesteryczny, H-PDLC) | NIEROZSTRZYGNIĘTE | brak pomiaru stożka i tła | R\_on = 0,37–0,99; Δz = 0,1–0,7 mm; odbicia od elektrod ITO 0,5–2% na warstwę, a przy kryterium jakości „tło ≤ 1% sygnału” i R\_on = 0,37 dopuszczalne tło to 0,0037 łącznie | Chen 2019; Natarajan 1999 |
| A. Lustro Bragga z zimnych atomów w sieci 1D | NIEROZSTRZYGNIĘTE | brak pomiaru przy 1 mW; przesuwu z odbiciem nie pokazano | R\_max ≈ 0,8 przy N = 5·10⁷, L ≈ 3 mm (słaba sonda); transport w sieci na cm istnieje (Schmid 2006); szacunek dla atomów niezależnych przy 1 mW: 5·10⁷ × 1,21 pW = 61 µW, czyli 6% | Schilke 2011 |
| E. Pęsety optyczne jako piksele | NIEROZSTRZYGNIĘTE | tylko szacunek | piksel 10 × 10 µm: P ≤ N·ħω·Γ/8 = 344 × 1,21 pW = 0,42 nW dla atomów niezależnych; przy OD = 1 odstęp 0,54 µm < λ, czyli reżim kolektywny | rachunek T1 |
| F. Rozpraszanie kolektywne, lustro z warstwy 2D | NIEROZSTRZYGNIĘTE | brak demonstracji przy 1 mW i 1 s; bilans atomów niezależnych nie jest granicą | R = 0,58 przy \~200 węzłach i s ≈ 3·10⁻⁴, w kącie zbierania obiektywu; degradacja powyżej 70 fotonów na węzeł; przy 1 mW w wiązce 1 mm s ≈ 76 | Rui 2020 |
| H. Siatka gazowa zapisana laserem w powietrzu | NIEROZSTRZYGNIĘTE | brak pomiaru odbicia wstecz w wymaganej geometrii | 96% dotyczy dyfrakcji w transmisji przy 63 mJ/cm² UV, okno \~10 ns; podtrzymanie ciągłe \~MW (szacunek T8) | Michine & Yoneda 2020 |
| B. Selektywne odbicie od pary przy oknie | ODRZUCONE | strukturalnie: warstwa odbijająca to granica okna (\~0,12 µm) | kontrola in situ (komórka klinowa) przesuwa ją o ≤ 2 µm wobec 10 µm; mechaniczny przesuw okna wykluczony założeniem | Sautenkov 2024; Keaveney 2012 |
| C1. Siatki multipleksowane we wspólnej objętości | ODRZUCONE | strukturalnie: wszystkie siatki w tej samej objętości | Δz = 0 przy zmianie kanału; limit M ≤ 3,16·M/# ≈ 133 | Mok 1996; Dhar 1999 |
| D. Metapowierzchnia (ognisko w z) | ODRZUCONE | z definicji: w z nie ma materii | płaszczyzna odbicia (metapowierzchnia) nieruchoma | Khorasaninejad 2016; Arbabi 2018 |
| J. Cząstka w pułapce fotoforetycznej | ODRZUCONE | górna granica ze zmierzonej mocy całkowitej | moc rozproszona w 4π szacowana przez autorów na rząd nW przy wiązkach 15–30 mW, czyli ≤ \~10⁻⁷ mocy; stożek < 1° to jej część | Rogers 2019; Smalley 2018 |
| K. Mikrohologramy wielowarstwowe (adresowanie ogniskiem) | ODRZUCONE | strukturalnie (T2): stożek odbicia = apertura odczytu | stożek < 1° wymaga NA ≤ 0,0087, a wtedy głębia ostrości ≥ 14 mm; zademonstrowane układy: R ≤ 0,01, półkąt odczytu 9,2° | McLeod 2005; Ostroverkhov 2009 |

Linie rubidu (780 i 795 nm) leżą na granicy widzialności. Według funkcji CIE 1924 V(780 nm) = 1,5·10⁻⁵, więc 1 mW daje 1,0·10⁻⁵ lm. Przy 532 nm ta sama moc daje 0,60 lm. Mechanizmy A, B, F i G są więc dla oka praktycznie ciemne, niezależnie od R.

## Ograniczenia szczegółowe i ich zakres

Pięć ograniczeń eliminuje większość mechanizmów, ale każde obowiązuje tylko dla określonej klasy układów. Pierwsze wydanie przedstawiało je jako ogólne; audyt słusznie to zakwestionował. Żadne z nich nie jest twierdzeniem o niemożliwości.

**T1. Budżet fotonów, szacunek dla atomów niezależnych.** Atom dwupoziomowy rozprasza koherentnie najwyżej \~Γ/8 fotonów na sekundę, przy s = 1. Dla Rb D2 daje to 1,21 pW na atom.

```latex
N \ge \frac{0{,}1\,P_{\mathrm{in}}}{\hbar\omega\,\Gamma/8} = \frac{10^{-4}\ \mathrm{W}}{1{,}21\cdot 10^{-12}\ \mathrm{W}} = 8{,}2\cdot 10^{7}
```

Zakres: atomy niezależne. Dla piksela 10 × 10 µm przy OD = 1 (N = A/σ₀ = 344) daje to P ≤ 344 × 1,21 pW = 0,42 nW w całym 4π. W uporządkowanej warstwie odpowiedź jest kolektywna: zmieniają się jednocześnie szerokość rezonansu, amplituda, faza dipoli, rozkład kątowy promieniowania i nasycenie. Wynik 8,2·10⁷ nie jest więc granicą dla takiej warstwy, a samej szerokości Γ\_kol nie wolno użyć jako prostego mnożnika. Pomiar R = 0,58 (Rui i in. 2020) pokazuje tę kolektywność, ale przy s ≈ 3·10⁻⁴, bez demonstracji przy 1 mW i 1 s. Przy OD = 1 w pikselu odstęp atomów wynosi 0,54 µm < λ, więc i rachunek dla E jest tylko szacunkiem.

**T2. Ognisko kontra głębokość woksla.** Woksel utworzony przez ognisko ma głębokość równą głębi ostrości 2λ/NA². Stożek o pełnym kącie < 1° oznacza półkąt 0,5°.

```latex
\theta_{\mathrm{pełny}} < 1^\circ \Rightarrow \mathrm{NA} \le \sin 0{,}5^\circ = 0{,}0087 \Rightarrow \mathrm{DOF} \ge \frac{2\cdot 532\ \mathrm{nm}}{0{,}0087^2} = 14\ \mathrm{mm}
```

Zakres: tylko woksle definiowane przez ognisko (D, holograficzna soczewka w C1, mikrohologramy w K). Woksel o głębokości 10 µm wymaga NA ≥ 0,33. Nie dotyczy materii zlokalizowanej w z. Pierwsze wydania liczyły T2 dla półkąta 1° (DOF ≥ 3,5 mm), niezgodnie z T9.

**T3. Sprzężenie warstwy Bragga w obojętnym gazie.** Warstwa o grubości L i modulacji Δn odbija R = tanh²(πΔnL/λ).

```latex
R \ge 0{,}1 \iff \Delta n\, L \ge 0{,}1042\,\lambda = 55{,}5\ \mathrm{nm}\ \ (\lambda = 532\ \mathrm{nm})
```

Zakres: modulacja gęstości obojętnego, nierezonansowego gazu przy 1 atm, gdzie |Δn| ≤ n − 1 ≈ 2,8·10⁻⁴, więc L ≥ 198 µm. Nie dotyczy plazmy (wolne elektrony dają ujemne Δn, które może przekroczyć n − 1 powietrza) ani ośrodków rezonansowych. Zmierzone siatki gazowe mają 3–10 mm i są siatkami transmisyjnymi, nie zwierciadłami.

**T6. Surowe oszacowanie liczby kanałów kątowych.** Kanały rozdziela się w zmiennej q = cosθ wewnątrz bloku. Pierwsze zero listka leży przy Δq = λ/(2n₀L), a dostępny zakres przy n₀ = 1,5 to 0,255.

```latex
N_{\mathrm{ch}} \approx 0{,}255\cdot\frac{2 n_0 L}{\lambda} \approx 1{,}4\ \text{kanału na mikrometr grubości warstwy}
```

Zakres: oszacowanie bez interferencji między warstwami, wymaganej izolacji kanałów, apodyzacji i strat; nie jest fizycznym maksimum. Rachunek macierzy przejścia pokazuje, że interferencja zmienia R wybranego kanału o 9–22%, a przy n₁ = 0,03 odbicie poza kanałami sięga 49% najsłabszego kanału.

**T9. Stożek < 1° a widzenie obuoczne.** W odległości 30 cm stożek o pełnym kącie 1° daje plamkę 5,2 mm, a rozstaw oczu to \~63 mm. Zakres: warunek 1 sam nie zapewnia widzenia obuocznego, bo pojedynczy stożek wymusza małą aperturę kątową. Stereoskopię można odzyskać co najmniej dwiema niezależnymi wiązkami, po jednej na każde oko.

## C2 po audytach: stos siatek adresowanych kątem (tylko model)

W modelu 97–99% odbitej mocy pochodzi z wybranej warstwy, a R wewnątrz bloku wynosi 0,22–0,29 na kanał przy stałej barwie. Konstrukcja z warstwami co 10 µm leży jednak dokładnie na progu warunku 2 i w trzech z czterech przejść go nie osiąga. Bez powłoki AR stożek zawiera też nieprzesuwające się odbicie od powierzchni o mocy 23–84% sygnału. Warunki 3 i 4 nie są wykazane, a układ nie adresuje obrazu w x–y. Werdykt: NIEROZSTRZYGNIĘTE.

Model: blok o n₀ = 1,5, pięć niesłantowanych warstw po \~10 µm (całkowita liczba okresów: 55, 53, 51, 48, 46), λ₀ = 532 nm, polaryzacja s, pełna macierz przejścia, bez dyspersji materiałowej i absorpcji. Amplitudę n₁ = 0,008 wzięto z tabeli 3 pracy Bruder i in. 2017; te wartości dotyczą wariantów fotoinicjatora w badanej żywicy i nie są pomiarem Δn w stosie C2. Karta producenta podaje dla Bayfol HX200 Δn = 0,03 (według Blanche i in. 2020; samej karty nie pobrano). Przemiatanie n₁ niżej pokazuje, że 0,008 nie jest zachowawcze pod każdym względem.

Dwie różne wielkości, których nie wolno utożsamiać:

- **Położenie materii:** warstwa k zajmuje z konstrukcji przedział o grubości 9,90–10,05 µm. Środki warstw: 4,98 / 14,95 / 24,97 / 34,94 / 44,87 µm, kroki 9,97 / 10,02 / 9,97 / 9,92 µm. Odbicie powstaje w całej tej grubości (rozkładane sprzężenie w teorii fal sprzężonych), więc nie ma jednej płaszczyzny odbicia.
- **Efektywna głębokość odpowiedzi:** wielkość wyliczona z odpowiedzi optycznej, zależna od wybranej metryki. Poniżej dwie metryki: centroid osiowej odpowiedzi impulsowej μ\_k i głębokość z opóźnienia grupowego z\_gd.

Definicje metryk dla kanału k przy stałym kącie θ\_k:

```latex
h_k(z) = \sum_{\lambda} W(\lambda)\, r_k(\lambda)\, e^{-i\,2 k_0 n_0 \cos\theta_k\, z}, \qquad I_k(z) = |h_k(z)|^2
```

```latex
\mu_k = \frac{\int z\, I_k\, dz}{\int I_k\, dz}, \qquad C_{ij} = \frac{\int I_i I_j\, dz}{\sqrt{\int I_i^2\, dz \int I_j^2\, dz}}, \qquad H_{ij} = R_{\text{warstwa } i}(\theta_j)
```

W to okno Hanna w paśmie ±10 nm wokół λ₀; szerokość I\_k zależy od tego pasma, bo sonda monochromatyczna nie ma bramkowania osiowego. z\_gd = |dφ/dk₀|/(2n₀cosθ\_k) to grupowe położenie odbicia w modelu bez dyspersji; rzeczywisty pomiar OCT wymagałby uwzględnienia dyspersji i geometrii interferometru. FWHM\_k < |Δμ| oraz małe C\_ij to dodatkowe kryteria jakości, spoza pięciu warunków.

| Kanał | Kąt wewnętrzny | Kąt z powietrza | R w bloku (zbieżne) | Środek warstwy | μ\_k | FWHM\_k | z\_gd | Udział warstwy k (H) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 11,69° | 17,7° | 0,219 | 4,98 µm | 5,3 µm | 8,1 µm | 5,7 µm | 98,3% |
| 1 | 20,03° | 30,9° | 0,262 | 14,95 µm | 14,7 µm | 8,3 µm | 14,3 µm | 97,1% |
| 2 | 25,51° | 40,2° | 0,250 | 24,97 µm | 24,5 µm | 8,6 µm | 23,8 µm | 96,8% |
| 3 | 30,60° | 49,8° | 0,295 | 34,94 µm | 34,6 µm | 8,8 µm | 34,2 µm | 96,9% |
| 4 | 34,81° | 58,9° | 0,289 | 44,87 µm | 44,4 µm | 9,1 µm | 42,9 µm | 98,7% |

Kroki: środki warstw 9,97 / 10,02 / 9,97 / 9,92 µm, μ\_k 9,4 / 9,9 / 10,1 / 9,9 µm, z\_gd 8,6 / 9,5 / 10,4 / 8,8 µm; nakładanie sąsiadów C = 0,12–0,17. Konstrukcja ze skokiem równym progowi nie ma marginesu w żadnej z tych miar. Nie wykazano natomiast, że żadna wersja C2 nie może przekroczyć 10 µm.

Zbieżność (8, 16, 32 i 64 podwarstwy na okres): R rośnie o 4–5% względnie między 8 a 64 podwarstwami, a między 32 a 64 o ≤ 0,5%; tabela podaje wartości dla 64. Kroki μ\_k, FWHM\_k, z\_gd i udziały H zmieniają się o ≤ 0,05 µm (lub ≤ 0,1 punktu procentowego).

Macierz H\_ij (wiersz: warstwa i, kolumna: kąt kanału j; 16 podwarstw na okres) to rozkład niekoherentny. W sumie koherentnej interferencja zmienia R wybranego kanału o 9–22% względem samej warstwy.

| Warstwa \\ kąt | θ₀ | θ₁ | θ₂ | θ₃ | θ₄ |
| --- | --- | --- | --- | --- | --- |
| 0 | 0,1962 | 0,0025 | 0,0010 | 0,0004 | < 0,0001 |
| 1 | 0,0016 | 0,2119 | 0,0008 | 0,0014 | 0,0004 |
| 2 | 0,0013 | 0,0021 | 0,2216 | 0,0026 | 0,0015 |
| 3 | 0,0004 | 0,0013 | 0,0043 | 0,2416 | 0,0015 |
| 4 | < 0,0001 | 0,0004 | 0,0012 | 0,0034 | 0,2632 |

Przemiatanie n₁ (16 podwarstw na okres):

| n₁ | R kanałów w bloku | Kroki μ\_k \[µm\] | FWHM\_k \[µm\] | C sąsiadów | Udział warstwy k | Maks. R poza kanałami / najsłabszy kanał |
| --- | --- | --- | --- | --- | --- | --- |
| 0,004 | 0,061–0,086 | 9,4 / 9,9 / 10,1 / 9,8 | 8,2–9,3 | 0,13–0,19 | 97–99% | 9,0% |
| 0,008 | 0,216–0,292 | 9,4 / 9,9 / 10,1 / 9,9 | 8,1–9,1 | 0,12–0,17 | 97–99% | 9,4% |
| 0,012 | 0,408–0,520 | 9,3 / 9,9 / 10,0 / 9,9 | 8,0–8,9 | 0,11–0,16 | 96–99% | 9,7% |
| 0,020 | 0,724–0,827 | 9,4 / 9,9 / 9,9 / 9,9 | 7,6–8,6 | 0,08–0,13 | 95–98% | 19,1% |
| 0,030 | 0,912–0,958 | 9,6 / 10,0 / 9,9 / 9,9 | 6,5–8,3 | 0,06–0,11 | 92–96% | 49,3% |

Zmiana n₁ nie naprawia warunku 2, bo kroki wyznacza skok warstw, nie modulacja. R ≥ 0,1 wymaga n₁ ≳ 0,005. Wyższe n₁ podnosi R, ale też odbicie poza kanałami (49% najsłabszego kanału przy 0,03) i obniża udział wybranej warstwy.

Interfejsy z powietrzem (polaryzacja s, bez powłoki AR, grube podłoże, sumowanie niekoherentne):

| Kanał | Kąt z powietrza | Fresnel R\_s jednej powierzchni | Sygnał (1 − R\_s)²·R | Tło z powierzchni | Tło / sygnał |
| --- | --- | --- | --- | --- | --- |
| 0 | 17,7° | 0,045 | 0,197 | 0,045 | 23% |
| 1 | 30,9° | 0,059 | 0,230 | 0,059 | 26% |
| 2 | 40,2° | 0,078 | 0,211 | 0,078 | 37% |
| 3 | 49,8° | 0,111 | 0,231 | 0,111 | 48% |
| 4 | 58,9° | 0,167 | 0,199 | 0,167 | 84% |

Tło z przedniej powierzchni leży w tym samym kierunku zwierciadlanym co sygnał, ale na stałym z. Dla cienkiej, swobodnej warstwy 50 µm interferencja koherentna z powierzchniami zmienia R do 0,19–0,40. Wymagana jest więc powłoka AR działająca dla polaryzacji s w zakresie 17,7–58,9°.

Sprawdzenie warunków:

- **1, niepełne.** R w bloku 0,22–0,29 i \~0,20–0,23 po przejściu przez powierzchnię bez AR, w jednowymiarowym modelu fal płaskich. Mocy w stożku < 1° nie policzono: brak skończonej apertury, chropowatości, rozpraszania i zniekształceń frontu.
- **2, na progu, w trzech z czterech przejść poniżej.** Zarówno materia, jak i obie metryki efektywnej głębokości przesuwają się o około 10 µm bez marginesu.
- **3, niepoliczone.** Brak modelu detektora; 0,2 mW przy 532 nm daje tylko idealny limit szumu śrutowego.
- **4, niewykazane.** Źródło pierwszego wydania (Curtis & Psaltis 1994) dotyczy filmu transmisyjnego HRF-150 i pokazuje w odczycie wybielanie; trwałość C2 nie została wykazana, co nie znaczy, że wykazano jej brak.
- **Adresowanie x–y, brak.** Kąt wybiera warstwę, nie piksel. Z modulatorem przestrzennym budżet woksla to P\_woksel = P\_in · T\_optyka · T\_SLM · R\_C2 · η\_stożek, więc R\_C2 ≈ 0,2 nie oznacza 20% sprawności wyświetlacza. Test: dwa woksle naraz w różnych (x, y, z).

Wykonalność (poza modelem): model zakłada pięć warstw po \~10 µm bez szczelin. Handlowy Bayfol HX200 ma warstwę 16 µm (Blanche i in. 2020), a zapis interferencyjny w materiale liniowym obejmuje całą grubość. Stos wymagałby więc cieńszych warstw nagranych osobno i zlaminowanych. Nie modelowano kleju i jego indeksu, skurczu i przesunięcia widmowego po utrwaleniu, dyfuzji między warstwami ani błędów orientacji siatek.

Scenariusz modelowy laminatu: przekładki 51 µm (grubość zmierzona w innym układzie, Shams Lahijani i in. 2023) o założonym n = 1,48, bez kleju i absorpcji. Daje R = 0,25–0,31, kroki μ\_k 58–59 µm, FWHM 8,2–8,9 µm i C = 0,012–0,014. Warunek 2 przechodzi w tym modelu z marginesem, ale to scenariusz, nie opis rzeczywistego laminatu.

Wniosek: C2 jest interesującą hipotezą modelową. Wymaga eksperymentalnego wykazania osiowej separacji, sprawności w stożku < 1°, SNR, trwałości i przede wszystkim niezależnego adresowania x–y.

## Jak daleko od warunku 1

&#91;embedded content: Liczby z tabeli wyników oraz skryptów obliczenia.py i tmm\_stos\_siatek.py · 10 mechanizmów; A i E pominięte, bo nie oceniano ich przy 1 mW\]

Wykres pokazuje tylko warunek 1, nie werdykty. Szacunki dla F i H oraz zmierzona moc całkowita dla J leżą od \~5·10⁴ do \~3·10⁶ razy poniżej progu; z nich tylko J jest górnym ograniczeniem. Puste kółka to kandydaci bez pomiaru przy 1 mW, w tym C2, który ma tylko wynik modelu. Metapowierzchnia (D) i selektywne odbicie (B) przekraczają próg, ale padają na warunku 2.

## Czego nie dowiedziono

Referat nie wykazał, że którykolwiek mechanizm spełnia pięć warunków naraz, ani pomiarem, ani rachunkiem. Nie wykazał też, że jasny, adresowalny obraz 3D w powietrzu jest niemożliwy. Wykluczył liczbowo konkretne mechanizmy przy konkretnych założeniach.

- **Pięć warunków nie koduje obrazu 3D w powietrzu.** Dosłownie spełnia je zwykłe lustro na stoliku piezo; dlatego referat wyklucza mechaniczny przesuw stałego reflektora. Ewentualne „spełnienie pięciu warunków” nie byłoby jeszcze wyświetlaczem.
- **C2 to model wielopłaszczyznowego reflektora, nie wyświetlacza.** Brakuje adresowania x–y, pomiaru stosu, policzonego SNR detektora i dowodu trwałości materiału. Wersja z warstwami co 10 µm leży na progu warunku 2; inne wersje nie zostały wykluczone.
- **„Efektywna głębokość odpowiedzi” to nie płaszczyzna materii.** W grubej siatce odbicie powstaje w całej warstwie; μ\_k i z\_gd różnią się od siebie i od środka warstwy o do \~1,5 µm.
- **A, E, F i H nie są fizycznie wykluczone.** Ich wcześniejsze odrzucenia opierały się na szacunkach dla atomów niezależnych albo na braku pomiaru w wymaganej geometrii.
- **Ograniczenia T1–T3 mają zakres.** T1 dotyczy atomów niezależnych, T2 woksli ogniskowych, T3 obojętnego gazu bez rezonansu.
- **Warunek 1 sam nie zapewnia widzenia obuocznego (T9).** Pojedynczy stożek < 1° trafia do jednego oka; stereoskopia wymaga co najmniej dwóch niezależnych wiązek.
- **J+ to jeden obiekt.** Nawet przy drganiach ≤ 0,15° jedno lewitowane lusterko nie tworzy obrazu; potrzebne byłyby liczne, niezależnie sterowane elementy.

## Korekty

Pięć błędów wykrył recenzent w trakcie pracy, szesnaście pierwszy audyt zewnętrzny, dziewiętnaście poprawek wprowadził drugi audyt (druga tabela), a szesnaście trzeci (trzecia tabela). Zarzuty źródłowe sprawdzono w pełnych tekstach prac: Curtis & Psaltis 1994, Bruder i in. 2017, Bajcsy i in. 2003 (wersja arXiv), Blanche i in. 2020, Rui i in. 2020 (wersja arXiv) oraz Michine & Yoneda 2020.

| Co | Było | Jest | Skutek dla werdyktu | Wykrył |
| --- | --- | --- | --- | --- |
| Werdykt C2 | POTWIERDZONE rachunkiem | NIEROZSTRZYGNIĘTE, tylko model | zmieniony lead i wnioski | audyt |
| Kroki płaszczyzny w C2 | „9,7–10,6 µm” | z₅₀: 9,7 / 10,1 / 10,6 / 9,4 µm; z opóźnienia grupowego: 8,6 / 9,5 / 10,3 / 8,8 µm | warunek 2 pada dla wersji 10 µm | audyt |
| z₅₀ jako „płaszczyzna odbicia” | płaszczyzna | metryka nieodporna; zastąpiona głębokością z opóźnienia grupowego | jak wyżej | audyt |
| Warunek 3 w C2 | „SNR \~2·10⁷” | tylko idealny limit szumu śrutowego; SNR detektora niepoliczony | warunek 3 niewykazany | audyt |
| Warunek 4 w C2 | Curtis & Psaltis 1994 jako dowód | film transmisyjny HRF-150; w odczycie zachodzi wybielanie | warunek 4 niewykazany | audyt, potwierdzone w tekście pracy |
| n₁ = 0,008 | „zmierzona górna granica Bayfol HX w odbiciu” | wartość z tab. 3 dla wariantów fotoinicjatora w żywicy; założenie zachowawcze | liczby bez zmian | audyt, potwierdzone w tekście pracy |
| Laminat ze skokiem \~66 µm | „nadal spełnia warunek 2” bez rachunku | policzony: kroki 51–60 µm przy n przekładki = 1,48 (założenie) | nowa hipoteza modelowa | audyt |
| R = 0,22–0,29 w C2 | utożsamione z mocą w stożku < 1° | R całkowite w modelu 1D; moc w stożku niepoliczona | warunek 1 niepełny | audyt |
| Przesłuch w C2 | „0,020” bez odniesienia | 9,4% najsłabszego kanału; inne warstwy 0,7–5,0% sygnału; interferencja zmienia R o 9–22% | brak | audyt |
| T1, T2, T3 | ograniczenia ogólne | ograniczenia z podanym zakresem | brak | audyt |
| E: pole 1 mm² | traktowane jak dana | pochodzi z punktu startowego; argument oparty na budżecie mocy przy 1 mW | werdykt bez zmian, inne uzasadnienie | audyt |
| F: „rekord 1500 atomów” | jak granica | stan techniki; brak demonstracji przy 1 mW | werdykt bez zmian, inne uzasadnienie | audyt |
| H | „odbicie” | dyfrakcja w transmisji | brak | audyt |
| J+ | tylko brak pomiaru przechyłu | także: jeden obiekt to nie obraz | brak | audyt |
| Liczba odrzuconych | 8 | 9 | brak | audyt |
| Liczba iteracji | 11, „każda jeden mechanizm” | 12 iteracji (0–11) dla 13 mechanizmów | brak | audyt |
| Atomy dla OD = 1 na 1 mm² (punkt startowy) | \~3·10⁹ | A/σ₀ = 3,4·10⁶ | brak | recenzent |
| Odczyt warunku 2 (iteracje 1–2) | rozróżnialny woksel 10 µm | przesunięcie płaszczyzny odbicia o ≥ 10 µm | werdykty C1 i D bez zmian | recenzent |
| Zhou i in. 2018 jako dowód C2 | dwie warstwy adresowane kątem | dwa elementy HOE o różnych funkcjach w okularach AR | C2 bez pomiaru | recenzent |
| DOI pracy Michine & Yoneda 2020 | …-0286-1 | 10.1038/s42005-020-0286-6 | brak | recenzent |
| Cytowanie Ling, Li, Xiao | PRA 57, 1014 | PRA 57, 1338 (1998) | brak | recenzent |

Drugi audyt zewnętrzny:

| Co | Było | Jest |
| --- | --- | --- |
| Lead | „ani pomiarem, ani rachunkiem” | „na podstawie dostępnych danych literaturowych i przedstawionych rachunków” |
| E: „≤ 0,4 nW odbite” | liczba bez równania | P ≤ N·ħω·Γ/8 = 344 × 1,21 pW = 0,42 nW w 4π; szacunek dla atomów niezależnych, a przy OD = 1 odstęp 0,54 µm < λ |
| T1 i F: Γ\_kol | mnożnik budżetu („czynnik rzędu jedności”) | kolektywność zmienia bilans; 8,2·10⁷ nie jest granicą dla uporządkowanej warstwy |
| z\_gd w C2 | „to, co zmierzyłby OCT” | grupowe położenie odbicia w modelu bez dyspersji; OCT wymaga uwzględnienia dyspersji i geometrii |
| Pojedyncza warstwa | „w swoim środku” | blisko środka geometrycznego, \~0,4 µm przed nim |
| Rozdzielenie płaszczyzn | bez formalnej definicji | μ\_k, FWHM\_k, C\_ij i macierz H\_ij; kroki μ 9,4 / 9,9 / 10,1 / 9,9 µm |
| Margines progu 10 µm | niejasny | z\_gd stabilne numerycznie do 0,01 µm, metryki różnią się o ≤ 1,5 µm: brak marginesu; inne wersje C2 niewykluczone |
| Przesłuch 0,020 | 9,4% najsłabszego kanału | 0,0202 / 0,2164 = 9,3% |
| Próg przesłuchu ≤ 5% | wyglądał na warunek | dodatkowe kryterium jakości, spoza pięciu warunków |
| Δn = 0,03 producenta | bez źródła | karta Covestro cytowana przez Blanche i in. 2020; samej karty nie pobrano |
| Bruder 2017 | — | dopisano, że wartości z tabeli nie są pomiarem Δn w stosie C2 |
| Przekładki 51 µm | „wariant laminatu” | scenariusz modelowy; grubość pochodzi z innego układu |
| G | „siatka Bragga indukowana optycznie”, bez miejsca w pracy | zwierciadło Bragga z modulacji absorpcji EIT; R \~0,8 na rys. 2B, krzywa (ii), pomiar CW, sonda 250 µW |
| H | sama liczba 2,5·10⁻⁶ | pomiaru odbicia wstecz ≥ 10% brak; 96% dotyczy dyfrakcji w transmisji |
| T9 | „każdy woksel widzi jedno oko” | pojedynczy stożek nie zapewnia widzenia obuocznego; dwie wiązki mogą |
| „Odbicie od materii w z” | definicja domyślna | jawna, jako wybór definicji problemu |
| Zdanie o „przełomie” | było | usunięte |
| Opis metody | „dziesięciu agentów” | ścieżki wyszukiwania wspomagane AI, weryfikacja w źródłach pierwotnych |
| Test x–y | jeden woksel | dwa woksle w różnych (x, y, z) naraz |

Trzeci audyt zewnętrzny:

| Co | Było | Jest |
| --- | --- | --- |
| Stożek < 1° | T2 liczone dla półkąta 1°, T9 dla pełnego kąta | wszędzie pełny kąt 1° (półkąt 0,5°); T2: DOF ≥ 14 mm zamiast 3,5 mm |
| „Płaszczyzna odbicia” w C2 | centroid i z\_gd jako płaszczyzna | osobno położenie materii (kroki 9,92–10,02 µm) i efektywna głębokość odpowiedzi |
| Interfejsy z powietrzem | pominięte | Fresnel R\_s 0,045–0,167; tło z powierzchni 23–84% sygnału bez AR |
| Zbieżność TMM | tylko z\_gd przy 16 i 32 podwarstwach | 8 / 16 / 32 / 64 podwarstwy dla R, μ, FWHM, z\_gd i H; R podane dla 64 |
| n₁ = 0,008 „zachowawcze” | twierdzenie bez rachunku | przemiatanie 0,004–0,03: kroki bez zmian, przesłuch rośnie do 49% |
| Sonda 1 mW | moc bez pola wiązki | 1 mW na Ø 1 mm, 127 mW/cm², s ≈ 76 dla Rb |
| A | ODRZUCONE (z skwantowane okresem sieci) | NIEROZSTRZYGNIĘTE: transport w sieci na cm istnieje, brak pomiaru z odbiciem i przy 1 mW |
| E | ODRZUCONE | NIEROZSTRZYGNIĘTE: tylko szacunek dla atomów niezależnych |
| F | ODRZUCONE | NIEROZSTRZYGNIĘTE: bilans atomów niezależnych nie jest granicą |
| H | ODRZUCONE | NIEROZSTRZYGNIĘTE: brak pomiaru w wymaganej geometrii |
| J, K, B | uzasadnienie bez rodzaju ograniczenia | J: moc całkowita \~nW; K: T2; B: strukturalnie, przy wykluczeniu przesuwu mechanicznego |
| N: „≤ 10⁻⁴” | liczba niezgodna z kryterium „tło ≤ 1%” | tło ≤ 0,0037 łącznie przy R\_on = 0,37; to kryterium jakości, spoza pięciu warunków |
| Warunki 3 i 4 | nieoperacyjne | proponowane doprecyzowanie (czas integracji, detektor, tolerancje) |
| Warunek 5 | równanie traktowane jak dowód | rozróżnienie: „spełnia w modelu” kontra POTWIERDZONE (pomiar) |
| Weryfikacja liczb | „sprawdzone w źródłach albo w Crossref” | sześć prac sprawdzonych w pełnym tekście; Crossref tylko dane bibliograficzne |
| Założenie o przesuwie | niejawne | jawne: wykluczony mechaniczny przesuw stałego reflektora (lustro na piezo spełniałoby warunki 1–5) |

## Otwarte pytania rozstrzygalne pomiarem lub rachunkiem

Pięć zadań rozstrzygnie werdykty, które dziś są otwarte. Każde ma próg sukcesu zapisany przed pomiarem.

- [ ] **C2, rzeczywisty laminat.** Najpierw model z prawdziwymi warstwami (podłoże, klej i indeksy z kart materiałowych) i skokiem warstw z marginesem ponad 10 µm. Potem pomiar 2–5 osobno nagranych warstw przy 532 nm i 1 mW, z powłoką antyrefleksyjną dla polaryzacji s w zakresie 17,7–58,9°: moc w stożku < 1° na zdefiniowanym detektorze w 30 cm, głębokość odbicia (np. OCT z korektą dyspersji) i zmiana sprawności po 1 s odczytu. Sukces według pięciu warunków: ≥ 10% mocy w stożku, kroki centroidów ≥ 10 µm, brak zmiany sprawności. Dodatkowe kryterium jakości, spoza pięciu warunków: przesłuch ≤ 5% sygnału.
- [ ] **C2, adresowanie x–y.** Określić mechanizm (x, y) → amplituda odbicia, np. modulator przestrzenny na wejściu. Test: dwa woksle naraz w różnych (x₁, y₁, z₁) i (x₂, y₂, z₂); sprawdzić, czy nie odbija cała warstwa, i przeliczyć budżet mocy, przesłuch i stożek.
- [ ] **J+, lusterko lewitowane.** W układzie Liu i in. 2026 zmierzyć dźwignią optyczną (ekran w 1 m) rms przechyłu w ciągu 1 s. Sukces: ≤ 0,15°, także po przesunięciu lusterka w z o ≥ 10 µm.
- [ ] **G, zwierciadło EIT w parze Rb.** W układzie Bajcsy i in. zmierzyć R przy sondzie 0,25 → 1 mW i sprzężeniu 40 mW na wiązkę. Sukces: R ≥ 0,1 przy 1 mW.
- [ ] **N, stos przełączalny.** Dla dwóch warstw cholesterycznych zmierzyć stożek odbicia oraz tło odbite od elektrod i warstw wyłączonych. Sukces: ≥ 10% mocy w stożku < 1° i tło ≤ 1% sygnału.

## Aneks C2-Laminat: hipotezy wdrożeniowe (iteracje 15–26)

Aneks rozwija C2 w stronę wyświetlacza. Wszystkie wyniki to modele (macierz przejścia, teoria Kogelnika, RCWA) bez pomiaru, więc werdykty z sekcji Wyniki się nie zmieniają. Najważniejszy wniosek: z siatkami niesłantowanymi każda warstwa świeci w innym kierunku. Siatki skośne kierują warstwy do jednego widza, ale górna warstwa odbija wyjście dolnej, jeśli oba wychodzą w tym samym kierunku (iteracja 17). Odchylenie usuwające to cieniowanie (≥ 0,75° na warstwę) przekracza kąt źrenicy widzianej z 30 cm (0,67°), więc przy L = 100 µm jedno oko widzi najwyżej trzy warstwy po ≥ 10% (iteracja 18).

### Iteracja 15: polaryzacja p, kąt Brewstera i tolerancja SLM

Polaryzacja p usuwa tło z powierzchni bez powłoki AR, ale wymaga wyższej modulacji n₁ ≈ 0,02. W p sprzężenie siatki niesłantowanej maleje jak |cos 2θ|, czyli do 0,385 przy wewnętrznym kącie Brewstera 33,7°. Centrowanie kanałów na Brewsterze nie jest potrzebne: przy pierwotnych kątach R\_p ≤ 3,5% dla 17,7–58,9°.

| Wariant (macierz przejścia, pojedyncza λ) | Sygnał po powierzchni | Tło z powierzchni / sygnał | Maks. R poza kanałami / najsłabszy kanał |
| --- | --- | --- | --- |
| pol. s, n₁ = 0,008 (pierwotny) | 0,20–0,23 | 23–84% | 8,6% |
| pol. p, n₁ = 0,008 | 0,04–0,18 | 2–20% | 23% |
| pol. p, n₁ = 0,02 | 0,23–0,63 | 0,4–5,5% | 18,5% |
| wachlarz wokół Brewstera, skok 0,03 w cosθ | — | — | 62–103% (kanały się zlewają) |
| wachlarz wokół Brewstera, skok 0,04, 4 kanały, pol. p, n₁ = 0,02 | 0,15–0,49 | 0–11,5% | 21% |
| laminat (przekładki 51 µm, n = 1,48 założone), pol. p, n₁ = 0,02 | 0,24–0,67 | 0,4–5,3% | inne warstwy 1,2–8,1% sygnału |

Laminat w polaryzacji p ma kroki efektywnej głębokości 59–60 µm, FWHM 7,7–9,2 µm i C = 0,009–0,012. Wartości R w tej tabeli dotyczą jednej długości fali; iteracja 16 pokazuje, że R przy stałej λ faluje o 36–64% międzyszczytowo, a średnie po λ wynoszą 0,21–0,64.

Tolerancja kątowa wiązki, np. po SLM (płaszczyzna padania, pol. s, n₁ = 0,008):

| Rozbieżność wiązki (półkąt 1/e²) | Sprawność Bragga / szczyt | Moc w stożku o pełnym kącie 1° |
| --- | --- | --- |
| 0,25° | 99–100% | \~100% |
| 0,5° | 96–99% | 86,5% |
| 1° | 89–96% | 39,3% |

Ogranicza stożek warunku 1, nie akceptacja siatki. Szczegół na warstwie musi mieć co najmniej λ/(2 sin 0,5°) = 30,5 µm (dla wiązki Gaussa 2w₀ ≥ 39 µm), co daje \~10⁵ woksli na cm².

Hipotezy:

- **H1, holografia bez „materia w z”: NIEROZSTRZYGNIĘTE (decyzja definicyjna).** Wiąże warunek 1, nie definicja materii. Przy stożku 1° woksel ogniskowy ma 74 µm szerokości i 14 mm głębokości, przy 12° (dwoje oczu w 30 cm) 6,2 µm i 0,097 mm. Obraz 1 cm przy 12° wymaga \~3930 × 3930 pikseli o skoku ≤ 2,54 µm.
- **H2, laminat + pol. p + SLM: NIEROZSTRZYGNIĘTE.** Najlepszy dotychczas model; brak pomiaru, warunków 3–4 i wykonalności laminatu.
- **H3, warstwa atomów z subradiacją: NIEROZSTRZYGNIĘTE.** Jeśli bilans skaluje się z Γ\_kol ≈ (3/4π)(λ/a)²·Γ, subradiacja go pogarsza (a = 532 nm: 0,51Γ, N ≈ 1,6·10⁸), a gęstsza sieć poprawia około dwukrotnie (a = 266 nm: 2,05Γ, N ≈ 4·10⁷).
- **H4, plazma w powietrzu: NIEROZSTRZYGNIĘTE, bardzo niekorzystne.** R ≥ 0,1 na 100 µm wymaga n\_e = 4,4·10¹⁸ cm⁻³ (17,5% cząsteczek), na 10 µm 175%. Siatka wsteczna o okresie 266 nm żyłaby \~0,2–1,8 ps przy założonej dyfuzji ambipolarnej 10–100 cm²/s.

### Iteracja 16: przekładki, kierunek wyjścia, siatki skośne, podwójna źrenica

Z siatkami niesłantowanymi każda warstwa odbija zwierciadlanie pod własnym kątem: −17,4°, −30,8°, −40,8°, −49,9° i −59,2° w powietrzu. Rozrzut 41,8° wobec stożka 1° oznacza, że widz w jednym miejscu widzi jedną warstwę. W tej geometrii C2, włącznie z kandydatem z iteracji 15, nie jest wyświetlaczem 3D. Siatki skośne, które kierują każdy kanał wzdłuż normalnej, usuwają ten problem w modelu.

**Przekładki makroskopowe** (macierz przejścia, pol. p, n₁ = 0,02, n przekładki 1,48):

| Przekładka | R średnie po λ (kanały 0–4) | Zafalowanie R przy stałej λ (międzyszczytowo / średnia) | Okres prążków w λ | Moc innych warstw / sygnał |
| --- | --- | --- | --- | --- |
| 51 µm | 0,24–0,71 | 36–64% | \~2,1 nm | 1,2–8,1% |
| 200 µm | 0,21–0,65 | — | \~0,53 nm | 1,1–6,1% |
| 500 µm | 0,21–0,64 | — | \~0,21 nm | 0,9–7,2% |
| 1000 µm | 0,21–0,64 | 42–62% | \~0,11 nm | 1,1–6,5% |

Przekładka nie prowadzi światła: całkowite odbicie na granicy 1,5 → 1,48 zachodzi dopiero powyżej 80,6° wewnątrz, a kanały mają 11,7–34,8°. Zafalowanie R jest jednak własnością koherentnego stosu i nie maleje z grubością przekładki; grubość zmienia tylko okres prążków, czyli czułość na dryf λ i temperatury. Stabilny obraz wymaga źródła o paśmie szerszym niż okres prążków albo stabilizacji termicznej. Moc z niewłaściwych warstw nie maleje z grubością przekładki (1–8% sygnału), bo to przesłuch kątowy, nie przestrzenny. Przy przekładkach 1 mm wiązka po odbiciu od najgłębszej warstwy przesuwa się bocznie o 5,6 mm, więc przy aperturze 10 mm zostaje 44% użytecznego pola.

**Siatki skośne** (teoria Kogelnika, wyjście wzdłuż normalnej, L = 10 µm, okres 178–186 nm, skos 5,7–17,5°):

- sprawność η = 0,62–0,68 w pol. p przy n₁ = 0,02, bo współczynnik polaryzacyjny to |cosθ| = 0,82–0,98 zamiast |cos 2θ|;
- światło z niewłaściwej, sąsiedniej siatki wychodzi pod kątem 5,3–12,3° od normalnej, czyli poza stożkiem widza;
- odbicie od powierzchni idzie w kierunku zwierciadlanym wejścia, nie do widza;
- szerokość akceptacji kątowej maleje jak 1/L: 10,6° / 3,5° / 1,0° w powietrzu dla L = 10 / 30 / 100 µm przy stałym n₁·L. Warstwy \~100 µm (n₁ ≈ 0,002) pozwalają upakować kanały co \~2°, co ułatwia skanowanie deflektorem akustooptycznym.

**Podwójna źrenica** (dwie siatki ±6° w powietrzu, ±4,0° wewnątrz, Kogelnik z symetrycznym sprzężeniem trzech fal): podział Δn = 0,03 na dwie siatki po 0,015 daje łącznie 0,70 (L = 10 µm) albo 0,92 (L = 16 µm) w pol. p, czyli 0,35 albo 0,46 na oko. Jedna siatka n₁ = 0,03 daje 0,88 albo 0,98. Obie wiązki wychodzą z tego samego fizycznego woksla, więc dysparycja odpowiada prawdziwej głębokości. Każde oko musi jednak trafić w plamkę 5,2 mm w 30 cm, więc pole widzenia głowy jest bardzo małe. Model zakłada zapis sekwencyjny (bez siatki krzyżowej) i liniową odpowiedź materiału.

**Bilans czasowy** (deflektor akustooptyczny 80%, SLM 60%, R = 0,4, 5 warstw sekwencyjnie): 38,4 µW średnio na warstwę, z czego 33,2 µW w stożku przy rozbieżności 0,5°. To \~8,9·10¹³ fotonów/s i graniczny SNR szumu śrutowego \~10⁷ w 1 s. Przy 10³ wokslach na warstwie wypada 33 nW na woksel, więc warunek 3 nie jest tu ograniczeniem. Ograniczeniami są:

- tempo SLM, 5 × 60 = 300 wzorów/s;
- étendue deflektora: iloczyn apertury i zakresu skanowania jest stały, więc duży rozrzut kątów kanałów zmniejsza pole obrazu;
- bezpieczeństwo oka, bo wiązka trafia prosto do źrenicy (do sprawdzenia według IEC 60825-1).

**Przekaźnik osiowy 4f** (M\_z = M\_x², kąt maleje jak 1/M\_x): rozciągnięcie skoku 60 µm do 30 mm (M\_z = 500) zmniejsza półkąt stożka z 0,5° do 0,022°. Plamka w 30 cm ma wtedy 0,23 mm wobec źrenicy 3–4 mm, więc oko traci wskazówkę akomodacji (efekt otworkowy), a szczegół 30 µm rośnie do 0,67 mm. Przy stożku 1° i źrenicy \~3,5 mm w 30 cm akomodacja przetrwa tylko M\_z ≲ 2.

Werdykty iteracji 16:

- **1A, przekładki makroskopowe: NIEROZSTRZYGNIĘTE.** Głębia rośnie bez utraty średniej sprawności, ale pojawia się koherentne zafalowanie 36–64% i winietowanie.
- **1B, przekaźnik 4f: ODRZUCONE** jako sposób na postrzegalną głębię. Niezmiennik Lagrange’a wiąże M\_z z M\_θ⁻²; założenie: źrenica \~3,5 mm.
- **2, podwójna źrenica: NIEROZSTRZYGNIĘTE.** Model daje 0,35–0,46 na oko, ale pole widzenia głowy to dwie plamki po 5,2 mm.
- **3, superradiacja: NIEROZSTRZYGNIĘTE.** Lustro Rui i in. jest subradiacyjne (zmierzone Γ = 4,04 MHz wobec Γ₀ = 6,06 MHz), a superradiacja w warstwie wymaga a < 0,49λ ≈ 381 nm i daje około dwukrotny zysk przy a = 266 nm.
- **4, deflektor + SLM: NIEROZSTRZYGNIĘTE.** SNR wystarcza z zapasem; ogranicza tempo SLM i étendue deflektora.
- **C2 z siatkami skośnymi (nowy wariant): NIEROZSTRZYGNIĘTE.** Najlepszy kierunek modelowy, ale tylko w teorii Kogelnika (pojedyncze siatki, bez interferencji między warstwami).

Następne pytanie: czy pełny rachunek dla dwóch skośnych warstw grubości \~100 µm (n₁ ≈ 0,002) z przekładką \~1 cm, np. metodą RCWA, potwierdza wyjście obu kanałów wzdłuż normalnej z ≥ 10% mocy w stożku 1° i przesłuchem w stożku widza ≤ 1%?

### Iteracja 17: RCWA dwóch i trzech warstw skośnych

Iteracja 16 opierała się na teorii Kogelnika dla pojedynczych siatek. Tu stos policzono rygorystyczną analizą fal sprzężonych (RCWA; Moharam i in., JOSA A 12, 1068, 1995; metoda „enhanced transmittance”, dla polaryzacji p z regułą odwrotności Li) we własnym skrypcie rcwa.py. Walidacja (rcwa\_walidacja.py): profil zależny tylko od z daje to samo co macierz przejścia (s 0,21502; p 0,13444), siatka skośna 20° → normalna zgadza się z Kogelnikiem (p: 0,6654 wobec 0,6659), R + T = 1 z dokładnością 10⁻⁶, wynik nie zależy od liczby rzędów (M = 3/5/7), a 32 plastry na okres dają błąd \~0,1%.

Parametry z polecenia: L = 100 µm, n₁ = 0,002, n₀ = 1,5, λ₀ = 532 nm, polaryzacja p, przekładka 10 mm o n = 1,48. Warstwa A przyjmuje wiązkę pod 20° wewnątrz (30,87° w powietrzu), warstwa B pod 22° (34,19°). Warstwy łączono niekoherentnie, bo różnica dróg przez przekładkę wynosi 2·1,48·10 mm ≈ 29,6 mm.

**Sprawność i wyższe rzędy.** Każda warstwa osobno kieruje do zadanego wyjścia η = 0,665 (A) i 0,660 (B). Wszystkie pozostałe rzędy odbite niosą ≤ 3·10⁻⁷ mocy, w tym jeden uwięziony przez całkowite wewnętrzne odbicie.

**Cieniowanie.** Z zasady wzajemności górna siatka jest dopasowana Bragga także do wiązki biegnącej w górę wzdłuż normalnej. Gdy oba kanały wychodzą wzdłuż normalnej, warstwa A odbija z powrotem w dół 66,5% wyjścia B i przepuszcza 33,5%. Akceptacja tego „portu” jest wąska: przepuszczalność rośnie do 0,64 / 0,96 / 0,97 przy odchyleniu wyjścia B o 0,5 / 0,75 / 1,0° w powietrzu. Przy N warstwach z wyjściem na normalnej dolny kanał dostaje około 0,62·0,335^(N−1), więc już trzecia warstwa spada poniżej 10%.

**Bilans kanałów** (moc sondy w stożku 1° u widza, z odbiciami Fresnela na powierzchniach; linia wąska / źródło gaussowskie o szerokości 1,5 nm; iteracja17b.py):

| Stos (wyjścia w powietrzu) | Kanał 1 | Kanał 2 | Kanał 3 | Obce światło w stożku ±0,5° |
| --- | --- | --- | --- | --- |
| 0° / 0° (z polecenia) | 0,623 / 0,391 | 0,206 / 0,172 | — | 0; najbliższe 2,8° od wyjścia |
| 0° / 1° | 0,623 / 0,391 | 0,597 / 0,359 | — | 0; najbliższe 1,7–1,8° |
| 0° / 2° | 0,623 / 0,391 | 0,599 / 0,381 | — | 0; najbliższe 0,7–0,8° |
| 0° / 3° | 0,623 / 0,391 | 0,608 / 0,381 | — | 0,39–0,72% mocy sondy |
| 0° / 2° / 4° | 0,623 / 0,391 | 0,599 / 0,381 | 0,602 / 0,376 | 0; najbliższe 0,68–0,76° |
| 0° / 3° / 6° | 0,623 / 0,391 | 0,608 / 0,381 | 0,594 / 0,374 | 0,59–0,72% mocy sondy |

Przy odchyleniu 3° odbicie warstwy A dla kąta wejścia kanału 2 (wychodzące pod 2,8°) wpada w stożek wyjścia kanału 2, stąd przesłuch. Okno działania to odchylenie 1–2° na warstwę. Przesłuch liczono jako górne oszacowanie (pełna transmisja warstw nad warstwą odbijającą) przy λ₀ i λ₀ ± 1,5 nm.

**Widmo i źródło 1,5 nm.** Szerokość połówkowa widma odbicia warstwy A wynosi 1,20 nm (proste oszacowanie λ²/(2nL) daje 0,94 nm). Uśrednienie po źródle gaussowskim daje η = 0,630 / 0,524 / 0,417 / 0,340 dla szerokości 0,5 / 1,0 / 1,5 / 2,0 nm, czyli 95 / 79 / 63 / 51% szczytu. Argument „L < L\_c, więc brak strat” nie działa: straty wyznacza stosunek szerokości widma źródła do szerokości widma siatki, a nie grubość warstwy wobec drogi koherencji. Prążki przekładki zanikają już przy znacznie węższym źródle. Widoczność dla widma gaussowskiego wynosi

```latex
V = \exp\!\left[-\frac{(\pi\,\mathrm{OPD}\,\Delta\lambda/\lambda^2)^2}{4\ln 2}\right]
```

i przy OPD = 29,6 mm daje V = 0,02 dla Δλ = 0,01 nm, 2·10⁻⁷ dla 0,02 nm i praktycznie zero dla 1,5 nm. W geometrii skośnej wiązki kanałów są też rozsunięte kątowo (≥ 0,7°) i bocznie (walk-off w przekładce 10 mm·tan 22,3° = 4,1 mm), więc koherentne tło w stożku sygnału wymaga dwóch odbić Fresnela (≲ 2·10⁻⁴ sygnału bez powłok AR).

**Śledzenie źrenicy.** Zmiana kąta wejścia o +0,25 / 0,5 / 1 / 2 / 5° w powietrzu daje η = 0,62 / 0,45 / 0,0002 / 0,004 / 0,002. Użyteczny zakres to ±0,5°, czyli przesunięcie plamki o ±2,2 mm w odległości 30 cm, a nie o kilka centymetrów. Szerszy zakres daje tylko cieńsza warstwa (akceptacja 10,6° przy L = 10 µm, iteracja 16), kosztem selektywności, od której zależy liczba kanałów.

**Bezpieczeństwo oka.** Wyjście jest skolimowane, więc cała moc kanału (0,39–0,62 mW przy sondzie 1 mW) może wejść w źrenicę. Wzór 7·10⁻⁴·C6·T2^(−0,25) W z C6 = 1 i T2 = 10 s daje AEL klasy 1 równe 0,39 mW, ale tekstu normy IEC 60825-1:2014 nie zweryfikowano. Margines 6× zachodzi tylko wtedy, gdy sonda oświetla woksele widoczne z jednej źrenicy przez nie więcej niż 10–17% czasu. Obraz statyczny w polu \~9 mm daje 1,0–1,6 AEL.

Werdykty iteracji 17:

- **Konfiguracja z polecenia (oba wyjścia wzdłuż normalnej, źródło 1,5 nm): NIEROZSTRZYGNIĘTE.** Oba kanały przekraczają 10% w stożku 1° (0,39 i 0,17) bez obcego światła w stożku, ale cieniowanie wyklucza trzecią warstwę.
- **Wyjścia odchylone o 1–2° na warstwę: NIEROZSTRZYGNIĘTE.** Trzy kanały po 0,376–0,391 przy 1,5 nm bez przesłuchu w stożku, ale każdy w innej pozycji oka (korekta w iteracji 18). To rachunek, nie pomiar; trwałość materiału (warunek 4) i modulacja n₁ = 0,002 w siatce skośnej 100 µm pozostają niezmierzone.
- **„L < L\_c, więc brak strat η”: ODRZUCONE** rachunkiem: źródło 1,5 nm obniża η do 63% szczytu.
- **Śledzenie źrenicy w zakresie kilku centymetrów deflektorem przy jednej siatce 100 µm: ODRZUCONE.** η < 0,004 przy odchyleniu ≥ 1° (górna granica z krzywej akceptacji).
- **Bezpieczeństwo oka z marginesem 6×: NIEROZSTRZYGNIĘTE.** Zależy od czasu oświetlenia w polu jednej źrenicy; normy nie sprawdzono.

Następne pytanie: ile warstw z wyjściami odchylonymi o 1–2° mieści się w polu wejścia (każda zużywa około 2° kąta wejścia wewnątrz), zanim przesłuch w stożku przekroczy 1%?

### Iteracja 18: źrenica widza a odchylone wyjścia

**Korekta iteracji 17.** Odchylenie wyjścia o 1–2° na warstwę usuwa cieniowanie, ale w odległości 30 cm wiązki z jednego punktu płyty rozchodzą się o 300·tan 1,5° = 7,9 mm na warstwę, a źrenica ma około 3,5 mm. Dla wyjść 0 / 1,5 / 3 / 4,5 / 6° plamki leżą w 0 / 7,9 / 15,7 / 23,6 / 31,5 mm, więc nieruchome oko widzi jedną warstwę z pięciu. Wniosek iteracji 17 o trzech kanałach dotyczył mocy w stożku, nie wspólnej źrenicy. Błąd wskazał audyt (skrypt iteracja18.py).

**Soczewka polowa.** Soczewka f = 300 mm z okiem w ognisku stawia plamki w x = f·tan α, czyli w tych samych 7,9 mm na 1,5°, bo zamienia kąt na położenie. Ogólnie dla dowolnego układu paraksjalnego płyta → źrenica położenie w źrenicy wynosi x\_p = A·x + B·α. Wszystkie warstwy z pola o szerokości W trafiają w źrenicę p tylko wtedy, gdy

```latex
|A|\,W + |B|\,\Theta \le p \quad\Rightarrow\quad D_{\mathrm{app}} = \frac{W}{\Omega} \le \frac{p}{\Theta}
```

gdzie Θ to wachlarz wyjść, a Ω kąt, pod którym oko widzi pole. Dla Θ = 6° obraz musi wyglądać jak z odległości ≤ 33 mm (okular, nie obraz w powietrzu), a przy D\_app = 300 mm wachlarz musi być ≤ 0,67° (0,48° przy wiązce 1 mm). Soczewka leży poza stosem, więc wyniki RCWA się nie zmieniają.

**RCWA pięciu warstw i stosów w jednej źrenicy** (wejścia 20–28° co 2°, L = 100 µm, n₁ = 0,002, pol. p; linia wąska, źródło 0,15 nm daje 99,5% tych wartości):

| Stos (wyjścia w powietrzu) | Moc w stożku 1°, kanały od góry | Obce światło w stożku | Warstwy w źrenicy 3,5 mm |
| --- | --- | --- | --- |
| 0 / 1,5 / 3 / 4,5 / 6° (z polecenia) | 0,623 / 0,607 / 0,605 / 0,582 / 0,584 | 0,72% mocy sondy (1,2% sygnału) | 1 z 5 |
| 0 / −1,5 / −3 / −4,5 / −6° | 0,623 / 0,597 / 0,612 / 0,617 / 0,624 | 0,99% mocy sondy | 1 z 5 |
| wszystkie 0° | 0,623 / 0,206 / 0,071 / 0,024 / 0,008 | 0 | 5 z 5 |
| 0 / 0,45° | 0,623 / 0,356 | 0 | 2 z 2 |
| 0 / 0,225 / 0,45° | 0,623 / 0,239 / 0,146 | 0 | 3 z 3 |
| 0 / 0,15 / 0,3 / 0,45° | 0,623 / 0,221 / 0,099 / 0,063 | 0 | 4 z 4 |

Pięć warstw z polecenia spełnia próg 10% w każdym kanale, ale przesłuch przekracza 1% sygnału, a każda warstwa trafia w inną pozycję oka. Przy L = 100 µm jedno oko w 30 cm widzi najwyżej trzy warstwy po ≥ 10%.

**Pojemność 16 warstw.** Wejście 8–38° wewnątrz to 12,0–67,4° w powietrzu. Od strony powietrza nie ma całkowitego wewnętrznego odbicia; zakres ogranicza Fresnel i czynnik p równy cos θ. Bez odchylenia wyjść dolny kanał dostaje około 0,62·0,335¹⁵ = 5·10⁻⁸, a z odchyleniem ≥ 0,75° na warstwę wachlarz ma 11°. Przy przekładkach 1 mm różnica dróg to 2,96 mm, więc źródło 0,02–0,05 nm nie gasi prążków (widoczność 0,86 i 0,38); gasi je dopiero 0,11–0,15 nm (0,009 i 1,6·10⁻⁴). Głębia 16 mm w 30 cm to Δ(1/z) = 0,169 D, czyli rozmycie 2,0′ przy źrenicy 3,5 mm, i około jedna głębia ostrości woksela w stożku 1° (T2: 14 mm). Wiązka skolimowana w ogóle nie daje bodźca akomodacji, bo najostrzejszy obraz powstaje przy ogniskowaniu na nieskończoność.

**Multipleksowanie azymutalne.** Model Kogelnika 3D zgadza się z RCWA dla odchylenia w płaszczyźnie siatki (T = 0,334 / 0,401 / 0,643 / 0,960 / 0,974 wobec 0,335 / 0,402 / 0,644 / 0,962 / 0,973 przy 0–1°). Dla odchylenia prostopadłego T wynosi 0,30 / 0,31 / 0,38 / 0,62 / 0,98 przy 1 / 2 / 3 / 4 / 5°, bo rozstrojenie Bragga jest tam drugiego rzędu; potrzeba ≥ 5° zamiast 0,75°. Warstwa obrócona o 90° z wyjściem na normalnej ma dla górnej warstwy polaryzację s i przechodzi gorzej: T = 0,296 zamiast 0,335. Dwa kierunki we wspólnym oknie 0,67° są zawsze bliżej niż 0,75°, więc żaden układ dwuwymiarowy nie daje T ≥ 0,96 przy L = 100 µm.

Werdykty iteracji 18:

- **Luka źrenicy wskazana przez audyt: POTWIERDZONE** (geometria: 300·tan 1,5° = 7,9 mm wobec źrenicy 3,5 mm).
- **Soczewka polowa f = 300 mm: ODRZUCONE.** Górne ograniczenie paraksjalne D\_app ≤ p/Θ.
- **16 warstw w jednej źrenicy przy L = 100 µm: ODRZUCONE.** Cieniowanie bez odchylenia, wachlarz ≥ 11° z odchyleniem; RCWA daje 4. kanał 0,063 już w wachlarzu 0,45°.
- **Multipleksowanie azymutalne: ODRZUCONE.** Rozstrojenie drugiego rzędu, model zwalidowany wobec RCWA.
- **C2 ze skośnymi siatkami: NIEROZSTRZYGNIĘTE**, z limitem trzech warstw na oko przy L = 100 µm.

Następne pytanie: siatki grubsze (L \~ 1 mm, n₁ \~ 2·10⁻⁴) mają port około 10× węższy. Ile warstw zmieści się w wachlarzu 0,48° i czy wiązka woksela wypełniająca źrenicę (≥ 0,67°, potrzebna do akomodacji) nie zostanie wycięta przez porty warstw wyżej?

### Iteracja 19: siatki skośne 1 mm w jednej źrenicy

Iteracja 18 pokazała, że przy L = 100 µm odchylenie usuwające cieniowanie (≥ 0,75°) nie mieści się w kącie źrenicy z 30 cm (0,67°). Akceptacja kątowa skaluje się jak 1/L, więc tu warstwy mają L = 1 mm przy n₁ = 2·10⁻⁴ (ten sam iloczyn n₁·L). Model Kogelnika 3D sprawdzono punktowo RCWA (około 175 tysięcy plastrów na rozwiązanie); różnice nie przekraczają 0,0012 (skrypt iteracja19.py).

**Pojedyncza siatka.** Sprawność szczytowa 0,665, akceptacja kątowa wejścia 0,122° w powietrzu (FWHM), szerokość widma 0,122 nm. Sprawność ≥ 90% szczytu wymaga utrzymania długości fali w ±0,030 nm i kąta wiązki w ±0,030°. Źródło gaussowskie 0,01 / 0,05 / 0,11 / 1,5 nm daje 100 / 95 / 75 / 8% szczytu. Port przepuszcza 0,982 / 0,943 / 0,981 przy odchyleniu 0,10 / 0,12 / 0,15°; 0,12° trafia w listek boczny, więc lepszy jest krok 0,10 albo 0,15°.

**Stos pięciu warstw** (wejścia 20–28° co 2°, wyjścia −0,24 / −0,12 / 0 / +0,12 / +0,24°, RCWA):

| Długość fali | Moc w stożku 1°, kanały od góry | Przepuszczalność portów |
| --- | --- | --- |
| λ₀ | 0,623 / 0,586 / 0,586 / 0,596 / 0,603 | 1 / 0,943 / 0,946 / 0,967 / 0,983 |
| λ₀ − 0,05 nm | 0,425 / 0,407 / 0,416 / 0,404 / 0,396 | 1 / 0,959 / 0,982 / 0,953 / 0,939 |
| λ₀ + 0,05 nm | 0,425 / 0,423 / 0,419 / 0,415 / 0,412 | 1 / 0,997 / 0,989 / 0,980 / 0,976 |

Obce światło w stożkach ±0,5° wynosi 0; najbliższy obcy rząd leży 2,19° od wyjść i niesie 6,6·10⁻⁵ mocy sondy. Plamki w 30 cm leżą w −1,26 … +1,26 mm, a wiązka 1 mm mieści się w źrenicy 3,5 mm w 99,3–100%. To pierwszy model, w którym pięć warstw trafia w jedno nieruchome oko, każda z ≥ 10% mocy.

**Stożek woksela i akomodacja.** Wyjście jest wejściem przesuniętym w kx, więc w osi x stożek woksela nie może przekroczyć akceptacji 0,12°, a wypełnienie źrenicy wymaga 0,67°. W osi y akceptacja wejścia wynosi ±1,26°, a stożek ±0,33° przechodzi przez porty czterech warstw wyżej w 98%. Bodziec akomodacji jest więc możliwy tylko w jednym południku; czy oko na taki bodziec reaguje, nie sprawdzono.

**Prążki.** Przy przekładkach 1 mm różnica dróg to 2,96 mm, a okres prążków w długości fali 0,096 nm. Źródło 0,01 nm daje widoczność 0,96, więc prążki zostają. Ich amplitudę ogranicza tło z dwóch odbić Fresnela, ≤ R₁R₂: bez powłok (R = 4%) zafalowanie ≤ ±8%, z powłokami AR (R = 0,25%) ≤ ±0,5%.

**Pole widzenia.** Przy stożku 1° jedno oko w 30 cm widzi najwyżej p/D + 1° = 1,67°, czyli około 8,7 mm płyty; w osi x, gdzie stożek ma 0,12°, około 0,79°. To skutek samego warunku 1, niezależny od rodzaju siatki.

**Materiał.** Odbiciowe siatki objętościowe w szkle fototermorefrakcyjnym (PTR) mają zmierzone L = 5,5 mm, Δn = 230 ppm, R > 99% i szerokość widma 215 pm przy 1064 nm. W wersji multipleksowanej jest to L = 6,5 mm i Δn = 130 ppm na siatkę, ze sprawnością > 98% (Ott i in. 2013, Opt. Express 21, 29620). Mhibik i in. 2016 (Light Sci. Appl. 5, e16026) podają L = 8,3 mm, Δn = 63 ppm, 35 pm przy 633 nm i 98 ± 1%. Maksymalne Δn w PTR to około 10⁻³, więc n₁ = 2·10⁻⁴ jest wartością typową. Cztery odbiciowe siatki w szeregu po około 99,7% przeniosły łącznie ponad 750 W CW (Sevian i in. 2008, Opt. Lett. 33, 384), a siatka multipleksowana 420 W przy kilku kW/cm² (Ott 2013). Warunek 4 przy 1 mW ma więc zapas wielu rzędów wielkości, ale zmierzono to przy 1064 nm, nie przy 532 nm. Odbiciowej siatki PTR przy 532 nm z podanymi L i Δn w recenzowanej literaturze nie znaleziono. Blok PQ:PMMA osiąga Δn do 1,16·10⁻⁴ przy skurczu 0,09–0,4% (Hu i in. 2022, ACS Appl. Mater. Interfaces 14, 21544); skurcz przesuwa długość fali Bragga o 0,5–2 nm, 16–70 razy poza tolerancją ±0,03 nm. Liczby z Ott 2013, Mhibik 2016, Sevian 2008 i Hu 2022 sprawdzono w pełnych tekstach.

**Kompensacja translacyjna** (wyjścia 1–2°, start wiązki przesunięty o −D·tan θ, czyli −5,2 / −10,5 mm dla 1 / 2°). Wiązki trafiają wtedy w źrenicę, ale kierunek widzenia warstwy jest kierunkiem jej wiązki, więc warstwy widać przesunięte o Δθ. Łatka widoczna z jednej warstwy ma ±0,43°, więc łatki różnych warstw nakładają się tylko przy Δθ < 0,86°. Przesunięcie 4,1 mm w przekładce dotyczy wiązki sondy, nie kierunku wyjścia.

Werdykty iteracji 19:

- **Stos pięciu warstw skośnych 1 mm w jednej źrenicy: NIEROZSTRZYGNIĘTE.** W modelu spełnia warunek 1 (0,59–0,62) i warunek 2 (warstwy co ≥ 1 mm, przełączanie kątem przy stałej λ) bez przesłuchu w stożku. Brak pomiaru, warunki 3–4 i adresowanie x–y niewykazane, bodziec głębi tylko w jednym południku.
- **Kompensacja translacyjna: ODRZUCONE.** Przesunięcie kierunku widzenia równe Δθ ≥ 1° przekracza 0,86°, więc warstwy nie nakładają się w polu widzenia.

Następne pytanie: pomiar dwóch skośnych siatek odbiciowych 1 mm w szeregu przy 532 nm, ze źródłem jednoczęstotliwościowym i odchyleniem wyjść 0,10°. Model przewiduje moc 0,62 i około 0,61 w aperturze 3,5 mm w 30 cm oraz przepuszczalność portu górnej siatki 0,98.

### Iteracja 20: woksel, bezpieczeństwo oka i tolerancja wykonania

Wiązkę sondy rozkładamy na fale płaskie i uśredniamy sprawność po jej widmie kątowym: η\_śr = ∫ η(θ)·I(θ) dθ, z η(θ) z modelu Kogelnika 3D sprawdzonego RCWA w iteracji 19. Półkąt wiązki gaussowskiej to θ₀ = λ/(πw₀) (skrypt iteracja20.py).

**Woksel anamorficzny.** W osi x (płaszczyzna padania) sprawność wynosi 0,31 / 0,49 / 0,58 / 0,64 / 0,66 przy talii w₀x = 50 / 100 / 150 / 250 / 500 µm; wiązka o średnicy 0,3 mm zachowuje 87% sprawności fali płaskiej. W osi y średnica 15 µm daje stożek 2,59° i tylko 56% mocy w ±0,5°. Warunek 1 wymaga średnicy ≥ 39 µm, a wypełnienie źrenicy (potrzebne do akomodacji) ≤ 58 µm; w tym oknie η = 0,648–0,650. Jedno oko widzi pole 0,86° × 1,67° (4,5 × 8,7 mm), bo stożek w osi x ma tylko około 0,1°. Daje to około 2,3 tysiąca woksli na warstwę dla 300 × 50 µm i około 1 tysiąc dla 660 × 50 µm. Rzędy modulatora SLM leżą ≥ 1,5° od osi i nie są odbijane (strata), chyba że m·λ/p trafi w odstęp kanałów Δkx = 0,0489 (skok p = 10,9·m µm); wtedy oświetlają sąsiednią warstwę i trzeba je odfiltrować w płaszczyźnie Fouriera.

**Bezpieczeństwo oka.** Granice wzięto z wytycznych ICNIRP 2013 (Health Phys. 105(3):271–295, Tabela 5, apertura 7 mm); IEC 60825-1:2014 sprawdzono tylko wtórnie, jej wartości zgadzają się z kolumną W/J ICNIRP. Moc kanału w źrenicy przy sondzie 1 mW to 0,60 mW, ramka 60 Hz, pięć warstw kolejno.

| Kryterium | Wartość | Granica | Wynik |
| --- | --- | --- | --- |
| 1, pojedynczy impuls, N = 100 (33 µs) | 20 nJ | 307 nJ | zapas 15× |
| 1, pojedynczy impuls, N = 1000 (3,3 µs) | 2 nJ | 77 nJ | zapas 39× |
| 3, ciąg impulsów, N = 1000, Cp = 0,2 | 2 nJ | 15 nJ | zapas 7,7× |
| 2, średnia w 10 s, treść w jednej warstwie | 0,60 mW | 0,39 mW | 1,54 granicy |
| 2, średnia w 10 s, treść równo w 5 warstwach | 0,12 mW | 0,39 mW | 0,31 granicy |

Skanowanie nie zmniejsza mocy średniej wchodzącej do źrenicy. Gdy oko ogniskuje na nieskończoność, wiązki skolimowane jednej warstwy trafiają w jedno miejsce siatkówki. Klasa 1 przy sondzie 1 mW zależy więc od treści obrazu, a przy sondzie ≤ 0,65 mW jest spełniona we wszystkich trzech kryteriach.

**Tolerancja wykonania.** Błąd okresu δΛ/Λ = 1·10⁻⁴ obniża sprawność do 0,42, a zmiana kąta wejścia o 0,054° przywraca 0,666 (RCWA: 0,665). Zakres deflektora ±0,5° pokrywa błędy do około 1·10⁻³, ale wyjście przesuwa się o około 0,9 korekty: 0,049° / 0,15° / 0,48° dla 1·10⁻⁴ / 3·10⁻⁴ / 1·10⁻³. Przy kroku wyjść 0,12° przesunięcie ±0,05° obniża przepuszczalność portu najwyżej do 0,90. Praktyczna tolerancja to |δΛ/Λ| ≲ 1·10⁻⁴ i błąd skosu ≲ 0,03°.

Werdykty iteracji 20:

- **Woksel anamorficzny: NIEROZSTRZYGNIĘTE (model).** Średnica 0,3–0,66 mm × 39–58 µm zachowuje η ≥ 0,58 i stożek < 1°; proponowane 15 µm w osi y wyrzuca 44% mocy poza stożek.
- **„Skanowanie daje Klasę 1 z zapasem przy 1 mW”: ODRZUCONE.** Kontrprzykład: treść w jednej warstwie i oko zogniskowane na nieskończoność dają 1,54 granicy w kryterium mocy średniej.
- **Kompensacja błędu okresu kątem wejścia: NIEROZSTRZYGNIĘTE**; w modelu działa dla |δΛ/Λ| ≤ 1·10⁻⁴.

Następne pytanie: jak oko widzi obraz z woksli skolimowanych w osi x? Przy ogniskowaniu na płytę rozdzielczość w x to około w/D = 2,2 mrad (7,6′ dla 0,66 mm), a przy ogniskowaniu na nieskończoność struktura w x znika. Trzeba policzyć rozkład światła na siatkówce dla wiązki anamorficznej.

### Iteracja 21: obraz woksla na siatkówce i warunek 3

Woksel to wiązka gaussowska z taliami w₀x i w₀y w warstwie, oglądana z 300 mm. Oko modelujemy jako cienką soczewkę f = 17 mm ze źrenicą 3,5 mm; rozkład na siatkówce to transformata Fouriera pola w źrenicy z fazą akomodacji (skrypt iteracja21.py).

**Wiązka w źrenicy.** W osi x przy w₀ = 150 µm czoło fali ma promień 359 mm (2,79 D), a przy w₀ = 330 µm 1679 mm (0,60 D); w osi y przy w₀ = 25 µm 300 mm (3,33 D). Wiązka y ma w źrenicy 4,06 mm i ją wypełnia, wiązka x tylko 0,74 mm.

| Woksel, akomodacja | FWHM x | FWHM y | Kontrast sąsiednich woksli x / y |
| --- | --- | --- | --- |
| 300 × 50 µm, na warstwę (3,33 D) | 2,03′ (10,1 µm) | 0,52′ (2,6 µm) | 0,56 / 0,08 |
| 300 × 50 µm, na nieskończoność | 4,23′ | 22′ | 0 / 0 |
| 660 × 50 µm, na warstwę | 4,43′ | 0,52′ | 0,57 / 0,09 |
| 660 × 50 µm, na nieskończoność | 2,08′ | 26′ | 0 / 0 |

Oko zogniskowane na warstwie odwzorowuje talię wiązki, więc punkt daje elipsę o proporcjach woksla, a nie kreskę. Przy ogniskowaniu na nieskończoność znika cały obraz, bo położenie woksla nie zmienia kierunku jego wiązki. Skok 50 µm w osi y (0,57′) leży poniżej rozdzielczości źrenicy (0,64′), więc rozróżnialny skok to około 90 µm; daje to około 1,1 tysiąca rozróżnialnych woksli na warstwę dla jednego oka.

**Faza cylindryczna na wejściu.** Wiązkę o średnicy 1 mm z fazą soczewki f = −300 mm przepuszczono przez filtr Bragga (amplituda √η(θ), faza odbicia pominięta). Sprawność spada do 0,491, czoło fali x ma przy oku 1,67 D zamiast 3,33 D (źródło pozorne leży 600 mm od oka), a obraz x poszerza się do 4,63′. Dla porównania talia 0,3 mm w warstwie daje η = 0,581, 2,47 D i 2,51′. Wergencja 3,33 D wymaga źródła pozornego w warstwie, czyli talii w warstwie, a jej rozmiar ogranicza akceptacja Bragga (w₀·θ ≥ λ/π).

**Warunek 3.** Przy sondzie 0,50 mW do detektora trafia 0,30 mW, czyli 8,0·10¹⁴ fotonów/s. Detektor krzemowy 1 cm² (wydajność kwantowa 0,70) z filtrem 10 nm i czasem 1 s daje SNR ograniczony szumem śrutowym 2,4·10⁷ w ciemni i 2,0·10⁷ przy 10 tysiącach luksów. Niestabilność lasera 0,1% lub 1% obniża SNR do około 10³ lub 10². Jasność jest ogromna: 0,18 lm w stożku to luminancja około 1,7·10⁸ cd/m² średnio po polu widzenia, więc wyświetlacz potrzebuje mocy o kilka rzędów mniejszej.

Werdykty iteracji 21:

- **„Astygmatyczna kreska zamazująca detal x”: ODRZUCONE.** Przy akomodacji na warstwę obraz woksla to 2,03′ × 0,52′, a sąsiednie woksle w osi x (skok 0,3 mm) są rozdzielone z kontrastem 0,56.
- **Faza cylindryczna jako naprawa: ODRZUCONE.** Daje 1,67 D zamiast 3,33 D, η = 0,49 i gorszy obraz; ograniczenie w₀·θ ≥ λ/π.
- **Warunek 3: NIEROZSTRZYGNIĘTE (spełniony w modelu).** SNR od 10² do 2·10⁷ zależnie od stabilności lasera; brak pomiaru.

Następne pytanie: czy oko faktycznie akomoduje na warstwę, gdy bodziec niesie tylko oś y? Bez akomodacji na 3,33 D obraz znika, więc potrzebny jest pomiar optometryczny reakcji na bodziec astygmatyczny.

### Iteracja 22: akomodacja, projekcja warstwowa i plan próby

Model siatkówki jak w iteracji 21; woksel 300 × 50 µm, skok 300 µm w osi x i 90 µm w osi y (skrypt iteracja22.py). Kontrast sąsiednich woksli liczono dla woksli zapalanych kolejno (suma natężeń) oraz jednocześnie przez modulator przy koherentnym laserze (suma pól).

| Akomodacja | FWHM x | FWHM y | Kontrast x: kolejno / jednocześnie w fazie | Kontrast y: kolejno / jednocześnie |
| --- | --- | --- | --- | --- |
| 2,79 D | 1,83′ | 4,24′ | 0,48 / 0,18 | 0,04 / 0 |
| 3,06 D | 1,91′ | 1,79′ | 0,55 / 0,28 | 0,00 / 0 |
| 3,20 D | 1,96′ | 0,65′ | 0,57 / 0,31 | 0,29 / 0 |
| 3,33 D (warstwa) | 2,03′ | 0,52′ | 0,56 / 0,30 | 0,90 / 0,80 |
| 3,45 D | 2,09′ | 0,60′ | 0,57 / 0,31 | 0,44 / 0,12 |

**Akomodacja kompromisowa.** Wiązka y wypełnia źrenicę, więc błąd akomodacji 0,27 D rozmywa ją o p·ΔA = 0,95 mrad (3,2′), a kontrast w osi y spada z 0,90 do 0. Oś x ma w źrenicy tylko 0,74 mm i jest prawie niewrażliwa na akomodację. Najlepsza jest akomodacja na warstwę (3,33 D), z tolerancją około ±0,1 D dla osi y.

**Projekcja warstwowa przez modulator.** Przy sondzie 0,50 mW, sprawności modulatora 0,65, η = 0,60, 1100 wokslach i pięciu warstwach na woksel przypada 295 nW w czasie świecenia warstwy i 35,5 nW średnio w stożku. Luminancja równoważna to około 2,5·10⁷ cd/m², więc 1000 cd/m² daje już sonda około 20 nW. Cała zapalona warstwa wnosi do źrenicy 0,195 mW, czyli 0,50 / 0,19 / 0,04 granicy ICNIRP dla źródła punktowego / plamy 4 mrad / obrazu 22 mrad. Woksle zapalane jednocześnie koherentnym laserem interferują: kontrast w osi x spada z 0,56 do 0,30. Przełączanie warstw wymaga zmiany kąta wejścia w zakresie 30,87–44,77° (13,9°) przy wiązce szerokiej na 8,7 mm; czy da to deflektor akustooptyczny, trzeba sprawdzić w karcie urządzenia.

**Plan próby z dwiema płytkami PTR 1 mm.** Płytka A: wejście 20,0° wewnątrz (30,87° w powietrzu), wyjście 0°, okres 180,07 nm, płaszczyzny nachylone o 10,00°. Płytka B: wejście 22,0° (34,19°), wyjście +0,10°, okres 180,67 nm, nachylenie 10,97°. RCWA przewiduje 0,623 dla kanału A i 0,609 dla B przy przepuszczalności portu 0,982; przy wyjściu +0,12° kanał B ma 0,585 przy porcie 0,943. Kryteria zapisane przed pomiarem:

- **Warunek 1:** moc w stożku 1° (soczewka f = 200 mm i przesłona 3,49 mm w jej ognisku) ≥ 10% mocy padającej dla każdego kanału.
- **Warunek 2:** przy tej samej długości fali (miernik, zmiana < 0,01 nm) przełączenie kąta wejścia przesuwa płaszczyznę odbicia o ≥ 10 µm. Warstwa B leży 2 mm głębiej, więc punkt wyjścia na powierzchni przesuwa się o około 0,77 mm; 10 µm głębi odpowiada 3,8 µm przesunięcia.
- **Model obalają:** sprawność płytki < 0,5, przepuszczalność portu przy 0,10° < 0,9, akceptacja kątowa poza 0,10–0,15° albo szerokość widma poza 0,10–0,15 nm.
- **Warunki 3 i 4:** SNR ≥ 100 na detektorze Si 1 cm² z filtrem 532 ± 5 nm w 1 s; zmiana sprawności < 1% w ciągu 1 s odczytu przy 0,5 mW.

Werdykty iteracji 22:

- **Akomodacja kompromisowa 3,06 D: ODRZUCONE.** Rachunek falowy daje kontrast 0 w osi y przy skoku 90 µm wobec 0,90 przy akomodacji na warstwę.
- **Projekcja warstwowa: NIEROZSTRZYGNIĘTE.** Jasność z zapasem około 2,5·10⁴ razy i Klasa 1 spełniona, ale interferencja obniża kontrast w osi x do 0,30, a zakres deflektora nie jest sprawdzony.

Następne pytanie: czy dekoherencja sąsiednich woksli w osi y, gdzie akceptacja Bragga jest szeroka (±1,26°), przywróci kontrast w osi x ≥ 0,5 bez spadku sprawności i bez wyjścia poza stożek 1°?

### Iteracja 23: kontrast przy oświetleniu koherentnym i adresowanie warstw

W osi x oko zogniskowane na warstwie odwzorowuje pole odbite w warstwie, bo wiązka x jest dużo węższa od źrenicy. Pole odbite to pole wejściowe przefiltrowane amplitudą √η(θ) siatki 1 mm z modelu Kogelnika 3D; fazę odbicia pominięto (skrypt iteracja23.py).

**Korekta iteracji 21–22.** Tam kontrast w osi x liczono bez filtru Bragga. Filtr poszerza woksel z 177 do 217 µm (FWHM, w₀x = 150 µm), więc przy skoku 300 µm kontrast zapalania kolejnego wynosi 0,30 zamiast 0,56, a jednoczesnego w fazie 0,02 zamiast 0,30.

| Talia w₀x | η | Kontrast przy skoku 300 / 400 / 500 / 660 µm |
| --- | --- | --- |
| 100 µm | 0,49 | 0,56 / 0,89 / 1,00 / 1,00 |
| 150 µm | 0,58 | 0,30 / 0,70 / 0,93 / 1,00 |
| 250 µm | 0,64 | 0,02 / 0,22 / 0,50 / 0,84 |
| 330 µm | 0,65 | 0,00 / 0,04 / 0,20 / 0,54 |

**Sposoby zapalania pary sąsiednich woksli** (w₀x = 150 µm, skok 300 µm):

| Sposób | Kontrast | η | Moc średnia względem zapalania kolejnego |
| --- | --- | --- | --- |
| kolejno | 0,30 | 0,581 | 100% |
| jednocześnie, w fazie | 0,02 | 0,624 | 107% |
| jednocześnie, przeciwfaza 0/π | 1,00 | 0,525 | 90% |
| podramki nieparzyste/parzyste (DMD) | 0,30 | 0,581 | 50% |
| dwie podramki z fazą względną 0 i π | 0,30 | 0,575 | 99% |

Wzór 0/π o skoku 300 µm ma składowe kątowe ±0,051° przy połowie akceptacji 0,061°, więc sprawność spada o 10%. Kontrast 1,00 bierze się z wymuszonego ciemnego prążka między każdymi dwoma zapalonymi sąsiadami, więc linia ciągła staje się przerywana. Podramki odtwarzają obraz niekoherentny: DMD kosztem połowy światła, modulator fazy prawie bez strat, ale tylko dla najbliższych sąsiadów. Losowa faza w osi y wspólna dla sąsiadów w osi x nie zmienia ich interferencji. Osobne maski działają dopiero przy komórkach mniejszych od obrazu y w warstwie (45 µm), a komórka 25 µm rozprasza już na 1,22°, poza stożek 1°.

**Adresowanie warstw.** Iloczyn czasu i pasma deflektora akustooptycznego to TBP = D·Δθ/λ = 3967 dla wiązki 8,7 mm i zakresu 13,9° (281 MHz). Teleskop nie zmienia tego iloczynu: deflektor o aperturze 1 mm przed teleskopem rozszerzającym 8,7× musiałby odchylać o 121° (2448 MHz). Gęstsze kanały obniżają wymaganie, bo grube siatki prawie nie odbijają wiązek sąsiednich kanałów:

| Skok kanałów (wewnątrz) | Zakres w powietrzu | Pasmo | TBP | Odbicie sąsiedniej siatki |
| --- | --- | --- | --- | --- |
| 2,0° | 13,9° | 281 MHz | 3967 | 1,6·10⁻⁴ sygnału |
| 0,5° | 3,3° | 67 MHz | 948 | 2,5·10⁻³ sygnału |
| 0,38° | 2,5° | 51 MHz | 719 | 4,7·10⁻³ sygnału |
| 0,25° | 1,7° | 33 MHz | 471 | 5,1·10⁻³ sygnału |

Dyskretne źródła, na przykład jeden laser z przełącznikiem 1×5 do pięciu kolimatorów pod stałymi kątami, nie mają ograniczenia TBP i zachowują jedną długość fali, czego wymaga warunek 2. Strata na oświetlenie prostokątnego pola wiązką gaussowską jest wspólna dla wszystkich wariantów: w polu zostaje 58 / 25 / 13% mocy przy natężeniu brzegu ≥ 50 / 80 / 90% szczytu. Parametrów rynkowych deflektorów nie sprawdzono.

Werdykty iteracji 23:

- **Teleskop przy deflektorze: ODRZUCONE.** Iloczyn D·Δθ jest niezmiennikiem.
- **Faza 0/π: ODRZUCONE jako naprawa kontrastu.** Zmienia obraz (sztuczne przerwy) i obniża sprawność o 10%.
- **Losowa faza w osi y: ODRZUCONE.** Wspólna maska nie działa, osobne maski wyprowadzają światło poza stożek 1°.
- **Podramki: NIEROZSTRZYGNIĘTE (działają w modelu).** Odtwarzają kontrast niekoherentny; DMD traci 50% mocy, co przy zapasie jasności około 2,5·10⁴ nie ma znaczenia.

Następne pytanie: jaka grubość siatki (0,5–1 mm) daje najlepszy kompromis między mniejszym wokslem x po filtrze Bragga (szersza akceptacja) a szerszym portem, czyli większym cieniowaniem i mniejszą liczbą warstw w wachlarzu 0,48°?

### Iteracja 24: grubość siatki

Grubość L zmieniano przy stałym iloczynie n₁·L = 0,2 µm, więc sprawność dla fali płaskiej zostaje 0,666 przy każdej grubości. Liczono modelem Kogelnika 3D; przy L = 0,5 mm RCWA daje η = 0,665 (Kogelnik 0,666) i przepuszczalność portu 0,9505 (Kogelnik 0,9502) (skrypt iteracja24.py). Krok wyjść dobrano tak, żeby port każdej warstwy wyżej przepuszczał ≥ 0,95 w każdej wielokrotności kroku. Wariant odporny wymaga tego w całym przedziale ±0,02° wokół niej, co odpowiada błędowi okresu siatki około 4·10⁻⁵ (iteracja 20).

| L | Warstwy w 0,48° (krok), nominalnie | Warstwy (krok), tolerancja ±0,02° | Woksel x po filtrze (wejście 177 µm) | Kontrast przy skoku 300 / 400 µm | Woksle x z kontrastem ≥ 0,5 |
| --- | --- | --- | --- | --- | --- |
| 0,5 mm | 4 (0,160°) | 3 (0,180°) | 183 µm | 0,53 / 0,87 | 15 |
| 0,7 mm | 5 (0,120°) | 4 (0,131°) | 193 µm | 0,46 / 0,83 | 14 |
| 0,85 mm | 6 (0,096°) | 5 (0,110°) | 205 µm | 0,38 / 0,78 | 13 |
| 1,0 mm | 7 (0,080°) | 4 (0,160°) | 217 µm | 0,30 / 0,70 | 12 |
| 1,2 mm | 8 (0,069°) | 4 (0,146°) | 237 µm | 0,21 / 0,57 | 11 |

Wzór funkcji celu nie dotarł w poleceniu, więc przyjęto F = liczba warstw w wachlarzu 0,48° × liczba woksli x z kontrastem ≥ 0,5 × 96 woksli w osi y.

&#91;embedded content: skrypt iteracja24.py · L = 0,5–1,2 mm, n₁·L = 0,2 µm, w₀x = 150 µm\]

Nominalnie F rośnie z grubością: grubsza siatka mieści więcej warstw, a traci tylko po jednym wokslu x. Kroki 0,07–0,10° leżą jednak tuż przy stromym zboczu portu, więc tolerancja ±0,02° zabiera grubym siatkom najwięcej warstw i optimum wypada przy 0,85 mm. Ważenie mocą najsłabszego kanału (0,59–0,62 sondy) i sprawnością woksla nie zmienia kolejności. Szerokość widma maleje z 0,244 do 0,102 nm, a odbicie sąsiedniego kanału przy skoku wejść 0,38° rośnie dla cieńszych siatek do 0,94% sygnału przy 0,7 mm.

Werdykty iteracji 24:

- **Pięć warstw przy kroku ≤ 0,12°: NIEROZSTRZYGNIĘTE (model).** Nominalnie od L = 0,7 mm; z tolerancją ±0,02° dopiero przy 0,85 mm.
- **Grubość optymalna: NIEROZSTRZYGNIĘTE (model).** L\_opt = 0,85 mm przy tolerancji wyjścia ±0,02°; bez tolerancji optimum leży na krańcu badanego przedziału.

Następne pytanie: czy zapis siatek PTR osiąga błąd okresu ≤ 4·10⁻⁵ i dokładność skosu ≤ 0,013° (pomiar w literaturze)? Jeśli nie, ile warstw zostaje przy realnym rozrzucie?

### Iteracja 25 — audyt iteracji 19–24

Audyt sprawdza tezę o pięciu warstwach i „optymalnej” grubości 0,85 mm we własnym modelu, bez nowego mechanizmu. Zmiany modelu:

- każda siatka ma pełną odpowiedź zespoloną r i t (Kogelnik 3D jako macierz exp(M·d) 2×2);
- pole liczone jest jako widmo kątowe 2D (κx, κy), z poprawnym przeliczeniem kx na kąt;
- liczone są wszystkie pięć warstw (wejścia 20–28°) i jedno położenie oka.

Stos jak w iteracji 24: L = 0,85 mm, krok wyjść 0,110°, przekładki 1 mm, w₀x = 150 µm, w₀y = 25 µm, D = 300 mm, źrenica 3,5 mm. Kod: research/iteracja25.py i research/kogelnik\_zesp.py. Dane wyjściowe: research/wyniki\_it25.

**Odpowiedź zespolona.** Kogelnik zespolony zgadza się z RCWA w 18 punktach (L = 0,85 mm):

- |r|² różni się o ≤ 0,0012;
- faza r o ≤ 0,002 rad;
- faza t portu o ≤ 0,0011 rad.

Faza odbicia jest prawie nieparzysta w kącie: ±1,04 rad przy ±0,05° i ±3,07 rad przy ±0,12°.

Audyt znalazł błąd w iteracjach 20–24: częstość przestrzenną w płaszczyźnie warstwy przeliczano na kąt bez czynnika 1/cos(kąta wejścia). Widmo kątowe woksla było przez to zaniżone o czynnik 0,86 w warstwie 0 i 0,71 w warstwie 4. Warstwy 4 wcześniej nie liczono.

Trzy warianty mają to samo pole wejściowe i moc sondy 1:

- A — tylko filtr |r|, czyli model iteracji 21–24;
- B — zespolone r jednej siatki;
- C — pełny stos: zespolone przejścia wejścia i portów oraz propagacja.

Kontrast to kontrast Michelsona pary woksli na siatkówce, liczony w położeniach nominalnych.

| warstwa, wariant | η przy powierzchni | FWHM w warstwie | przesunięcie | kontrast 300 / 400 µm | skok dla kontrastu 0,5 |
| --- | --- | --- | --- | --- | --- |
| 0 (20°), A | 0,584 | 218 µm | 0 | 0,30 / 0,70 | 348 µm |
| 0, B = C | 0,584 | 223 µm | +120 µm | 0,28 / 0,69 | 353 µm |
| 2 (24°), C | 0,504 | 264 µm | +161 µm | 0,11 / 0,48 | 408 µm |
| 4 (28°), A | 0,481 | 257 µm | 0 | 0,12 / 0,42 | 430 µm |
| 4, B | 0,481 | 304 µm | +171 µm | 0,00 / 0,29 | 457 µm |
| 4, C | 0,456 | 303 µm | +185 µm | 0,00 / 0,30 | 457 µm |

Co robi faza:

- daje stałe przesunięcie boczne (kompensowane adresowaniem);
- poszerza woksel o 2–18%;
- podnosi najmniejszy skok najgłębszej warstwy z 430 do 457 µm;
- nie zmienia ogniskowania.

Para woksli zapalonych w fazie przy skoku 300 µm ma kontrast 0 we wszystkich warstwach. Kolumny naprzemienne i przerwa jednej kolumny przy skoku 400 µm mają kontrast ≥ 0,98.

**Najgłębszy woksel i wspólna źrenica.** Moce dla warstwy 4 przy sondzie 1 to różne wielkości i nie wolno ich utożsamiać:

| etap | moc |
| --- | --- |
| odbita przez siatkę | 0,480 |
| przy powierzchni | 0,456 |
| w stożku o pełnym kącie 1° | 0,433 |
| w źrenicy (oko na osi wiązki) | 0,397 |
| w komórce woksla na siatkówce | 0,321 |

Wszystkie woksle jednej warstwy świecą w tym samym kierunku. Dlatego łatki widoczności kolejnych warstw są przesunięte przy oku o D·tan o\_k, czyli o 0,58 mm na krok. Przedział położeń oka dla jednej warstwy (moc ≥ 50% maksimum i kontrast ≥ 0,5 przy skoku 500 µm) ma 2,3–2,7 mm w x i 3,7 mm w y.

Wspólny obszar widziany z jednego położenia oka, przy skoku 500 µm:

| liczba warstw N | woksli razem |
| --- | --- |
| 1 | 208 |
| 2 | 328 |
| 3 | 306 |
| 4 | 248 |
| 5 | 150 |

Dla N = 5 jest to obszar 0,22 × 2,75 mm, czyli jedna kolumna i 30 wierszy. Przy progu mocy 80% zostaje 55 woksli. Iteracja 24 podawała 6240 woksli, bo sumowała pola widziane z różnych położeń oka.

&#91;image: Warstwa 4: liczba warstw spełniających kryteria w zależności od położenia woksla, natężenie i faza w źrenicy, obraz na siatkówce\]

**Tolerancje.** Okno „±0,02°” z iteracji 24 dotyczyło błędu względnego dwóch warstw. Przeliczenie go na tolerancję jednej warstwy było niespójne o czynnik 2.

Porty liczone z widmem wiązki, a nie z falą płaską, przepuszczają przy kroku 0,110° tylko 0,938. Przy błędzie względnym ±0,04° najmniejsze T spada do 0,74–0,88. Krok potrzebny przy błędzie jednej warstwy ±0,01° wynosi 0,1375°, a przy ±0,02° — 0,1575°.

Pokrętła kalibracji (materiał stały, λ wspólna i stała):

- C0 — bez kalibracji;
- C1 — kąt wejścia kanału w x i y;
- C1′ — odstrojenie w akceptacji przy η ≥ 0,9, co przesuwa wyjście o ±0,02–0,03°;
- C2 — pochylenie płytki przy montażu; niewykonane ilościowo.

Po C1 błąd ±0,01° jednej warstwy odpowiada błędowi okresu (2,0–2,9)·10⁻⁵, skosu 0,0067° albo średniego n 3·10⁻⁵.

Literatura, z rozdzieleniem rezonansu, orientacji i jednorodności:

- rezonans: ±10 pm od celu (Chen i in. 2019, tylko streszczenie); u producentów 0,1–0,5 nm;
- dryf rezonansu: zmierzone 8 pm/K;
- orientacja wektora siatki: brak zmierzonej tolerancji;
- jednorodność sprawności: < 5%, a na 13 × 17 mm ≤ 1%;
- gradient współczynnika załamania w grubości: 20–28 ppm/mm, w modelu bez znaczenia;
- mapa rezonansu w poprzek apertury: nie znaleziono.

**Przesłuch i optimum.**

- Kanały co 2°: odbicia innych warstw trafiają przy oku 13–54 mm od sygnału, więc w źrenicy dają 0.
- Duch etalonowy dwóch powierzchni: modulacja ±2,7% bez powłoki antyrefleksyjnej, ±0,2% z powłoką R = 0,25%.
- Kanały co 0,38°: przesłuch do 1,2·10⁻² w źrenicy (ponad kryterium 1%). Trafia w inne komórki obrazu, nie w komórkę sygnału.

Gęste przemiatanie L = 0,75–1,0 mm co 0,025 mm (pełne dane: wyniki\_it25/grubosc.txt):

| L \[mm\] | krok δ przy E = 0 / 0,01 / 0,02° | skok woksla, warstwa 4, A / C | maks. woksli E = 0 (N) | E = 0,01° (N) | N = 5 |
| --- | --- | --- | --- | --- | --- |
| 0,75 | 0,129 / 0,149 / 0,169 | 400 / 419 µm | 291 (3) | 268 (2) | 1 kolumna |
| 0,85 | 0,118 / 0,138 / 0,158 | 430 / 457 µm | 303 (3) | 272 (2) | 1 kolumna |
| 1,00 | 0,104 / 0,124 / 0,144 | 471 / 528 µm | 300 (3) | 214 (2) | 1 kolumna |

Liczba woksli we wspólnym obszarze jest płaska w L (±3%). Sprawność maleje z L. Faza dodaje 5–12% do skoku woksla i przesuwa korzyść w stronę cieńszych siatek, ale nie odwraca rankingu. Pojedynczego optimum nie ma; teza „L\_opt = 0,85 mm” nie ma oparcia.

**Dowody.**

- Zbieżność siatki obliczeniowej 512²–2048²: różnice < 0,7%.
- Szerokość widma źródła 0,05 nm: η spada o 4%.
- Bilans energii: suma mocy 1,000000.
- RCWA z M = 5 daje to samo co z M = 3.
- Skończona apertura siatek leżących wyżej nie zmienia wyniku, jeśli krawędź jest ≥ 1 mm od woksla.

| twierdzenie | wynik | werdykt |
| --- | --- | --- |
| Kogelnik 3D zgodny z RCWA, także w fazie | ≤ 0,0012 i ≤ 0,002 rad | spełnione w modelu |
| woksel 205 µm, 13 woksli x na warstwę | 218–303 µm, skok 348–457 µm | obalone (model) |
| faza odbicia pomijalna | poszerzenie do 18%, skok +27 µm | obalone dla warstw 2–4 |
| 5 warstw widocznych w jednej źrenicy | 1 kolumna × 30 wierszy | obalone w podanych warunkach |
| odporność ±0,02° przy kroku 0,110° | T\_min 0,74 przy ±0,04° | obalone (model) |
| L\_opt = 0,85 mm | brak optimum, maksimum przy N = 2–3 | obalone |
| tolerancje okresu i skosu osiągalne | brak pomiaru orientacji i mapy rezonansu | nierozstrzygnięte |
| przesłuch < 1% przy kanałach co 2° | 0 w źrenicy, etalon ±0,2% z powłoką AR | spełnione w modelu |
| kanały co 0,38° | do 1,2·10⁻² w źrenicy | obalone (kryterium 1%) |
| kalibracja montażowa C2 | brak danych | niewykonany |

Werdykt iteracji: ODRZUCONE, w modelu i w podanych warunkach. Pięć warstw nie daje użytecznego obrazu we wspólnej źrenicy po uwzględnieniu pełnej fazy, skończonego pola i względnych błędów wykonania. Nominalnie zostaje jedna kolumna woksli, a przy błędzie względnym ±0,04° — żadna. Maksimum wspólnej objętości daje N = 2–3 warstwy, około 210–306 woksli.

Uwaga po iteracji 26: werdykt ODRZUCONE został wycofany. Wynikał z dodatkowych progów, a nie z granicy optycznej. Liczby woksli z tej sekcji obowiązują tylko przy jej kryteriach (kontrast w x przy Δy = 0).

Następne pytanie: czy kompensacja fazy na wejściu i ustawienie płytek przy montażu (rozdzielczość ≤ 0,003°) dają N = 3 warstwom ≥ 5 kolumn? I czy liczba warstw N ≥ 5 wymaga wyjść zbieżnych do źrenicy? Tego mechanizmu nie badano.

### Iteracja 26 — kontrola odrzucenia z iteracji 25

Werdykt iteracji 25 (ODRZUCONE) został wycofany. Wynikał z trzech założeń dodatkowych, których nie ma w pięciu warunkach pierwotnych:

- progu przepuszczalności 0,95 dla każdego pojedynczego portu;
- progu kontrastu 0,5 przy kroku wyjść 0,110°;
- niepełnych kryteriów obrazu.

Kod jest w research/iteracja26.py, dane w research/wyniki\_it26. Jedna tabela 948 wyników z etykietami jest w pliku tabela\_uzgodniona.csv. Każdy wiersz ma etykiety: skład stosów, skok, próg mocy, próg kontrastu, model błędów.

**Kryteria.** Pięć warunków pierwotnych nie wymaga wspólnej źrenicy. Warunek 1 (≥ 10% mocy w stożku o pełnym kącie < 1°) spełnia każdy kanał.

Kryteria obrazu są dodatkowe i jawne:

- moc w źrenicy powyżej progu względnego (ułamek maksimum warstwy) albo bezwzględnego (ułamek mocy sondy);
- kontrast Michelsona par woksli w x i y co najmniej C;
- zmiana położenia obrazu najwyżej skok/4.

Liczby iteracji 25 odtwarzam co do woksla przy jej kryteriach. Przy pełnych kryteriach, w których kontrast zależy od przesunięcia oka w y i dochodzi kontrast w y, wyniki dla tego samego projektu są niższe:

| liczba warstw | woksli razem (pełne kryteria) | iteracja 25 |
| --- | --- | --- |
| 1 | 153 | 208 |
| 2 | 216 | 328 |
| 3 | 192 | 306 |
| 4 | 116 | 248 |
| 5 | 0 | 150 |

Maksimum przypada na dwie warstwy. Zdanie „maksimum przy N = 2–3” myliło dwa różne modele.

Przy kroku 0,110° i pięciu warstwach wynik zależy od progu kontrastu, nie od progu jasności:

| próg kontrastu | kolumny woksli |
| --- | --- |
| 0,5 | 0 (przy każdym progu mocy) |
| 0,3 | 1 |
| 0,15 | 2 |

Ograniczenie geometryczne wspólnej szerokości W₅ ≤ min(p + f) − (X\_max − X\_min) wynosi tu 1,78 mm, czyli nie jest zerowe.

Jedna kolumna × 30 wierszy to adresowalny przekrój y–z: 150 woksli w pięciu głębokościach. Nie jest to obraz 2D w każdej warstwie, ale nie jest to też brak obrazu przestrzennego.

**Uzgodnienia.** Czynnik 0,71 to cosinus kąta wejścia w powietrzu (44,77° dla 28° wewnątrz), a nie cos 28°:

- kx to składowa równoległa do powierzchni płytki;
- da/dkx = 1/(k₀·cos a);
- iteracje 20–24 miały Δkx = 2π·fx·cos a₀.

Szerokości woksla dla wariantów A, B i C były podane w tej samej płaszczyźnie warstwy. Przy powierzchni różnią się o ≤ 1 µm.

Moc 0,321 to moc w komórce woksla 330 × 90 µm (±1,86′ × ±0,51′). Cała moc na siatkówce wynosi 0,395. W sąsiednich komórkach jest 0,069 — ta energia jest rozlana, nie stracona.

**Faza.** Test niezmienniczości przesuwa płaszczyznę odniesienia o ±0,5 mm albo na dno siatki. Obraz zostaje taki sam do 6·10⁻¹³.

Przesunięcie woksla 117–178 µm wynika z nachylenia fazy samego odbicia r (głębokość wnikania około 0,33 mm). Nie wynika z propagacji: podwójne liczenie grubości siatek przesuwa szczyt tylko o 5 µm.

Rozkład fazy dla warstwy 4:

| co usunięto | szerokość woksla | najmniejszy skok |
| --- | --- | --- |
| nic | 303 µm | 457 µm |
| tylko część liniową | 303 µm | 454 µm |
| całą fazę | 262 µm | 432 µm |

Część liniowa tylko przesuwa woksel. Poszerzenie powoduje reszta nieliniowa.

**Optymalizacja stosu.** Bez progu 0,95 na pojedynczy port kryteria liczone są dla całego stosu. Liczby to woksle na warstwę we wspólnym obszarze pięciu warstw, z jednego położenia oka:

| L, odstęp wyjść | warunek 1 (najsłabszy kanał) | moc ≥ 50%, kontrast ≥ 0,5 | moc ≥ 0,1 sondy, kontrast ≥ 0,3 |
| --- | --- | --- | --- |
| 0,85 mm, 0° | NIE (0,014) | 195 | 0 |
| 0,85 mm, 0,03° | tak (0,183) | 97 (3 × 39) | 130 |
| 0,85 mm, 0,04° | tak (0,246) | 90 (3 × 39) | 150 (4 × 43) |
| 0,85 mm, 0,110° | tak (0,432) | 0 | 39 |
| 0,75 mm, 0,03° | tak (0,164) | 101 | 118 |
| 1,00 mm, 0,03° | tak (0,204) | 82 | 122 |

Najlepsze odstępy nierówne dają 106 woksli na warstwę, ale najsłabszy kanał ma wtedy zapas tylko do 0,109.

**Błędy.** Model błędów: niezależne błędy okresu ε i orientacji wektora siatki φ w każdej warstwie, przy kalibracji kątem wejścia. Wektory wybrałem modelem zastępczym i sprawdziłem pełnym modelem siatek (rezonans, sprawność, faza, porty, łatki).

| konfiguracja | budżet ε / φ | najgorszy wektor | warunek 1 | woksli na warstwę |
| --- | --- | --- | --- | --- |
| odstęp 0,04° | 1·10⁻⁵ / 0,002° | ε \[+1, +1, −1, −1, −1\]·10⁻⁵, φ przeciwnie | tak (0,181) | 85–94 |
| odstęp 0,04° | 2·10⁻⁵ / 0,005° | ε \[+2, +2, +2, −2, −2\]·10⁻⁵, φ przeciwnie | tak (0,123) | 77–92 |
| odstęp 0,04° | 5·10⁻⁵ / 0,01° | ε \[+5, +5, 0, −5, −5\]·10⁻⁵, φ przeciwnie | NIE (0,054) | 64–85 |
| odstęp 0,03° | 2·10⁻⁵ / 0,005° | ε \[+2, +2, +2, −2, −2\]·10⁻⁵, φ przeciwnie | NIE (0,071) | 81–92 |

**Odpowiedź na pytanie iteracji.** Konfigurację pięciowarstwową znalazłem w określonym przeszukaniu: L = 0,85 mm, wyjścia co 0,03–0,04°, jedno położenie oka. Daje 90–97 woksli na warstwę (3 × 39), nominalnie i przy budżecie |ε| ≤ 2·10⁻⁵, |φ| ≤ 0,005° (konfiguracja 0,04°). Przy budżecie 5·10⁻⁵ / 0,01° nie spełnia warunku 1.

Zakres przeszukania:

- grubość L w trzech wartościach;
- odstęp wyjść 0–0,12°;
- wyjścia nierówne przy L = 0,85 mm;
- w₀x, wejścia i n₁·L stałe.

Werdykt iteracji: NIEROZSTRZYGNIĘTE. Brak zmierzonej tolerancji orientacji siatek PTR, więc nie wiadomo, czy budżet 0,005° jest osiągalny.

Następne pytanie: jaki jest zmierzony rozrzut kierunku wyjścia między płytkami z jednej serii po kalibracji kątem wejścia? Czy mieści się w ±0,015° na płytkę?

## Źródła

Prace recenzowane, w kolejności pojawienia się w tabeli wyników:

1. [Schilke, Zimmermann, Courteille, Guerin, PRL 106, 223903 (2011)](https://doi.org/10.1103/PhysRevLett.106.223903) — R\_max ≃ 80%, N = 5·10⁷.
2. [Bajcsy, Zibrov, Lukin, Nature 426, 638 (2003)](https://doi.org/10.1038/nature02176) — zwierciadło Bragga z modulacji absorpcji EIT, R do \~80% w pomiarze CW (rys. 2B, krzywa ii), sonda 250 µW.
3. [Liu, Huo, He, Ma, Opt. Express 34, 19811 (2026)](https://doi.org/10.1364/OE.592104) — lusterko lewitowane ultradźwiękami, ±8°.
4. [Chen, Peng, Li, Liu, Opt. Express 27, 12039 (2019)](https://doi.org/10.1364/OE.27.012039) — dwie płaszczyzny z filmami cholesterycznymi.
5. [Natarajan i in., MRS Proc. 559, 109 (1999)](https://doi.org/10.1557/PROC-559-109) — przełączalne siatki odbiciowe H-PDLC, \~50 µs.
6. [Sautenkov, Saakyan, Bobrov, Zelener, JQSRT 328, 109153 (2024)](https://doi.org/10.1016/j.jqsrt.2024.109153) — selektywne odbicie w gęstej parze.
7. [Keaveney i in., PRL 109, 233001 (2012)](https://doi.org/10.1103/PhysRevLett.109.233001) — n = 1,26 w warstwie pary 250 nm.
8. [Mok, Burr, Psaltis, Opt. Lett. 21, 896 (1996)](https://doi.org/10.1364/OL.21.000896) — prawo η = (M/#/M)².
9. [Dhar i in., Opt. Lett. 24, 487 (1999)](https://doi.org/10.1364/OL.24.000487) — M/# = 42 w 1 mm fotopolimeru.
10. [Khorasaninejad i in., Science 352, 1190 (2016)](https://doi.org/10.1126/science.aaf6644) — metasoczewki 66–86%.
11. [Arbabi E. i in., Nat. Commun. 9, 812 (2018)](https://doi.org/10.1038/s41467-018-03155-6) — metasoczewka MEMS, > 60 D.
12. [Rui i in., Nature 583, 369 (2020)](https://doi.org/10.1038/s41586-020-2463-x) — lustro z warstwy atomów, R = 0,58.
13. [Srakaew i in., Nat. Phys. (2023)](https://doi.org/10.1038/s41567-023-01959-y) — do 1500 atomów.
14. [Michine & Yoneda, Commun. Phys. 3, 24 (2020)](https://doi.org/10.1038/s42005-020-0286-6) — siatka gazowa 96%.
15. [Smalley i in., Nature 553, 486 (2018)](https://doi.org/10.1038/nature25176) — wyświetlacz z pułapką fotoforetyczną.
16. [Rogers, Laney, Peatross, Smalley, Appl. Opt. 58, G363 (2019)](https://doi.org/10.1364/AO.58.00G363) — moc rozproszona rzędu nW.
17. [McLeod i in., Appl. Opt. 44, 3197 (2005)](https://doi.org/10.1364/AO.44.003197) — 12 warstw mikrohologramów.
18. [Ostroverkhov i in., Jpn. J. Appl. Phys. 48, 03A035 (2009)](https://doi.org/10.1143/JJAP.48.03A035) — materiał progowy.
19. [Bruder, Fäcke, Rölle, Polymers 9, 472 (2017)](https://doi.org/10.3390/polym9100472) — Δn₁ = 0,0065–0,0090 dla wariantów fotoinicjatora w badanej żywicy (tab. 3); nie są pomiarem Δn w stosie C2.
20. [Curtis & Psaltis, Appl. Opt. 33, 5396 (1994)](https://doi.org/10.1364/AO.33.005396) — film transmisyjny; w 100-godzinnym odczycie zachodzi wybielanie, więc praca nie potwierdza warunku 4.
21. [Wahlstrand, Cheng, Milchberg, PRA 85, 043820 (2012)](https://doi.org/10.1103/PhysRevA.85.043820) — n₂ powietrza.
22. [Kogelnik, Bell Syst. Tech. J. 48, 2909 (1969)](https://doi.org/10.1002/j.1538-7305.1969.tb01198.x) — teoria fal sprzężonych.

Dodane po drugim audycie: [Blanche, Mahamat, Buoye, Materials 13, 5498 (2020)](https://doi.org/10.3390/ma13235498). Praca podaje Δn = 0,03 „per the manufacturer’s specifications” i cytuje karty Covestro: „Bayfol HX200 Description and Application Information” (2018) oraz „Bayfol HX200 Technical Data Sheet” (2020). Samych kart nie udało się pobrać.

Źródła słabsze, oznaczone w tekście: preprint Ou i in., arXiv:2601.09963 (2026); preprint Koller i in., [arXiv:2609.17787](https://arxiv.org/abs/2609.17787) (2026); patenty US 6,020,985 i US 8,343,608; materiały konferencyjne Shams Lahijani i in., Proc. SPIE 12574, 1257403 (2023), [arXiv:2304.03059](https://arxiv.org/abs/2304.03059), źródło grubości przekładki 51 µm. Funkcja CIE 1924 V(λ) pochodzi z pakietu colour-science.
