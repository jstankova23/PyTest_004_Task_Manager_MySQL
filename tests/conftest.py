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
-------------------------------------------------------------------------------------
1) fix_create_db_table:
vytvoří tabulku 'ukoly' v testovací databázi, spouští se jednou za celou testovací 
relaci, scope="session"

2) fix_test_conn:
vytvoří nové připojení pro každý test, před i po testu vyčistí tabulku 'ukoly',
spouští se pro každou testovací funkci, scope="function"

Cílem těchto fixtures je zajistit izolované, opakovatelné a nezávislé testování 
databázových funkcí bez vzájemného ovlivnění dat.
=====================================================================================
"""

import pytest
from src.task_manager_mysql import pripojeni_db, vytvoreni_tabulky


# 1) Fixture pro jednorázové vytvoření tabulky 'ukoly' v testovací databázi
# spouští se pouze jednou za celou testovací relaci
@pytest.fixture(scope="session")
def fix_create_db_table():
    conn = pripojeni_db(test_db=True)
    assert conn is not None, "Nepodařilo se připojit k testovací databázi"
    vytvoreni_tabulky(conn)
    conn.close()


# 2) Fixture pro připojení a čištění tabulky 'ukoly' v testovací databázi
# spouští se u každé test funkce, pro kterou vždy provede akce:
# a) otevře nové připojení;
# b) před testem i po testu vyčistí tabulku 'ukoly';
# c) vrací objekt conn pro použití v testech
@pytest.fixture(scope="function")
def fix_test_conn(fix_create_db_table):
    # a) připojení k test databázi
    conn = pripojeni_db(test_db=True)       
    assert conn is not None, "Nepodařilo se připojit k testovací databázi"

    # b) před testem vymazat data
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly;")
    conn.commit()

    yield conn  # c) předání objektu conn do parametru test funkce; vystoupení z fixture, spustí se test funkce 

    # b) po testu znovu vymazat data
    cursor.execute("DELETE FROM ukoly;")
    conn.commit()
    cursor.close()
    conn.close()