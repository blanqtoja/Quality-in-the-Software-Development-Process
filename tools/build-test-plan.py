"""Generate consistent Markdown/DOCX catalogues from the shared test-case registry."""

from __future__ import annotations

import argparse
from copy import deepcopy
from io import BytesIO
import html
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "af43160fc201760d3d49d66c8f6a4a2b615c9ed0"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
HEADERS = ["ID", "Kto odpowiada", "Priorytet", "Metoda / Endpoint lub widok UI", "Warunki wstępne", "Warunki końcowe", "Kroki jakie będą wykonane"]
GROUPS = [("api", "aleksander"), ("api", "lukasz"), ("frontend", "aleksander"), ("frontend", "lukasz")]


def main_bytes(name: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{MAIN_SHA}:{name}"], cwd=ROOT)


def scenarios() -> list[list[str]]:
    with ZipFile(BytesIO(main_bytes("Plan_Testow_ERPSystem_Nowy.docx"))) as archive:
        tree = ET.fromstring(archive.read("word/document.xml"))
    for table in tree.findall(".//w:tbl", NS):
        rows = [["".join(t.text or "" for t in cell.findall(".//w:t", NS)) for cell in row.findall("w:tc", NS)] for row in table.findall("w:tr", NS)]
        if rows and rows[0][0] == "ID Scenariusza":
            return rows[1:]
    raise ValueError("Scenario table missing in the baseline plan")


def values(case: dict) -> list[str]:
    return [case["id"], case["author"], case["priority"], case["view"], case["preconditions"], case["postconditions"], case["steps"]]


def markdown_table(cases: list[dict]) -> str:
    text = "| " + " | ".join(HEADERS) + " |\n|" + "---|" * len(HEADERS) + "\n"
    for case in cases:
        cells = values(case)
        cells[0] = f"**{cells[0]}**"
        text += "| " + " | ".join(str(c).replace("|", "\\|").replace("\n", "<br>") for c in cells) + " |\n"
    return text + "\n"


def groups(cases: list[dict], starting_at: int = 2) -> str:
    text = ""
    for number, (layer, owner) in enumerate(GROUPS, starting_at):
        author = "Aleksander Kaźmierczak" if owner == "aleksander" else "Łukasz Murza"
        label = "REST API" if layer == "api" else "Frontend UI"
        text += f"## {number}. Przypadki {label} - {author}\n\n"
        text += markdown_table([c for c in cases if c["layer"] == layer and c["owner"] == owner])
    return text


def coverage_table(cases: list[dict]) -> str:
    text = "| Przypadek UI | Scenariusz zadania 1 | Pokryty zakres | Implementacja |\n|---|---|---|---|\n"
    for case in cases:
        if case["layer"] == "frontend":
            text += f"| {case['id']} | {case['scenario_id']} | {case['coverage_note']} | `{case['test_file']}::{case['function']}` |\n"
    return text + "\n"


def render_markdown(cases: list[dict]) -> tuple[str, str]:
    intro = '''# Plan Testów - Manufacturing ERP: API i UI

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

'''
    architecture = '''## 6. Wspólna architektura i wykonanie

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

'''
    plan = intro + groups(cases) + architecture
    plan += "## 7. Scenariusze i pokrycie UI\n\n"
    plan += "| ID scenariusza | Moduł | Nazwa z zadania 1 |\n|---|---|---|\n"
    for row in scenarios():
        plan += f"| {row[0]} | {row[1]} | {row[2]} |\n"
    plan += "\n" + coverage_table(cases)
    plan += '''## 8. Kryteria wyjścia, metryki i artefakty

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
'''
    catalogue = '''# Przypadki Testowe API i UI - Manufacturing ERP

## 1. Informacje o zadaniu, autorstwie i identyfikatorach

Zespół: Aleksander Kaźmierczak (251544), Łukasz Murza (251592). Stan: 22.11.2026.
Katalog zawiera 16 istniejących API i 8 UI; nowa praca dotyczy czterech UI Łukasza.
GET/POST zamiast PUT/DELETE zaakceptował prowadzący. Standard ID:
`TC-{API|UI}-{AK|LM}-{NUMER}`; scenariusze zachowują osobne ID `SC-*`.
Źródło tabel: `docs/test_cases.json`. Nadrzędny plan: [PLAN_TESTOW_API_UI.md](PLAN_TESTOW_API_UI.md).

'''
    catalogue += groups(cases) + architecture
    catalogue += "### 6.1. Powiązanie przypadków UI ze scenariuszami\n\n" + coverage_table(cases)
    return plan.rstrip() + "\n", catalogue.rstrip() + "\n"


def plain(value: str) -> str:
    value = re.sub(r"<br\s*/?>", "\n", value)
    return html.unescape(re.sub(r"\*\*|`|(?<!\w)\*(?!\s)|(?<!\s)\*(?!\w)", "", value))


def replace_cell(cell, value: str) -> None:
    # Keep the inherited main-branch table font/paragraph formatting for new rows.
    paragraph = cell.paragraphs[0]
    paragraph_properties = deepcopy(paragraph._p.pPr)
    run_properties = deepcopy(paragraph.runs[0]._r.rPr) if paragraph.runs else None
    cell.text = plain(value)
    for paragraph in cell.paragraphs:
        if paragraph._p.pPr is not None:
            paragraph._p.remove(paragraph._p.pPr)
        if paragraph_properties is not None:
            paragraph._p.insert(0, deepcopy(paragraph_properties))
        for run in paragraph.runs:
            if run._r.rPr is not None:
                run._r.remove(run._r.rPr)
            if run_properties is not None:
                run._r.insert(0, deepcopy(run_properties))


def fill_table(table, records: list[list[str]], headers: list[str]) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    template = deepcopy(table.rows[1]._tr)
    for row in list(table.rows)[1:]:
        table._tbl.remove(row._tr)
    for cell, text in zip(table.rows[0].cells, headers):
        replace_cell(cell, text)
    header_props = table.rows[0]._tr.get_or_add_trPr()
    if header_props.find(qn("w:tblHeader")) is None:
        header_props.append(OxmlElement("w:tblHeader"))
    for record in records:
        table._tbl.append(deepcopy(template))
        for cell, value in zip(table.rows[-1].cells, record):
            replace_cell(cell, str(value))


def write_docx(cases: list[dict]) -> None:
    from docx import Document

    api = [c for c in cases if c["layer"] == "api"]
    ui = [c for c in cases if c["layer"] == "frontend"]
    for name in ["Plan_Testow_ERPSystem_Nowy.docx", "Przypadki_Testowe_API_ERPSystem.docx"]:
        document = Document(BytesIO(main_bytes(name)))
        if name.startswith("Plan_"):
            fill_table(document.tables[18], [values(c) for c in api], HEADERS)
            fill_table(document.tables[19], [values(c) for c in ui], HEADERS)
            for paragraph in document.paragraphs:
                if paragraph.text.startswith("18."):
                    paragraph.text = "18. Zestaw przypadków testowych REST API - zespół (16)"
                elif paragraph.text.startswith("19."):
                    paragraph.text = "19. Zestaw przypadków testowych Frontend UI - zespół (8)"
                elif paragraph.text.startswith("14. Przypadki"):
                    paragraph.text = "14. Historyczne propozycje przypadków zadania 1 (obecna implementacja: rozdziały 18-19)"
                elif paragraph.text.startswith("15.3"):
                    paragraph.text = "15.3 Przykładowa tabela ze wstępnego planu - nie jest bieżącym raportem wykonania"
                elif "Poniższa tabela przedstawia zestaw 4 przypadków" in paragraph.text:
                    paragraph.text = "Poniższa tabela zawiera 8 przypadków UI obu osób we wspólnym Python/pytest/Playwright POM. Aktualny stan wykonania: reports/RAPORT_ZADANIE_3.md."
                elif "Poniższa tabela" in paragraph.text and "REST API" in paragraph.text:
                    paragraph.text = "Poniższa tabela zawiera 16 przypadków API obu osób: po 4 GET i 4 POST na osobę, zgodnie z uzgodnieniem prowadzącego."
        else:
            fill_table(document.tables[1], [values(c) for c in api], HEADERS)
            fill_table(document.tables[2], [values(c) for c in ui], HEADERS)
            for paragraph in document.paragraphs:
                if paragraph.text.startswith("3."):
                    paragraph.text = "3. Zbiorcza tabela przypadków testowych REST API - zespół (16)"
                elif paragraph.text.startswith("4."):
                    paragraph.text = "4. Zbiorcza tabela przypadków testowych Frontend UI - zespół (8)"
                elif paragraph.text.startswith("6."):
                    paragraph.text = "6. Bieżący stan weryfikacji API i UI (bez deklaracji wykonania)"
                elif "Poniższa tabela przedstawia 4 przypadki" in paragraph.text:
                    paragraph.text = "Tabela obejmuje cztery istniejące przypadki Aleksandra i cztery przypadki Łukasza, zaimplementowane we wspólnym Python/pytest/Playwright POM."
            for row in document.tables[0].rows[1:]:
                if "251592" in " ".join(c.text for c in row.cells):
                    replace_cell(row.cells[-1], "8 istniejących API + 4 UI; test_frontend_lukasz.py")
            reports = [[c["id"], "API" if c["layer"] == "api" else "UI", c["function"], c["kind"], plain(c["view"]), "NIE POWTÓRZONO" if c["owner"] == "aleksander" or c["layer"] == "api" else "NOT RUN"] for c in cases]
            fill_table(document.tables[4], reports, ["ID Testu", "Warstwa", "Funkcja testowa w Pytest", "Typ ścieżki", "Weryfikowany obszar", "Status"])
            architecture = document.tables[3]
            for row in architecture.rows[1:]:
                if row.cells[0].text.strip() == "tests/test_frontend_lukasz.py":
                    replace_cell(row.cells[2], "Implementacja czterech przypadków TC-UI-LM-01..04")
                    replace_cell(row.cells[3], "Wspólne fixtury pytest i POM w tests/pages/")
            for module, role in [("tests/pages/purchasing_page.py", "Walidacja pozycji zamówienia zakupu"), ("tests/pages/reporting_page.py", "Zgodność tabeli bilansu próbnego z odpowiedzią API")]:
                architecture._tbl.append(deepcopy(architecture.rows[-1]._tr))
                for cell, value in zip(architecture.rows[-1].cells, [module, "Frontend UI", role, "Wspólny BaseErpPage i fixtury pytest"]):
                    replace_cell(cell, value)
        document.add_paragraph("Aktualizacja 22.11.2026: 16 API + 8 UI, jednolite identyfikatory TC-{API|UI}-{AK|LM}-{NN}. Nowa implementacja dotyczy wyłącznie Łukasza; przypadki Aleksandra przejęto z main. Definicje i pokrycie: PLAN_TESTOW_API_UI.md; wyniki wykonania: reports/RAPORT_ZADANIE_3.md.")
        document.core_properties.subject = "Wspólny katalog API i UI - 16 API + 8 UI"
        document.save(ROOT / name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown-only", action="store_true")
    args = parser.parse_args()
    cases = json.loads((ROOT / "docs/test_cases.json").read_text(encoding="utf-8"))
    plan, catalogue = render_markdown(cases)
    (ROOT / "PLAN_TESTOW_API_UI.md").write_text(plan, encoding="utf-8", newline="\n")
    (ROOT / "PRZYPADKI_TESTOWE_API.md").write_text(catalogue, encoding="utf-8", newline="\n")
    if not args.markdown_only:
        write_docx(cases)
    print("Generated shared plan/catalogue: 16 API + 8 UI (4 new UI for Lukasz)")


if __name__ == "__main__":
    main()
