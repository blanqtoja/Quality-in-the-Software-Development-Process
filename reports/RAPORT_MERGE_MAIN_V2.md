# Raport integracji main z feat/moje-testy-UI

## 1. Wynik i stan Git

Stan na 22.11.2026. Poprawiono treść wszystkich 11 konfliktujących plików.
Weryfikacja statyczna zakończyła się powodzeniem. **Merge nie został zakończony:**
środowisko pozwala wyłącznie odczytywać `.git`, dlatego próba `git add` zakończyła
się kodem 128: `Unable to create .../.git/index.lock: Permission denied`.
Git nadal oznacza 11 ścieżek jako `unmerged`, mimo poprawnej treści plików roboczych.
Nie utworzono nowego commita ani nowego SHA. Nie wykonano pushowania.

| Właściwość | Wartość |
|---|---|
| Gałąź | `feat/moje-testy-UI` |
| HEAD, wersja V2 Łukasza | `37339aa0f0b02907517ede1de68162d76a9caa74` |
| MERGE_HEAD, integrowany main | `af43160fc201760d3d49d66c8f6a4a2b615c9ed0` |
| Konflikty treści w plikach roboczych | 0 znaczników konfliktów |
| Konflikty nierozliczone w indeksie | 11, wymagają udanego `git add` |
| Nowy merge commit | Nie powstał, zapis do indeksu zablokowany |

Nie uruchamiano ponownie merge'a, nie przerywano go, nie resetowano repozytorium
i nie usuwano gałęzi. Zachowano również zmiany automatycznie połączone przez Git:
usunięcie śledzonych plików bytecode Pythona i historyczny raport HTML z main.
Ten HTML nie stanowi wyniku bieżącej weryfikacji.

## 2. Rozwiązanie poszczególnych konfliktów

Każdy plik porównano osobno z wersjami w etapach 2 i 3 indeksu.
Nie używano globalnego `--ours` ani `--theirs`. W tych konkretnych konfliktach
zweryfikowane V2 stanowiło kompletną wersję wspólną lub rozszerzenie main,
dlatego zachowano jego treść po sprawdzeniu zgodności.

| Plik | Strategia i zachowana zawartość |
|---|---|
| `.gitignore` | Suma reguł obu gałęzi, bez powtórzeń. V2 zawiera wszystkie reguły main oraz `tmp/` i `reports/ui/`: Python, pytest, środowiska wirtualne, Playwright, pliki tymczasowe. |
| `PRZYPADKI_TESTOWE_API.md` | Zachowano pełny katalog V2 i odtworzono Markdown z `docs/test_cases.json`. Jest 24 przypadków; main zawierał tylko 12 ujednoliconych ID. Zachowano autorów, kroki, warunki i rezultaty. |
| `Plan_Testow_ERPSystem_Nowy.docx` | Zachowano bajtowo V2 po potwierdzeniu 16 API i 8 UI, zawartości wszystkich siedmiu kolumn i zgodności definicji stylów z main. |
| `Przypadki_Testowe_API_ERPSystem.docx` | Zachowano bajtowo V2 po analogicznej kontroli 24 przypadków i stylów main. |
| `run_tests.py` | Zachowano wspólną macierz zestawów i domyślne zachowanie main oraz rozszerzenia V2: alias `ui`, kolekcję bez wykonania, adresy środowiska, tryby backendu i wybór przeglądarki. |
| `tests/conftest.py` | Zachowano wszystkie fixtury API/UI z main oraz `purchasing_page`, `reporting_page`, metadane pochodzenia backendu i kontrolę rzeczywistego frontendu z V2. Parametr `request` służy wstrzyknięciu fixtury pytest, nie zmienia kontraktu klientów ani POM. |
| `tests/pages/__init__.py` | Zachowano wszystkie eksporty main oraz `PurchasingPage` i `ReportingPage`. |
| `tests/pages/base_page.py` | Zachowano wszystkie metody main i ich kontrakty; dodatkowo pozostawiono `record_post_requests` do kontroli braku zapisu w negatywnych testach LM. |
| `tests/pages/ledger_page.py` | Zachowano obsługę ręcznych dekretów AK i pozostałe metody main; dodatkowo pozostawiono `load_missing_reversal_entry` z V2. |
| `tests/pages/master_data_page.py` | Zachowano wszystkie metody main, w tym wyszukiwanie w tabeli i formularze; dodatkowo pozostawiono `expect_partner_read_only`. |
| `tests/test_frontend_lukasz.py` | Zachowano cztery rzeczywiste testy V2 zamiast pustej klasy z main. Nie przywrócono JavaScript ani testu niezbilansowanego dekretu Łukasza. |

Z main zachowano źródła wszystkich 12 testów Aleksandra i wspólną architekturę
Python/pytest/Playwright/POM. Z feature zachowano V2 Łukasza, rozszerzenia POM,
obsługę runnera, wspólny rejestr i kompletne dokumenty.
W tej integracji **nie zmieniono logiki żadnego testu**. Testy Aleksandra są
identyczne bajtowo z MERGE_HEAD; wszystkie 59 istniejących metod POM main
ma identyczne drzewa składniowe. API Łukasza zachowuje wcześniejszą logikę;
ujednolicenie jego ID i nazw funkcji nastąpiło już w V2.

## 3. Liczba przypadków i odrębność UI

| Autor | API | UI | Razem |
|---|---:|---:|---:|
| Aleksander Kaźmierczak (AK) | 8 | 4 | 12 |
| Łukasz Murza (LM) | 8 | 4 | 12 |
| Łącznie | 16 | 8 | 24 |

Są to liczby potwierdzone statycznie w kodzie i dokumentacji, **nie wynik kolekcji pytest**.
Każda funkcja ma właściwy znacznik autora i unikalny identyfikator.

| Przypadek UI | Odrębny cel biznesowy |
|---|---|
| `TC-UI-AK-01` | Dashboard: uzgodnienie Hero, podksiąg i kont przejściowych. |
| `TC-UI-AK-02` | GUEST: brak uprawnień do Audit Trail, ekran 403 i powrót na Dashboard. |
| `TC-UI-AK-03` | ADMIN: utworzenie kontrahenta przez formularz i potwierdzenie zapisu. |
| `TC-UI-AK-04` | Blokada niezbilansowanego dekretu, poprawienie kwot i księgowanie. |
| `TC-UI-LM-01` | GUEST: odczyt konkretnego kontrahenta i brak akcji tworzenia. |
| `TC-UI-LM-02` | Nieistniejący wpis do storna: GET 404, komunikat błędu, brak formularza i POST. |
| `TC-UI-LM-03` | Niekompletne zamówienie zakupu: komunikat walidacji, otwarty formularz, brak POST. |
| `TC-UI-LM-04` | Raportowanie: zgodność tabeli bilansu próbnego, sum i statusu z odpowiedzią API. |

Wspólna rola GUEST lub obszar księgowości nie oznacza powtórzenia przypadku.
LM-02 pokrywa ujemną ścieżkę SC-GL-03, a nie całe udane storno.
LM-04 pokrywa prezentację bilansu w SC-REP-01, a nie uzgodnienie Dashboard Hero.
Powiązania ze scenariuszami zadania 1 pozostają w rejestrze i wspólnych tabelach.

## 4. Weryfikacja

| Kontrola | Wynik |
|---|---|
| `git diff --check` | OK, bez błędów białych znaków w plikach roboczych. |
| `git diff --cached --check` | OK dla zmian dostępnych w indeksie; nie oznacza zakończenia merge'a. |
| Znaczniki konfliktów | 0 w śledzonych plikach tekstowych. |
| Składnia Pythona | OK, 27 modułów, bez generowania bytecode. |
| Importy wewnętrzne | OK, 50 instrukcji importu: istnieją moduły i importowane symbole. |
| Zależności fixtur | OK, 75 zależności rozwiązywanych statycznie. |
| Kontrakty POM main | Zachowano 59 istniejących metod bez zmian. |
| Runner | Poprawne parsowanie 12 kombinacji suite/layer, aliasu ui, URL-i, kolekcji i trzech trybów backendu; właściwe ścieżki plików. |
| `tools/check-test-plan.py` | OK, 24 przypadki: ID, właściciele, warstwy, Markdown, DOCX i zachowanie testów AK. |
| Jedna infrastruktura UI | Python/pytest/Playwright; brak package.json, konfiguracji Playwright Test i testów CJS w ui. |
| Próba kolekcji pytest | ZABLOKOWANA, kod 4: `Missing dependency: pytest`. Brakuje też httpx, playwright i pytest-html. |
| Wykonanie API / UI E2E | NOT RUN; 0 wykonanych przypadków, brak wyniku PASSED/FAILED. |
| Dostępność ERP | Niepotwierdzona: próby połączenia z lokalnymi portami 8080/8081/5173 zablokowane przez PermissionError; brak lokalnego builda React. |

Nie instalowano zależności, nie pobierano przeglądarek i nie korzystano z uprawnień
administratora. Braku kolekcji nie zastąpiono symulowanym wynikiem pytest.
Tryb `live` nie przechodzi na backend referencyjny. Model referencyjny jest jawnie
opisany w dokumentacji i metadanych raportu jako test double, nie rzeczywisty ERP.

Dowody maszynowe: `reports/MERGE_WERYFIKACJA.json`. Wcześniejsze raporty zadania 3
opisują przygotowanie V2; aktualny stan integracji określa niniejszy dokument.

## 5. Stan DOCX i dokumentacji

Oba pliki DOCX pozostawiono identyczne bajtowo z HEAD V2. Każdy zawiera wszystkie
24 ID i właściwych autorów. Porównano pełne wiersze bieżących tabel z rejestrem:
warunki, priorytety, kroki i rezultaty również są zgodne. Nie zastąpiono tych
plików niekompletnymi wersjami z main. Zachowano `word/styles.xml` main.

Plan ma 20 tabel, bieżące katalogi API/UI są w rozdziałach 18 i 19 i zawierają
16 i 8 wierszy przypadków. Pozostaje też 14 scenariuszy zadania 1. Dokument przypadków
ma pięć tabel, rozdziały 1–6 w kolejności oraz bieżące tabele 16 API i 8 UI.
Tabele mają wspólny układ siedmiu kolumn. Historyczne przykłady w ogólnym planie
pozostają oznaczone jako historyczne, a nie jako drugi aktualny zestaw testów.

Markdown odtworzono z `docs/test_cases.json`; nadrzędny plan to
`PLAN_TESTOW_API_UI.md`, a `PRZYPADKI_TESTOWE_API.md` jest katalogiem przypadków.
Nie powstała konkurencyjna wersja planu.

Próba renderowania DOCX zakończyła się błędem `LibreOffice soffice.exe was not
found on PATH`; również resolver środowiska dokumentowego był niedostępny.
Nie potwierdzono wizualnie podziału stron, szerokości tabel ani braku obcięć.
Zgodność definicji stylów nie stanowi potwierdzenia poprawnego układu każdej strony.

## 6. Pozostałe kroki i ryzyka

Najpierw trzeba zapisać rozwiązania do indeksu z terminala mającego prawo zapisu
do `.git`. Dopiero po potwierdzeniu pustej listy unmerged można zakończyć merge.
Poniższe polecenia nie zostały wykonane skutecznie w tej sesji i nie obejmują pushowania:

```powershell
git add -- .gitignore PRZYPADKI_TESTOWE_API.md Plan_Testow_ERPSystem_Nowy.docx Przypadki_Testowe_API_ERPSystem.docx run_tests.py tests/conftest.py tests/pages/__init__.py tests/pages/base_page.py tests/pages/ledger_page.py tests/pages/master_data_page.py tests/test_frontend_lukasz.py
git add -- README.md TODO.md reports/RAPORT_ZADANIE_3.md reports/RAPORT_MERGE_MAIN_V2.md reports/MERGE_WERYFIKACJA.json
git diff --check
git diff --cached --check
git diff --name-only --diff-filter=U
git status
# Kontynuuj tylko, gdy lista unmerged jest pusta i kontrole powyżej nie zgłosiły błędów.
git commit -m "Merge main into feat/moje-testy-UI: preserve both test suites and V2 documentation"
git status
git rev-parse HEAD
```

Po udostępnieniu zależności należy zebrać wszystkie 24 przypadki pytest, uruchomić
regresję obu autorów na rzeczywistym, spójnym środowisku ERP i obejrzeć oba DOCX.
Statyczna zgodność nie rozstrzyga działania selektorów UI ani kontraktów rzeczywistej
aplikacji. W tej sesji nie stwierdzono nierozwiązanego konfliktu treści ani utraty
testów; blokadą zakończenia merge'a jest prawo zapisu do `.git`.
