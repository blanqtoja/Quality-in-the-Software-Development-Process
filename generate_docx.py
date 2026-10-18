import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_document():
    doc = docx.Document()

    # Standard A4 Margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = RGBColor(18, 63, 60) # Ink Primary

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(14)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(13)
        run.font.italic = True
        run.font.color.rgb = RGBColor(90, 90, 90)

    def add_meta(label, val):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"{label}: ")
        r1.font.bold = True
        r1.font.name = 'Calibri'
        r1.font.size = Pt(10.5)
        r2 = p.add_run(val)
        r2.font.name = 'Calibri'
        r2.font.size = Pt(10.5)

    def add_heading1(text):
        p = doc.add_heading(level=1)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = RGBColor(18, 63, 60)

    def add_heading2(text):
        p = doc.add_heading(level=2)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(37, 99, 235)

    def add_heading3(text):
        p = doc.add_heading(level=3)
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(55, 65, 81)

    def add_p(text, bold_prefix=None, italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Calibri'
            r_pre.font.bold = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(10.5)
        if italic:
            run.font.italic = True

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Calibri'
            r_pre.font.bold = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(10.5)

    def add_table_data(headers, rows):
        table = doc.add_table(rows=len(rows)+1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True
        hdr_cells = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            shading = parse_xml(r'<w:shd {} w:fill="123F3C"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading)
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Calibri'
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(9.5)
        for r_idx, row in enumerate(rows):
            row_cells = table.rows[r_idx+1].cells
            bg_color = "F9FAFB" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row):
                row_cells[c_idx].text = str(val)
                shading = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), bg_color))
                row_cells[c_idx]._tc.get_or_add_tcPr().append(shading)
                p = row_cells[c_idx].paragraphs[0]
                for r in p.runs:
                    r.font.name = 'Calibri'
                    r.font.size = Pt(9)
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_after = Pt(4)

    # Document Header
    add_title("PLAN TESTÓW OPROGRAMOWANIA")
    add_subtitle("System ERP dla Przedsiębiorstwa Produkcyjnego (Manufacturing ERP)")
    
    add_meta("Przedmiot", "Jakość w procesie wytwarzania oprogramowania")
    add_meta("Standard", "IEEE 829 / ISO/IEC/IEEE 29119 oraz wzorce uczelniane")
    add_meta("Wersja", "1.0.0")
    add_meta("Data opracowania", "18 października 2026 r.")

    # Zespół projektowy
    add_heading2("Zespół projektowy i recenzenci")
    add_table_data(
        ["Rola w zespole", "Imię i nazwisko", "Kontakt (adres e-mail)"],
        [
            ["Autor przewodni", "Główny Inżynier Jakości (QA Lead)", "qa-lead@erp-project.org"],
            ["Współautorzy", "Zespół Inżynierii Jakości i Testów (SDET), Architekt Backend", "dev-qa-team@erp-project.org"],
            ["Recenzenci", "Kierownik Projektu, Właściciel Produktu (Product Owner)", "po-management@erp-project.org"]
        ]
    )

    # Historia zmian
    add_heading1("Historia zmian (Dziennik rewizji dokumentu)")
    add_table_data(
        ["Rewizja", "Data", "Modyfikujący", "Zmodyfikowane paragrafy", "Komentarz / Zakres zmian"],
        [
            ["0.1.0", "2026-10-18", "Główny Inżynier QA", "Wszystkie", "Utworzenie pierwotnej wersji szkieletu planu testów."],
            ["0.5.0", "2026-10-18", "Główny Inżynier QA", "Rozdz. 4-9", "Włączenie twardych reguł bilansowych (GL, GR-IR, WIP, Deferred-COGS)."],
            ["0.9.0", "2026-10-18", "Zespół QA & Architekt", "Rozdz. 10-14", "Dodanie szczegółowych przypadków testowych TC-001 do TC-010 i wytycznych AI."],
            ["1.0.0", "2026-10-18", "Kierownik Jakości", "Całość dokumentu", "Finalna redakcja i formalne zatwierdzenie dokumentu."]
        ]
    )

    # 1. Wstęp
    add_heading1("1. Wstęp")
    add_p("Niniejszy dokument przedstawia plan testów dla zintegrowanego systemu klasy ERP dedykowanego przedsiębiorstwom produkcyjnym (Manufacturing ERP), dostępnego w repozytorium ERPSystem. Dokument stanowi bezpośrednią realizację wymagań i wytycznych dla przedmiotu „Jakość w procesie wytwarzania oprogramowania”.")
    add_p("W kolejnych rozdziałach dokumentu opisano wyniki prac:")
    add_bullet("Teoretycznych, mających określić kontekst testowania, model dziedzinowy systemu ERP (ze szczególnym uwzględnieniem księgi głównej podwójnego zapisu, wyceny magazynowej metodą średniej ważonej oraz rozliczeń produkcyjnych) oraz ryzyka z niego wynikające.")
    add_bullet("Koncepcyjnych, mających określić optymalne podejście do testowania systemu Manufacturing ERP na wszystkich poziomach piramidy testów oraz odpowiednie techniki projektowania testów.")
    add_bullet("Projektowych, mających określić wymagane metryki jakościowe, personel, organizację środowisk testowych oraz harmonogram testowania systemu w metodyce Scrum.")

    # 2. Terminologia i definicje
    add_heading1("2. Terminologia i definicje")
    add_table_data(
        ["Termin / skrót", "Opis"],
        [
            ["Manufacturing ERP / System", "Zintegrowany system informatyczny klasy ERP do zarządzania produkcją, magazynem, finansami i kadrami."],
            ["GL (General Ledger)", "Księga Główna - centralny rejestr księgowy ewidencjonujący wszystkie zdarzenia w ujęciu bilansowym."],
            ["Double-Entry GL", "Zasada podwójnego zapisu: każda transakcja gospodarcza bilansuje się tak, że SUM(debit) = SUM(credit) w tej samej transakcji DB."],
            ["Subledger", "Księga pomocnicza (magazynowa StockLedgerEntry, rozrachunków AP i AR) uzgadniana z kontem syntetycznym GL."],
            ["GR-IR", "Goods Receipt / Invoice Receipt (konto 2150) - konto rozliczenia zakupu, zerujące się po otrzymaniu towaru i faktury."],
            ["Deferred-COGS", "Odroczony koszt własny sprzedaży (konto 1340) - koszt wydania towaru przeksięgowywany na COGS w momencie faktury."],
            ["WIP", "Work in Progress (konto 1320) - konto produkcji w toku, czyszczone do zera po przyjęciu wyrobu gotowego."],
            ["Moving-Average Valuation", "Wycena zapasów metodą średniej ważonej ruchomej z bezpośrednią rewaluacją przy odchyleniach cen."],
            ["RBAC", "Role-Based Access Control - kontrola dostępu oparta na rolach: ADMIN, ACCOUNTANT, WAREHOUSE, SALES, HR, GUEST."],
            ["RFC 9457", "Standard ujednoliconych odpowiedzi o błędach HTTP w formacie application/problem+json."],
            ["ArchUnit", "Narzędzie do automatycznego testowania architektury kodu Java i granic modułów w CI."],
            ["Testcontainers", "Biblioteka powołująca rzeczywistą instancję bazy PostgreSQL 16 w kontenerze Docker na czas testów."],
            ["HITL", "Human-in-the-Loop - wymóg bezpośredniego zatwierdzenia przez człowieka operacji zapisu asystenta AI."]
        ]
    )

    # 3. Zakres dokumentu
    add_heading1("3. Zakres dokumentu")
    add_p("Niniejszy plan testów obejmuje zintegrowany system Manufacturing ERP składający się z modularnego backendu w technologii Java/Spring Boot, bazy PostgreSQL, aplikacji klienckiej React oraz wbudowanego modułu asystenta AI (ERP Copilot). Dokument obejmuje wszystkie fazy testowania systemu, stanowiąc nadrzędny dokument kontroli jakości w projekcie.")

    # 4. Opis testowanego systemu
    add_heading1("4. Opis testowanego systemu (System Manufacturing ERP)")
    add_p("System Manufacturing ERP został zaprojektowany i zaimplementowany jako Monolit Modułowy (Modular Monolith) z heksagonalnym podziałem na moduły biznesowe. Każdy moduł komunikuje się z pozostałymi wyłącznie za pośrednictwem opublikowanego interfejsu (pakiet *.api), bez bezpośredniego odwoływania się do wewnętrznych encji czy tabel obcych modułów.")
    
    add_heading2("Model Architektoniczny i Granice Komponentów")
    add_p("Architektura systemu obejmuje trzy główne warstwy: (1) Warstwę Prezentacji SPA (React 19, Mantine UI, WCAG AA, ERP Copilot Drawer), (2) Ustandaryzowany Interfejs REST API z filtrem autoryzacji RBAC/JWT, oraz (3) Rdzeń Monolitu Modułowego komunikujący się z bazą danych PostgreSQL 16.")
    add_p("Rysunek 4.1 w dokumentacji projektu przedstawia architekturę heksagonalną z wydzielonymi modułami: purchasing, sales, manufacturing, inventory, hr, ledger, reporting, iam, assistant oraz audit/observation. Rysunek 4.2 obrazuje przepływ transakcyjny operacji Buy -> Make -> Sell z atomowym podwójnym zapisem i weryfikacją raportu uzgodnienia (Hero Check).", italic=True)

    add_p("Główne komponenty systemu:")
    add_bullet("Moduł ledger: podwójny zapis Winien=Ma, okresy obrachunkowe, zamknięcie roku, odwracanie zapisów.")
    add_bullet("Moduł masterdata: kartoteki towarów, kontrahentów, magazynów, lokacji, reguł księgowania.")
    add_bullet("Moduł inventory: wycena średnią ważoną ruchomą, podwójna księga StockLedgerEntry, pesymistyczne blokowanie stanów.")
    add_bullet("Moduł purchasing (P2P): zamówienia zakupu (PO), przyjęcia (GRN), faktury zakupu, rozliczenie GR-IR i subledgera AP.")
    add_bullet("Moduł sales (O2C): zamówienia sprzedaży (SO), wydania (Delivery), faktury, zwroty, rozliczenie Deferred-COGS i subledgera AR.")
    add_bullet("Moduł manufacturing: struktury BOM, zlecenia produkcyjne Work Order, rozliczenie produkcji w toku WIP do zera.")
    add_bullet("Moduł hr: pracownicy, urlopy, timesheety, naliczanie płac i automatyczny dekret do Księgi Głównej.")
    add_bullet("Moduł iam: uwierzytelnianie JWT (Access w pamięci, Refresh w ciasteczku httpOnly) oraz autoryzacja 5 ról + gość.")
    add_bullet("Moduł assistant: asystent AI Claude z 12 narzędziami analitycznymi i wymogiem zatwierdzenia zapisu (HITL).")
    add_bullet("Moduł reporting: sprawozdania finansowe oraz centralny raport uzgodnienia ksiąg (Reconciliation Hero Check).")
    add_bullet("Frontend SPA: React 19, Mantine UI 9.4 (motyw Ink Ledger), dostępność WCAG AA, całkowity brak floatów w kwotach.")

    # 5. Zakres testowania
    add_heading1("5. Zakres testowania")
    add_p("W ramach planu testów weryfikacji podlegają komponenty backendu, granice modułów, baza danych, interfejsy REST API, interfejs użytkownika oraz asystent AI.")
    add_p("W ramach testów zostaną przeprowadzone testy na poziomie jednostkowym, architektonicznym, integracyjnym, systemowym oraz dostępności. Zostaną wykorzystane następujące typy testów: funkcjonalne, strukturalne, regresyjne, bezpieczeństwa, współbieżności oraz związane ze zmianą.")

    # 6. Założenia i ograniczenia
    add_heading1("6. Założenia i ograniczenia")
    add_bullet("Całkowity brak float/double w kwotach finansowych: operacje w backendzie realizowane na BigDecimal, w JSON serializowane jako String.")
    add_bullet("Zasada podwójnego zapisu jest bezwzględnie wymuszana triggerem bazy PostgreSQL (DEFERRED CONSTRAINT).")
    add_bullet("Środowisko testowe integracyjne powołuje rzeczywistą instancję bazy PostgreSQL 16 w kontenerze Docker (Testcontainers).")
    add_bullet("Ograniczenia: system operuje w jednej walucie, jest instalacją jednodostępną (brak multi-tenancy), a struktury BOM są jednopoziomowe.")

    # 7. Interesariusze i komunikacja
    add_heading1("7. Interesariusze i komunikacja")
    add_p("Interesariuszami procesu testowego dla systemu Manufacturing ERP są:")
    add_bullet("Właściciel Produktu (Product Owner) i Analitycy Biznesowi,")
    add_bullet("Deweloperzy backendu (Java / Spring Boot),")
    add_bullet("Deweloperzy frontendu (React / TypeScript),")
    add_bullet("Inżynierowie Jakości i Testerzy Automatyzujący (QA / SDET),")
    add_bullet("Administratorzy i Inżynierowie DevOps.")
    add_p("Kanały komunikacji: codzienne spotkania stand-up (Scrum), komunikator zespołowy (MS Teams/Slack), system zgłoszeń błędów GitHub Issues/Jira oraz automatyczne powiadomienia potoków CI/CD.")

    # 8. Strategia testowania
    add_heading1("8. Strategia testowania")
    add_p("Proces testowy dla systemu Manufacturing ERP przewiduje pełną automatyzację przypadków testowych opracowanych na podstawie wymagań funkcjonalnych, niezmienników księgowych oraz specyfikacji architektury systemu (Tabela 1).")
    
    add_heading2("8.1 Podejście do testów w pierwszej fazie projektu (Tabela 1)")
    add_table_data(
        ["Komponent", "Poziom testów", "Typ testów"],
        [
            ["Ledger (Księga Główna)", "Jednostkowe i integracyjne", "Funkcjonalne, strukturalne, regresyjne, integralności danych"],
            ["Inventory (Gospodarka magazynowa)", "Jednostkowe i integracyjne", "Funkcjonalne, współbieżności (concurrency/locking), regresyjne"],
            ["Purchasing & Sales (P2P / O2C)", "Jednostkowe, integracyjne, E2E", "Funkcjonalne, transakcyjne, regresyjne"],
            ["Manufacturing (Produkcja)", "Jednostkowe i integracyjne", "Funkcjonalne, maszyn stanów, regresyjne"],
            ["HR & Payroll (Kadry i płace)", "Jednostkowe i integracyjne", "Funkcjonalne, kalkulacyjne, transakcyjne"],
            ["IAM & Security (Uprawnienia RBAC)", "Jednostkowe, integracyjne i API", "Bezpieczeństwa, autoryzacji, negatywne"],
            ["Assistant (ERP Copilot AI)", "Integracyjne i kontraktowe", "Funkcjonalne, bezpieczeństwa (HITL), rate-limitingu"],
            ["Architektura monolitu modułowego", "Architektoniczne (ArchUnit)", "Strukturalne, hermetyzacji pakietów, jakości kodu"],
            ["Frontend SPA (Interfejs użytkownika)", "Jednostkowe, komponentowe, E2E", "Użyteczności, dostępności (a11y axe-core), regresyjne"],
            ["Komunikacja REST API & Kontrakt", "Kontraktowe i integracyjne", "Zgodności z OpenAPI 3.1, standardu RFC 9457"]
        ]
    )

    add_heading2("8.2 Techniki projektowania testów")
    add_bullet("Analiza klas równoważności i wartości brzegowych (Equivalence Partitioning & Boundary Value Analysis) - dla kwot, stanów magazynowych i stawek VAT.", bold_prefix="1. ")
    add_bullet("Testowanie przejść między stanami (State Transition Testing) - dla maszyn stanów zamówień, zlecenia produkcyjnego i zamknięcia roku.", bold_prefix="2. ")
    add_bullet("Testowanie niezmienników bilansowych (Invariant / Property-based Testing) - matematyczny bilans Winien=Ma oraz zerowanie kont GR-IR, WIP, Deferred-COGS.", bold_prefix="3. ")
    add_bullet("Testowanie negatywne i uprawnień (Negative & Security Testing) - próby dostępu dla ról o niewystarczających uprawnieniach (HTTP 401/403) oraz blokada zapisu GUEST.", bold_prefix="4. ")
    add_bullet("Testowanie współbieżności (Concurrency Testing) - symulacja 8 równoległych wątków modyfikujących stany magazynowe w celu weryfikacji blokad pesymistycznych bez deadlocków.", bold_prefix="5. ")

    add_heading2("8.3 Miary i metryki procesu testowego")
    add_table_data(
        ["Metryka", "Próg akceptacji", "Sposób pomiaru", "Narzędzie"],
        [
            ["Pokrycie linii kodu (Line Coverage)", ">= 80%", "Procent wykonanych linii w kodzie", "JaCoCo / Maven"],
            ["Pokrycie gałęzi decyzyjnych", ">= 70%", "Procent pokrytych rozgałęzień", "JaCoCo / Maven"],
            ["Zdawalność testów P0 i P1", "100%", "Wszystkie testy krytyczne muszą przejść", "Surefire / Vitest"],
            ["Wskaźnik uzgodnienia ksiąg", "100% (healthy)", "Subledgery zgodne z kontami GL", "ReconciliationIT"],
            ["Czystość architektury", "0 naruszeń", "Brak zakazanych zależności pakietów", "ArchUnit"],
            ["Błędy dostępności WCAG AA", "0 błędów", "Audyt dostępności cyfrowej", "@axe-core/playwright"],
            ["Czas wykonania potoku CI", "< 10 minut", "Czas przejścia testów w GitHub Actions", "CI Runner"]
        ]
    )

    add_heading2("8.4 Kryteria wejścia i wyjścia dla faz testowych")
    add_p("Kryteria wejścia (Entry Criteria): Pomyślna kompilacja kodu, poprawne wykonanie migracji Flyway, dostępność kontenera PostgreSQL 16.")
    add_p("Kryteria wyjścia (Exit Criteria): Wykonanie 100% zaplanowanych testów, 100% zdawalności testów P0/P1, osiągnięcie progu pokrycia JaCoCo >= 80%, pozytywny wynik raportu Reconciliation Hero Check (healthy: true).")

    add_heading2("8.5 Klasyfikacja defektów i priorytetyzacja napraw")
    add_table_data(
        ["Klasyfikacja", "Wpływ na system", "Priorytet naprawy", "SLA naprawy"],
        [
            ["Najwyższy (P0 / Blocker)", "Defekt blokujący kluczową funkcję, naruszenie zasady Winien=Ma, zakleszczenie bazy.", "Najwyższy; wstrzymuje wdrożenie.", "Natychmiast (< 4h)"],
            ["Wysoki (P1 / Critical)", "Kluczowa funkcja błędnie zaimplementowana (błąd wyceny, maszyny stanów).", "Potencjał na opóźnienie; dopuszczalne obejście.", "W sprincie (< 24h)"],
            ["Średni (P2 / Major)", "Drugorzędna funkcja źle zaimplementowana (brak paginacji, niepełne ciało 403).", "Naprawa w kolejnym sprincie.", "Następny sprint"],
            ["Niski (P3 / Minor)", "Drobna usterka estetyczna, brakujące tłumaczenie i18n.", "Naprawa w wolnym czasie.", "W miarę zasobów"],
            ["Najniższy (P4 / Trivial)", "Nieistotny defekt (np. literówka w dokumentacji Swagger UI).", "Kiedy czas pozwoli.", "Backlog"]
        ]
    )

    add_heading2("8.6 Warunki akceptacji i wdrożenia")
    add_p("Pełna akceptacja: Wszystkie artefakty wytworzone, 100% testów automatycznych zaliczonych (BUILD SUCCESS), raport uzgodnienia zwraca healthy: true, brak otwartych defektów P0/P1.")
    add_p("Częściowa akceptacja: Brak otwartych defektów P0, nieliczne defekty P1/P2 z udokumentowanymi obejściami zaakceptowane przez Product Ownera.")
    add_p("Odrzucenie wdrożenia: Wystąpienie co najmniej jednego błędu P0/Blocker lub asymetrii księgowej.")

    add_heading2("8.7 Artefakty z procesu testowego")
    add_p("W pierwszej fazie realizacji Projektu:", bold_prefix="")
    add_bullet("Niniejszy dokument (Plan Testów)")
    add_bullet("Suita testów jednostkowych i architektonicznych backendu (unit-test-suite)")
    add_bullet("Suita testów integracyjnych z Testcontainers PostgreSQL (integration-test-suite)")
    add_bullet("Suita testów jednostkowych i komponentowych frontendu (frontend-unit-test-suite)")
    add_bullet("Suita testów manualnych i eksploracyjnych")
    add_bullet("Raport końcowy testów dla pierwszej fazy projektu")

    add_p("W drugiej fazie realizacji Projektu:", bold_prefix="")
    add_bullet("Zaktualizowany Plan Testów")
    add_bullet("Zaktualizowane suity testów automatycznych")
    add_bullet("Suita testów End-to-End w narzędziu Playwright (e2e-test-suite)")
    add_bullet("Raport z audytu dostępności cyfrowej WCAG 2.1 AA (axe-core-audit-report)")
    add_bullet("Raport końcowy testów dla drugiej fazy projektu")

    add_p("W trzeciej fazie realizacji Projektu:", bold_prefix="")
    add_bullet("Końcowa wersja Planu Testów")
    add_bullet("Końcowe wersje suit testów automatycznych zintegrowanych w CI/CD")
    add_bullet("Raport z testów współbieżności i wydajności operacji magazynowych")
    add_bullet("Zbiór raportów z testów (Test Summary Reports)")
    add_bullet("Raport z zakończenia testów (Test Closure Report)")

    # 9. Środowisko testowe
    add_heading1("9. Środowisko testowe")
    add_bullet("Środowisko deweloperskie: lokalny Spring Boot (:8080), PostgreSQL 16 w Dockerze (:5432), Vite dev (:5173).")
    add_bullet("Środowisko CI/CD: GitHub Actions z Maven Surefire, Failsafe + Testcontainers Postgres 16, Vitest i Playwright Headless.")
    add_bullet("Środowisko demonstracyjne: docker compose -f compose.demo.yaml up --build (Nginx :8081, auto-seeder danych).")

    # 10. Harmonogram testowania
    add_heading1("10. Harmonogram testowania")
    add_p("Wytwarzanie modułu Manufacturing ERP odbywa się w metodologii SCRUM. W związku z tym:")
    add_bullet("Proces wytwarzania oprogramowania i testowania odbywa się w dwutygodniowych Sprintach.")
    add_bullet("Planowanie aktywności testowych musi być włączone w planowanie Sprintów.")
    add_bullet("Dokumentowanie i implementacja testów są integralnymi częściami implementowanych Historii Użytkownika.")
    add_bullet("Wyniki testów pierwszej fazy są prezentowane w ramach procesu CI / CD.")
    add_bullet("Proces testowania jest ściśle powiązany z procesem wytwarzania projektu jako całości i przestrzega harmonogramu wyznaczonego dla całego projektu.")

    # 11. Organizacja testów
    add_heading1("11. Organizacja testów")
    add_p("Proces testowy oparty jest na wymaganiach funkcjonalnych, regułach bilansowych oraz przypadkach użycia procesów Buy -> Make -> Sell. Testowanie w fazach projektu opiera się na testach automatycznych wbudowanych w strumień CI/CD. Każde wdrożenie wymaga przejścia przez zautomatyzowany zestaw testów. W przypadku, gdy jakikolwiek test nie zostanie zaliczony dalsze kroki strumienia zostaną zatrzymane do naprawy systemu.")
    add_p("Do implementacji testów wykorzystane zostaną narzędzia: JUnit5, Maven, Testcontainers, ArchUnit, Vitest, Playwright, axe-core.")
    
    add_heading2("Tabela 2: Grupy testów systemu Manufacturing ERP")
    add_table_data(
        ["Grupa testów", "Nazwa suity testowej", "Narzędzie", "Zakres odpowiedzialności"],
        [
            ["Testy jednostkowe backendu", "unit-test-suite", "Maven Surefire", "Reguły biznesowe, walidacja Money/Quantity, domena"],
            ["Testy architektury monolitu", "architecture-test-suite", "ArchUnit", "Czystość granic pakietów com.erp.*, hermetyzacja"],
            ["Testy integracyjne i DB", "integration-test-suite", "Maven Failsafe + Testcontainers", "Transakcje bazodanowe, serwisy, triggery PostgreSQL"],
            ["Testy kontraktu błędów i OpenAPI", "contract-test-suite", "Spring MockMvc + Testcontainers", "Zgodność z OpenAPI 3.1 i RFC 9457"],
            ["Testy jednostkowe frontendu", "frontend-unit-test-suite", "Vitest", "Komponenty Mantine, reduktory, obliczenia walutowe"],
            ["Testy funkcjonalne E2E", "e2e-test-suite", "Playwright", "Kluczowe ścieżki użytkownika w przeglądarce"],
            ["Testy dostępności cyfrowej", "accessibility-test-suite", "@axe-core/playwright", "Dostępność WCAG 2.1 AA, kontrast motywu"]
        ]
    )

    # 12. Implementacja testów i organizacja kodu
    add_heading1("12. Implementacja testów i organizacja kodu")
    add_p("Kod testowy w repozytorium jest podzielony zgodnie z warstwami:")
    add_bullet("Backend (src/test/java/com/erp/): ArchitectureTest.java (ArchUnit), pakiety domenowe (*Test.java), pakiety aplikacyjne (*IT.java z @SpringBootTest i TestcontainersConfiguration), testy kontraktu błędów (ErrorContractIT.java).")
    add_bullet("Frontend (frontend/src/ oraz frontend/e2e/): testy jednostkowe (*.test.ts, *.test.tsx), testy kontrastu motywu Ink Ledger (contrast.test.ts), testy E2E (nav.spec.ts, axe.spec.ts, assistant.spec.ts).")

    # 13. Lista scenariuszy testowych
    add_heading1("13. Lista scenariuszy testowych")
    add_table_data(
        ["ID Scenariusza", "Moduł", "Nazwa scenariusza", "Opis funkcjonalności"],
        [
            ["SC-GL-01", "Ledger", "Integralność podwójnego zapisu", "Weryfikacja reguły Dt=Ct i natychmiastowego odrzucenia asymetrii przez bazę."],
            ["SC-GL-02", "Ledger", "Zamknięcie okresu i roku", "Weryfikacja soft-close i hard-close z przeksięgowaniem wyniku na konto 3200."],
            ["SC-GL-03", "Ledger", "Odwracanie zapisów księgowych", "Lustrzany zapis korygujący bez mutacji wpisu pierwotnego."],
            ["SC-INV-01", "Inventory", "Wycena średnią ważoną", "Rekalkulacja kosztu jednostkowego po dostawach i rewaluacja przy odchyleniach."],
            ["SC-INV-02", "Inventory", "Współbieżność gospodarki magazynowej", "Odporność na zakleszczenia przy 8 wątkach dzięki stałej kolejności blokad."],
            ["SC-P2P-01", "Purchasing", "Cykl zakupu Procure-to-Pay", "Ścieżka PO->GRN->Bill->Payment i zerowanie konta GR-IR (2150)."],
            ["SC-O2C-01", "Sales", "Cykl sprzedaży Order-to-Cash", "Ścieżka SO->Delivery->Invoice->Receipt i zerowanie Deferred-COGS (1340)."],
            ["SC-MFG-01", "Manufacturing", "Cykl zlecenia produkcyjnego", "Pobranie surowców, produkcja wyrobu gotowego, zerowanie konta WIP (1320)."],
            ["SC-HR-01", "HR & Payroll", "Naliczenie płac i dekretacja", "Kalkulacja listy płac i automatyczny zbalansowany dekret do Księgi Głównej."],
            ["SC-IAM-01", "IAM", "Macierz uprawnień RBAC", "Weryfikacja uprawnień dla 5 ról oraz bezwzględnej blokady zapisu dla GUEST."],
            ["SC-ERR-01", "Config", "Standard kontraktu błędów RFC 9457", "Zwracanie problem+json dla kodów 400, 401, 403 oraz 409."],
            ["SC-AI-01", "Assistant", "ERP Copilot i ochrona HITL", "Wstrzymanie operacji zapisu na karcie do momentu kliknięcia zgody przez człowieka."],
            ["SC-UI-01", "Frontend", "Dostępność cyfrowa WCAG AA", "Weryfikacja kontrastów motywu Ink Ledger, nawigacji klawiaturą i audyt axe-core."],
            ["SC-REP-01", "Reporting", "Raport uzgodnienia Hero Check", "Weryfikacja zbiorcza flagi healthy: true, próbnego bilansu i subledgerów."],
            ["SC-ARC-01", "Architecture", "Egzekwowanie granic modułów", "Weryfikacja zakazu sięgania do wewnętrznych pakietów obcych modułów."]
        ]
    )

    # 14. Przypadki testowe
    add_heading1("14. Przypadki testowe (Wzorcowa specyfikacja szczegółowa)")
    add_p("Poniżej przedstawiono 10 kluczowych przypadków testowych reprezentujących krytyczne ścieżki i niezmienniki biznesowe systemu. Pełny zbiór ponad 90 klas testowych automatycznych znajduje się bezpośrednio w repozytorium kodu.", italic=True)

    def add_tc(tc_id, sc_id, name, mod, goal, prio, pre, data, exp, steps):
        add_heading2(f"Przypadek testowy: {tc_id} - {name}")
        add_table_data(
            ["Atrybut", "Wartość"],
            [
                ["Identyfikator", tc_id],
                ["Identyfikator scenariusza", sc_id],
                ["Moduł systemu", mod],
                ["Cel", goal],
                ["Priorytet", prio],
                ["Warunki wstępne", pre],
                ["Dane testowe", data],
                ["Oczekiwany wynik", exp]
            ]
        )
        add_p("Przebieg testu (Kroki wykonania):", bold_prefix="")
        for idx, s in enumerate(steps, 1):
            add_bullet(f"{idx}. {s}")

    add_tc(
        "TC-GL-001", "SC-GL-01", "Blokada asymetrycznego zapisu w Księdze Głównej", "ledger",
        "Weryfikacja odrzucenia asymetrycznego dekretu księgowego (Dt != Ct) przez bazę danych i aplikację.",
        "Najwyższy (P0 / Blocker)",
        "Aktywna baza Postgres z triggerem bilansującym. Użytkownik uwierzytelniony jako ACCOUNTANT.",
        "Konto 1000 Dt: 100.00 PLN, Konto 7000 Ct: 95.00 PLN (asymetria 5.00 PLN).",
        "Kod błędu HTTP 400 Bad Request w formacie problem+json. Transakcja wycofana (ROLLBACK). Brak wpisu w bazie.",
        [
            "Przygotuj żądanie HTTP POST /api/ledger/journal-entries z asymetrycznymi kwotami.",
            "Wyślij żądanie z nagłówkiem Authorization Bearer dla roli ACCOUNTANT.",
            "Zweryfikuj kod statusu HTTP 400.",
            "Upewnij się, że ciało błędu zawiera informację o braku bilansu.",
            "Wykonaj zapytanie SQL upewniając się, że żaden rekord nie został zapisany."
        ]
    )

    add_tc(
        "TC-P2P-001", "SC-P2P-01", "Wyzerowanie konta GR-IR w cyklu zakupowym", "purchasing",
        "Weryfikacja zerowania salda konta przejściowego rozliczenia zakupu GR-IR (2150) po dostawie i fakturze.",
        "Najwyższy (P0 / Blocker)",
        "Zdefiniowany dostawca V-01 i indeks surowca RM-01. Otwarty okres obrachunkowy.",
        "Zamówienie zakupu: 100 szt. RM-01 po cenie 10.00 PLN netto. Stawka VAT: STANDARD (5%).",
        "Konto 2150 wykazuje dokładnie 0.00 PLN salda po zaksięgowaniu faktury. Subledger AP uzgodniony z kontem 2100.",
        [
            "Utwórz zamówienie zakupu PO przez POST /api/purchasing/orders.",
            "Zatwierdź PO przez POST /api/purchasing/orders/{id}/confirm.",
            "Zarejestruj przyjęcie zewnętrzne GRN (PZ) na 100 szt. towaru.",
            "Zweryfikuj, że konto 2150 posiada saldo kredytowe 1000.00 PLN.",
            "Zarejestruj fakturę dostawcy Vendor Bill na 100 szt. po 10.00 PLN.",
            "Pobierz raport GET /api/reporting/reconciliation i zweryfikuj saldo konta 2150 równe 0.00 PLN."
        ]
    )

    add_tc(
        "TC-MFG-001", "SC-MFG-01", "Rozliczenie kosztu wyrobu i wyzerowanie konta WIP", "manufacturing",
        "Weryfikacja rozliczenia rzeczywistego kosztu zlecenia produkcyjnego i wyczyszczenia salda konta WIP (1320).",
        "Wysoki (P1 / Critical)",
        "Struktura BOM: 2 szt. RM-01 na 1 szt. FG-01. Stan surowca RM-01 na magazynie: minimum 200 szt.",
        "Zlecenie produkcyjne na 10 szt. wyrobu gotowego FG-01.",
        "Pobrane surowce obciążają konto WIP (200.00 PLN). Przyjęcie wyrobów przenosi 200.00 PLN na wyroby gotowe. Saldo WIP wynosi 0.00 PLN.",
        [
            "Utwórz BOM przez POST /api/manufacturing/boms.",
            "Utwórz zlecenie produkcyjne przez POST /api/manufacturing/work-orders.",
            "Zmień status zlecenia na RELEASED.",
            "Wydaj komponenty surowcowe przez POST /api/manufacturing/work-orders/{id}/issue.",
            "Zakończ zlecenie i przyjmij wyrób gotowy przez POST /api/manufacturing/work-orders/{id}/complete.",
            "Sprawdź raport uzgodnienia i upewnij się, że konto WIP ma saldo 0.00 PLN."
        ]
    )

    add_tc(
        "TC-AI-001", "SC-AI-01", "Wstrzymanie operacji zapisu asystenta AI (Human-in-the-Loop)", "assistant",
        "Weryfikacja braku samowolnego zapisu danych w bazie przez model LLM bez jawnego kliknięcia potwierdzenia przez człowieka.",
        "Wysoki (P1 / Critical)",
        "Włączona flaga APP_ASSISTANT_ENABLED=true. Użytkownik zalogowany jako sales.",
        "Prompt czatu: 'Utwórz zamówienie sprzedaży dla klienta C-01 na 5 sztuk wyrobu FG-01'.",
        "Asystent wyświetla kartę potwierdzenia. Rekord w bazie NIE powstaje do momentu zatwierdzenia przez użytkownika.",
        [
            "Otwórz szufladę ERP Copilot w interfejsie użytkownika.",
            "Wprowadź prompt zlecający utworzenie zamówienia.",
            "Odbierz strumień SSE i zweryfikuj pojawienie się karty potwierdzenia.",
            "Sprawdź bazę danych - upewnij się, że zamówienie nie istnieje.",
            "Kliknij przycisk 'Zatwierdź' na karcie w interfejsie.",
            "Potwierdź utworzenie zamówienia i zapis w tabeli audit_log."
        ]
    )

    add_tc(
        "TC-INV-001", "SC-INV-01", "Wycena magazynu średnią ważoną ruchomą i rewaluacja zapasów", "inventory",
        "Weryfikacja przeliczenia średniej ceny jednostkowej zapasu oraz poprawności rewaluacji zapasu przy odchyleniu ceny faktury.",
        "Wysoki (P1 / Critical)",
        "Utworzony surowiec RM-02 o początkowym stanie 0 szt.",
        "Dostawa 1: 100 szt. po 10.00 PLN; Dostawa 2: 100 szt. po 20.00 PLN; Faktura: 22.00 PLN/szt.",
        "Po dostawie 2 średni koszt = 15.00 PLN. Po fakturze z odchyleniem koszt = 16.00 PLN (rewaluacja +200.00 PLN w GL).",
        [
            "Zarejestruj przyjęcie zewnętrzne GRN dla 100 szt. RM-02 po 10.00 PLN.",
            "Sprawdź stan magazynowy i koszt w tabeli item_cost_state.",
            "Zarejestruj drugie przyjęcie GRN dla 100 szt. RM-02 po 20.00 PLN.",
            "Zweryfikuj, że średni koszt wynosi dokładnie 15.00 PLN.",
            "Zaksięguj fakturę zakupu dla partii 2 z ceną 22.00 PLN.",
            "Potwierdź rekalkulację kosztu do 16.00 PLN oraz zgodność subledgera z kontem 1300."
        ]
    )

    add_tc(
        "TC-O2C-001", "SC-O2C-01", "Kompletny cykl sprzedaży Order-to-Cash i zerowanie Deferred-COGS", "sales",
        "Weryfikacja odroczenia kosztu na koncie 1340 przy WZ i przeksięgowania na COGS (5000) z wyzerowaniem salda 1340 po fakturze.",
        "Najwyższy (P0 / Blocker)",
        "Klient C-01. Na magazynie 50 szt. FG-01 o koszcie jednostkowym 20.00 PLN/szt.",
        "Zamówienie SO na 10 szt. FG-01 po cenie sprzedaży 35.00 PLN netto (VAT 23%).",
        "Po wydaniu towaru konto 1340 ma saldo 200.00 PLN. Po wystawieniu faktury saldo konta 1340 wynosi dokładnie 0.00 PLN.",
        [
            "Utwórz zamówienie sprzedaży przez POST /api/sales/orders.",
            "Potwierdź zamówienie przez POST /api/sales/orders/{id}/confirm.",
            "Wygeneruj wydanie zewnętrzne przez POST /api/sales/deliveries.",
            "Sprawdź raport próbnego bilansu - potwierdź saldo konta 1340 równe 200.00 PLN.",
            "Wystaw fakturę sprzedaży przez POST /api/sales/invoices.",
            "Wywołaj GET /api/reporting/reconciliation i potwierdź saldo 1340 równe 0.00 PLN."
        ]
    )

    add_tc(
        "TC-IAM-001", "SC-IAM-01", "Egzekwowanie ról RBAC i blokada zapisu dla roli GUEST", "iam",
        "Weryfikacja, czy żądania modyfikacji danych wysyłane przez użytkownika o roli GUEST są odrzucane z kodem HTTP 403 Forbidden.",
        "Wysoki (P1 / Critical)",
        "Użytkownik uwierzytelniony tokenem JWT z rolą ROLE_GUEST.",
        "Próba utworzenia nowego kontrahenta przez POST /api/masterdata/partners.",
        "Kod błędu HTTP 403 Forbidden w formacie problem+json. Brak nowego rekordu w bazie danych.",
        [
            "Zaloguj się na konto testowe o roli GUEST i pobierz token JWT.",
            "Wyślij żądanie GET /api/masterdata/partners - upewnij się, że odczyt zwraca 200 OK.",
            "Wyślij żądanie POST /api/masterdata/partners z danymi nowego kontrahenta.",
            "Zweryfikuj, że serwer zwrócił kod błędu HTTP 403 Forbidden.",
            "Upewnij się, że odpowiedź zawiera pole status: 403 i title: Forbidden."
        ]
    )

    add_tc(
        "TC-ERR-001", "SC-ERR-01", "Standaryzacja kontraktu błędów HTTP zgodnie z RFC 9457", "config",
        "Weryfikacja, czy błędy walidacji Bean Validation są zwracane w formacie application/problem+json z listą pól invalidParams.",
        "Średni (P2 / Major)",
        "Uruchomiony backend Spring Boot.",
        "Wysłanie niepoprawnego żądania POST /api/sales/orders z pustym ciałem JSON {}.",
        "Odpowiedź HTTP 400 Bad Request z nagłówkiem application/problem+json i tablicą invalidParams.",
        [
            "Wyślij żądanie POST /api/sales/orders z pustym ciałem {}.",
            "Zweryfikuj nagłówek odpowiedzi Content-Type: application/problem+json.",
            "Sprawdź obecność pól status: 400 oraz title: Validation Failure.",
            "Potwierdź, że invalidParams wskazuje brakujące pole partnerId."
        ]
    )

    add_tc(
        "TC-REP-001", "SC-REP-01", "Zbiorczy raport uzgodnienia ksiąg (Reconciliation Hero Check)", "reporting",
        "Weryfikacja działania centralnego endpointu uzgadniającego syntetykę GL z subledgerami i zerowania kont przejściowych.",
        "Najwyższy (P0 / Blocker)",
        "Zakończone pełne cykle zakupowe, produkcyjne i sprzedażowe w bazie danych.",
        "Wywołanie GET /api/reporting/reconciliation.",
        "HTTP 200 OK, flaga healthy: true, brak rozbieżności, salda kont 2150, 1320 i 1340 równe 0.00 PLN.",
        [
            "Zaloguj się z uprawnieniami roli ACCOUNTANT.",
            "Wyślij żądanie GET /api/reporting/reconciliation.",
            "Zweryfikuj trialBalanceBalanced: true (Dt == Ct).",
            "Zweryfikuj inventorySubledgerBalanced: true, apSubledgerBalanced: true, arSubledgerBalanced: true.",
            "Potwierdź, że nadrzędne pole healthy zwraca wartość true."
        ]
    )

    add_tc(
        "TC-ARC-001", "SC-ARC-01", "Weryfikacja granic modułów monolitu w ArchUnit", "architecture",
        "Automatyczna weryfikacja zakazu nieuprawnionego sięgania do wewnętrznych pakietów modułów i eliminacja pętli cyklicznych.",
        "Wysoki (P1 / Critical)",
        "Skompilowany kod klas produkcyjnych backendu (target/classes).",
        "Uruchomienie klasy testowej com.erp.ArchitectureTest.",
        "Zakończenie testu statusem PASS. 0 naruszeń reguł izolacji modułów.",
        [
            "Wykonaj polecenie Maven: ./mvnw test -Dtest=ArchitectureTest.",
            "Zweryfikuj regułę modulesShouldOnlyDependOnApiPackages.",
            "Zweryfikuj regułę domainLayerShouldNotDependOnApplicationLayer.",
            "Zweryfikuj brak zapętleń cyklicznych w grafie pakietów."
        ]
    )

    # 15. Procedury raportowania i metryki
    add_heading1("15. Procedury raportowania i metryki")
    add_heading2("15.1 Raportowanie stanu testów")
    add_p("Raportowanie odbywa się na koniec każdego Sprintu oraz w trybie ciągłym poprzez dashboard GitHub Actions. Każdy raport zawiera identyfikator, statystykę suit testowych, pokrycie JaCoCo, wynik Reconciliation Hero Check oraz rejestr defektów.")

    add_heading2("15.2 Obowiązkowy format zgłoszenia defektu")
    add_p("Pola formularza zgłoszenia błędu: Tytuł i ID, Klasyfikacja (P0-P4), Środowisko (SHA/kontener), Kroki do odtworzenia, Rezultat rzeczywisty, Rezultat oczekiwany, Przyczyna źródłowa (plik/linia), Propozycja naprawy.")

    add_heading2("15.3 Szablon raportu z aktualnego stanu testów")
    add_p("Raport stanu testów generowany w cyklach sprintowych:")
    add_table_data(
        ["Scenariusz", "Przypadek testowy", "Oczekiwane wyniki", "Aktualny wynik", "Status", "Komentarz"],
        [
            ["SC-GL-01", "TC-GL-001", "Błąd 400 Bad Request, Rollback", "Transakcja odrzucona przez trigger bazy", "PASS", "Trigger PostgreSQL działa poprawnie"],
            ["SC-P2P-01", "TC-P2P-001", "Saldo GR-IR równe 0.00 PLN po fakturze", "Saldo konta 2150 wynosi dokładnie 0.00", "PASS", "Rozliczenie zakupu bezbłędne"],
            ["SC-MFG-01", "TC-MFG-001", "Saldo WIP równe 0.00 PLN po wyrobie", "Saldo konta 1320 wynosi 0.00 PLN", "PASS", "Rozliczenie produkcji zakończone"],
            ["SC-INV-01", "TC-INV-001", "Rekalkulacja średniej ważonej", "Nowy koszt 16.00 PLN, zgodność z GL", "PASS", "Wycena magazynu prawidłowa"],
            ["SC-O2C-01", "TC-O2C-001", "Wyzerowanie Deferred-COGS (1340)", "Saldo 1340 równe 0.00 PLN po fakturze", "PASS", "Odroczony koszt zaksięgowany"],
            ["SC-IAM-01", "TC-IAM-001", "Blokada zapisu dla GUEST (403)", "Serwer zwrócił 403 Forbidden", "PASS", "Zabezpieczenie RBAC aktywne"],
            ["SC-ERR-01", "TC-ERR-001", "Format application/problem+json", "Poprawna struktura RFC 9457", "PASS", "Zgodność ze standardem błędów"],
            ["SC-AI-01", "TC-AI-001", "Wstrzymanie zapisu do zatwierdzenia HITL", "Karta potwierdzenia w UI, zapis po kliknięciu", "PASS", "Ochrona Human-in-the-Loop działa"],
            ["SC-REP-01", "TC-REP-001", "Flaga healthy: true i zerowe odchylenia", "Raport zwrócił healthy: true", "PASS", "Centralne uzgodnienie pozytywne"],
            ["SC-ARC-01", "TC-ARC-001", "0 naruszeń reguł ArchUnit", "Wykonanie w 1.4s, 0 naruszeń", "PASS", "Granice modułów zachowane"]
        ]
    )

    # 16. Ryzyka projektowe i mitygacja
    add_heading1("16. Ryzyka projektowe i mitygacja")
    add_table_data(
        ["Ryzyko", "Prawdopodobieństwo", "Wpływ", "Plan mitygacji (Działania zapobiegawcze)"],
        [
            ["Naruszenie bilansu transakcyjnego", "Średnie", "Najwyższy (P0)", "Relacyjne triggery PostgreSQL (DEFERRED CONSTRAINT) oraz test ReconciliationIT w CI."],
            ["Zakleszczenia bazy danych przy współbieżności", "Średnie", "Wysoki (P1)", "Stała kolejność blokowania ItemCostState przed zapisem dekretu i test wielowątkowy StockPostingConcurrencyIT."],
            ["Niezamierzone operacje zapisu przez AI", "Średnie", "Wysoki (P1)", "Bezwzględna separacja narzędzi odczytu od zapisu, wymóg potwierdzenia HITL i dziedziczenie uprawnień JWT."],
            ["Rozejście się kontraktu API", "Niskie", "Wysoki (P1)", "Automatyczne generowanie typów TypeScript ze specyfikacji OpenAPI oraz test OpenApiSpecIT."],
            ["Utrata precyzji kwot finansowych w JS", "Niskie", "Wysoki (P1)", "Globalna serializacja BigDecimal do String w JSON oraz testy jednostkowe Money.test.ts."]
        ]
    )

    # 17. Podsumowanie
    add_heading1("17. Podsumowanie")
    add_p("Niniejszy Plan Testów zapewnia pełne pokrycie weryfikacyjne i walidacyjne systemu Manufacturing ERP na wszystkich poziomach piramidy testowej. Zapewnia nienaruszalność kluczowych zasad rachunkowości, stabilność modularnej architektury oraz bezpieczeństwo i ergonomię użytkownika końcowego. Realizacja powyższego planu gwarantuje wysoką jakość oprogramowania spełniającą rygorystyczne standardy inżynierii systemów klasy Enterprise oraz kryteria stawiane w ramach przedmiotu „Jakość w procesie wytwarzania oprogramowania”.")

    output_path = "Plan_Testow_ERPSystem.docx"
    try:
        doc.save(output_path)
        print(f"Updated document created at: {output_path}")
    except PermissionError:
        alt_path = "Plan_Testow_ERPSystem_Nowy.docx"
        doc.save(alt_path)
        print(f"Plik '{output_path}' jest otwarty w programie Word. Zapisano zaktualizowany dokument jako: {alt_path}")

if __name__ == "__main__":
    create_document()
