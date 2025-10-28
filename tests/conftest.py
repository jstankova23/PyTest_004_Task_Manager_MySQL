"""
====================================================================================
PyTest – Fixtures pro testování databázových funkcí (Task Manager - Python + MySQL)
------------------------------------------------------------------------------------
Autor:        Jana Staňková
Vytvořeno:    28.10.2025
Python:       3.10+

Popis:
Tento soubor obsahuje fixtures pro automatizované testy, které ověřují správnou 
funkčnost databázových operací aplikace (Task Manager – Python + MySQL).

Architektura programu je rozdělena na:
    • UI funkce – zpracovávají uživatelský vstup (input, print)
    • DB funkce – provádějí operace nad databází (INSERT, UPDATE, DELETE)

V rámci PyTestů jsou testovány pouze databázové funkce, nikoliv UI funkce. 
Testování UI funkcí by vyžadovalo mockování pomocí monkeypatch na input().

Fixtures definované v tomto souboru:
1) fix_create_db_table:
vytvoří tabulku 'ukoly' v testovací databázi, spouští se jednou za celou testovací 
relaci, scope="session"

2) fix_test_conn:
vytvoří nové připojení pro každý test, před i po testu vyčistí tabulku 'ukoly',
spouští se pro každou testovací funkci, scope="function"

Cílem těchto fixtures je zajistit izolované, opakovatelné a nezávislé testování 
databázových funkcí bez vzájemného ovlivnění dat.


Speciální chování v CI prostředí (GitHub Actions):
Pokud testy běží v GitHub Actions (proměnná prostředí CI=true) a připojení k testovací databázi
MySQL není dostupné, testy se automaticky přeskočí (pytest.skip), aby build nepadal kvůli 
chybějící databázi.
=====================================================================================
"""


import os
import pytest
from task_manager_mysql.task_manager_mysql_p2 import pripojeni_db, vytvoreni_tabulky

# Fixture pro vytvoření testovací tabulky 'ukoly' (vytvoří se jednou za testovací session)
@pytest.fixture(scope="session")
def fix_create_db_table():
    # a) připojení k test databázi
    conn = pripojeni_db(test_db=True)

    # --- GitHub Actions prostředí ---
    # Pokud test běží v GitHub Actions (CI=true) a DB není dostupná,
    # testy se přeskočí, aby build nepadal na chybějící databázi.
    if os.getenv("CI") == "true" and conn is None:
        pytest.skip("Test přeskočen: nelze se připojit k testovací databázi v prostředí GitHub Actions.")

    # --- Lokální prostředí ---
    # Pokud se k DB nelze připojit lokálně, považujeme to za chybu.
    assert conn is not None, "Nepodařilo se připojit k testovací databázi"

    # b) vytvoření tabulky, pokud ještě neexistuje
    vytvoreni_tabulky(conn)
    conn.close()


# Fixture pro připojení k databázi a zajištění čistoty dat v tabulce 'ukoly'
@pytest.fixture(scope="function")
def fix_test_conn(fix_create_db_table):
    # a) připojení k test databázi
    conn = pripojeni_db(test_db=True)

    # --- GitHub Actions prostředí ---
    # GitHub automaticky nastavuje proměnnou prostředí CI=true.
    # Pokud běžíme v CI a databáze není dostupná, testy se přeskočí.
    if os.getenv("CI") == "true" and conn is None:
        pytest.skip("Test přeskočen: nelze se připojit k testovací databázi v prostředí GitHub Actions.")

    # --- Lokální prostředí ---
    # Pokud databáze není dostupná lokálně, považujeme to za chybu.
    assert conn is not None, "Nepodařilo se připojit k testovací databázi"

    # b) před testem vymazat data
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly;")
    conn.commit()

    # c) předání objektu conn do parametru test funkce; vystoupení z fixture, spustí se test funkce 
    yield conn

    # d) po testu znovu vymazat data
    cursor.execute("DELETE FROM ukoly;")
    conn.commit()
    cursor.close()
    conn.close()
