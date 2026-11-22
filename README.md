# QitSDP - testy API i UI Manufacturing ERP

Aktualny zakres zadania 3: **wyłącznie osoba 2, Łukasz Murza (251592) - 4 testy UI**.
Repozytorium zachowuje istniejące 16 testów API obu osób z zadania 2. Prowadzący
zaakceptował dla API GET/POST zamiast PUT/DELETE.

- [Plan Testów: istniejące API i UI Łukasza](PLAN_TESTOW_API_UI.md)
- [Raport części Łukasza](reports/RAPORT_ZADANIE_3.md)
- [Lista prac](TODO.md)
- [Katalog czterech przypadków UI](ui/cases.json)

Plan wykorzystuje scenariusze zadania 1 z `Plan_Testow_ERPSystem_Nowy.docx`
i wzory z katalogu `Zasoby/Zasoby`. Wersja Markdown jest bieżącym planem API/UI;
pierwotny DOCX pozostaje źródłem scenariuszy i strategii całego ERP.

## Uruchomienie UI Łukasza

Wymagane: Node.js 20+, osiągalny frontend ERP z backendem, konta guest/accountant/warehouse,
kontrahent i dostawca oraz niepusty bilans z kontami 1010/3100.
Polecenia dla PowerShell w katalogu repozytorium:

```powershell
npm install
npx playwright install chromium
node tools/check-ui-plan.cjs
npm run test:ui:list

$env:ERP_UI_BASE_URL = 'http://localhost:8081'
npm run test:ui:lukasz
npm run report:ui
```

`npm run test:ui` również uruchamia wyłącznie dostępne 4 testy Łukasza.
Zamiast pobierania Chromium można ustawić `$env:ERP_UI_CHANNEL = 'chrome'`
albo `'msedge'` dla zainstalowanej przeglądarki.

Domyślne hasła kont demonstracyjnych są równe loginom. Własne dane:
`ERP_UI_<ROLA>_USERNAME` i `ERP_UI_<ROLA>_PASSWORD`. Inne konta księgowe:
`ERP_UI_DEBIT_ACCOUNT` i `ERP_UI_CREDIT_ACCOUNT`.

UI-LUK-001..004 sprawdzają uprawnienia guest w kartotekach kontrahentów, blokadę
niezbilansowanego dekretu, walidację pustej pozycji zakupu i zgodność bilansu próbnego
z rzeczywistą odpowiedzią API. Testy logują się przez formularz, mają osobne konteksty
przeglądarki i korzystają ze wspólnych Page Objects. Nie podmieniają odpowiedzi API
ani nie zastępują niedostępnego UI symulatorem. Nie księgują dokumentów;
logowanie może zmieniać sesję i rejestr audytowy.

## Wspólny runner i plan

```powershell
python run_tests.py --layer ui --suite lukasz --ui-base-url http://localhost:8081
python run_tests.py --layer ui --collect-only
python tools/build-test-plan.py
node tools/check-ui-plan.cjs

# Istniejące testy API obu osób pozostają dostępne:
python -m pip install -r requirements-test.txt
python run_tests.py --layer api --suite all --base-url http://localhost:8081
```

Domyślny zestaw dla UI i `--layer all` to Łukasz; dotychczasowy domyślny zestaw
samego API pozostaje Aleksander. `--suite all` w warstwie UI oznacza wszystkie
dostępne przypadki UI, czyli 4 Łukasza. Wybór UI Aleksandra jest odrzucany,
ponieważ jego część nie jest objęta tą aktualizacją.

Raporty UI: `reports/ui/html/` i `reports/ui/results.json`; screenshoty i trace
przy niepowodzeniu: `test-results/ui/`. `--list` nie nadpisuje raportu wykonania.

Po zawężeniu zakresu zebrano 4 testy Łukasza i sprawdzono zgodność planu z kodem.
Wcześniejsza kontrola dostępności ERP zakończyła się `connect EACCES ::1:8081`
przed wykonaniem przypadków. Testy Łukasza pozostają niewykonane na SUT;
ta kontrola nie jest dowodem PASSED ani defektu ERP.
