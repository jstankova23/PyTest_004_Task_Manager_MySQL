"""
=================================================================================
PyTest – automatizované testy databázových funkcí (Task Manager – Python + MySQL)
---------------------------------------------------------------------------------
Autor:        Jana Staňková
Verze testů:  1.0.0
Vytvořeno:    28.10.2025
Aktualizace:  
Python:       3.10+

Popis:
Vzhledem k architektuře programu, kde jsou funkce rozděleny na uživatelské (UI) 
a databázové (DB) varianty, jsou v rámci automatizovaných testů s využitím PyTest 
testovány pouze databázové funkce.

UI funkce pracují s uživatelským vstupem input() a jejich testování by vyžadovalo 
mockování pomocí monkeypatch na input().

Testy tedy ověřují pouze správnost funkcí:
    • pridat_ukol_db()
    • aktualizovat_ukol_db()
    • odstranit_ukol_db()

Každá funkce má dva testy:
    – pozitivní scénář (platné vstupy)
    – negativní scénář (neplatné vstupy)

Testy pracují s testovací databází definovanou v .env souboru a využívají fixtures z 
conftest.py pro vytvoření tabulky 'ukoly' a izolaci jednotlivých testovacích případů.
================================================================================
"""


import pytest
from datetime import date
from task_manager_mysql.task_manager_mysql_p2 import pridat_ukol_db, aktualizovat_ukol_db, odstranit_ukol_db


# 1) TESTY PRO DB FUNKCI pridat_ukol_db()
# a) pozitivní test: test vložení úkolu s platným názvem a popisem do tabulky 'ukoly' v test db 
@pytest.mark.positive
def test_pridat_ukol_pozitivni(fix_test_conn):
    conn = fix_test_conn
    # volání testované funkce
    vysledek_pridat = pridat_ukol_db("název test úkolu", "popis test úkolu", conn)
    # ověření přes assert, že testovaná funkce proběhla úspěšně
    assert vysledek_pridat is True

    # ověření přes select, že došlo k vložení záznamu do tabulky 'ukoly'
    cursor = conn.cursor(dictionary=True) # vrátí slovník (ne n-tice) - přístup k hodnotám podle názvů sloupců tabulky

    # načtení vložených dat přes select z tabulky 'ukoly' pro následné kontroly přes assert
    cursor.execute("SELECT * FROM ukoly WHERE nazev = 'název test úkolu'")
    pridany_ukol = cursor.fetchone() # načtení 1 řádku s vloženým úkolem
    cursor.close()
    # ověření přes assert, že byl úkol skutečně vložen
    assert pridany_ukol is not None
    # ověření přes assert, že jsou hodnoty jednotlivých sloupců vloženého záznamu správné
    assert pridany_ukol["popis"] == "popis test úkolu"       
    assert pridany_ukol["stav"] == "nezahájeno"            
    assert isinstance(pridany_ukol["datum_vytvoreni"], date) # kontrola datového typu date, ne hodnoty samotné

# b) negativní test: simulace chybného uživatelského vstupu
# test vložení úkolu s neplatnou (prázdnou) hodnotou pro název ukolu do tabulky 'ukoly' v test db 
@pytest.mark.negative
def test_pridat_ukol_negativni(fix_test_conn):
    conn = fix_test_conn
    # volání testované funkce – očekává se neúspěch (False)
    pridany_ukol = pridat_ukol_db("", "Popis úkolu", conn)
    assert pridany_ukol is False

    # ověření přes select, že se záznam s novým úkolem skutečně nepřidal
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ukoly")
    count = cursor.fetchone()[0]
    cursor.close()
    # ověření přes assert, že tabulka zůstala prázdná
    assert count == 0, "Po neúspěšném insertu by tabulka 'ukoly' měla zůstat prázdná."

# ==================================================================================================================================
# 2) TESTY PRO DB FUNKCI aktualizovat_ukol_db()
# a) pozitivní test: test úspěšné změny stavu úkolu, který je v rámci tohoto testu nejdříve přidán do tabulky 'ukoly' v test db 
@pytest.mark.positive
def test_aktualizovat_ukol_pozitivni(fix_test_conn):
    conn = fix_test_conn
    
    # příprava testovacích dat - vložení úkolu do tabulky 'ukoly' pomocí funkce pro přidání úkolu
    pridat_ukol_db("test ukol pro aktualizaci", "test změny stavu úkolu", conn)

    # načtení ID vloženého úkolu pomocí SELECTu (je potřeba pro aktualizaci stavu)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ukoly WHERE nazev = 'test ukol pro aktualizaci'")
    ukol_id = cursor.fetchone()[0]  

    # volání testované funkce – změna stavu úkolu na 'hotovo' a ověření úspěšnosti pomocí assertu
    result = aktualizovat_ukol_db(ukol_id, "hotovo", conn)
    assert result is True

    # načtení aktuálního stavu úkolu pomocí SELECTu z tabulky 'ukoly' pro následné ověření pomocí assertu
    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (ukol_id,))
    new_state = cursor.fetchone()[0]
    cursor.close()
    assert new_state == "hotovo"

# b) Negativní test: pokus o změnu stavu neexistujícího úkolu (bez přípravy dat, smyšlené ID)
@pytest.mark.negative
def test_aktualizovat_ukol_negativni(fix_test_conn):
    conn = fix_test_conn
    result = aktualizovat_ukol_db(999999999, "probíhá", conn) # smyšlené ID ukolu 999999999
    # funkce by měla vrátit False – aktualizace stavu úkolu neproběhla
    assert result is False

# ==================================================================================================================================
# 3) TESTY PRO DB FUNKCI odstranit_ukol_db()
# a) pozitivní test: test úspěšného odstranění úkolu, který je v rámci tohoto testu nejdříve přidán do tabulky 'ukoly' v test db
 
@pytest.mark.positive
def test_odstranit_ukol_pozitivni(fix_test_conn):

    # příprava testovacích dat - vložení úkolu do tabulky 'ukoly' pomocí funkce pro přidání úkolu
    conn = fix_test_conn
    pridat_ukol_db("test úkol k odstranění", "úkol pro test výmazu", conn)
    
    # načtení ID vloženého úkolu pomocí SELECTu (je potřeba pro odstranění úkolu)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ukoly WHERE nazev = 'test úkol k odstranění'")
    ukol_id = cursor.fetchone()[0]

    # volání testované funkce – vymazání úkolu a ověření úspěšnosti pomocí assertu
    result = odstranit_ukol_db(ukol_id, conn)
    assert result is True

   # ověření pomocí SELECTu, že podle ID úkolu již daný záznam v tabulce 'ukoly' v test db neexistuje (assert)
    cursor.execute("SELECT COUNT(*) FROM ukoly WHERE id = %s", (ukol_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    assert count == 0

# b) Negativní test: pokus o odstranění neexistujícího úkolu (bez přípravy dat, smyšlené ID)
@pytest.mark.negative
def test_odstranit_ukol_negativni(fix_test_conn):
    conn = fix_test_conn
    result = odstranit_ukol_db(999999999, conn) # smyšlené ID ukolu 999999999
    # funkce by měla vrátit False – odstranění neproběhlo, protože úkol s daným ID v tabulce 'ukoly' neexistuje
    assert result is False
    
# ==================================================================================================================================
