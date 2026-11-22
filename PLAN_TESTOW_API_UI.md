# Plan Testów - Manufacturing ERP: API i UI

**Wersja 2, aktualizacja 22.11.2026: zadanie 3.**
Zespół: Aleksander Kaźmierczak (251544), Łukasz Murza (251592).
Zakres tej aktualizacji zadania 3: wyłącznie osoba 2, Łukasz Murza.

## Dziennik zmian

| Data | Zakres | Powód |
|---|---|---|
| 18.10.2026 | Pierwotny plan w `Plan_Testow_ERPSystem_Nowy.docx` | Zadanie 1: zakres, scenariusze i strategia całego ERP |
| 22.11.2026 | Bieżąca wersja planu: 16 istniejących przypadków API i 4 UI Łukasza | Zadanie 3, wyłącznie osoba 2; API i UI w jednym Planie Testów |

Ta wersja jest aktualnym planem przypadków API/UI. Pierwotny DOCX pozostaje
źródłem scenariuszy zadania 1. Szczegółowe dane testów UI pochodzą z `ui/cases.json`;
polecenie `python tools/build-test-plan.py` odtwarza ten dokument.

## Wstęp i zakres

Plan dotyczy Manufacturing ERP: backendu Spring Boot, PostgreSQL i interfejsu
React/Mantine. Obejmuje istniejące testy REST API oraz testy formularzy i widoków UI.
Stanowi rozwinięcie zadania 1 na potrzeby zadania 3, bez rozszerzania implementacji
o wszystkie dalsze scenariusze współbieżności, produkcji, płac, AI i WCAG.

Źródła: `Zadanie_3_UI.pdf`, slajdy 4-5; pierwotny plan w repozytorium; wzory
`Przyklad_Plan_Testów.docx`, `Przyklad_raport_z_testow.docx` i
`Szablony_dokumentow_jakosc_w_procesie_wytwarzania_oprogramowania.docx` z katalogu
`Zasoby/Zasoby`. Wzory wykorzystano do struktury planu, opisu przypadków i raportu.
Ich wyniki przykładowe nie są wynikami testów ERP.

### Wymagania zadania 3

| ID | Kryterium | Realizacja |
|---|---|---|
| UI-W1 | Testy UI wynikają ze scenariuszy zadania 1 | Identyfikator SC przy każdym przypadku; tabela scenariuszy poniżej |
| UI-W2 | Minimum 4 opisane przypadki na osobę | UI-LUK-001..004; część osoby 1 poza zakresem tej aktualizacji |
| UI-W3 | Plan Testów zawiera przypadki API i UI | Istniejące 16 API i 4 UI Łukasza zamieszczone w tym dokumencie |
| UI-W4 | Implementacja zaplanowanych przypadków | `ui/tests/lukasz.spec.cjs` - 4 testy |
| UI-W5 | Jeden wspólny, spójny projekt, w miarę możliwości wzorce | Wspólny runner, konfiguracja, fixtury i Page Object Model |

Zgodnie z zakresem użytkownika uzupełnienie zadania 3 obejmuje wyłącznie Łukasza.
Nie przygotowuje się tu przypadków UI Aleksandra ani nie ocenia ukończenia jego części.
Prowadzący zaakceptował
GET/POST zamiast PUT/DELETE dla zadania 2; plan zachowuje dotychczasowe 8 testów API
na osobę i nie wymaga uzupełniania PUT/DELETE.

## Terminologia, organizacja i odpowiedzialność

| Pojęcie | Znaczenie |
|---|---|
| SUT | Rzeczywisty frontend i backend Manufacturing ERP |
| Scenariusz SC | Funkcjonalność opisana w zadaniu 1; może wymagać wielu przypadków |
| Przypadek UI | Konkretny cel, dane, warunki, kroki i wynik; jedna funkcja Playwright |
| POM | Page Object Model: lokatory i interakcje skupione w obiektach stron |
| Test API | Dotychczasowy przypadek HTTP wykonywany przez pytest/HTTPX |
| Test UI | Interakcje w prawdziwej przeglądarce przez Playwright Test |

Zestaw Łukasza jest w `ui/tests/lukasz.spec.cjs`. Infrastruktura pozostaje we
wspólnym projekcie i może posłużyć do późniejszego dołączenia części drugiej osoby.
Istniejące testy API obu osób zachowano jako zastaną część planu. Defekty opisuje
się przez ID testu, środowisko, kroki, wynik oczekiwany i rzeczywisty oraz załączniki.

## Strategia, technologia i założenia

API: istniejący pytest + HTTPX + Pydantic. UI: Node.js 20+ i Playwright Test 1.62.1,
Chromium albo zainstalowany Chrome/Edge. Jeden projekt repozytorium nie wymaga
jednej technologii: `run_tests.py --layer api|ui|all` steruje obiema warstwami.

UI używa rzeczywistego formularza logowania i API. Nie podmienia odpowiedzi HTTP
ani sesji tokenem. Wymusza wyłącznie język EN i pomija przewodnik onboardingowy,
aby interakcje nie zależały od poprzedniego użytkownika. Każdy test ma osobny
kontekst przeglądarki. Lokatory opierają się na rolach i etykietach; selektory
pozycyjne ograniczono do nienazwanych pól tabeli dekretu.

Zakres UI obejmuje odczyt, uprawnienia i walidację przed zapisem. Nie księguje
dekretów ani poprawnych zamówień. Obserwacja żądań POST w przypadkach negatywnych
potwierdza brak wysłania zapisu. Nie zastępuje to testowania zabezpieczeń backendu.
Logowanie może zmieniać sesje i rejestr audytowy. Test P2P obejmuje początkową
walidację zamówienia zakupu, a raportowanie bilans próbny; nie deklarują całych cykli
zakupowych/sprzedażowych ani pełnego uzgodnienia subledgerów.

Warstwa UI działa tylko na wskazanym SUT. Kontrola wstępna `/login` przerywa
uruchomienie, gdy interfejs jest nieosiągalny; nie przechodzi na symulator.

## Środowisko, dane oraz kryteria wejścia i wyjścia

| Element | Wymaganie |
|---|---|
| Adres UI | `ERP_UI_BASE_URL`, domyślnie `http://localhost:8081`; frontend musi proxywać `/api` |
| Uwierzytelnianie UI | Konta guest/accountant/warehouse; domyślnie hasło równe loginowi |
| Konfiguracja kont | `ERP_UI_<ROLA>_USERNAME` oraz `ERP_UI_<ROLA>_PASSWORD` |
| Kartoteki UI | Co najmniej jeden kontrahent i dostawca |
| Księga | Co najmniej jeden wiersz bilansu; konta 1010 i 3100 lub `ERP_UI_DEBIT_ACCOUNT`/`ERP_UI_CREDIT_ACCOUNT` |
| Przeglądarka | `npx playwright install chromium` albo `ERP_UI_CHANNEL=chrome/msedge` |
| Izolacja | Nowy kontekst per test, jeden worker, brak ponawiania niepowodzeń |

Kryteria wejścia: osiągalna aplikacja zgodna ze sprawdzonym interfejsem, zainstalowane
zależności i przeglądarka, przygotowane konta i dane. Opisy lokatorów porównano ze
źródłami frontendu `q86865511/ERPSystem`, SHA
`33b5df13594bcb456ba8a3d20e0bc455ac79aa75`; wersję docelowej instalacji należy
odnotować przy wykonaniu.

Kryteria wyjścia tej części: 4/4 przypadków Łukasza opisanych i zaimplementowanych;
zgodność planu z kodem; rzeczywiste wykonanie wszystkich 4 przypadków i raport
z ich wynikami. Brak środowiska oznacza blokadę wykonania, a nie PASSED.

Priorytety: P0 - blokada krytycznego błędu finansowego, P1 - istotna funkcjonalność
lub uprawnienia, P2 - pozostała prezentacja. Defekt P0/P1 wymaga wyjaśnienia przed
uznaniem odpowiedniego kryterium wyjścia za spełnione.

## Scenariusze pochodzące z zadania 1

Tabela zachowuje identyfikatory pierwotnego planu. Przypisanie testu do scenariusza
oznacza pokrycie konkretnego opisanego wycinka, a nie całego scenariusza.

| ID | Moduł | Scenariusz | Nowe przypadki UI |
|---|---|---|---|
| SC-GL-01 | Ledger | Integralność podwójnego zapisu | UI-LUK-002 |
| SC-GL-02 | Ledger | Zamknięcie okresu i roku | Poza zakresem 4 przypadków Łukasza |
| SC-GL-03 | Ledger | Odwracanie zapisów księgowych | Poza zakresem 4 przypadków Łukasza |
| SC-INV-01 | Inventory | Wycena średnią ważoną | Poza zakresem 4 przypadków Łukasza |
| SC-INV-02 | Inventory | Współbieżność gospodarki magazynowej | Poza zakresem 4 przypadków Łukasza |
| SC-P2P-01 | Purchasing | Cykl zakupu Procure-to-Pay | UI-LUK-003 |
| SC-O2C-01 | Sales | Cykl sprzedaży Order-to-Cash | Poza zakresem 4 przypadków Łukasza |
| SC-MFG-01 | Manufacturing | Cykl zlecenia produkcyjnego | Poza zakresem 4 przypadków Łukasza |
| SC-HR-01 | HR & Payroll | Naliczenie płac i dekretacja | Poza zakresem 4 przypadków Łukasza |
| SC-IAM-01 | IAM | Macierz uprawnień RBAC | UI-LUK-001 |
| SC-ERR-01 | Config | Standard kontraktu błędów RFC 9457 | Poza zakresem 4 przypadków Łukasza |
| SC-AI-01 | Assistant | ERP Copilot i ochrona HITL | Poza zakresem 4 przypadków Łukasza |
| SC-UI-01 | Frontend | Dostępność cyfrowa WCAG AA | Poza zakresem 4 przypadków Łukasza |
| SC-REP-01 | Reporting | Raport uzgodnienia Hero Check | UI-LUK-004 |

## Przypadki testowe API - istniejąca część zadania 2

Zachowano 16 implementacji i ich oczekiwania. Poniżej pełne tabele obu osób; szczegóły architektury API są w `PRZYPADKI_TESTOWE_API.md`.

### API - Aleksander Kaźmierczak

| ID | Kto odpowiada | Priorytet | Metoda i Endpoint (Typ) | Warunki wstępne | Kroki jakie będą wykonane | Warunki końcowe |
|---|---|---|---|---|---|---|
| **TC-API-AK-01** | Aleksander Kaźmierczak (251544) | **P0** (Krytyczny) | `GET /api/reporting/reconciliation`<br>*(Happy Path)* | 1. Uruchomiony serwer REST API systemu ERP.<br>2. Klient uwierzytelniony tokenem JWT dla roli `ACCOUNTANT`.<br>3. Spójny stan początkowy Księgi Głównej i podksiąg. | 1. Pobierz token JWT dla roli `ACCOUNTANT` (`POST /api/auth/login`).<br>2. Wyślij żądanie `GET /api/reporting/reconciliation` z nagłówkiem `Authorization: Bearer <token>`.<br>3. Zweryfikuj kod statusu HTTP `200 OK` i nagłówek `application/json`.<br>4. Zwaliduj odpowiedź modelem Pydantic `ReconciliationReportModel`.<br>5. Sprawdź flagi `healthy == True`, `trialBalanceBalanced == True` oraz `reconciled == True` i równość `subledger == glControl` (`Decimal`) dla każdej podksięgi. | System zwraca kompletny raport uzgodnienia ze statusem `200 OK`, potwierdzając równowagę bilansową. Stan bazy danych pozostaje niezmieniony. |
| **TC-API-AK-02** | Aleksander Kaźmierczak (251544) | **P1** (Wysoki) | `GET /api/masterdata/items/by-sku`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony tokenem roli `ADMIN`.<br>3. Istniejący w bazie towar testowy utworzony przez fixturę `seeded_item` o znanym kodzie `sku`. | 1. Przygotuj towar testowy z unikalnym kodem `sku` poprzez fixturę.<br>2. Wyślij żądanie `GET /api/masterdata/items/by-sku?sku=<sku>`.<br>3. Zweryfikuj kod statusu HTTP `200 OK`.<br>4. Zwaliduj strukturę odpowiedzi modelem `ItemResponseModel`.<br>5. Porównaj pola `id`, `sku`, `name`, `itemType` oraz `standardCost` (`Decimal`) z obiektem źródłowym. | Zwrócono poprawne szczegóły szukanego towaru (`200 OK`). Brak modyfikacji stanu bazy danych. |
| **TC-API-AK-03** | Aleksander Kaźmierczak (251544) | **P2** (Średni) | `GET /api/masterdata/items/{id}`<br>*(Negative Path — 404)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony tokenem roli `GUEST`.<br>3. Identyfikator `id = 999999999` nie istnieje w kartotece towarów. | 1. Wyślij żądanie `GET /api/masterdata/items/999999999` z ważnym tokenem JWT.<br>2. Zweryfikuj kod odpowiedzi HTTP `404 Not Found`.<br>3. Sprawdź nagłówek `Content-Type: application/problem+json`.<br>4. Zwaliduj ciało błędu modelem RFC 9457 `ProblemDetailModel` (`status == 404`, `title == "Not Found"`, niepuste pole `detail`). | Żądanie zostaje odrzucone ze statusem `404 Not Found` i ustrukturyzowanym opisem błędu RFC 9457. Stan systemu nie ulega zmianie. |
| **TC-API-AK-04** | Aleksander Kaźmierczak (251544) | **P1** (Wysoki) | `GET /api/audit`<br>*(Negative Path — 403 RBAC)* | 1. Działający serwer REST API z aktywną kontrolą uprawnień RBAC.<br>2. Klient uwierzytelniony jako `GUEST` (brak uprawnień `ROLE_ADMIN`). | 1. Uwierzytelnij klienta na koncie `guest` o uprawnieniach tylko do odczytu zwykłych modułów.<br>2. Wyślij żądanie `GET /api/audit` z tokenem roli `GUEST`.<br>3. Zweryfikuj kod odpowiedzi HTTP `403 Forbidden`.<br>4. Sprawdź zgodność odpowiedzi ze standardem RFC 9457 (`status == 403`, `title == "Forbidden"`, informacja o braku uprawnień w `detail`). | Nieautoryzowany dostęp do logów audytowych zostaje zablokowany (`403 Forbidden`); wrażliwe dane audytowe nie zostają ujawnione. |
| **TC-API-AK-05** | Aleksander Kaźmierczak (251544) | **P1** (Wysoki) | `POST /api/masterdata/partners`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ADMIN`.<br>3. Wygenerowany unikalny kod kontrahenta (`PRT-...`) za pomocą `TestDataFactory`. | 1. Wygeneruj ładunek JSON nowego kontrahenta (`code`, `name`, `vendor=True`, `customer=True`, `paymentTermsDays=45`, `apAccountCode="2100"`, `arAccountCode="1200"`).<br>2. Wyślij żądanie `POST /api/masterdata/partners` z tokenem `ADMIN`.<br>3. Zweryfikuj kod statusu HTTP `201 Created` i zwaliduj odpowiedź modelem `PartnerResponseModel`.<br>4. Sprawdź nadane `id > 0` oraz `active == True`.<br>5. Wykonaj kontrolne żądanie `GET /api/masterdata/partners/{id}` potwierdzające trwałość zapisu. | W bazie danych zostaje trwale utworzony nowy, aktywny kontrahent dostępny pod nadanym identyfikatorem (`201 Created`). |
| **TC-API-AK-06** | Aleksander Kaźmierczak (251544) | **P0** (Krytyczny) | `POST /api/ledger/journal-entries`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ACCOUNTANT`.<br>3. Otwarty okres obrachunkowy (`2026-06-15`) oraz aktywne konta księgowe `1010` i `3100`. | 1. Wygeneruj ładunek `JournalEntryRequest` z dwiema zbilansowanymi liniami: Dt `1010` = `350.0000`, Ct `3100` = `350.0000`.<br>2. Wyślij żądanie `POST /api/ledger/journal-entries` z tokenem `ACCOUNTANT`.<br>3. Zweryfikuj status HTTP `201 Created` oraz model `JournalEntryResponseModel`.<br>4. Sprawdź za pomocą `Decimal`, że `totalDebit == 350.0000`, `totalCredit == 350.0000` oraz `status == "POSTED"`.<br>5. Pobierz bilans próbny (`GET /api/ledger/trial-balance`) i potwierdź `balanced == True`. | Zbilansowany dekret księgowy zostaje zapisany ze statusem `POSTED`, a Księga Główna zachowuje pełną równowagę `Winien == Ma`. |
| **TC-API-AK-07** | Aleksander Kaźmierczak (251544) | **P0** (Krytyczny) | `POST /api/ledger/journal-entries`<br>*(Negative Path — 422)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ACCOUNTANT`.<br>3. Odczytany stan początkowy bilansu próbnego Księgi Głównej. | 1. Odczytaj sumy bilansu próbnego przed testem (`GET /api/ledger/trial-balance`).<br>2. Przygotuj niezbilansowany ładunek dekretu: Dt `1010` = `100.0000`, Ct `4100` = `95.0000` (asymetria `5.0000`).<br>3. Wyślij żądanie `POST /api/ledger/journal-entries`.<br>4. Zweryfikuj kod odpowiedzi HTTP `422 Unprocessable Entity` i kontrakt `ProblemDetailModel`.<br>5. Ponownie pobierz bilans próbny i potwierdź brak zmiany sum `totalDebit` i `totalCredit`. | Asymetryczny dekret zostaje odrzucony (`422 Unprocessable Entity`), transakcja wycofana (rollback), a stan Księgi Głównej pozostaje nienaruszony. |
| **TC-API-AK-08** | Aleksander Kaźmierczak (251544) | **P2** (Średni) | `POST /api/sales/sales-orders`<br>*(Negative Path — 400)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `SALES`. | 1. Przygotuj niekompletny ładunek JSON `{}` (brak wymaganych pól `@NotNull partnerId`, `orderDate` oraz `@NotEmpty lines`).<br>2. Wyślij żądanie `POST /api/sales/sales-orders` z tokenem `SALES`.<br>3. Zweryfikuj kod odpowiedzi HTTP `400 Bad Request`.<br>4. Zwaliduj odpowiedź modelem RFC 9457 `ProblemDetailModel` (`status == 400`, `title == "Bad Request"`, niepuste pole `detail`). | Niepoprawne żądanie zostaje odrzucone na warstwie walidacji kontraktu (`400 Bad Request`); w bazie nie powstaje uszkodzony rekord zamówienia. |

### API - Łukasz Murza

| ID | Kto odpowiada | Priorytet | Metoda i Endpoint (Typ) | Warunki wstępne | Kroki jakie będą wykonane | Warunki końcowe |
|---|---|---|---|---|---|---|
| **LUK-001** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `GET /api/auth/me`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Konto `admin` jest dostępne.<br>3. Klient uwierzytelniony tokenem JWT dla roli `ADMIN`. | 1. Wyślij żądanie `GET /api/auth/me`.<br>2. Zweryfikuj status `200 OK` i nagłówek JSON.<br>3. Zwaliduj odpowiedź modelem `CurrentUserResponseModel`.<br>4. Sprawdź `username == "admin"` oraz role `ADMIN`, `ACCOUNTANT`, `HR`, `SALES`, `WAREHOUSE`. | System zwraca poprawny profil administratora (`200 OK`). Stan systemu pozostaje niezmieniony. |
| **LUK-002** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `GET /api/inventory/items/1/on-hand`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Istnieje towar `RM-DEMO` o ID `1`.<br>3. Klient uwierzytelniony jako `GUEST`. | 1. Wyślij żądanie dla ID towaru `1`.<br>2. Zweryfikuj status `200 OK` i strukturę pięciu pól odpowiedzi.<br>3. Sprawdź SKU oraz wartości `onHandQty`, `avgUnitCost` i `totalValue` z użyciem `Decimal`.<br>4. Potwierdź zależność `totalValue == onHandQty * avgUnitCost`. | System zwraca poprawny stan magazynowy (`200 OK`), a wartości finansowe są spójne. Stan magazynu pozostaje niezmieniony. |
| **LUK-003** | Łukasz Murza (`251592`) | **P2** (Średni) | `GET /api/masterdata/items/by-sku`<br>*(Negative Path — 404)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony.<br>3. SKU `LUK-NONEXISTENT-SKU` nie istnieje w kartotece towarów. | 1. Wyślij żądanie `GET /api/masterdata/items/by-sku?sku=LUK-NONEXISTENT-SKU`.<br>2. Zweryfikuj status `404 Not Found`.<br>3. Zwaliduj odpowiedź RFC 9457 modelem `ProblemDetailModel`.<br>4. Sprawdź tytuł `Not Found` i opis zawierający informację o SKU. | Żądanie zostaje odrzucone jako brakujący zasób (`404 Not Found`). Żaden towar nie zostaje utworzony ani zmodyfikowany. |
| **LUK-004** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `GET /api/auth/me`<br>*(Negative Path — 401)* | 1. Działający serwer REST API.<br>2. Klient nie posiada tokenu JWT. | 1. Wyślij żądanie `GET /api/auth/me` bez nagłówka `Authorization`.<br>2. Zweryfikuj status `401 Unauthorized`.<br>3. Zwaliduj odpowiedź RFC 9457 modelem `ProblemDetailModel`.<br>4. Sprawdź tytuł `Unauthorized` oraz szczegół `Authentication required`. | Dostęp bez uwierzytelnienia zostaje zablokowany (`401 Unauthorized`); profil użytkownika nie zostaje ujawniony. |
| **LUK-005** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `POST /api/masterdata/items`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ADMIN`.<br>3. Fabryka danych generuje unikalny SKU. | 1. Wygeneruj poprawny JSON towaru z nazwą, typem, jednostką oraz kosztami `42.750000`, `7.000000`, `21.000000`.<br>2. Wyślij żądanie POST.<br>3. Zweryfikuj `201 Created` i odpowiedź modelem `ItemResponseModel`.<br>4. Porównaj SKU, nazwę i wartości dziesiętne z żądaniem.<br>5. Pobierz `GET /api/masterdata/items/{id}` i potwierdź trwałość zapisu. | Towar zostaje utworzony (`201 Created`) z poprawnymi danymi i jest dostępny po nadanym ID. |
| **LUK-006** | Łukasz Murza (`251592`) | **P2** (Średni) | `POST /api/masterdata/warehouses`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ADMIN`.<br>3. Fabryka danych generuje unikalny kod magazynu. | 1. Przygotuj JSON z kodem i nazwą `Lukasz Test Warehouse`.<br>2. Wyślij żądanie POST.<br>3. Zweryfikuj `201 Created` i odpowiedź modelem `WarehouseResponseModel`.<br>4. Sprawdź `active == True`.<br>5. Pobierz listę magazynów i odszukaj utworzony rekord. | Magazyn zostaje utworzony jako aktywny (`201 Created`) i jest widoczny na liście zasobów. |
| **LUK-007** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `POST /api/purchasing/purchase-orders`<br>*(Negative Path — 404)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `WAREHOUSE`.<br>3. Partner o ID `999999999` nie istnieje. | 1. Przygotuj poprawnie uformowane zamówienie zakupu z nieistniejącym `partnerId`.<br>2. Wyślij żądanie POST.<br>3. Zweryfikuj status `404 Not Found`.<br>4. Zwaliduj odpowiedź RFC 9457 modelem `ProblemDetailModel`.<br>5. Sprawdź, że opis błędu wskazuje brak partnera. | Zamówienie zakupu nie zostaje utworzone; API zwraca `404 Not Found`. |
| **LUK-008** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `POST /api/auth/login`<br>*(Negative Path — 401)* | 1. Działający serwer REST API.<br>2. Użytkownik `lukasz-invalid-user` nie istnieje. | 1. Wyślij `POST /api/auth/login` z `username=lukasz-invalid-user` i `password=wrong-password`.<br>2. Zweryfikuj status `401 Unauthorized`.<br>3. Zwaliduj odpowiedź RFC 9457 modelem `ProblemDetailModel`.<br>4. Sprawdź tytuł `Unauthorized` i opis `Invalid username or password`. | Logowanie zostaje odrzucone (`401 Unauthorized`); token JWT nie zostaje wydany, a stan systemu pozostaje niezmieniony. |

## Przypadki testowe UI - zadanie 3

### UI-LUK-001 - GUEST odczytuje kontrahentów, ale nie ma akcji tworzenia

| Atrybut | Wartość |
|---|---|
| Scenariusz zadania 1 | SC-IAM-01 |
| Osoba | Łukasz Murza (251592) |
| Cel | Sprawdzić prezentację uprawnień tylko do odczytu w UI kartotek. |
| Priorytet | P1 |
| Implementacja | `ui/tests/lukasz.spec.cjs`; tytuł zaczyna się od `UI-LUK-001` |

Warunki wstępne:

- Działające ERP i konto guest z pustą listą ról.
- W bazie istnieje co najmniej jeden kontrahent demonstracyjny.

Dane testowe:

- Konto guest; adres /masterdata?tab=partners; interfejs EN.

Przebieg:

1. Zaloguj się przez formularz jako guest.
2. Otwórz kartoteki kontrahentów.
3. Sprawdź aktywną zakładkę Partners i widoczny nagłówek kolumny Code.
4. Sprawdź brak przycisku New partner i brak okna tworzenia.

Oczekiwany wynik:

- Widok odczytu jest dostępny i zakładka Partners jest aktywna.
- Akcja tworzenia nie jest dostępna; nie otwiera się formularz zapisu.

Stan końcowy: Nie powstaje nowy kontrahent; kontekst przeglądarki jest zamykany po teście.

### UI-LUK-002 - Niezbilansowany dekret ma zablokowany przycisk księgowania

| Atrybut | Wartość |
|---|---|
| Scenariusz zadania 1 | SC-GL-01 |
| Osoba | Łukasz Murza (251592) |
| Cel | Zweryfikować blokadę asymetrycznego zapisu na etapie formularza UI. |
| Priorytet | P0 |
| Implementacja | `ui/tests/lukasz.spec.cjs`; tytuł zaczyna się od `UI-LUK-002` |

Warunki wstępne:

- Działające ERP i konto accountant z rolą ACCOUNTANT.
- Bilans próbny zawiera konta 1010 i 3100 albo konta wskazane w konfiguracji.

Dane testowe:

- Dwie linie: 1010 Debit 100.00, 3100 Credit 95.00; asymetria 5.00.

Przebieg:

1. Zaloguj się jako accountant i otwórz Ledger / Manual entry.
2. Wybierz oba konta z rzeczywistych list i wpisz kwoty.
3. Sprawdź oznaczenie Unbalanced i disabled przycisku Post entry.
4. Najedź na otoczenie przycisku i sprawdź tooltip wyjaśniający wymóg równych kwot.
5. Sprawdź, że podczas edycji nie wysłano POST /api/ledger/journal-entries.

Oczekiwany wynik:

- Widoczny status Unbalanced oraz wyłączony przycisk Post entry.
- Tooltip wyjaśnia wymóg bilansowania; liczba żądań księgowania wynosi zero.

Stan końcowy: Formularz nie zapisuje dekretu. Test nie ocenia odrzucenia błędu po stronie serwera.

### UI-LUK-003 - Zamówienie zakupu nie może powstać bez kompletnej pozycji

| Atrybut | Wartość |
|---|---|
| Scenariusz zadania 1 | SC-P2P-01 |
| Osoba | Łukasz Murza (251592) |
| Cel | Sprawdzić walidację wejścia do cyklu zakupu w formularzu UI. |
| Priorytet | P1 |
| Implementacja | `ui/tests/lukasz.spec.cjs`; tytuł zaczyna się od `UI-LUK-003` |

Warunki wstępne:

- Działające ERP i konto warehouse z rolą WAREHOUSE.
- Istnieje co najmniej jeden dostawca dostępny do wyboru.

Dane testowe:

- Pierwszy dostępny dostawca; domyślna data; pusta pozycja zamówienia.

Przebieg:

1. Zaloguj się jako warehouse i otwórz Purchase orders.
2. Otwórz New purchase order i wybierz dostawcę.
3. Pozostaw pozycję bez towaru, ilości i ceny; kliknij Create.
4. Sprawdź komunikat Add at least one complete line i nadal otwarte okno.
5. Sprawdź brak POST /api/purchasing/purchase-orders.

Oczekiwany wynik:

- UI wyświetla błąd wymaganej kompletnej pozycji.
- Okno pozostaje otwarte; żądanie tworzenia zamówienia nie jest wysyłane.

Stan końcowy: Nowe zamówienie zakupu nie powstaje. Przypadek obejmuje walidację początku P2P, nie cały cykl rozliczenia.

### UI-LUK-004 - Bilans próbny prezentuje wartości otrzymane z API

| Atrybut | Wartość |
|---|---|
| Scenariusz zadania 1 | SC-REP-01 |
| Osoba | Łukasz Murza (251592) |
| Cel | Zweryfikować zgodność prezentacji raportu z rzeczywistymi danymi finansowymi. |
| Priorytet | P1 |
| Implementacja | `ui/tests/lukasz.spec.cjs`; tytuł zaczyna się od `UI-LUK-004` |

Warunki wstępne:

- Działające ERP i konto accountant.
- GET /api/reporting/trial-balance zwraca co najmniej jeden wiersz i sumy jako liczby dziesiętne.

Dane testowe:

- Bieżąca data raportu; rzeczywista odpowiedź GET /api/reporting/trial-balance, bez stubów.

Przebieg:

1. Zaloguj się jako accountant i otwórz Reports / Trial balance.
2. Przechwyć odpowiedź GET bilansu próbnego i sprawdź status 200 oraz niepustą listę.
3. Sprawdź aktywny panel raportu i zgodność oznaczenia Balanced/Unbalanced z odpowiedzią.
4. Porównaj sumy Winien/Ma w stopce tabeli z odpowiedzią API.
5. Porównaj nazwę oraz kwoty pierwszego konta w tabeli z API.

Oczekiwany wynik:

- Raport jest widoczny; status, sumy i pierwszy wiersz są zgodne z odpowiedzią API.
- Kwoty są pokazane z separatorem tysięcy i dwiema cyframi po przecinku.

Stan końcowy: Dane pozostają niezmienione. Test obejmuje bilans próbny ze scenariusza raportowania, nie pełne uzgodnienie wszystkich subledgerów.

## Artefakty, metryki i harmonogram

| Artefakt / miara | Cel |
|---|---|
| Ten Plan Testów | 16 istniejących przypadków API oraz 4 UI Łukasza |
| `ui/cases.json` i `ui/tests/lukasz.spec.cjs` | 4 planowane i zaimplementowane przypadki UI Łukasza |
| `node tools/check-ui-plan.cjs` | 100% zgodności ID i przypisania do scenariuszy |
| Playwright `--list` | 4 zebrane testy Łukasza; innych przypadków UI nie dodano |
| Rzeczywiste wykonanie UI | 4 wyniki; liczba PASSED/FAILED/BLOCKED raportowana oddzielnie |
| HTML/JSON, screenshoty i trace | `reports/ui/` oraz `test-results/ui/`; dane z rzeczywistych wykonań |
| `reports/RAPORT_ZADANIE_3.md` | Stan prac, odchylenia, metryki i ryzyka |

Kolejność prac: analiza źródeł -> przypadki i powiązanie ze scenariuszami -> wspólne
obiekty stron -> implementacja części Łukasza -> kontrola plan/kod i zebranie testów ->
wykonanie na osiągalnym ERP -> analiza niepowodzeń i raport. Bieżący stan i otwarte
prace są w `TODO.md`; nie ustalono nowej daty oddania w przekazanym poleceniu.

Ryzyka: zmiana etykiet interfejsu, brak danych lub ról, niedostępność SUT oraz
różna wersja docelowej instalacji. Ograniczają je POM, jawne warunki wstępne,
stabilne etykiety EN, kontrola wejściowa i załączniki przy błędach. Zakres czterech
testów nie jest audytem całego ERP ani potwierdzeniem pełnego WCAG.
