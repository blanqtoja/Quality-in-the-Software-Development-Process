# Przypadki Testowe i Implementacja Testów REST API — Manufacturing ERP

- **Przedmiot:** Jakość w procesie wytwarzania oprogramowania
- **Testowany system (SUT):** Manufacturing ERP (`ERPSystem` — Spring Boot 4.1 / PostgreSQL 16)
- **Autorzy (Zespół):**
  - **Osoba 1 (zaimplementowany zestaw 8 testów + architektura i narzędzia wspólne):** Aleksander Kaźmierczak (`251544`)
  - **Osoba 2 (moduł rozszerzeń):** Łukasz Murza (`251592`)
- **Data opracowania:** 31 października 2026 r.

---

## 1. Dobór metod HTTP i struktura zestawu testowego

W badanym systemie **Manufacturing ERP** wszystkie operacje biznesowe (księga główna podwójnego zapisu, ruchy magazynowe, dokumenty zakupowe i sprzedażowe, rejestr audytowy) są z założenia **niezmienne (append-only / immutable)** — korekty wykonuje się dokumentami stornowania (`POST .../reverse`) zamiast nadpisywania lub kasowania rekordów. Z tego powodu kontrolery REST API systemu udostępniają wyłącznie metody **`GET`** oraz **`POST`** (brak metod `PUT` oraz `DELETE`).

Zgodnie z wymaganiami zadania:
- na jedną osobę przypada **8 różnych testów API**,
- dla każdej dostępnej metody HTTP przygotowano minimum 2 testy (w tym po równym podziale na ścieżki pozytywne **Happy Path** i negatywne **Negative Path**):
  - **4 testy dla metody `GET`**: 2× *Happy Path* (`TC-API-AK-01`, `TC-API-AK-02`) oraz 2× *Negative Path* (`TC-API-AK-03`, `TC-API-AK-04`),
  - **4 testy dla metody `POST`**: 2× *Happy Path* (`TC-API-AK-05`, `TC-API-AK-06`) oraz 2× *Negative Path* (`TC-API-AK-07`, `TC-API-AK-08`).

---

## 2. Tabela przypadków testowych REST API (Osoba 1: Aleksander Kaźmierczak)

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

---

## 3. Architektura kodu testowego (Zasady DRY i SRP oraz narzędzia dla drugiej osoby)

Kod testowy został zaprojektowany z wyraźnym podziałem odpowiedzialności (Single Responsibility Principle) oraz eliminacją powtórzeń (Don't Repeat Yourself), tak aby druga osoba w zespole (**Łukasz Murza**) mogła od razu pisać własne testy z użyciem gotowych komponentów:

```text
├── run_tests.py                  # Orkiestrator CLI (--suite aleksander | lukasz | all)
├── pytest.ini                    # Konfiguracja Pytest i markerów kategoryzujących
├── requirements-test.txt         # Zależności Pythona (pytest, httpx, pydantic, pytest-html)
└── tests/
    ├── config.py                 # Konfiguracja URL, timeoutów i ról RBAC (ErpRole, ROLE_ACCOUNTS)
    ├── models.py                 # Modele kontraktowe Pydantic (ProblemDetailModel, DTOs)
    ├── client.py                 # Klient ErpApiClient z buforowaniem tokenów JWT per rola
    ├── factories.py              # Fabryka TestDataFactory generująca unikalne, idempotentne dane
    ├── assertions.py             # Wspólne asercje HTTP, RFC 9457 problem+json oraz Decimal
    ├── local_erp_server.py       # Wbudowany silnik referencyjny (automatyczny fallback bez Dockera)
    ├── conftest.py               # Fixtury Pytest dla wszystkich ról i danych wstępnych
    ├── test_api_aleksander.py    # 8 zaimplementowanych testów API (Osoba 1: Aleksander Kaźmierczak)
    └── test_api_lukasz.py        # Gotowy moduł z zaimportowanymi narzędziami (Osoba 2: Łukasz Murza)
```

### Sposób uruchomienia testów

```bash
# Uruchomienie 8 testów Aleksandra Kaźmierczaka przez orkiestrator (generuje też raport HTML):
python run_tests.py --suite aleksander

# Uruchomienie testów drugiej osoby:
python run_tests.py --suite lukasz

# Uruchomienie całej suity zespołu bezpośrednio przez Pytest:
python -m pytest
```

---

## 4. Tabela przypadków testowych REST API (Osoba 2: Lukasz Murza)

W zweryfikowanym kontrakcie systemu występują wyłącznie metody `GET` i `POST`; operacje `PUT` i `DELETE` nie są udostępniane. Poniższe przypadki są odrębne od scenariuszy Aleksandra.

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

Każdy przypadek odpowiada jednej funkcji `test_luk_*` w pliku `tests/test_api_lukasz.py`.
