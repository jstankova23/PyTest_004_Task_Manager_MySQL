# Task Manager – Python + MySQL

**Autor:** Jana Staňková  
**Verze projektu:** 1.2.1  
**Datum vytvoření:** 27. 10. 2025  
**Datum poslední aktualizace:** 28. 10. 2025  
**Licence:** MIT  
**Python:** 3.10+  

---

## Popis aplikace

Tento projekt představuje **vylepšenou verzi aplikace Task Manager**, vytvořenou jako součást výuky modulu *Python a MySQL* v rámci Engeto Academy.  
Aplikace slouží ke **správě úkolů** pomocí databáze **MySQL**, kde se jednotlivé úkoly ukládají do tabulky `ukoly`.  
Každý úkol odpovídá jednomu řádku v databázi a obsahuje sloupce:

- `id` – unikátní identifikátor úkolu (automaticky generovaný),  
- `nazev` – krátký název úkolu,  
- `popis` – detailní popis úkolu,  
- `stav` – aktuální stav úkolu (`nezahájeno`, `probíhá`, `hotovo`),  
- `datum_vytvoreni` – datum vytvoření úkolu (nastavuje se automaticky).

Aplikace umožňuje kompletní operace **CRUD**:
- **Create** – vytváření nových úkolů  
- **Read** – zobrazení úkolů  
- **Update** – změna stavu úkolů  
- **Delete** – odstranění úkolů

Data jsou trvale ukládána do databáze, takže po ukončení programu nedochází ke ztrátě informací.  
Na rozdíl od dřívější verze aplikace, která pracovala jen s daty uloženými v paměti (seznam slovníků), tato verze používá **MySQL**.

Aplikace je zároveň připravena pro **automatizované testování pomocí PyTestu**.  
Testy mohou probíhat na produkční i testovací databázi – testovací databáze je doporučená a používá se pro simulaci dat bez ovlivnění ostrého prostředí.
Testy pracují s testovací databází definovanou v .env souboru a využívají fixtures z conftest.py pro vytvoření tabulky 'ukoly' a izolaci jednotlivých testovacích případů.
Vzhledem k architektuře programu, kde jsou funkce rozděleny na uživatelské (UI) a databázové (DB) varianty, jsou v rámci automatizovaných testů s využitím PyTest testovány pouze databázové funkce.

UI funkce pracují s uživatelským vstupem input() a jejich testování by vyžadovalo 
mockování pomocí monkeypatch na input().

Testy tedy ověřují pouze správnost funkcí:
    • pridat_ukol_db()
    • aktualizovat_ukol_db()
    • odstranit_ukol_db()

Každá funkce má dva testy:
    – pozitivní scénář (platné vstupy)
    – negativní scénář (neplatné vstupy)

---

## Struktura projektu

```
task_manager_mysql/
│
├─ src/    
│   └─ task_manager_mysql/                  
│       ├─ __init__.py               # inicializační soubor balíčku (importy)
│       └─ task_manager_mysql_p2.py  # hlavní zdrojový soubor aplikace
│
├─ tests/
│   ├─ __init__.py                   # prázdný soubor pro inicializaci testovacího balíčku
│   ├─ conftest.py                   # fixtures pro vytvoření testovací tabulky a připojení k DB
│   └─ test_task_manager_mysql_p2.py # testy jednotlivých DB funkcí (PyTest)
│
├─ .env                              # konfigurační soubor prostředí (lokální, neveřejný)
├─ .env.example                      # ukázkový konfigurační soubor pro ostatní uživatele
├─ .gitignore                        # definuje soubory ignorované Gitem
├─ pyproject.toml                    # konfigurace projektu a závislostí
├─ pytest.ini                        # konfigurace PyTestu
├─ README.md                         # dokumentace projektu
├─ requirements.txt                  # seznam závislostí (potřebných knihoven)
├─ setup.cfg                         # doplňková konfigurace pro build/test nástroje
└─ .github/
    └─ workflows/
        └─ ci.yml                    # GitHub Actions – automatické spouštění testů
```

---

## Instalace projektu

1. **Naklonujte projekt z GitHubu:**
   ```bash
   git clone https://github.com/<váš-uživatelský-účet>/task_manager_mysql.git
   cd task_manager_mysql
   ```

2. **Vytvořte a aktivujte virtuální prostředí:**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux / macOS
   venv\Scripts\activate         # Windows
   ```

3. **Nainstalujte potřebné knihovny:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Vytvořte konfigurační soubor `.env`:**
   - použijte vzorový soubor `.env.example`
   - doplňte své přihlašovací údaje pro MySQL (produkční a testovací databázi)

   ```bash
   DB_HOST=localhost
   DB_NAME=task_manager_prod
   DB_USER=root
   DB_PASSWORD=heslo
   DB_TEST_NAME=task_manager_test
   DB_TEST_USER=root
   DB_TEST_PASSWORD=heslo
   ```

5. **Spusťte aplikaci:**
   ```bash
   python src/task_manager_mysql/task_manager_mysql_p2.py
   ```

---
## Architektura programu a rozdělení funkcí

Program je rozdělen do několika vrstev, které od sebe oddělují práci s uživatelským vstupem, databází a řízením aplikace.  
Tento přístup zajišťuje snadnější testování jednotlivých částí programu. Program je koncipován pro automatizované testování (PyTest).

### 1. Databázové funkce (DB funkce)
Tyto funkce **pracují přímo s MySQL databází**. Otevírají kurzor, provádějí SQL dotazy a zpracovávají chyby.  
Nemají žádné uživatelské vstupy – místo toho dostávají data jako parametry.  
Tímto způsobem mohou být snadno testovány pomocí **PyTestu**.

- `pripojeni_db(test_db=False)` – připojí aplikaci k MySQL databázi (produkční nebo testovací).  
- `vytvoreni_tabulky(conn)` – ověří existenci tabulky `ukoly` a pokud neexistuje, vytvoří ji.  
- `pridat_ukol_db(nazev, popis, conn)` – vloží nový úkol do tabulky s výchozím stavem `nezahájeno`.  
- `aktualizovat_ukol_db(id_ukolu, novy_stav, conn)` – změní stav úkolu na základě ID (`probíhá` nebo `hotovo`).  
- `odstranit_ukol_db(id_ukolu, conn)` – odstraní úkol z databáze podle ID.

---

### 2. Uživatelské (UI) funkce
Tyto funkce zajišťují **interakci s uživatelem** – načítají vstupy pomocí `input()` a validují je.  
Poté volají odpovídající databázové funkce s ověřenými daty.

- `pridat_ukol(conn)` – načte název a popis od uživatele, ověří jejich platnost a zavolá `pridat_ukol_db()`.  
- `aktualizovat_ukol(conn)` – vypíše všechny úkoly, nechá uživatele vybrat ID a nový stav a zavolá `aktualizovat_ukol_db()`.  
- `odstranit_ukol(conn)` – vypíše všechny úkoly, nechá uživatele vybrat ID a zavolá `odstranit_ukol_db()`.

Pokud v databázi nejsou žádné úkoly, funkce nevyvolají chybu, ale zobrazí informaci o prázdné tabulce.

---

### 3. Zobrazovací funkce (SELECT dotazy)
Slouží pro výpis dat z databáze. Každý řádek z tabulky `ukoly` je načten jako slovník (`dictionary=True`), což umožňuje čitelnější přístup ke klíčovým hodnotám.

- `zobrazit_ukoly(conn)` – vypíše pouze **nedokončené** úkoly (stav `nezahájeno` nebo `probíhá`).  
- `zobrazit_vsechny_ukoly(conn)` – vypíše **všechny** úkoly bez ohledu na stav (používá se i jako pomocná funkce pro jiné akce).

Pokud tabulka neobsahuje žádné záznamy, funkce vracejí prázdný seznam `[]` (nejde o chybu).  
Pokud dojde k SQL chybě, vrací `False`.

---

### 4. Řídicí funkce
Řídí hlavní běh programu a navigují uživatele mezi jednotlivými částmi aplikace.

- `hlavni_menu(conn)` – zobrazí hlavní nabídku a zpracovává volby uživatele.  
  Umožňuje výběr mezi přidáním, zobrazením, aktualizací nebo odstraněním úkolu.  
- `main()` – hlavní vstupní bod programu.  
  Zajistí připojení k databázi, vytvoření tabulky a spuštění hlavního menu.

Program se spouští příkazem:

```bash
python task_manager.py
```

---

## Spuštění testů pomocí PyTest

Automatizované testy lze spustit jednoduše příkazem:

```bash
pytest -v
```

Testy ověřují funkčnost tří hlavních databázových funkcí:

- `pridat_ukol_db()` – vložení nového úkolu  
- `aktualizovat_ukol_db()` – změna stavu úkolu  
- `odstranit_ukol_db()` – odstranění úkolu  

Každá z těchto funkcí má:
- jeden **pozitivní test** (ověření správné funkčnosti),
- jeden **negativní test** (ověření reakce na neplatné vstupy).

Po dokončení testů jsou testovaná data smazána, databáze tak zůstane po dokončení testovacího cyklu čistá.

---

## Požadavky a závislosti

Projekt využívá tyto knihovny:

```bash
mysql-connector-python
python-dotenv
pytest
```

Všechny závislosti lze nainstalovat jedním příkazem:
```bash
pip install -r requirements.txt
```

---

## Shrnutí

Aplikace **Task Manager – Python + MySQL** kombinuje:
- přehlednou architekturu (oddělení UI a DB funkcí),
- bezpečné načítání přihlašovacích údajů z `.env`,
- plnou testovatelnost pomocí **PyTestu**,
- a automatické ověřování správnosti kódu pomocí **GitHub Actions**.

---

