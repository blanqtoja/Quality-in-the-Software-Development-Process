# Plan Testów - Manufacturing ERP: API i UI

## 1. Zakres, źródła i wymagania

Stan na 22.11.2026. Zespół: Aleksander Kaźmierczak (251544), Łukasz Murza (251592).
Nowa implementacja w tej gałęzi obejmuje wyłącznie cztery testy UI Łukasza.
Istniejące 16 testów API i cztery testy UI Aleksandra zostały uwzględnione ze stanu
`main` (`af43160fc201760d3d49d66c8f6a4a2b615c9ed0`), bez przepisywania jego testów.
Wspólny katalog obejmuje zatem **16 API + 8 UI**, przy zachowaniu autorstwa.

Podstawa: zadanie 3, scenariusze zadania 1 z `Plan_Testow_ERPSystem_Nowy.docx`
oraz wzory planu/raportu z `Zasoby/Zasoby`. Prowadzący zaakceptował GET/POST
zamiast PUT/DELETE w zadaniu 2. Zakres zadania 3: po co najmniej cztery opisane
i zaimplementowane przypadki UI na osobę, powiązane ze scenariuszami, w jednym
spójnym projekcie. Nie deklaruje się pokrycia całych scenariuszy jednym testem.

Standard identyfikatorów: `TC-{API|UI}-{AK|LM}-{01..NN}`. Identyfikatory `SC-*`
pozostają identyfikatorami scenariuszy. Poprzednie ID Łukasza mają mapowanie
w raporcie migracji; nie służą już jako aktywne identyfikatory przypadków.

Źródłem wszystkich tabel jest `docs/test_cases.json`. Generator odtwarza ten plan,
`PRZYPADKI_TESTOWE_API.md` i oba dokumenty DOCX w jednolitym formacie siedmiu kolumn.
Formatowanie Worda jest przejmowane z dokumentów `main`, a nie z nowego szablonu.

## 2. Przypadki REST API - Aleksander Kaźmierczak

| ID | Kto odpowiada | Priorytet | Metoda / Endpoint lub widok UI | Warunki wstępne | Warunki końcowe | Kroki jakie będą wykonane |
|---|---|---|---|---|---|---|
| **TC-API-AK-01** | Aleksander Kaźmierczak (251544) | **P0** (Krytyczny) | `GET /api/reporting/reconciliation`<br>*(Happy Path)* | 1. Uruchomiony serwer REST API systemu ERP.<br>2. Klient uwierzytelniony tokenem JWT dla roli `ACCOUNTANT`.<br>3. Spójny stan początkowy Księgi Głównej i podksiąg. | System zwraca kompletny raport uzgodnienia ze statusem `200 OK`, potwierdzając równowagę bilansową. Stan bazy danych pozostaje niezmieniony. | 1. Pobierz token JWT dla roli `ACCOUNTANT` (`POST /api/auth/login`).<br>2. Wyślij żądanie `GET /api/reporting/reconciliation` z nagłówkiem `Authorization: Bearer <token>`.<br>3. Zweryfikuj kod statusu HTTP `200 OK` i nagłówek `application/json`.<br>4. Zwaliduj odpowiedź modelem Pydantic `ReconciliationReportModel`.<br>5. Sprawdź flagi `healthy == True`, `trialBalanceBalanced == True` oraz `reconciled == True` i równość `subledger == glControl` (`Decimal`) dla każdej podksięgi. |
| **TC-API-AK-02** | Aleksander Kaźmierczak (251544) | **P1** (Wysoki) | `GET /api/masterdata/items/by-sku`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony tokenem roli `ADMIN`.<br>3. Istniejący w bazie towar testowy utworzony przez fixturę `seeded_item` o znanym kodzie `sku`. | Zwrócono poprawne szczegóły szukanego towaru (`200 OK`). Brak modyfikacji stanu bazy danych. | 1. Przygotuj towar testowy z unikalnym kodem `sku` poprzez fixturę.<br>2. Wyślij żądanie `GET /api/masterdata/items/by-sku?sku=<sku>`.<br>3. Zweryfikuj kod statusu HTTP `200 OK`.<br>4. Zwaliduj strukturę odpowiedzi modelem `ItemResponseModel`.<br>5. Porównaj pola `id`, `sku`, `name`, `itemType` oraz `standardCost` (`Decimal`) z obiektem źródłowym. |
| **TC-API-AK-03** | Aleksander Kaźmierczak (251544) | **P2** (Średni) | `GET /api/masterdata/items/{id}`<br>*(Negative Path — 404)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony tokenem roli `GUEST`.<br>3. Identyfikator `id = 999999999` nie istnieje w kartotece towarów. | Żądanie zostaje odrzucone ze statusem `404 Not Found` i ustrukturyzowanym opisem błędu RFC 9457. Stan systemu nie ulega zmianie. | 1. Wyślij żądanie `GET /api/masterdata/items/999999999` z ważnym tokenem JWT.<br>2. Zweryfikuj kod odpowiedzi HTTP `404 Not Found`.<br>3. Sprawdź nagłówek `Content-Type: application/problem+json`.<br>4. Zwaliduj ciało błędu modelem RFC 9457 `ProblemDetailModel` (`status == 404`, `title == "Not Found"`, niepuste pole `detail`). |
| **TC-API-AK-04** | Aleksander Kaźmierczak (251544) | **P1** (Wysoki) | `GET /api/audit`<br>*(Negative Path — 403 RBAC)* | 1. Działający serwer REST API z aktywną kontrolą uprawnień RBAC.<br>2. Klient uwierzytelniony jako `GUEST` (brak uprawnień `ROLE_ADMIN`). | Nieautoryzowany dostęp do logów audytowych zostaje zablokowany (`403 Forbidden`); wrażliwe dane audytowe nie zostają ujawnione. | 1. Uwierzytelnij klienta na koncie `guest` o uprawnieniach tylko do odczytu zwykłych modułów.<br>2. Wyślij żądanie `GET /api/audit` z tokenem roli `GUEST`.<br>3. Zweryfikuj kod odpowiedzi HTTP `403 Forbidden`.<br>4. Sprawdź zgodność odpowiedzi ze standardem RFC 9457 (`status == 403`, `title == "Forbidden"`, informacja o braku uprawnień w `detail`). |
| **TC-API-AK-05** | Aleksander Kaźmierczak (251544) | **P1** (Wysoki) | `POST /api/masterdata/partners`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ADMIN`.<br>3. Wygenerowany unikalny kod kontrahenta (`PRT-...`) za pomocą `TestDataFactory`. | W bazie danych zostaje trwale utworzony nowy, aktywny kontrahent dostępny pod nadanym identyfikatorem (`201 Created`). | 1. Wygeneruj ładunek JSON nowego kontrahenta (`code`, `name`, `vendor=True`, `customer=True`, `paymentTermsDays=45`, `apAccountCode="2100"`, `arAccountCode="1200"`).<br>2. Wyślij żądanie `POST /api/masterdata/partners` z tokenem `ADMIN`.<br>3. Zweryfikuj kod statusu HTTP `201 Created` i zwaliduj odpowiedź modelem `PartnerResponseModel`.<br>4. Sprawdź nadane `id > 0` oraz `active == True`.<br>5. Wykonaj kontrolne żądanie `GET /api/masterdata/partners/{id}` potwierdzające trwałość zapisu. |
| **TC-API-AK-06** | Aleksander Kaźmierczak (251544) | **P0** (Krytyczny) | `POST /api/ledger/journal-entries`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ACCOUNTANT`.<br>3. Otwarty okres obrachunkowy (`2026-06-15`) oraz aktywne konta księgowe `1010` i `3100`. | Zbilansowany dekret księgowy zostaje zapisany ze statusem `POSTED`, a Księga Główna zachowuje pełną równowagę `Winien == Ma`. | 1. Wygeneruj ładunek `JournalEntryRequest` z dwiema zbilansowanymi liniami: Dt `1010` = `350.0000`, Ct `3100` = `350.0000`.<br>2. Wyślij żądanie `POST /api/ledger/journal-entries` z tokenem `ACCOUNTANT`.<br>3. Zweryfikuj status HTTP `201 Created` oraz model `JournalEntryResponseModel`.<br>4. Sprawdź za pomocą `Decimal`, że `totalDebit == 350.0000`, `totalCredit == 350.0000` oraz `status == "POSTED"`.<br>5. Pobierz bilans próbny (`GET /api/ledger/trial-balance`) i potwierdź `balanced == True`. |
| **TC-API-AK-07** | Aleksander Kaźmierczak (251544) | **P0** (Krytyczny) | `POST /api/ledger/journal-entries`<br>*(Negative Path — 422)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ACCOUNTANT`.<br>3. Odczytany stan początkowy bilansu próbnego Księgi Głównej. | Asymetryczny dekret zostaje odrzucony (`422 Unprocessable Entity`), transakcja wycofana (rollback), a stan Księgi Głównej pozostaje nienaruszony. | 1. Odczytaj sumy bilansu próbnego przed testem (`GET /api/ledger/trial-balance`).<br>2. Przygotuj niezbilansowany ładunek dekretu: Dt `1010` = `100.0000`, Ct `4100` = `95.0000` (asymetria `5.0000`).<br>3. Wyślij żądanie `POST /api/ledger/journal-entries`.<br>4. Zweryfikuj kod odpowiedzi HTTP `422 Unprocessable Entity` i kontrakt `ProblemDetailModel`.<br>5. Ponownie pobierz bilans próbny i potwierdź brak zmiany sum `totalDebit` i `totalCredit`. |
| **TC-API-AK-08** | Aleksander Kaźmierczak (251544) | **P2** (Średni) | `POST /api/sales/sales-orders`<br>*(Negative Path — 400)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `SALES`. | Niepoprawne żądanie zostaje odrzucone na warstwie walidacji kontraktu (`400 Bad Request`); w bazie nie powstaje uszkodzony rekord zamówienia. | 1. Przygotuj niekompletny ładunek JSON `{}` (brak wymaganych pól `@NotNull partnerId`, `orderDate` oraz `@NotEmpty lines`).<br>2. Wyślij żądanie `POST /api/sales/sales-orders` z tokenem `SALES`.<br>3. Zweryfikuj kod odpowiedzi HTTP `400 Bad Request`.<br>4. Zwaliduj odpowiedź modelem RFC 9457 `ProblemDetailModel` (`status == 400`, `title == "Bad Request"`, niepuste pole `detail`). |

## 3. Przypadki REST API - Łukasz Murza

| ID | Kto odpowiada | Priorytet | Metoda / Endpoint lub widok UI | Warunki wstępne | Warunki końcowe | Kroki jakie będą wykonane |
|---|---|---|---|---|---|---|
| **TC-API-LM-01** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `GET /api/auth/me`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Konto `admin` jest dostępne.<br>3. Klient uwierzytelniony tokenem JWT dla roli `ADMIN`. | System zwraca poprawny profil administratora (`200 OK`). Stan systemu pozostaje niezmieniony. | 1. Wyślij żądanie `GET /api/auth/me`.<br>2. Zweryfikuj status `200 OK` i nagłówek JSON.<br>3. Zwaliduj odpowiedź modelem `CurrentUserResponseModel`.<br>4. Sprawdź `username == "admin"` oraz role `ADMIN`, `ACCOUNTANT`, `HR`, `SALES`, `WAREHOUSE`. |
| **TC-API-LM-02** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `GET /api/inventory/items/1/on-hand`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Istnieje towar `RM-DEMO` o ID `1`.<br>3. Klient uwierzytelniony jako `GUEST`. | System zwraca poprawny stan magazynowy (`200 OK`), a wartości finansowe są spójne. Stan magazynu pozostaje niezmieniony. | 1. Wyślij żądanie dla ID towaru `1`.<br>2. Zweryfikuj status `200 OK` i strukturę pięciu pól odpowiedzi.<br>3. Sprawdź SKU oraz wartości `onHandQty`, `avgUnitCost` i `totalValue` z użyciem `Decimal`.<br>4. Potwierdź zależność `totalValue == onHandQty * avgUnitCost`. |
| **TC-API-LM-03** | Łukasz Murza (`251592`) | **P2** (Średni) | `GET /api/masterdata/items/by-sku`<br>*(Negative Path — 404)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony.<br>3. SKU `LUK-NONEXISTENT-SKU` nie istnieje w kartotece towarów. | Żądanie zostaje odrzucone jako brakujący zasób (`404 Not Found`). Żaden towar nie zostaje utworzony ani zmodyfikowany. | 1. Wyślij żądanie `GET /api/masterdata/items/by-sku?sku=LUK-NONEXISTENT-SKU`.<br>2. Zweryfikuj status `404 Not Found`.<br>3. Zwaliduj odpowiedź RFC 9457 modelem `ProblemDetailModel`.<br>4. Sprawdź tytuł `Not Found` i opis zawierający informację o SKU. |
| **TC-API-LM-04** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `GET /api/auth/me`<br>*(Negative Path — 401)* | 1. Działający serwer REST API.<br>2. Klient nie posiada tokenu JWT. | Dostęp bez uwierzytelnienia zostaje zablokowany (`401 Unauthorized`); profil użytkownika nie zostaje ujawniony. | 1. Wyślij żądanie `GET /api/auth/me` bez nagłówka `Authorization`.<br>2. Zweryfikuj status `401 Unauthorized`.<br>3. Zwaliduj odpowiedź RFC 9457 modelem `ProblemDetailModel`.<br>4. Sprawdź tytuł `Unauthorized` oraz szczegół `Authentication required`. |
| **TC-API-LM-05** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `POST /api/masterdata/items`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ADMIN`.<br>3. Fabryka danych generuje unikalny SKU. | Towar zostaje utworzony (`201 Created`) z poprawnymi danymi i jest dostępny po nadanym ID. | 1. Wygeneruj poprawny JSON towaru z nazwą, typem, jednostką oraz kosztami `42.750000`, `7.000000`, `21.000000`.<br>2. Wyślij żądanie POST.<br>3. Zweryfikuj `201 Created` i odpowiedź modelem `ItemResponseModel`.<br>4. Porównaj SKU, nazwę i wartości dziesiętne z żądaniem.<br>5. Pobierz `GET /api/masterdata/items/{id}` i potwierdź trwałość zapisu. |
| **TC-API-LM-06** | Łukasz Murza (`251592`) | **P2** (Średni) | `POST /api/masterdata/warehouses`<br>*(Happy Path)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `ADMIN`.<br>3. Fabryka danych generuje unikalny kod magazynu. | Magazyn zostaje utworzony jako aktywny (`201 Created`) i jest widoczny na liście zasobów. | 1. Przygotuj JSON z kodem i nazwą `Lukasz Test Warehouse`.<br>2. Wyślij żądanie POST.<br>3. Zweryfikuj `201 Created` i odpowiedź modelem `WarehouseResponseModel`.<br>4. Sprawdź `active == True`.<br>5. Pobierz listę magazynów i odszukaj utworzony rekord. |
| **TC-API-LM-07** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `POST /api/purchasing/purchase-orders`<br>*(Negative Path — 404)* | 1. Działający serwer REST API.<br>2. Klient uwierzytelniony jako `WAREHOUSE`.<br>3. Partner o ID `999999999` nie istnieje. | Zamówienie zakupu nie zostaje utworzone; API zwraca `404 Not Found`. | 1. Przygotuj poprawnie uformowane zamówienie zakupu z nieistniejącym `partnerId`.<br>2. Wyślij żądanie POST.<br>3. Zweryfikuj status `404 Not Found`.<br>4. Zwaliduj odpowiedź RFC 9457 modelem `ProblemDetailModel`.<br>5. Sprawdź, że opis błędu wskazuje brak partnera. |
| **TC-API-LM-08** | Łukasz Murza (`251592`) | **P1** (Wysoki) | `POST /api/auth/login`<br>*(Negative Path — 401)* | 1. Działający serwer REST API.<br>2. Użytkownik `lukasz-invalid-user` nie istnieje. | Logowanie zostaje odrzucone (`401 Unauthorized`); token JWT nie zostaje wydany, a stan systemu pozostaje niezmieniony. | 1. Wyślij `POST /api/auth/login` z `username=lukasz-invalid-user` i `password=wrong-password`.<br>2. Zweryfikuj status `401 Unauthorized`.<br>3. Zwaliduj odpowiedź RFC 9457 modelem `ProblemDetailModel`.<br>4. Sprawdź tytuł `Unauthorized` i opis `Invalid username or password`. |

## 4. Przypadki Frontend UI - Aleksander Kaźmierczak

| ID | Kto odpowiada | Priorytet | Metoda / Endpoint lub widok UI | Warunki wstępne | Warunki końcowe | Kroki jakie będą wykonane |
|---|---|---|---|---|---|---|
| **TC-UI-AK-01** | Aleksander Kaźmierczak (251544) | **P0** (Krytyczny) | Widok `Dashboard` (`/`) — sekcja `ReconciliationHero`<br>*(Odpowiednik API: `TC-API-AK-01` `GET /api/reporting/reconciliation` — Happy Path)* | 1. Działający backend Spring Boot + PostgreSQL oraz zbudowana aplikacja SPA React 19.<br>2. Czysty kontekst przeglądarki Playwright (`erp.locale='en'`).<br>3. Spójny stan początkowy Księgi Głównej i podksiąg. | Dashboard potwierdza pełną równowagę bilansową (`Books reconcile`, `Trial balance balanced`, wszystkie podksięgi `Reconciled`, konta przejściowe `Cleared`). | 1. Otwórz `/login` i zaloguj się jako `accountant` (`LoginPage.login_as_role`).<br>2. Zweryfikuj przekierowanie na `/` oraz tożsamość `Signed in as accountant` (`ACCOUNTANT`).<br>3. Sprawdź nagłówek `Books reconcile` oraz zielony badge `Trial balance balanced`.<br>4. Zweryfikuj w tabeli podksiąg (`1200`, `2100`, `1310`, `1330`) ikony `Reconciled`.<br>5. Sprawdź w kartach kont przejściowych (`GR-IR`, `Deferred COGS`, `WIP`) ikony `Cleared`. |
| **TC-UI-AK-02** | Aleksander Kaźmierczak (251544) | **P1** (Wysoki) | Nawigacja `AppShell` oraz `/audit` (`ForbiddenPage`)<br>*(Odpowiednik API: `TC-API-AK-04` `GET /api/audit` — Negative Path 403 RBAC)* | 1. Działający serwer backendu oraz frontend SPA z aktywną kontrolą uprawnień `<RequireRole role="ADMIN">`.<br>2. Niezalogowana sesja przeglądarki na ekranie `/login`. | Dostęp roli `GUEST` do Rejestru Audytowego zostaje zablokowany zarówno w nawigacji bocznej, jak i przy bezpośrednim wejściu URL (`403 Forbidden`). | 1. Otwórz `/login` i kliknij przycisk `Browse as guest (read-only)`.<br>2. Potwierdź zalogowanie jako `guest` na widoku Dashboard.<br>3. Sprawdź, że w menu bocznym `.mantine-AppShell-navbar` pozycja `Audit Trail` jest ukryta.<br>4. Wykonaj bezpośrednią nawigację pod adres `/audit`.<br>5. Zweryfikuj wyrenderowanie `ForbiddenPage` (nagłówek `403`, komunikat `You don't have the role required for this action.`) i kliknij `Back to dashboard`. |
| **TC-UI-AK-03** | Aleksander Kaźmierczak (251544) | **P1** (Wysoki) | Widok `Master Data` (`/masterdata`) — zakładka `Partners` i modal `New partner`<br>*(Odpowiednik API: `TC-API-AK-05` `POST /api/masterdata/partners` — Happy Path)* | 1. Działający backend oraz frontend SPA.<br>2. Użytkownik zalogowany w UI jako `admin`.<br>3. Wygenerowany unikalny kod kontrahenta (`PRT-...`) przez `TestDataFactory`. | Nowy kontrahent zostaje utworzony przez formularz modalny, wyświetla się w tabeli UI z rolami `Vendor` i `Customer` oraz jest trwale zapisany w PostgreSQL. | 1. Zaloguj się w UI jako `admin`.<br>2. Przejdź przez menu boczne do `Master Data` (`/masterdata`) i otwórz zakładkę `Partners`.<br>3. Kliknij `New partner`, wypełnij `Code`, `Name`, włącz przełączniki `Vendor` i `Customer`, wpisz `Tax ID`, `Payment terms (days) = 45` oraz konta `2100`/`1200`.<br>4. Kliknij `Create` i zweryfikuj powiadomienie toast `Partner <CODE> created`.<br>5. Odszukaj wiersz w tabeli UI (z obsługą paginacji) i potwierdź zapis przez `GET /api/masterdata/partners`. |
| **TC-UI-AK-04** | Aleksander Kaźmierczak (251544) | **P0** (Krytyczny) | Widok `Ledger` (`/ledger`) — `ManualEntryPanel`<br>*(Odpowiednik API: `TC-API-AK-07` [Negative 422] oraz `TC-API-AK-06` [Happy Path] `POST /api/ledger/journal-entries`)* | 1. Działający backend oraz frontend SPA.<br>2. Użytkownik zalogowany w UI jako `accountant`.<br>3. Aktywne konta Księgi Głównej `1010` oraz `3100`. | Asymetryczny dekret jest blokowany w UI (`Unbalanced`, `Post entry` disabled), a po zbilansowaniu kwot zostaje pomyślnie zaksięgowany z zachowaniem równowagi Księgi Głównej. | 1. Zaloguj się w UI jako `accountant` i przejdź do modułu `Ledger` (`/ledger`).<br>2. W wierszu 1 wybierz konto `1010` i wpisz `Debit = 100.00`; w wierszu 2 wybierz konto `3100` i wpisz `Credit = 95.00`.<br>3. Zweryfikuj czerwony badge `Unbalanced` oraz zablokowanie przycisku `Post entry` (`disabled`).<br>4. Skoryguj kwoty w obu wierszach do równej wartości `350.00` (`Debit 1010 = 350.00`, `Credit 3100 = 350.00`).<br>5. Potwierdź zielony badge `Balanced`, kliknij `Post entry`, sprawdź toast `Journal entry #<nr> posted` oraz bilans próbny w API. |

## 5. Przypadki Frontend UI - Łukasz Murza

| ID | Kto odpowiada | Priorytet | Metoda / Endpoint lub widok UI | Warunki wstępne | Warunki końcowe | Kroki jakie będą wykonane |
|---|---|---|---|---|---|---|
| **TC-UI-LM-01** | Łukasz Murza (251592) | **P1** (Wysoki) | Master Data / Partners<br>*(Negative Path)* | 1. Działające ERP i konto guest z pustą listą ról.<br>2. W bazie istnieje co najmniej jeden kontrahent demonstracyjny. | 1. Konkretny kontrahent z API jest widoczny w tabeli UI.<br>2. GUEST nie ma dostępu do formularza tworzenia kontrahenta.<br>Nie powstaje nowy kontrahent; kontekst przeglądarki jest zamykany po teście. | 1. Pobierz jako GUEST listę kontrahentów z API i zapamiętaj kod oraz nazwę pierwszego istniejącego rekordu.<br>2. Zaloguj się przez formularz jako guest i otwórz Master Data / Partners.<br>3. Sprawdź widoczność konkretnego kodu i nazwy kontrahenta w wierszu tabeli.<br>4. Sprawdź brak przycisku New partner i okna tworzenia. |
| **TC-UI-LM-02** | Łukasz Murza (251592) | **P1** (Wysoki) | Ledger / Reversal<br>*(Negative Path)* | 1. Konto accountant z rolą ACCOUNTANT; wpis 999999999 nie istnieje, co potwierdza kontrolne GET 404. | 1. UI zgłasza brak wpisu; formularz wykonania storna nie jest udostępniony.<br>2. Nie powstaje żądanie zapisu w księdze.<br>Stan księgi pozostaje bez zmian. Pokryta jest ujemna ścieżka wyszukiwania do storna, a nie pełne poprawne odwrócenie zapisu. | 1. Potwierdź przez API brak wpisu 999999999 (404).<br>2. Zaloguj się jako accountant, otwórz Ledger i zakładkę Reversal.<br>3. Wpisz Entry no. = 999999999 i kliknij Load.<br>4. Sprawdź odpowiedź GET 404, komunikat No entry #999999999 i brak formularza Reverse entry / Reversal date.<br>5. Sprawdź, że nie wysłano żadnego POST do modułu Ledger. |
| **TC-UI-LM-03** | Łukasz Murza (251592) | **P1** (Wysoki) | Purchasing / Purchase orders<br>*(Negative Path)* | 1. Działające ERP i konto warehouse z rolą WAREHOUSE.<br>2. Istnieje co najmniej jeden dostawca dostępny do wyboru. | 1. UI wyświetla błąd wymaganej kompletnej pozycji.<br>2. Okno pozostaje otwarte; żądanie tworzenia zamówienia nie jest wysyłane.<br>Nowe zamówienie zakupu nie powstaje. Przypadek obejmuje walidację początku P2P, nie cały cykl rozliczenia. | 1. Zaloguj się jako warehouse i otwórz Purchase orders.<br>2. Otwórz New purchase order i wybierz dostawcę.<br>3. Pozostaw pozycję bez towaru, ilości i ceny; kliknij Create.<br>4. Sprawdź komunikat Add at least one complete line i nadal otwarte okno.<br>5. Sprawdź brak POST /api/purchasing/purchase-orders. |
| **TC-UI-LM-04** | Łukasz Murza (251592) | **P1** (Wysoki) | Reporting / Trial balance<br>*(Happy Path)* | 1. Działające ERP i konto accountant.<br>2. GET /api/reporting/trial-balance zwraca co najmniej jeden wiersz i sumy jako liczby dziesiętne. | 1. Raport jest widoczny; status, sumy i pierwszy wiersz są zgodne z odpowiedzią API.<br>2. Kwoty są pokazane z separatorem tysięcy i dwiema cyframi po przecinku.<br>Dane pozostają niezmienione. Test obejmuje bilans próbny ze scenariusza raportowania, nie pełne uzgodnienie wszystkich subledgerów. | 1. Zaloguj się jako accountant i otwórz Reports / Trial balance.<br>2. Przechwyć odpowiedź GET bilansu próbnego i sprawdź status 200 oraz niepustą listę.<br>3. Sprawdź aktywny panel raportu i zgodność oznaczenia Balanced/Unbalanced z odpowiedzią.<br>4. Porównaj sumy Winien/Ma w stopce tabeli z odpowiedzią API.<br>5. Porównaj nazwę oraz kwoty pierwszego konta w tabeli z API. |

## 6. Wspólna architektura i wykonanie

API i UI korzystają z **Python + pytest + Playwright**, wspólnego klienta HTTPX,
fabryki danych, modeli Pydantic i Page Object Model w `tests/pages/`.
`tests/test_frontend_lukasz.py` zawiera cztery rzeczywiste testy zamiast szablonu.
Nie ma drugiego runnera Node ani duplikatu POM w `ui/pages/`.

```powershell
python -m pip install -r requirements-test.txt
python -m playwright install chromium
python tools/check-test-plan.py
python run_tests.py --suite lukasz --layer frontend --collect-only
python run_tests.py --suite all --layer frontend --collect-only
python run_tests.py --suite all --layer all --collect-only
python run_tests.py --suite lukasz --layer frontend --backend-mode live --base-url http://localhost:8080 --frontend-url http://localhost:8081
```

`--layer ui` jest aliasem `frontend`, a `--ui-base-url` aliasem `--frontend-url`.
`--ui-channel chrome|msedge|chromium` wybiera przeglądarkę. Domyślny zestaw jest
zgodny z runnerem `main` (Aleksander); wybór Łukasza wymaga `--suite lukasz`.
`--suite all` uwzględnia obie osoby i osiem testów UI.

Tryb `--backend-mode live` wymaga rzeczywistego ERP i nie przechodzi na symulator.
`reference` jawnie wybiera istniejący model w pamięci. Domyślne `auto` zachowuje
wykrywanie z `main`; rodzaj faktycznie użytego backendu trafia do metadanych raportu.
Wynik na modelu referencyjnym nie potwierdza działania Spring Boot/PostgreSQL.
Przy jawnym adresie frontendu API musi wskazywać jego rzeczywisty backend.

Alternatywnie serwer SPA z `main` może podać zbudowane pliki React z
`ERPSystem/frontend/dist` lub `ERP_FRONTEND_DIST`. Każdy test ma osobny kontekst
przeglądarki, język EN i wyłączony onboarding. Logowanie pozostaje rzeczywiste.

UI Łukasza wymaga kont guest/accountant/warehouse, istniejącego kontrahenta
i dostawcy, niepustego bilansu oraz braku wpisu 999999999. Pozostałe wymagania
wynikają z tabel przypadków obu osób. Testy Aleksandra mogą tworzyć dokumenty;
używaj wydzielonej bazy testowej. Szczegóły konfiguracji są w README.

## 7. Scenariusze i pokrycie UI

| ID scenariusza | Moduł | Nazwa z zadania 1 |
|---|---|---|
| SC-GL-01 | Ledger | Integralność podwójnego zapisu |
| SC-GL-02 | Ledger | Zamknięcie okresu i roku |
| SC-GL-03 | Ledger | Odwracanie zapisów księgowych |
| SC-INV-01 | Inventory | Wycena średnią ważoną |
| SC-INV-02 | Inventory | Współbieżność gospodarki magazynowej |
| SC-P2P-01 | Purchasing | Cykl zakupu Procure-to-Pay |
| SC-O2C-01 | Sales | Cykl sprzedaży Order-to-Cash |
| SC-MFG-01 | Manufacturing | Cykl zlecenia produkcyjnego |
| SC-HR-01 | HR & Payroll | Naliczenie płac i dekretacja |
| SC-IAM-01 | IAM | Macierz uprawnień RBAC |
| SC-ERR-01 | Config | Standard kontraktu błędów RFC 9457 |
| SC-AI-01 | Assistant | ERP Copilot i ochrona HITL |
| SC-UI-01 | Frontend | Dostępność cyfrowa WCAG AA |
| SC-REP-01 | Reporting | Raport uzgodnienia Hero Check |

| Przypadek UI | Scenariusz zadania 1 | Pokryty zakres | Implementacja |
|---|---|---|---|
| TC-UI-AK-01 | SC-REP-01 | Raport uzgodnienia podksiąg i kont przejściowych w Dashboard. | `tests/test_frontend_aleksander.py::test_tc_ui_ak_01_reconciliation_hero_happy_path` |
| TC-UI-AK-02 | SC-IAM-01 | Dostęp GUEST do Audit Trail. | `tests/test_frontend_aleksander.py::test_tc_ui_ak_02_guest_audit_trail_rbac_403_forbidden` |
| TC-UI-AK-03 | SC-IAM-01 | Tworzenie kontrahenta przez ADMIN. | `tests/test_frontend_aleksander.py::test_tc_ui_ak_03_create_business_partner_modal_happy_path` |
| TC-UI-AK-04 | SC-GL-01 | Blokada asymetrycznego dekretu i księgowanie poprawnego wpisu. | `tests/test_frontend_aleksander.py::test_tc_ui_ak_04_unbalanced_journal_entry_blocked_and_balanced_posted` |
| TC-UI-LM-01 | SC-IAM-01 | Odczyt konkretnego kontrahenta i blokada tworzenia dla GUEST; inna funkcjonalność niż Audit Trail. | `tests/test_frontend_lukasz.py::test_tc_ui_lm_01_guest_reads_partner_without_create_action` |
| TC-UI-LM-02 | SC-GL-03 | Wyłącznie ujemna ścieżka ładowania nieistniejącego wpisu do storna; nie powiela formularza Manual entry. | `tests/test_frontend_lukasz.py::test_tc_ui_lm_02_missing_reversal_entry_shows_error_without_write` |
| TC-UI-LM-03 | SC-P2P-01 | Wyłącznie walidacja kompletności pozycji na początku P2P; nie pełny cykl zakupu. | `tests/test_frontend_lukasz.py::test_tc_ui_lm_03_purchase_order_requires_complete_line` |
| TC-UI-LM-04 | SC-REP-01 | Wyłącznie prezentacja bilansu próbnego; nie Hero Check ani pełne uzgodnienie subledgerów. | `tests/test_frontend_lukasz.py::test_tc_ui_lm_04_trial_balance_matches_api_presentation` |

## 8. Kryteria wyjścia, metryki i artefakty

Plan i kod muszą zawierać po osiem API i cztery UI na osobę, bez kolizji ID.
Każdy przypadek ma autora, priorytet, warunki, kroki, oczekiwania i powiązanie
z funkcją. Opis zakresu przy scenariuszu UI nie oznacza pełnego jego pokrycia.
Zmiana przypadku Łukasza nr 2 usuwa powielenie formularza niezbilansowanego dekretu.

Weryfikacja statyczna potwierdza zgodność rejestru, kodu, Markdown i DOCX.
Rzeczywiste wykonanie, zdawalność i defekty są raportowane osobno. W bieżącym
środowisku brakuje pytest/httpx/playwright, więc nowej suity Pythona nie zebrano
ani nie wykonano. Dawne wyniki runnera JavaScript nie są wynikami wersji Pythona.
Wymagane jest uruchomienie na osiągalnym ERP i sprawdzenie raportu HTML.

Status i dowody: `reports/RAPORT_ZADANIE_3.md`, `reports/UI_ZADANIE_3_WERYFIKACJA.json`.
Pozostałe prace: `TODO.md`. Generator: `python tools/build-test-plan.py`;
bez zależności Word: `python tools/build-test-plan.py --markdown-only`.
Historyczne propozycje przypadków zadania 1 w ogólnym DOCX są oznaczone jako takie;
obecny katalog implementacji jest w rozdziałach 18-19 tego dokumentu.
