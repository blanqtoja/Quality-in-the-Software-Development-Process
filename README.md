# QitSDP - wspólne testy API i UI Manufacturing ERP

Projekt korzysta z jednego stosu **Python + pytest + Playwright** i wspólnego POM
w `tests/pages/`. Nowa implementacja dotyczy wyłącznie 4 testów UI Łukasza.
Istniejące 8 API + 4 UI Aleksandra przejęto bez zmian z `main` (`af43160`).
Łączny katalog zespołu: **16 API + 8 UI**.

- [Nadrzędny Plan Testów](PLAN_TESTOW_API_UI.md)
- [Wspólny katalog przypadków](PRZYPADKI_TESTOWE_API.md)
- [Raport zmian i usuniętych rozbieżności](reports/RAPORT_ZADANIE_3.md)
- [Lista pozostałych prac](TODO.md)
- [Bieżący raport integracji main z V2](reports/RAPORT_MERGE_MAIN_V2.md)

## 1. Instalacja i weryfikacja

Python 3.12+; PowerShell w katalogu repozytorium:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe tools/check-test-plan.py

# Zebranie przypadków bez ich wykonania:
.\.venv\Scripts\python.exe run_tests.py --suite lukasz --layer frontend --collect-only
.\.venv\Scripts\python.exe run_tests.py --suite all --layer frontend --collect-only
.\.venv\Scripts\python.exe run_tests.py --suite all --layer all --collect-only
```

Oczekiwany zakres kolekcji: 4 UI Łukasza, 8 UI zespołu i 24 przypadki API/UI zespołu.
Kontrola `tools/check-test-plan.py` działa bez instalacji pytest i sprawdza strukturę,
ID, autorstwo oraz spójność Markdown/DOCX; nie jest wykonaniem testów.

## 2. Wykonanie na rzeczywistym ERP

```powershell
.\.venv\Scripts\python.exe run_tests.py --suite lukasz --layer frontend --backend-mode live --base-url http://localhost:8080 --frontend-url http://localhost:8081
.\.venv\Scripts\python.exe run_tests.py --suite all --layer frontend --backend-mode live --base-url http://localhost:8080 --frontend-url http://localhost:8081
.\.venv\Scripts\python.exe run_tests.py --suite all --layer all --backend-mode live --base-url http://localhost:8080 --frontend-url http://localhost:8081
```

Podaj rzeczywiste adresy backendu i frontendu tego samego środowiska. `live`
przerywa wykonanie, jeśli ERP jest niedostępny. Jawny adres frontendu nie może być
łączony z oddzielnym backendem referencyjnym. Wyniki na modelu referencyjnym nie
potwierdzają działania Spring Boot ani PostgreSQL.

Bez `--frontend-url` można korzystać ze wspólnego serwera SPA z `main`: wymaga
zbudowanego React w `ERPSystem/frontend/dist` albo w `ERP_FRONTEND_DIST`.
`--backend-mode reference` jawnie wybiera model w pamięci; domyślne `auto` zachowuje
automatyczne wykrywanie backendu z `main`. Faktyczny tryb trafia do metadanych HTML.

Pozostałe opcje: `--ui-channel chrome|msedge|chromium`, `--headed`,
`--html-report reports/test_report.html`. `--layer ui` jest aliasem `frontend`,
a `--ui-base-url` aliasem `--frontend-url`. Domyślny zestaw pozostaje zgodny
z `main` (Aleksander); swoją część uruchamiaj przez `--suite lukasz`.

## 3. Zakres Łukasza i dane

| ID | Scenariusz | Cel |
|---|---|---|
| TC-UI-LM-01 | SC-IAM-01 | GUEST widzi konkretny kod i nazwę kontrahenta z API, ale nie może go tworzyć |
| TC-UI-LM-02 | SC-GL-03 | Nieistniejący wpis do storna daje 404 i komunikat błędu, bez formularza odwrócenia i bez POST |
| TC-UI-LM-03 | SC-P2P-01 | Niekompletna pozycja zakupu jest odrzucana w formularzu bez POST |
| TC-UI-LM-04 | SC-REP-01 | Tabela bilansu próbnego prezentuje wartości otrzymane z API |

Drugi test zastępuje powielony przypadek niezbilansowanego dekretu. Czwarty pokrywa
wyłącznie bilans próbny, podczas gdy test Aleksandra sprawdza Dashboard Hero Check.
Wymagane są konta demonstracyjne z `tests/config.py`, kontrahent, dostawca,
niepusty bilans oraz brak wpisu 999999999. Używaj wydzielonej bazy: istniejące
testy Aleksandra tworzą partnera i księgują dekret. Nowe UI Łukasza nie tworzy
dokumentów; logowanie może zmieniać sesje i log audytowy.

## 4. Dokumentacja i identyfikatory

Standard: `TC-{API|UI}-{AK|LM}-{NN}`. ID scenariuszy `SC-*` są odrębne.
Tabele w Markdown i obu plikach Word są generowane z `docs/test_cases.json`:

```powershell
.\.venv\Scripts\python.exe tools/build-test-plan.py
.\.venv\Scripts\python.exe tools/check-test-plan.py
```

Generator przejmuje style Worda z zapisanej wersji `main`. Opcja `--markdown-only`
nie wymaga python-docx. Historycznych raportów wykonania nie renumeruje się ani
nie traktuje jako wyników nowej implementacji.

Bieżąca kontrola potwierdziła statycznie 24 przypadki i spójność dokumentacji.
Nie zebrano ani nie wykonano nowej suity Pythona: brakuje pytest/httpx/playwright.
Dokumenty Word zweryfikowano strukturalnie, ale podgląd stron jest zablokowany
brakiem LibreOffice. Szczegóły ograniczeń są w raporcie.
