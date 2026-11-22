# Raport zadania 3 - ujednolicenie części Łukasza z main

## 1. Zakres i wynik

Stan: 22.11.2026. Gałąź robocza: `feat/moje-testy-UI`, baza `fe53a0c`.
Sprawdzony `main`: `af43160fc201760d3d49d66c8f6a4a2b615c9ed0`.
Nowe testy są wyłącznie autorstwa Łukasza Murzy (251592): **TC-UI-LM-01..04**.
Cztery istniejące UI i osiem API Aleksandra przejęto bez zmian ze wskazanego `main`.
Cały wspólny katalog zawiera 16 API i 8 UI; nie oznacza to dopisania pracy za drugą osobę.

Usunięto powielony test niezbilansowanego dekretu, odrębną infrastrukturę JavaScript
i rozbieżne konwencje ID. Jeden runner pytest uwzględnia obie osoby. Plan i katalog
w Markdown oraz oba DOCX są generowane z jednego rejestru i zawierają te same 24 ID.
Zmiany przygotowano w drzewie roboczym; nie wykonano Git merge, commitu ani push.

## 2. Rozstrzygnięcie uwag z porównania

| Uwaga | Zmiana | Powiązanie z wymaganiem |
|---|---|---|
| Powielenie UI-LUK-002 z TC-UI-AK-04 | TC-UI-LM-02 dotyczy nieistniejącego wpisu w Reversal: GET 404, komunikat błędu, brak formularza i brak POST | UI-W1/UI-W4: odrębny przypadek SC-GL-03 |
| Za słaba asercja odczytu kontrahenta | TC-UI-LM-01 porównuje konkretny kod i nazwę rekordu z API z wierszem UI | UI-W2/UI-W4: pełniejsze oczekiwania i implementacja |
| Zbyt szerokie powiązanie bilansu z Hero Check | TC-UI-LM-04 opisano wyłącznie jako prezentację bilansu próbnego | UI-W1: jawny wycinek SC-REP-01 |
| Dwa frameworki i POM | Cztery testy Łukasza przeniesiono do Python/pytest/Playwright i wspólnego `tests/pages/` | UI-W5: spójny projekt i współdzielenie kodu |
| Runner nie obsługiwał obu zestawów | Macierz z main uruchamia cztery moduły API/UI obu osób; frontend/ui są aliasami jednej warstwy | UI-W5 |
| Różne ID i układ dokumentacji | Standard TC-{API|UI}-{AK|LM}-{NN}, wspólne tabele i numerowane rozdziały | UI-W2/UI-W3 |
| Niepełny wspólny Plan Testów | Jeden katalog 16 API + 8 UI, ze źródłem danych `docs/test_cases.json` | UI-W3 |
| Różne wersje DOCX | Odczyt treści i tabel, aktualizacja obu dokumentów na bazie stylów main | UI-W3: spójność formatów |

Wyłącznie przedmiot SC-GL-03 różni nowy drugi test od dawnego przypadku; nie jest
to kosmetyczna zmiana kwot lub ID. Nowy przypadek nie wypełnia formularza Manual
entry i nie sprawdza jego badge Unbalanced ani przycisku Post entry.

## 3. Zakres i odrębność czterech UI Łukasza

| ID | Scenariusz | Cel | Relacja do UI Aleksandra |
|---|---|---|---|
| TC-UI-LM-01 | SC-IAM-01 | Odczyt konkretnego kontrahenta i brak tworzenia przez GUEST | Wspólna rola, ale inna funkcjonalność niż Audit Trail; odmienny cel od tworzenia przez ADMIN |
| TC-UI-LM-02 | SC-GL-03 | Błąd ładowania nieistniejącego wpisu do storna, bez możliwości odwrócenia | Brak odpowiednika w czterech przypadkach Aleksandra |
| TC-UI-LM-03 | SC-P2P-01 | Zamówienie zakupu wymaga kompletnej pozycji | Brak odpowiednika UI Aleksandra |
| TC-UI-LM-04 | SC-REP-01 | Tabela bilansu próbnego zgadza się z odpowiedzią API | Odrębna prezentacja od Dashboard Hero Check i uzgodnienia podksiąg |

Powiązania są zawężone w tabeli pokrycia Planu Testów. TC-UI-LM-02 nie realizuje
poprawnego storna, TC-UI-LM-03 nie realizuje całego P2P, a TC-UI-LM-04 nie obejmuje
pełnego uzgodnienia podksiąg. Wymagane minimum czterech przypadków osoby 2 jest
zachowane bez ponownego implementowania przypadków osoby 1.

## 4. Wspólna infrastruktura i identyfikatory

Testy Łukasza są w `tests/test_frontend_lukasz.py`; pusty szablon zastąpiono
implementacją. Reużywane są LoginPage, MasterDataPage, LedgerPage i BaseErpPage.
PurchasingPage i ReportingPage rozszerzają tę samą bazę, a nie drugi POM.
Obserwowanie POST nie podmienia odpowiedzi. Wspólne logowanie wykorzystuje
istniejący LoginPage z main.

| Poprzednie ID | Bieżące ID | Charakter zmiany |
|---|---|---|
| LUK-001..008 | TC-API-LM-01..08 | ID i nazwy funkcji; bez zmiany logiki istniejących API |
| UI-LUK-001 | TC-UI-LM-01 | Migracja do Pythona i mocniejszy odczyt konkretnego rekordu |
| UI-LUK-002 | TC-UI-LM-02 | Zastąpienie przypadku innym scenariuszem biznesowym |
| UI-LUK-003 | TC-UI-LM-03 | Migracja do wspólnego POM Pythona |
| UI-LUK-004 | TC-UI-LM-04 | Migracja i jawne ograniczenie pokrycia do bilansu próbnego |
| TC-API-AK-01..08 / TC-UI-AK-01..04 | Bez zmian | Źródła testów identyczne z main |

Identyfikatory scenariuszy SC-* zachowano. Historyczne raporty nie są renumerowane
ani przedstawiane jako wyniki tej wersji. Nowe metadane raportu oznaczają faktyczny
backend (live/reference). `--backend-mode live` wyłącza fallback. Przy jawnym
frontendzie API musi wskazywać ten sam rzeczywisty backend.

## 5. Porównanie i ujednolicenie DOCX

Odczytano obie wersje binarnych dokumentów z Git, wraz z tabelami i definicjami
stylów. Dowód porównania: `reports/DOCX_POROWNANIE.json`.

| Dokument | Feature przed zmianą | main przed zmianą | Bieżący katalog |
|---|---|---|---|
| Plan_Testow_ERPSystem_Nowy.docx | 18 tabel; bez katalogu ID testów API/UI | 20 tabel; 8 API i 4 UI Aleksandra | 16 API + 8 UI |
| Przypadki_Testowe_API_ERPSystem.docx | 16 API, bez UI | 8 API i 4 UI Aleksandra | 16 API + 8 UI |

Definicje stylów ogólnego planu różniły się między gałęziami; w drugim dokumencie
były identyczne. Sam ten fakt nie dowodzi zmiany widocznej czcionki na każdej stronie.
Nowe wersje dokumentów
Word mają wspólne tabele siedmiu kolumn i te same 24 identyfikatory co Markdown.
Definicje `word/styles.xml` są identyczne z odpowiednimi dokumentami z main;
nowe wiersze dziedziczą formatowanie tabel źródłowych. Ogólny plan zachowuje
scenariusze zadania 1; jego propozycje i przykładowe wyniki oznaczono jako historyczne.
Aktualny katalog implementacji jest w rozdziałach 18-19.

Wizualna kontrola stron pozostaje niewykonana: renderer zakończył się błędem
`LibreOffice soffice.exe was not found on PATH`. Sprawdzono strukturę, zawartość,
ID i definicje stylów, ale nie można na tej podstawie potwierdzić paginacji ani
braku zawijania/obcięcia tekstu w każdym widoku Worda.

## 6. Weryfikacja i ograniczenia

| Kontrola | Wynik |
|---|---|
| Statyczny katalog kodu i ID | 24 przypadki: 16 API + 8 UI; po 4 UI na osobę |
| Spójność rejestru, Markdown i DOCX | 24/24 ID; jednolite autorstwo i format tabel |
| Źródła testów Aleksandra vs main | Identyczne bajtowo |
| Logika testów API Łukasza | Zachowana; zmieniono wyłącznie ID i nazwy funkcji |
| Składnia Pythona | Poprawna |
| Kolekcja nowego pytest | ZABLOKOWANA: brak pytest/httpx/playwright |
| Wykonanie przypadków na ERP | NOT RUN; brak podstaw do przypisania PASSED/FAILED |
| Renderowanie DOCX | ZABLOKOWANE: brak LibreOffice |

Próba `python run_tests.py --suite all --layer frontend --collect-only` zakończyła
się komunikatem o braku pytest i kodem 4. Narzędzie statyczne nie udaje kolekcji
pytest. Dawna kolekcja JavaScript nie dotyczy obecnej implementacji Pythona.
Po instalacji zależności trzeba wykonać kolekcję i testy na osiągalnym ERP, a następnie
sprawdzić regresję współdzielonych helperów także na niezmienionych testach Aleksandra.

## 7. Artefakty i dalsze kroki

Kod: `tests/test_frontend_lukasz.py`, `tests/pages/`, wspólny `run_tests.py`.
Źródło dokumentacji: `docs/test_cases.json`; generator: `tools/build-test-plan.py`.
Kontrola: `tools/check-test-plan.py`. Plan i katalog występują w Markdown i DOCX.
Stan weryfikacji: `reports/UI_ZADANIE_3_WERYFIKACJA.json`; otwarte kroki: `TODO.md`.

Powyższe wyniki dotyczą przygotowania V2 przed integracją Git. Bieżący stan
rozpoczętego merge'a, rozwiązań konfliktów i blokady zapisu do indeksu opisuje
[raport integracji](RAPORT_MERGE_MAIN_V2.md). Nadal wymagane są zależności,
rzeczywiste wykonanie testów i przegląd stron Worda. Nie wykonano pushowania.
