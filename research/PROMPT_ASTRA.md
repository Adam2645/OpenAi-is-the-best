# Prompt przekazania: kontynuacja recenzji „kierunkowe odbicie światła w wybranej odległości z”

Przejmujesz projekt recenzji naukowej prowadzony dotąd przez innego agenta (24 iteracje, trzy audyty
zewnętrzne). Masz go kontynuować w tym samym trybie i z tym samym rygorem. Poniżej: (1) oryginalne
polecenie użytkownika, słowo w słowo, (2) zasady doprecyzowane później, (3) gdzie leży dorobek,
(4) stan wyników z liczbami, (5) błędy, których nie wolno powtórzyć, (6) narzędzia, (7) zadanie na teraz.
Pisz po polsku.

---

## 1. Oryginalne polecenie użytkownika (bez zmian)

```text
Jesteś recenzentem fizyki optycznej. Pracujesz iteracyjnie, ale każda iteracja
kończy się tylko jednym z trzech werdyktów: POTWIERDZONE, ODRZUCONE albo
NIEROZSTRZYGNIĘTE. Nie wolno Ci ogłaszać wynalazku, przełomu ani nowej nazwy
fizycznej, dopóki twierdzenie nie przejdzie testu dowodu.

CEL
Sprawdzić, czy da się zrobić kierunkowe odbicie wiązki światła widzialnego
od materii atomowej w wybranej odległości z, tak aby z tego powstał
jasny, adresowalny obraz 3D w powietrzu.

DEFINICJA SUKCESU, wszystkie warunki naraz
1. Odbicie jest kierunkowe: co najmniej 10% mocy wchodzącej wraca
   w stożek mniejszy niż 1 stopień, a nie w 4π.
2. Odległość z jest wybierana, nie tylko jedna stała wartość Bragga.
   Zmiana sterowania przesuwa płaszczyznę odbicia o co najmniej 10 µm
   bez zmiany barwy źródła.
3. Jasność: przy 1 mW sondy detektor w odległości 30 cm zbiera sygnał
   wyraźnie ponad szumem tła, z podanym SNR.
4. Układ nie niszczy własnego ośrodka w czasie 1 s: atomy nie są
   wygrzewane z pułapki, polimer nie jest wybielany.
5. Jest cytat do pomiaru albo jawne równanie z podstawionymi liczbami.
   Analogia, nazwa marketingowa i „wydaje się” nie liczą się.

ZAKAZY
- Nie nazywaj projekcji na szybie, wentylatorze ani mgle hologramem.
- Nie proponuj „odbicia od pojedynczych atomów w powietrzu” bez policzenia
  głębokości optycznej OD = N * σ / A.
- Dla światła rezonansowego używaj σ0 = 3λ²/(2π), chyba że podasz inne
  przejście i uzasadnisz przekrój.
- Nie traktuj tablicy pęset optycznych jako wyświetlacza, dopóki nie
  porównasz liczby atomów z liczbą potrzebną do OD ~ 1 i nie sprawdzisz,
  czy odstęp atomów spełnia 2d sinθ = nλ.
- Nie zapętlaj tej samej hipotezy. Po ODRZUCONE zapisz powód liczbowo
  i przejdź do następnego mechanizmu.
- Nie cytuj forów jako dowodu. Forum może tylko wskazać artykuł;
  dowodem jest pomiar, wzór albo recenzowana praca.

PROTOKÓŁ JEDNEJ ITERACJI
Krok 1. Wybierz jeden mechanizm z listy albo jeden nowy, jeśli podasz
        równanie rządzące.
        Lista startowa:
        A. Lustro Bragga z zimnych atomów w sieci 1D.
        B. Selektywne odbicie par przy dielektryku.
        C. Hologram objętościowy / objętościowa siatka Bragga.
        D. Metapowierzchnia jako cienki modulator fazy.
        E. Tablica pojedynczych atomów w pęsetach jako „piksele”.
        F. Rozpraszanie kolektywne gęstej chmury zimnych atomów.
Krok 2. Wypisz wielkości: λ, d albo z, θ, N, A, OD, oczekiwane R.
Krok 3. Porównaj z co najmniej jednym pomiarem. Podaj autorów, rok
        i liczbę z pracy, nie ogólnik.
Krok 4. Test zabójczy: która z pięciu warunków sukcesu pada i przy jakiej
        liczbie.
Krok 5. Werdykt. Jeśli POTWIERDZONE tylko dla części warunków, napisz
        dokładnie które i nie uogólniaj na „hologram w powietrzu”.
Krok 6. Jedno następne pytanie, które da się rozstrzygnąć pomiarem
        albo rachunkiem. Potem stop. Nie dopisuj spekulacji.

FORMAT ODPOWIEDZI
Mechanizm:
Liczby:
Dowód:
Test zabójczy:
Werdykt: POTWIERDZONE | ODRZUCONE | NIEROZSTRZYGNIĘTE
Następne pytanie:

PUNKT STARTOWY, już policzony, nie odkrywaj go od nowa
Odbicie Bragga od sieci ⁸⁷Rb jest POTWIERDZONE jako lustro,
nie jako wyświetlacz: R do około 0,8 przy dostrojonym okresie sieci
blisko 780,8 nm. Warunek 2 pada, bo z jest skwantowane okresem sieci,
a nie dowolnie adresowane. Warunek na tablicę pęset jako piksele
pada ilościowo: σ0(780 nm) ≈ 2,9e-13 m², więc 1 mm² przy OD = 1
wymaga około 3e9 atomów, a największe tablice mają kilka tysięcy
i są trzymane daleko od rezonansu.

PIERWSZE DOZWOLONE PYTANIE
Czy da się multipleksować wiele siatek Bragga w jednym ośrodku
tak, aby każda odbijała inną głębokość przy tej samej λ, i jaki
jest limit liczby takich warstw zanim sprawność spadnie poniżej 10%?
Szukaj w holografii objętościowej i multipleksowaniu kątowym,
nie w science fiction.  masz sie zapętlać wysyłać pod agentów stawiać hipotezy i tak w kółko /goal
```

Uwaga: liczba „około 3e9 atomów” w punkcie startowym jest błędna o czynnik ~1000. Poprawnie
N = OD·A/σ₀ = 10⁻⁶ m² / 2,907·10⁻¹³ m² = 3,44·10⁶ (ujęte w sekcji Korekty raportu).

## 2. Zasady doprecyzowane później (obowiązują tak samo jak oryginał)

Tryb pracy:
- Pracuj w pętli iteracji: hipoteza → rachunek lub źródło → werdykt → jedno następne pytanie → kolejna
  iteracja. „Nie zapętlaj” znaczy: nie wracaj do odrzuconej hipotezy bez nowej liczby. Do przeszukiwania
  literatury i niezależnych rachunków używaj podagentów równolegle, jeśli je masz.
- Wyniki prowadź jako **referat naukowy** („zrób taki referat naukowy, czego dowiodłeś”): co wykazano,
  czego nie, z liczbami i źródłami. Każdą iterację dopisuj do referatu jako nową sekcję
  (dotąd: „Aneks C2-Laminat: hipotezy wdrożeniowe (iteracje 15–24)”) i do dziennika.
- Użytkownik przysyła audyty i propozycje hipotez. Każdy punkt audytu najpierw sprawdź (rachunkiem albo
  w pełnym tekście źródła), dopiero potem przyjmij albo odrzuć z liczbą. Propozycje użytkownika
  traktuj jak hipotezy, nie jak fakty; w it. 18 soczewka polowa, 16 warstw i multipleksowanie azymutalne
  padły na rachunku.

Rygor (z trzech audytów):
- **Stożek 1° to pełny kąt wierzchołkowy**: półkąt 0,5°, NA ≤ sin 0,5° = 0,0087, 2,39·10⁻⁴ sr.
- **POTWIERDZONE wymaga pomiaru.** Jawne równanie z niezmierzonymi parametrami daje tylko
  „spełnia w modelu” (werdykt NIEROZSTRZYGNIĘTE). **ODRZUCONE wymaga górnego ograniczenia**:
  strukturalnego, z przyjętej definicji albo ze zmierzonej mocy całkowitej. Szacunek lub brak pomiaru
  daje NIEROZSTRZYGNIĘTE.
- Wykluczony jest mechaniczny przesuw stałego reflektora: lustro na stoliku piezo spełnia dosłownie
  warunki 1–5, więc pięć warunków nie koduje „obrazu 3D”. Dopuszczalny jest przesuw materii polami.
- R siatki ≠ moc w stożku. Licz moc w stożku u widza: odbicia Fresnela na powierzchniach powietrze/szkło
  (dla właściwej polaryzacji), transmisję warstw po drodze w obie strony, rozbieżność wiązki.
- Sonda: 1 mW w wiązce 1 mm (127 mW/cm²). Doprecyzowanie warunku 3: SNR = średnia/odchylenie w 1 s,
  detektor Si 1 cm², filtr 532 ± 5 nm, tło przy wyłączonym kanale. Warunku 4: zmiana R < 1% w 1 s
  ciągłego odczytu (polimer); ubytek atomów < 10% i spadek R < 10% w 1 s (atomy).
- „Efektywna głębokość odpowiedzi” (centroid, opóźnienie grupowe) to nie płaszczyzna materii. Podawaj
  obie, z definicjami.
- Źródła: liczby sprawdzaj w pełnym tekście; Crossref potwierdza tylko bibliografię, nie liczby.
  Preprinty, patenty, karty producentów oznaczaj jako słabsze. Liczby z rysunków oznaczaj jako odczyt
  z wykresu. Czego nie sprawdziłeś, napisz wprost, że nie sprawdzono.
- Żadnych słów „przełom”, „wynalazek”, nowych nazw zjawisk. Nie nazywaj projekcji hologramem.

## 3. Gdzie jest dorobek

- Repozytorium: `https://github.com/Adam2645/OpenAi-is-the-best`, gałąź `claude/charming-galileo-wk6m37`,
  katalog `research/`.
  - `referat.md` — pełny referat (eksport z dokumentu Claude Docs, stan po iteracji 24; jest też `referat.pdf` w paczce zip). Oryginał
    w Claude Docs jest prywatny; jeśli nie masz do niego dostępu, prowadź dalej `referat.md`.
  - `recenzja-odbicie-kierunkowe.md` — dziennik wszystkich iteracji 0–24 z liczbami.
  - `obliczenia.py` (T0–T9), `tmm_stos_siatek.py`, `tmm_audyt*_c2.py` (macierz przejścia, metryki osiowe),
    `iteracja15.py`, `iteracja16.py` (Kogelnik, przekładki), `rcwa.py` + `rcwa_walidacja.py` (RCWA),
    `iteracja17.py`, `iteracja17b.py`, `iteracja18.py`.
- Commituj każdą iterację z opisowym komunikatem. Push na tę gałąź tylko wtedy, gdy użytkownik na to
  pozwala: commity bieżącej iteracji zostawiaj lokalnie, aż użytkownik zatwierdzi wynik (tak było w it. 21–24). W razie wątpliwości pytaj. Nie zakładaj
  pull requesta bez prośby.

## 4. Stan wyników

Werdykty mechanizmów (13): **0 POTWIERDZONE, 5 ODRZUCONE, 8 NIEROZSTRZYGNIĘTE.**

| Mechanizm | Werdykt | Podstawa |
|---|---|---|
| B. Selektywne odbicie od pary przy oknie | ODRZUCONE | warstwa odbijająca to granica okna; przesuw in situ ≤ 2 µm |
| C1. Siatki multipleksowane we wspólnej objętości | ODRZUCONE | Δz = 0 przy zmianie kanału |
| D. Metapowierzchnia (ognisko w z) | ODRZUCONE | z definicji: w z nie ma materii |
| J. Cząstka w pułapce fotoforetycznej | ODRZUCONE | zmierzona moc w 4π ~nW przy 15–30 mW |
| K. Mikrohologramy (adresowanie ogniskiem) | ODRZUCONE | T2: stożek < 1° ⇒ DOF ≥ 14 mm |
| C2. Stos warstw siatek odbiciowych adresowanych kątem | NIEROZSTRZYGNIĘTE | tylko model; patrz niżej |
| G. Zwierciadło EIT w parze Rb | NIEROZSTRZYGNIĘTE | R ≈ 0,8 przy 250 µW (Bajcsy 2003), brak 1 mW i przesuwu |
| J+. Lusterko lewitowane akustycznie | NIEROZSTRZYGNIĘTE | brak pomiaru przechyłu (wymagane ≤ 0,15°); to jeden obiekt |
| N. Stos reflektorów przełączanych (CLC, H-PDLC) | NIEROZSTRZYGNIĘTE | brak pomiaru stożka i tła od elektrod |
| A. Lustro Bragga z zimnych atomów | NIEROZSTRZYGNIĘTE | brak pomiaru przy 1 mW |
| E. Pęsety jako piksele | NIEROZSTRZYGNIĘTE | tylko szacunek (0,42 nW na piksel 10 µm dla atomów niezależnych) |
| F. Rozpraszanie kolektywne, warstwa 2D | NIEROZSTRZYGNIĘTE | R = 0,58 (Rui 2020) przy s ≈ 3·10⁻⁴, nie 1 mW |
| H. Siatka gazowa zapisana laserem | NIEROZSTRZYGNIĘTE | 96% to dyfrakcja w transmisji (Michine & Yoneda 2020) |

Ograniczenia z zakresem (pełne równania w `referat.md`):
- T1: atom niezależny rozprasza ≤ ħωΓ/8 = 1,21 pW (Rb D2) ⇒ N ≥ 8,2·10⁷ dla 0,1 mW; nie dotyczy
  odpowiedzi kolektywnej.
- T2: woksel ogniskowy w stożku 1° ma DOF ≥ 2λ/NA² = 14 mm.
- T3: R ≥ 0,1 ⇔ Δn·L ≥ 0,1042λ = 55,5 nm; w obojętnym gazie 1 atm L ≥ 198 µm.
- T6: ~1,4 kanału kątowego na µm grubości warstwy (surowe).
- T9: stożek 1° daje w 30 cm plamkę 5,2 mm; oczy dzieli ~63 mm, więc stereo wymaga dwóch wiązek.
- 532 nm: 1 mW = 0,60 lm; 780 nm: 1,0·10⁻⁵ lm, więc linie Rb są dla oka praktycznie ciemne.

### Linia C2 → wyświetlacz (iteracje 15–24, wszystko to modele)

- It. 15: polaryzacja p usuwa tło z powierzchni (R_p ≤ 3,5% dla 17,7–58,9°), ale wymaga n₁ ≈ 0,02.
  Laminat (przekładki 51 µm, pol. p): sygnał 0,24–0,67, kroki głębokości 59–60 µm. Szczegół ≥ 30,5 µm
  na warstwie wynika z samego stożka 1°.
- It. 16: siatki **niesłantowane** odbijają każdą warstwę pod innym kątem (−17,4 … −59,2°), więc widz widzi
  jedną warstwę: odrzucone jako wyświetlacz 3D. Przekładki makroskopowe dają zafalowanie 36–64% przy
  stałej λ. Przekaźnik 4f odrzucony (Lagrange: M_z = M_x², akomodacja wymaga M_z ≲ 2). Lustro Rui i in.
  jest subradiacyjne (Γ = 4,04 MHz < Γ₀ = 6,06 MHz).
- It. 17 (RCWA, siatki **skośne**, L = 100 µm, n₁ = 0,002, n₀ = 1,5, λ = 532 nm, pol. p, wejścia 20°/22°
  wewnątrz, wyjście wzdłuż normalnej): η = 0,665 / 0,660; wyższe rzędy ≤ 3·10⁻⁷. **Cieniowanie**: z zasady
  wzajemności górna siatka jest dopasowana Bragga do wiązki biegnącej w górę wzdłuż normalnej i odbija
  w dół 66,5% wyjścia dolnej warstwy. Przepuszczalność tego „portu” T = 0,34 / 0,40 / 0,64 / 0,96 / 0,97
  przy odchyleniu 0 / 0,25 / 0,5 / 0,75 / 1,0° (powietrze). Szerokość widma odbicia 1,20 nm (FWHM).
  Źródło gaussowskie 1,5 nm obniża η do 63% szczytu (0,5 nm: 95%). Prążki przekładki 10 mm
  (OPD 29,6 mm) gasi już źródło 0,02–0,05 nm. Akceptacja kątowa ±0,5° (η 0,45 przy 0,5°, 0,0002 przy 1°),
  więc śledzenie źrenicy deflektorem na „kilka cm” odrzucone.
- It. 18: odchylenie wyjść o 1–2° na warstwę usuwa cieniowanie, ale w 30 cm rozsuwa wiązki o 7,9 mm na
  warstwę przy źrenicy 3,5 mm, więc nieruchome oko widzi jedną warstwę. Ograniczenie paraksjalne
  (Lagrange): x_p = A·x + B·α ⇒ D_app ≤ p/Θ; przy oglądaniu z 30 cm wachlarz wyjść Θ ≤ 0,67°
  (0,48° z wiązką 1 mm). **Soczewka polowa: ODRZUCONE** (x_p = f·tanα, te same 7,9 mm).
  **16 warstw: ODRZUCONE** (bez odchylenia dolny kanał ~5·10⁻⁸; z odchyleniem wachlarz 11°).
  **Multipleksowanie azymutalne: ODRZUCONE** (Kogelnik 3D zgodny z RCWA co do 0,002; odchylenie
  prostopadłe wymaga ≥ 5° zamiast 0,75°; obrót o 90° daje T = 0,296). RCWA w wachlarzu 0,45°:
  2 warstwy 0,623 / 0,356; 3 warstwy 0,623 / 0,239 / 0,146; 4 warstwy … / 0,099 / 0,063.
  **Limit: przy L = 100 µm jedno oko w 30 cm widzi najwyżej 3 warstwy po ≥ 10%.** Przy przekładkach
  1 mm (OPD 2,96 mm) prążki gasi dopiero źródło ≥ 0,11–0,15 nm. Głębia 16 mm w 30 cm to 0,169 D
  (rozmycie 2,0′) ≈ jedna głębia ostrości woksela w stożku 1°. Wiązka skolimowana nie daje bodźca
  akomodacji.
- It. 19 (`iteracja19.py`): siatki **1 mm**, n₁ = 2·10⁻⁴. Kogelnik 3D zgodny z RCWA co do 0,0012
  (~175 tys. plastrów, 11 s/rozwiązanie). Akceptacja wejścia 0,122° (pow., FWHM), widmo 0,122 nm;
  η ≥ 90% szczytu tylko w ±0,030 nm i ±0,030°. Źródło 0,01 / 0,05 / 0,11 / 1,5 nm: 100 / 95 / 75 / 8% szczytu.
  Port: T = 0,982 / 0,943 / 0,981 przy 0,10 / 0,12 / 0,15° (0,12° to listek boczny). **RCWA stosu 5 warstw,
  wyjścia −0,24 … +0,24° co 0,12°: 0,623 / 0,586 / 0,586 / 0,596 / 0,603 w stożku, obce światło w stożku 0,
  wszystkie 5 wiązek w jednej źrenicy 3,5 mm (99,3–100%)** — pierwszy model z 5 warstwami w jednym oku
  (NIEROZSTRZYGNIĘTE: model, brak pomiaru). Przy λ₀ ± 0,05 nm: 0,40–0,43. Stożek woksela w osi x ≤ 0,12°
  (akceptacja), w osi y do ±1,26°: bodziec akomodacji tylko w jednym południku (reakcji oka nie sprawdzono).
  Prążki przy przekładkach 1 mm i źródle 0,01 nm: V = 0,96, zafalowanie ≤ ±8% bez AR, ≤ ±0,5% z AR 0,25%.
  Pole widzenia jednego oka przy stożku 1°: ≤ 1,67° (≈ 8,7 mm płyty w 30 cm) — skutek samego warunku 1.
  **Kompensacja translacyjna (start w x = −D·tanθ): ODRZUCONE** — warstwy widać przesunięte o Δθ, łatki
  nakładają się tylko przy Δθ < 0,86°.
  Materiał (pełne teksty): PTR, odbiciowe VBG: L = 5,5 mm, Δn = 230 ppm, R > 99% (Ott 2013, Opt. Express 21,
  29620); L = 8,3 mm, Δn = 63 ppm, 98% przy 633 nm (Mhibik 2016, LSA 5, e16026); 4 VBG w szeregu po ~99,7%,
  > 750 W CW (Sevian 2008, Opt. Lett. 33, 384); maks. Δn ~10⁻³. Pomiary przy 1064 nm, nie 532 nm; odbiciowej
  VBG w PTR przy 532 nm z L i Δn w recenzowanej literaturze nie znaleziono. PQ:PMMA: Δn ≤ 1,16·10⁻⁴, skurcz
  0,09–0,4% (Hu 2022, ACS AMI 14, 21544) — 16–70× poza tolerancją λ Bragga.

- It. 20 (`iteracja20.py`, η uśredniona po widmie kątowym wiązki): oś x — η = 0,31 / 0,49 / 0,58 / 0,64 / 0,66 przy
  w₀x = 50 / 100 / 150 / 250 / 500 µm; oś y — 2w₀y ≥ 39 µm (stożek < 1°) i ≤ 58 µm (wypełnienie źrenicy).
  Pole widzenia jednego oka 0,86° × 1,67° (4,5 × 8,7 mm). Rzędy SLM trafiają w sąsiedni kanał przy skoku
  p = 10,9·m µm (potrzebny filtr Fouriera). **Bezpieczeństwo oka (ICNIRP 2013, Health Phys. 105(3):271–295,
  Tabela 5, tekst pierwotny):** pojedynczy impuls — zapas 15× (N = 100) / 39× (N = 1000); ciąg impulsów —
  Cp = 0,2, zapas 7,7×; **moc średnia w 10 s** — skanowanie jej nie zmniejsza; oko na ∞ skupia wiązki warstwy
  w jednym miejscu: treść w jednej warstwie → 0,60 mW = 1,54 granicy 0,39 mW („skanowanie daje Klasę 1
  przy 1 mW”: ODRZUCONE). Sonda ≤ 0,65 mW spełnia wszystkie kryteria. Błąd okresu δΛ/Λ = 1·10⁻⁴: korekta
  wejścia 0,054° przywraca η = 0,666 (RCWA 0,665), ale wyjście przesuwa się o ~0,9 × korekta; tolerancja
  praktyczna |δΛ/Λ| ≲ 1·10⁻⁴, skos ≲ 0,03°.
- It. 21 (`iteracja21.py`, oko zredukowane f = 17 mm, źrenica 3,5 mm, FFT pola w źrenicy): wiązka x
  (2w₀ = 0,3 mm) ma w 300 mm R = 359 mm (2,79 D), y (50 µm) 300 mm (3,33 D). Przy akomodacji na warstwę obraz
  woksla 300 × 50 µm: 2,03′ × 0,52′, kontrast sąsiednich woksli x 0,56, y 0,08 (skok 50 µm poniżej rozdzielczości
  0,64′; rozróżnialny ~90 µm → ~1,1 tys. woksli na warstwę na oko). **Przy akomodacji na ∞ obraz znika**
  (kontrast 0 w obu osiach). „Astygmatyczna kreska Sturma”: ODRZUCONE. Faza cylindryczna na wejściu
  (1 mm, f = −300 mm): η = 0,491, wergencja x 1,67 D zamiast 3,33 D — ODRZUCONE (w₀·θ ≥ λ/π). Warunek 3 przy
  sondzie 0,50 mW: SNR śrutowy 2·10⁷, z niestabilnością lasera 0,1% / 1% ≈ 10³ / 10² (model). Luminancja
  ~1,7·10⁸ cd/m² średnio po polu — wyświetlacz potrzebuje mocy o rzędy mniejszej.

- It. 22 (`iteracja22.py`): akomodacja kompromisowa 3,06 D — ODRZUCONE: wiązka y wypełnia źrenicę, błąd 0,27 D
  rozmywa ją o 3,2′ i kontrast y (skok 90 µm) spada z 0,90 do 0; optimum to akomodacja na warstwę (3,33 D, ±0,1 D).
  Projekcja warstwowa SLM/DMD (sonda 0,50 mW, T_SLM 0,65, 1100 woksli, 5 warstw): luminancja ~2,5·10⁷ cd/m²
  (1000 cd/m² daje już ~20 nW sondy); pełna warstwa 0,195 mW w źrenicy = 0,50 / 0,19 / 0,04 granicy ICNIRP.
  Plan próby: płytka A 20,0° → 0°, Λ = 180,07 nm, skos 10,00°; płytka B 22,0° → +0,10°, Λ = 180,67 nm, skos 10,97°;
  RCWA: kanały 0,623 / 0,609, port 0,982 (przy +0,12°: 0,585 / 0,943); stożek 1° = soczewka f = 200 mm + przesłona
  3,49 mm; warunek 2 przez przesunięcie punktu wyjścia ~0,77 mm na powierzchni (10 µm głębi ↔ 3,8 µm).
- It. 23 (`iteracja23.py`, filtr Bragga √η(θ) w torze): **korekta it. 21–22** — filtr poszerza woksel x (177 → 217 µm),
  kontrast przy skoku 300 µm: kolejno 0,30 (nie 0,56), jednocześnie w fazie 0,02 (nie 0,30). Kontrast kolejny
  dla w₀x = 100 / 150 µm przy skoku 400 µm: 0,89 / 0,70. Faza 0/π: kontrast 1,00 przez wymuszony ciemny prążek, η −10% —
  ODRZUCONE jako naprawa. Podramki DMD: kontrast niekoherentny przy 50% mocy; modulator fazy (0, potem π): 99% mocy.
  Losowa faza w y: ODRZUCONE. Deflektor: TBP = D·Δθ/λ = 3967 (8,7 mm, 13,9°); teleskop nie zmienia D·Δθ —
  ODRZUCONE; gęste kanały wejścia (skok 0,38° / 0,25° wewn.): pasmo 51 / 33 MHz, TBP 719 / 471, przesłuch
  4,7·10⁻³ / 5,1·10⁻³ sygnału (L = 1 mm). Dyskretne źródła (jeden laser + przełącznik 1×5) bez limitu TBP.
- It. 24 (`iteracja24.py`, L = 0,5–1,2 mm przy n₁·L = 0,2 µm): krok wyjść dobrany tak, by port w każdej
  wielokrotności kroku miał T ≥ 0,95 → warstw w 0,48°: 4 / 5 / 6 / 7 / 8 (nominalnie), 3 / 4 / 5 / 4 / 4 przy tolerancji
  ±0,02° (≈ błąd okresu 4·10⁻⁵). Woksel x po filtrze 183–237 µm; woksle x z kontrastem ≥ 0,5: 15 / 14 / 13 / 12 / 11.
  F = warstwy × woksle x × 96: nominalnie rośnie z L (5760 … 8448), z tolerancją maksimum **L_opt = 0,85 mm**
  (6240 woksli, 5 warstw, krok 0,110°). Wykres w referacie. Wzór funkcji celu od użytkownika nie dotarł — F przyjęto.

## 5. Błędy już popełnione — nie powtarzaj

- Mieszanie półkąta i pełnego kąta stożka (T2 liczone najpierw dla półkąta 1°).
- Przypisanie pracom liczb, których tam nie ma (Curtis & Psaltis: HRF-150 to film transmisyjny
  z wybielaniem; Bruder tab. 3 opisana błędnie; Zhou 2018 źle przypisany).
- Odrzucanie na podstawie szacunku zamiast górnego ograniczenia (A, E, F, H musiały wrócić do
  NIEROZSTRZYGNIĘTE).
- Używanie Γ_kol jako prostego mnożnika w bilansie fotonów.
- Rachunek TMM bez interfejsów z powietrzem (Fresnel do 16,7% przy 58,9°).
- **Ogłoszenie „okna 1–2°” w it. 17 bez sprawdzenia, czy wszystkie warstwy trafiają w jedną źrenicę.**
  Każdy wynik dla wyświetlacza sprawdzaj w płaszczyźnie oka (30 cm, źrenica ~3,5 mm).
- Kontrast woksli w it. 21–22 liczony bez filtru Bragga (zawyżony 0,56 zamiast 0,30) — każdy wynik
  obrazowania licz z polem odbitym przez siatkę.
- Miara przesłuchu, która liczyła sygnał kanału o tym samym kierunku jako przesłuch (poprawione
  w `iteracja17b.py`). Podawaj przesłuch i względem mocy sondy, i względem sygnału.

## 6. Narzędzia

- `rcwa.solve(lam, theta_deg, n_I, n_II, pol, layers, M, Lx)` — RCWA (Moharam 1995, metoda „enhanced
  transmittance”, TM z regułą odwrotności Li). Siatka skośna jako warstwa `{'kind': 'slanted', ...}` cięta
  na plastry. Walidacja w `rcwa_walidacja.py`: zgodność z TMM i Kogelnikiem, R + T = 1 do 10⁻⁶,
  niezależność od M = 3/5/7; 32 plastry na okres z (błąd ~0,1%).
- `iteracja17b.py`: `grating(theta_in, out_air, flip)`, `channel((stack, k, lam))` (moc kanału u widza
  z Fresnelem, transmisją w dół i portami w górę), `crosstalk(stack, lam)`.
- `iteracja18.py`: `kogelnik3d(rho_hat, K, pol_factor)` — szybki model 3D zwalidowany wobec RCWA;
  `pupil_capture(outs)`.
- `iteracja20.py`: `gauss_avg(f, θ0)` — średnia po widmie kątowym wiązki gaussowskiej; trzy kryteria ICNIRP.
- `iteracja23.py`: `reflect(E)` — pole odbite przez siatkę 1 mm (filtr √η(θ)); `contrast` dla par i rzędów woksli.
- `iteracja24.py`: `study(L)` — port, krok wyjść, woksel x, widmo i przesłuch dla danej grubości.
- `iteracja21.py`: `retina(Ex, Ey, A, x0, y0)` — natężenie na siatkówce dla pola w źrenicy i akomodacji A.
- `iteracja19.py`: `grating(theta_in, out_air, L, n1, flip)`, `channel((stack, k, lam, L, n1))`, `stray(...)`,
  `kog(rho_hat, G, lam, L, n1)` — Kogelnik 3D z długością fali i grubością jako parametrami.
- Koszt: jedno rozwiązanie RCWA dla L = 100 µm (~17,5 tys. plastrów) to ~1 s; czas rośnie liniowo z L.
  Dla grubych siatek licz Kogelnikiem 3D i sprawdzaj wybrane punkty RCWA. Wymagany tylko numpy.

## 7. Zadanie na teraz: Iteracja 25

Stan po it. 24: model stosu skośnych siatek PTR o grubości ~0,85 mm daje 5 warstw w jednej źrenicy (krok 0,110°,
odporny na ±0,02°), kanały 0,59–0,62 mocy sondy, ~6,2 tys. rozróżnialnych woksli na oko; warunek 3 w modelu;
Klasa 1 przy sondzie ≤ 0,65 mW. Wszystko to modele — brak pomiaru. Otwarte (jedno na iterację):
1. **Tolerancja wykonania (najważniejsze):** znajdź pomiar dokładności zapisu siatek PTR — rozrzut okresu i skosu
   (wymagane |δΛ/Λ| ≲ 4·10⁻⁵, skos ≲ 0,013°). Jeśli nie ma — ile warstw zostaje przy realnym rozrzucie i czy korekta
   kątem wejścia na kanał (it. 20) wystarcza.
2. **Siatka 0,85 mm przy 532 nm:** czy n₁ = 2,35·10⁻⁴ i skośny zapis odbiciowy przy 532 nm w PTR są zmierzone;
   absorpcja i stabilność w zielonym (warunek 4).
3. **Akomodacja na bodziec jednoosiowy:** pomiar reakcji oka na bodziec tylko w osi y (bez akomodacji obraz znika).
4. **Deflektor / przełącznik:** karta konkretnego urządzenia (TeO₂ o aperturze ≥ 8,7 mm i TBP ≥ 470–720) albo
   przełącznik światłowodowy 1×5 — straty i czas przełączania (nie sprawdzono).

Pytania pomiarowe (do laboratorium): dwie skośne VBG w szeregu przy 532 nm (plan z it. 22); obraz dwóch sąsiednich
woksli w ognisku soczewki f = 17 mm z aperturą 3,5 mm (model z filtrem: kontrast 0,30 przy skoku 300 µm, 0,70 przy 400 µm).

Kolejka otwartych pytań z referatu (sekcja „Otwarte pytania”): pomiar rzeczywistego laminatu C2;
adresowanie x–y w C2 (dwa woksle naraz); przechył lusterka J+ (≤ 0,15° rms w 1 s); zwierciadło EIT G przy
1 mW (R ≥ 0,1); stos przełączalny N (stożek < 1°, tło ≤ 1% sygnału).

Na koniec każdej iteracji odpowiedz w formacie:

Mechanizm:
Liczby:
Dowód:
Test zabójczy:
Werdykt: POTWIERDZONE | ODRZUCONE | NIEROZSTRZYGNIĘTE
Następne pytanie:

Potem dopisz iterację do `research/recenzja-odbicie-kierunkowe.md` i `research/referat.md`, zacommituj
i przejdź do następnego pytania.
