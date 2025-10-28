"""
Balíček task_manager_mysql
--------------------------
Součást projektu Task Manager – Python + MySQL.

Obsahuje zdrojové funkce aplikace pro správu úkolů (CRUD operace)
a jejich připojení k MySQL databázi.
"""

from .task_manager_mysql_p2 import (
    pripojeni_db,
    vytvoreni_tabulky,
    pridat_ukol,
    pridat_ukol_db,
    zobrazit_ukoly,
    zobrazit_vsechny_ukoly,
    aktualizovat_ukol,
    aktualizovat_ukol_db,
    odstranit_ukol,
    odstranit_ukol_db,
    hlavni_menu,
    main
)
