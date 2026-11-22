# Zadanie 3 - integracja części Łukasza

Stan: 22.11.2026. Nowa praca obejmuje wyłącznie Łukasza; istniejący kod Aleksandra
z `main` jest zachowany. Katalog zespołu zawiera 16 API i 8 UI.

## 1. Wykonane

- [x] Potwierdzić aktualny `main` (`af43160`) i porównać cztery przypadki UI.
- [x] Zastąpić duplikat dekretu ujemną ścieżką ładowania wpisu do storna (SC-GL-03).
- [x] Wzmocnić test GUEST o sprawdzenie kodu i nazwy konkretnego kontrahenta.
- [x] Oznaczyć pokrycie bilansu próbnego jako wycinek SC-REP-01.
- [x] Przenieść cztery UI Łukasza do `tests/test_frontend_lukasz.py`.
- [x] Wykorzystać wspólny Python/pytest/Playwright POM z `main` i usunąć osobny Node/POM.
- [x] Ujednolicić ID Łukasza do TC-API-LM-01..08 i TC-UI-LM-01..04.
- [x] Udostępnić jeden runner dla obu osób i wszystkich 24 przypadków.
- [x] Zaktualizować wspólny plan i katalog: jednolite numerowane rozdziały oraz tabele.
- [x] Odczytać i porównać zawartość obu wersji DOCX, a nie tylko identyfikatory Git.
- [x] Uzupełnić oba DOCX o 16 API i 8 UI, zachowując definicje stylów `main`.
- [x] Sprawdzić statycznie ID, autorstwo, strukturę testów i spójność wszystkich formatów.
- [x] Potwierdzić, że źródła testów Aleksandra są identyczne z `main`.
- [x] Rozwiązać treść wszystkich 11 konfliktów rozpoczętego merge'a main z V2.
- [x] Sprawdzić importy, fixtury, zachowanie metod POM i wszystkie kombinacje runnera.

## 2. Do wykonania przed potwierdzeniem działania

- [ ] Zainstalować `requirements-test.txt` i przeglądarkę Playwright.
- [ ] Zebrać nową suitę pytest: 4 UI Łukasza, 8 UI zespołu i 24 API/UI zespołu.
- [ ] Zapewnić osiągalne ERP i przygotować konta oraz dane z Planu Testów.
- [ ] Wykonać UI Łukasza i regresję wspólnej infrastruktury z testami Aleksandra.
- [ ] Zachować rzeczywisty raport HTML i uzupełnić wyniki przypadków.
- [ ] Obejrzeć strony DOCX w Wordzie lub po renderowaniu; obecnie brak LibreOffice.
- [ ] Zapisać rozwiązania do indeksu Git i utworzyć merge commit. Blokada tej sesji: brak prawa zapisu do `.git/index.lock`.

Merge rozpoczął użytkownik. Treść konfliktów poprawiono, lecz 11 ścieżek pozostaje
`unmerged` w indeksie, ponieważ `git add` zwraca Permission denied. Nowy commit
nie powstał; push nie jest objęty tym zadaniem. Bieżący stan i polecenia zakończenia:
[raport integracji](reports/RAPORT_MERGE_MAIN_V2.md).
Brak wykonania testów nie oznacza PASSED.
