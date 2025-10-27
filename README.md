# PyTest_004_Task_Manager_MySQL
# Task Manager – správa úkolů (Python + MySQL)

**Autor:** Jana Staňková  
**Verze:** 1.1.0  
**Datum:** 27. října 2025  
**Licence:** MIT  
**Python:** 3.10+  

---

## Popis aplikace

Tento projekt představuje **vylepšenou verzi aplikace Task Manager**, vytvořenou jako součást výuky modulu *MySQL přes Python* v rámci Engeto Academy.  
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

## Testování pomocí PyTest

Každá databázová funkce je připravena pro testování pomocí **PyTestu**.  
Testy běží nad **testovací databází**, která má stejnou strukturu jako produkční tabulka.  

Každá testovaná funkce má dva testy:
- **Pozitivní test** – ověří správnou funkčnost (např. vložení nebo změna záznamu).  
- **Negativní test** – ověří, jak se funkce chová při neplatném vstupu nebo chybě (např. neexistující ID).  

Po dokončení testů lze testovací data smazat, databáze tak zůstane po dokončení testovacího cyklu čistá.

---

## Požadavky a závislosti

Aplikace vyžaduje nainstalované knihovny:

```bash
pip install mysql-connector-python python-dotenv pytest
```

A dále soubor `.env` s konfigurací připojení k databázi:

```bash
DB_HOST=localhost
DB_NAME=task_manager_prod
DB_USER=root
DB_PASSWORD=heslo
DB_TEST_NAME=task_manager_test
DB_TEST_USER=root
DB_TEST_PASSWORD=heslo
```

---


