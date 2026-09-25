# Audyt, plan i decyzje projektowe

Dokument opisuje stan na 25.09.2026. Ceny i możliwości API sprawdzono w oficjalnej dokumentacji
Google AI for Developers pobranej tego dnia (strony `pricing`, `models/gemini-3.8-live`, `live-api/*`,
`speech-generation`, `audio`, referencja WebSocket `api/live`).

## 1. Audyt — co dało się sprawdzić, a czego nie

| Element | Stan |
|---|---|
| Folder `SO_101_arm`, jego zależności i uruchamianie MuJoCo | **niesprawdzone** — praca odbyła się w chmurowym sandboksie (Linux), bez dostępu do laptopa. Na koncie GitHub był tylko publiczny `OpenAi-is-the-best`. |
| Model ramienia | oficjalny SO-101 z MuJoCo Menagerie (`robotstudio_so101`, 23.09.2026, Apache-2.0), pochodna `so101_new_calib.xml` TheRobotStudio; zakresy przegubów i serwa STS3215 z modelu |
| Wersje bibliotek | Python 3.12, mujoco 3.14.0, numpy 2.5.3, opencv-python 5.0.0, google-genai 2.25.0, sounddevice 0.5.6 (najnowsze w PyPI tego dnia) |
| macOS | niesprawdzony w praktyce; uwzględnione ograniczenia: okna OpenCV i render w głównym wątku, `mjpython` dla interaktywnego viewera (tu niepotrzebny), zgody na kamerę i mikrofon, CGL jako domyślny kontekst GL MuJoCo |
| Kamera, mikrofon, głośniki, klucz API | brak w sandboksie; zastąpione urządzeniami wirtualnymi i fałszywym serwerem Live |

Założenia wymagające potwierdzenia na laptopie: działanie `SpeakerOutput`/`MicInput` z CoreAudio,
kąt widzenia kamery (`CAMERA_HFOV_DEG=70`), sprzężenie akustyczne głośnik–mikrofon MacBooka,
rzeczywiste opóźnienie Live API, jakość polskiego głosu, zgodność rozliczeń z licznikiem.

## 2. Plan i architektura

```
 kamera ─► YuNet ─► FaceTracker ──(15 Hz, lokalnie)──────────────┐
   └──► VisionUplink (1 klatka po prośbie „spójrz”) ─────────┐    │
 mikrofon ─► VAD ─► bramka echa ─► detektor muzyki           │    ▼
                     │                                        │  stan robota ◄── dziennik
                     ▼                                        ▼    │
           ConversationBackend  (gemini-3.8-live | lokalny skrypt)│
             │ audio 24 kHz        │ prośby (enum)                ▼
             ▼                     └──► planista ─► arbiter ─► bezpieczny sterownik ─► MuJoCo
        bufor odtwarzania ──(obwiednia w chwili wyjścia)──► szczęka     (100 Hz)
```

- **Granice folderu:** wszystko w `SO_101_expressive/`, własne `.venv`, zasoby dołączone, brak
  importów z `SO_101_arm`, jedynym punktem styku jest opcjonalny `MJCF_PATH`.
- **Kolejność prac:** ruch i symulacja (sterownik, kinematyka, chwyt) → wejścia audio/wideo →
  rozmowa i budżet → aplikacja i panel → scenariusze → demo bez urządzeń z nagraniem.
- **Ryzyka:** echo głośników (największe), koszt narastającego kontekstu Live, stabilność chwytu
  w fizyce, fałszywe wykrycia muzyki, opóźnienie szczęki, różnice macOS.
- **Weryfikacja:** testy własności sterownika, scenariusze na pełnej pętli z wirtualnym audio,
  fałszywy serwer na typach SDK, ewaluacja detektora muzyki na prawdziwych nagraniach, YuNet na
  prawdziwym portrecie, demo 66 s z dziennikiem przejść i nagraniem.
- **Poza zakresem teraz:** sterownik prawdziwych serw, systemowe usuwanie echa macOS
  (AVAudioEngine voice processing), percepcja obiektów z kamery (kostka jest lokalizowana z symulacji),
  wariant B rozmowy, uczenie polityk.

## 3. Rozmowa: wariant A (Gemini 3.8 Live) kontra B (STT → Flash-Lite → TTS)

| Kryterium | A: `gemini-3.8-live` | B: `gemini-3.5-transcribe-live` → `gemini-3.5-flash-lite` → `gemini-3.8-flash-lite-tts` |
|---|---|---|
| Wsparcie funkcji | jeden WebSocket: audio→audio, wbudowany VAD i przerwania, asynchroniczne wywołania funkcji (`NON_BLOCKING` domyślnie, `SILENT`/`WHEN_IDLE`/`INTERRUPT`), transkrypcje, obraz, kompresja kontekstu, wznawianie sesji | trzy usługi; STT strumieniowe z wynikami pośrednimi; LLM z wywołaniami funkcji; TTS strumieniowe (surowy PCM 24 kHz) |
| Cennik (USD/1M tokenów) | wejście: audio 3,00 (≈0,005 $/min), obraz 1,00, tekst 0,75; wyjście: audio 12,00 (≈0,018 $/min), tekst 4,50. **Kontekst naliczany ponownie w każdej turze**, transkrypcje dopłatą; proactive audio (stałe w 3.8) nalicza wejście przez cały nasłuch | STT ≈0,009 $/min; Flash-Lite 0,30 / 2,50; TTS Flash-Lite 0,50 tekst / 6,00 audio (≈0,009 $/min mowy, cena promocyjna do 31.12.2026, potem ×2) |
| Szacunek minuty rozmowy* | ≈0,06–0,11 $ (0,22–0,40 zł); dominuje ponowne naliczanie kontekstu audio | ≈0,01–0,016 $ (0,04–0,06 zł); historia jest tanim tekstem |
| 130 zł starcza na* | ≈5–10 godzin aktywnej rozmowy | ≈35–55 godzin |
| Opóźnienie | najniższe (natywne audio→audio, bez rozumowania w 3.8 Live) — **niezmierzone tutaj** | suma trzech etapów, szacunkowo 1–2 s do pierwszego dźwięku — **niezmierzone** |
| Jakość polskiego | polski na liście 99 języków Live; natywny głos | STT 85+ języków; TTS ma polski; głos syntetyczny z tekstu |
| Przerwanie | serwer wysyła `interrupted`; przy głośnikach laptopa potrzebna lokalna bramka echa | pełna kontrola lokalna; ta sama bramka potrzebna dla STT |
| Synchronizacja dźwięku z ruchem | identyczna — szczęka czyta bufor odtwarzania, nie tekst | identyczna; dodatkowo tekst przed dźwiękiem ułatwia planowanie gestów |

\* Założenia: 40% czasu mówi użytkownik, 40% robot, ok. 4 tury na minutę; w A kompresja okna
12k→4k (średnio 4–8k tokenów kontekstu w turze). Liczby są przybliżeniem do weryfikacji na rachunku.

**Decyzja:** na pierwszy prototyp wariant A. Ma najniższe opóźnienie, wbudowane przerwania i wywołania
funkcji oraz najprostszą integrację, a do tego jest preferencją z briefu. Koszt kontroluje limit sesji
i limit całkowity, kompresja kontekstu, rozłączanie przy bezczynności i VAD. Jeśli budżet okaże się
wąskim gardłem, wariant B jest 7–10 razy tańszy. Wystarczy go zaimplementować jako kolejny
`ConversationBackend` (te same zdarzenia `AudioChunk`, `TurnStarted`, `TurnComplete`, `Interrupted`,
`IntentRequest`), bez zmian w planiście, arbitrze i sterowniku.

Nie obiecuję fine-tuningu Gemini Live — w dokumentacji Live API nie znalazłem takiej możliwości.

## 4. Stan robota i reguły pierwszeństwa

Czynności (`state.Activity`): słucha, mówi, odtwarza audio, śledzi rozmówcę, wykonuje gest, tańczy,
sięga po obiekt, trzyma obiekt, zatrzymany, bez chmury. „Mówi” (tura modelu trwa) i „odtwarza audio”
(próbki faktycznie wychodzą z głośnika) to osobne czynności. Przy opcji milczenia robot mówi,
ale niczego nie odtwarza. Każda zmiana pól stanu trafia do `runtime/logs/state-*.jsonl`.

| Warstwa (od najważniejszej) | Steruje | Wstrzymuje |
|---|---|---|
| awaryjny stop i limity | hamowanie wszystkich przegubów (2× przyspieszenie), zakresy, prędkości, prześwit | wszystko |
| utrzymanie obiektu | chwytak zamknięty od komendy chwytu do potwierdzonego zwolnienia | szczękę i gesty |
| cel manipulacyjny | całe ramię i chwytak (trajektorie minimum jerk, IK) | śledzenie, gesty, taniec |
| śledzenie rozmówcy | obrót podstawy i pochylenie nadgarstka | — |
| gesty i taniec | przesunięcia ramienia bez chwytaka | — |
| szczęka | chwytak w zakresie 0–0,45 rad | — |

Zmiana właściciela ramienia jest przenikana w 0,8 s, więc przejście np. z manipulacji do śledzenia
nie powoduje skoku. Przerwanie wygasza gest w 0,3 s, a szczęka zamyka się w rytmie limitów sterownika.

## 5. Chwyt: komenda, kontakt, potwierdzenie

W symulacji: siły normalne kontaktu obu szczęk z kostką > 0,5 N (zmierzono ok. 40 N), zablokowany
chwytak (pozycja o > 0,08 rad od zadanej), po uniesieniu brak kontaktu kostki z podłożem i kostka
w odległości < 3,5 cm od punktu chwytaka. Utrata któregokolwiek warunku przez 0,15–0,3 s oznacza
wyślizgnięcie. Przy prawdziwym robocie nie będzie czujnika siły, więc źródłem będzie jawna estymacja
`estimate`. Serwo STS3215 raportuje pozycję, obciążenie i prąd; chwyt oznacza wtedy blokadę pozycji
przy zamykaniu plus wzrost obciążenia. Stan ma być pokazany z pewnością estymacji, nigdy jako pewny.

## 6. Weryfikacja — co przetestowano i z jakim wynikiem

| Sprawdzenie | Wynik |
|---|---|
| `pytest` (96 testów: jednostkowe i 7 scenariuszy z briefu) | 96/96 zaliczone |
| Sterownik: 3000 kroków losowych celów | zakresy, prędkości i przyspieszenia zawsze w limitach (test wykrył i pomógł usunąć błąd dyskretnego hamowania) |
| Chwyt w fizyce MuJoCo | komenda → kontakt → potwierdzenie → uniesienie ≈9 cm → odłożenie ≤3 cm od celu; także z 3 innych póz startowych, przy kostce przesuniętej o 1–1,5 cm i po 3-sekundowym awaryjnym stopie w trakcie zamykania chwytaka (czas stopu nie liczy się do limitów faz); przy mowie i przy e-stopie chwytak bez zmian. Drugie nagranie demo ujawniło błąd wyboru gałęzi IK (pół obrotu nadgarstka nad kostką), poprawiony preferencją ciągłości i testem regresyjnym |
| Szczęka a dźwięk | zmierzona pozycja szczęki zgodna z obwiednią dźwięku w chwili wyjścia: opóźnienie ≤ 40 ms, korelacja ok. 0,7 przy `JAW_LEAD_S=0.11` |
| Detektor muzyki na nagraniach | 7/8 utworów (w tym piosenka z wokalem) wykrytych po 4,8–10,5 s; 0/5 fałszywych alarmów na mowie (LibriSpeech, polski espeak-ng); szum biały i różowy, cisza: 0% |
| Bramka echa (symulowane echo) | 0 s mowy robota wysłanej do chmury; wejście w słowo wykryte w ok. 0,1–0,2 s |
| YuNet (OpenCV 5.0) na portrecie z domeny publicznej | wykrycie 0,92–0,94; pusty i silnie zaszumiony obraz — brak wykrycia |
| Backend Live na fałszywym serwerze z typami SDK | tura audio + gest, odmowa błędnego wywołania, przerwanie, utrata sieci z ponawianiem, zły klucz bez pętli, budżet wyłącza API, GoAway ze wznowieniem, rozłączenie przy bezczynności |
| Demo wirtualne 66 s (wszystkie warstwy razem, polska mowa z espeak-ng) | sekwencja stanów zgodna z planem i identyczna w kolejnych przebiegach; nagranie z dźwiękiem `docs/media/demo_virtual.mp4` (ścieżka zgodna w czasie z symulacją, sprawdzone testem) oraz podglądy GIF i JPG |
| `--check` w sandboksie | MuJoCo, render (OSMesa) i YuNet OK; kamera i audio niedostępne (brak urządzeń) |

**Niezweryfikowane:** kamera, mikrofon i głośniki MacBooka, render CGL na macOS, prawdziwe połączenie
z `gemini-3.8-live` (brak klucza), rzeczywiste echo i opóźnienia, jakość polskiego głosu, rachunek
Google względem licznika, detektor muzyki przez mikrofon laptopa, dowolny sprzęt SO-101.

**Znane ograniczenie:** lokalny VAD mierzy energię i nie odróżnia muzyki od mowy. Gdy gra muzyka,
pasek pokazuje „użytkownik mówi”, a w trybie `MIC_STREAM_MODE=vad` dźwięk muzyki trafia do chmury,
co zwiększa koszt wejścia audio (limity budżetu nadal obowiązują). Możliwa poprawka: nie wysyłać
dźwięku, gdy detektor muzyki jest pewny, a bramka echa nie widzi mowy ponad muzyką.

## 7. Czy potrzebny jest trening

Nie na tym etapie: pożądane zachowania osiągnięto stanem, planowaniem, gestami parametrycznymi i IK,
a testy pokazują, że działa to deterministycznie. Trening ma sens dopiero przy konkretnym niedosycie.

- **Gesty:** teleoperacja ramieniem wiodącym (LeRobot) lub ręczne klatki kluczowe → zapis przebiegów
  przegubów z etykietą intencji; uczenie małej polityki generującej przesunięcia z tekstu lub
  prozodii. Miara: oceny ludzi A/B względem gestów parametrycznych, zero naruszeń limitów.
- **Chwytanie:** dopiero z kamerą na nadgarstku; demonstracje (ok. 50–200 epizodów)
  i polityka typu ACT/diffusion z LeRobot. Miara: skuteczność chwytu na zestawie pozycji, liczba
  interwencji e-stop. Na M1 Max 32 GB mały model ACT jest wykonalny, większe polityki lepiej trenować w chmurze.
- Model językowy pozostaje bez fine-tuningu, sterowany promptem i narzędziami.

## 8. Następne kroki po złożeniu prawdziwego ramienia

1. Kalibracja serw w LeRobot i zapis zakresów; porównanie kierunków i zer z modelem `new_calib`
   (w razie różnic — mapowanie znaków i offsetów w adapterze, a nie w logice zachowań).
2. Adapter sprzętowy z tym samym kontraktem co `MujocoSim` (`apply`, `joint_q`, `grasp_evidence`),
   pisanie pozycji do STS3215 przez magistralę Feetech, odczyt pozycji, obciążenia i prądu;
   `grasp_evidence` ze źródłem `estimate`.
3. Pierwsze uruchomienie z `SPEED_SCALE=0.3`, fizycznym wyłącznikiem zasilania serw pod ręką
   i ograniczeniem momentu w serwach; test e-stopu i zatrzymania przy utracie komunikacji (watchdog).
4. Ponowny pomiar opóźnienia szczęki i dobranie `JAW_LEAD_S` z nagrania wideo i dźwięku.
5. Strojenie bramki echa na MacBooku (`BARGE_IN_RATIO`) albo przejście na systemowe AEC.
6. Przejrzenie zakresów ekspresyjnych i prześwitu pod kątem blatu i kabli; test gestów przy trzymaniu.
7. Porównanie licznika kosztów z rachunkiem AI Studio po kilku sesjach i korekta współczynników.
