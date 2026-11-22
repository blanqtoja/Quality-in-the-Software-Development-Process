# Raport zadania 3 - Łukasz Murza, osoba 2

**ID:** JPWO-UI-LUK-2026-11-22. **Data:** 22.11.2026.
**Autor części:** Łukasz Murza (251592).
**Wersja bazowa repozytorium:** `8a1d9546fcd13affa208fee4d11c9bf1d7db5b52`.

## Zakres i wynik

Przygotowano wyłącznie część Łukasza: **UI-LUK-001..004**, czyli cztery opisane
i zaimplementowane przypadki UI oparte na scenariuszach zadania 1. Usunięto dodane
poza zakresem przypadki UI Aleksandra. Istniejące testy API obu osób zachowano.
Prowadzący zaakceptował GET/POST zamiast PUT/DELETE dla zadania 2.

Składnia, zgodność planu z kodem i kolekcja czterech testów są poprawne.
Testów nie wykonano na rzeczywistym ERP; wcześniejsza kontrola dostępności
zakończyła się `connect EACCES ::1:8081` przed rozpoczęciem przypadków.

## Podstawa i wykonane prace

Wykorzystano slajdy 4-5
[Zadanie_3_UI.pdf](https://chatgpt.com/library?file_id=libfile_dd1be252bf248191a1b3b2cc5a56ef72&account_id=personal),
scenariusze z `Plan_Testow_ERPSystem_Nowy.docx` i wzory planu/raportu oraz szablony
z katalogu `Zasoby/Zasoby`. Wymagane minimum to cztery przypadki na osobę;
ten raport ocenia wyłącznie realizację osoby 2.

| Wymaganie | Realizacja części Łukasza | Dowód |
|---|---|---|
| UI-W1: podstawa w zadaniu 1 | Przypisanie do SC-IAM-01, SC-GL-01, SC-P2P-01 i SC-REP-01 | `ui/cases.json`, tytuły testów i Plan Testów |
| UI-W2: minimum 4 opisane przypadki | Cel, priorytet, warunki, dane, kroki, oczekiwania i stan końcowy UI-LUK-001..004 | `PLAN_TESTOW_API_UI.md` |
| UI-W3: Plan Testów zawiera API i UI | Zachowane 16 istniejących przypadków API i dodane 4 UI Łukasza | `PLAN_TESTOW_API_UI.md` |
| UI-W4: implementacja planu | Cztery osobne testy | `ui/tests/lukasz.spec.cjs` |
| UI-W5: spójny wspólny projekt i wzorce | POM, fixtury, konfiguracja, raporty i runner API/UI | `ui/pages/`, `ui/support/`, `playwright.config.cjs`, `run_tests.py` |

Page Object Model oddziela interakcje z formularzami od przypadków testowych.
Każdy test używa nowego kontekstu przeglądarki, języka EN i rzeczywistego logowania.
Nie podmienia się odpowiedzi API ani nie przechodzi na symulator UI.
Wspólna infrastruktura pozostaje gotowa do późniejszej integracji pracy drugiej osoby.

## Aktualny stan przypadków

| Scenariusz | Przypadek | Sprawdzane zachowanie | Wynik wykonania |
|---|---|---|---|
| SC-IAM-01 | UI-LUK-001 | Odczyt kontrahentów dostępny dla guest, brak tworzenia | NOT RUN - niedostępne środowisko |
| SC-GL-01 | UI-LUK-002 | Niezbilansowany dekret blokuje przycisk, wyjaśnia przyczynę i nie wysyła POST | NOT RUN - niedostępne środowisko |
| SC-P2P-01 | UI-LUK-003 | Zamówienie zakupu bez kompletnej pozycji wyświetla błąd i nie wysyła POST | NOT RUN - niedostępne środowisko |
| SC-REP-01 | UI-LUK-004 | Bilans próbny pokazuje kwoty i status z rzeczywistej odpowiedzi API | NOT RUN - niedostępne środowisko |

Przypadek P2P obejmuje początkową walidację, a raportowanie bilans próbny.
Nie deklaruje się pokrycia całego cyklu zakupu ani pełnego uzgodnienia subledgerów.
Testy nie księgują dokumentów; logowanie może zmieniać sesje i rejestr audytowy.

## Weryfikacja i miary

| Kontrola | Wynik | Znaczenie |
|---|---|---|
| Planowanie i implementacja | 4/4 przypadków Łukasza | Minimum dla osoby 2 spełnione w kodzie i dokumentacji |
| Zgodność plan/kod/scenariusze | 4/4 | Potwierdzenie identyfikatorów, autorstwa i kompletności opisów |
| Playwright `--list` | 4 testy w 1 pliku | Kolekcja bieżącego zakresu zakończona poprawnie |
| Składnia JavaScript i Pythona | Poprawna | Źródła parsują się bez błędów |
| Wykonane ciała testów | 0/4 | Nie ma podstaw do wyliczania zdawalności |
| Ostatnia kontrola dostępności SUT | BLOCKED: EACCES | Historyczna próba przed zawężeniem zakresu, bez wykonania przypadków |

Po zawężeniu zakresu ponowiono kolekcję i kontrole lokalne. Nie ponawiano połączenia
z ERP: wcześniejsza kontrola `GET /login` na `http://localhost:8081` zakończyła się
`connect EACCES ::1:8081`, a próba przeglądarkowa `ERR_NETWORK_ACCESS_DENIED`.
To blokada środowiska wykonawczego, nie wynik testu ani dowód defektu ERP.
Zastane raporty w `reports/ui/` dokumentują tę wcześniejszą próbę, nie wykonanie
obecnego zestawu czterech testów.

Lokatory porównano ze źródłami
[ERPSystem, SHA 33b5df1](https://github.com/q86865511/ERPSystem/tree/33b5df13594bcb456ba8a3d20e0bc455ac79aa75).
Ich działanie w docelowej instalacji wymaga potwierdzenia pełnym uruchomieniem.

## Artefakty i pozostałe prace

- Plan: `PLAN_TESTOW_API_UI.md`; opisy: `ui/cases.json`.
- Implementacja: `ui/tests/lukasz.spec.cjs` oraz POM i fixtury w `ui/`.
- Kontrole: `tools/check-ui-plan.cjs`, `tools/build-test-plan.py`.
- Podsumowanie weryfikacji: `reports/UI_ZADANIE_3_WERYFIKACJA.json`.
- Instrukcja uruchomienia: `README.md`; otwarte prace: `TODO.md`.

Do potwierdzenia działania części Łukasza pozostają: osiągalna instancja ERP,
kontrola kont i danych oraz rzeczywiste wykonanie UI-LUK-001..004 z raportem wyników.
Nie ocenia się ukończenia części Aleksandra.
