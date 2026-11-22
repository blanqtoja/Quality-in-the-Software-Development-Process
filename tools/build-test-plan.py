"""Build the combined assignment-3 plan from existing API cases and the UI catalogue."""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def original_scenarios() -> list[list[str]]:
    with ZipFile(ROOT / "Plan_Testow_ERPSystem_Nowy.docx") as document:
        tree = ET.fromstring(document.read("word/document.xml"))
    for table in tree.findall(".//w:tbl", NS):
        rows = [
            ["".join(t.text or "" for t in cell.findall(".//w:t", NS)) for cell in row.findall("w:tc", NS)]
            for row in table.findall("w:tr", NS)
        ]
        if rows and rows[0][0] == "ID Scenariusza":
            return rows[1:]
    raise ValueError("Task-1 scenario table missing from the original test plan")


def render() -> str:
    cases = json.loads((ROOT / "ui/cases.json").read_text(encoding="utf-8"))
    api = (ROOT / "PRZYPADKI_TESTOWE_API.md").read_text(encoding="utf-8-sig")
    scenarios = original_scenarios()
    known = {row[0] for row in scenarios}
    assert all(case["scenario"] in known for case in cases)
    out = '''# Plan Testów - Manufacturing ERP: API i UI

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
'''
    for row in scenarios:
        linked = ", ".join(c["id"] for c in cases if c["scenario"] == row[0]) or "Poza zakresem 4 przypadków Łukasza"
        out += f"| {row[0]} | {row[1]} | {row[2]} | {linked} |\n"
    out += "\n## Przypadki testowe API - istniejąca część zadania 2\n\n"
    out += "Zachowano 16 implementacji i ich oczekiwania. Poniżej pełne tabele obu osób; szczegóły architektury API są w `PRZYPADKI_TESTOWE_API.md`.\n\n"
    for start, stop, heading in [("## 2.", "## 3.", "Aleksander Kaźmierczak"), ("## 4.", None, "Łukasz Murza")]:
        section = api[api.index(start):]
        if stop:
            section = section[:section.index(stop)]
        out += f"### API - {heading}\n\n"
        out += "\n".join(line for line in section.splitlines() if line.startswith("|")) + "\n\n"
    out += "## Przypadki testowe UI - zadanie 3\n\n"
    for case in cases:
        out += f"### {case['id']} - {case['name']}\n\n"
        out += "| Atrybut | Wartość |\n|---|---|\n"
        for label, value in [("Scenariusz zadania 1",case["scenario"]),("Osoba",case["author"]),("Cel",case["purpose"]),("Priorytet",case["priority"]),("Implementacja",f"`{case['file']}`; tytuł zaczyna się od `{case['id']}`")]:
            out += f"| {label} | {value} |\n"
        out += "\nWarunki wstępne:\n\n" + "\n".join(f"- {x}" for x in case["preconditions"]) + "\n"
        out += "\nDane testowe:\n\n" + "\n".join(f"- {x}" for x in case["data"]) + "\n"
        out += "\nPrzebieg:\n\n" + "\n".join(f"{i}. {x}" for i,x in enumerate(case["steps"],1)) + "\n"
        out += "\nOczekiwany wynik:\n\n" + "\n".join(f"- {x}" for x in case["expected"]) + "\n"
        out += f"\nStan końcowy: {case['postcondition']}\n\n"
    out += '''## Artefakty, metryki i harmonogram

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
'''
    return out


if __name__ == "__main__":
    target = ROOT / "PLAN_TESTOW_API_UI.md"
    target.write_text(render(), encoding="utf-8", newline="\n")
    print(f"Updated {target.name}: 16 existing API + 4 UI cases for Lukasz")
