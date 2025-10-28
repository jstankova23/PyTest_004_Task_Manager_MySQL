"""
===========================================================================================
 Task Manager – Python + MySQL
-------------------------------------------------------------------------------------------
Autor:        Jana Staňková
Verze:        1.2.2
Vytvořeno:    23.10.2025
Aktualizace:  28.10.2025
Licence:      MIT License
Python:       3.10+

Popis:
Aplikace pro správu úkolů (Task Manager). 
Ukládá úkoly do databáze MySQL a umožňuje jejich přidávání, zobrazení, aktualizaci a mazání.

Připojení k databázi používá proměnné prostředí, které se načítají ze souboru .env 
(pomocí python-dotenv). Ukázkový .env.example je součástí repozitáře.

Architektura programu je rozdělena na:
    • UI funkce – zpracovávají uživatelský vstup (input, print)
    • DB funkce – provádějí operace nad databází (INSERT, UPDATE, DELETE)

V rámci PyTestů jsou testovány pouze databázové funkce, nikoliv UI funkce. 
Testování UI funkcí by vyžadovalo mockování pomocí monkeypatch na input().

Aplikace umožňuje práci na produkčním i testovacím prostředí.
Souhrnný přehled návratových hodnot dle typu funkcí je uveden na konci programu.
==============================================================================================
"""

import os
import mysql.connector
from dotenv import load_dotenv   # import vyžaduje instalaci knihovny python-dotenv (pro nastavení prostředí)

# 1) Environment variables
# funkce load_dotenv() z knihovny python-dotenv načítá proměnné prostředí ze souboru .env;
# slouží k bezpečnému uložení přihlašovacích údajů (k MySQL) a umožňuje sdílení kódu bez citlivých dat
load_dotenv()       # načte proměnné z .env souboru (název databáze, uživatele, heslo)


# 2) Připojení k databázi
# funkce pro připojení k lokálním databázím (prod nebo test);
# funkce vrací None (chyba připojení) nebo objekt conn (připojení k prod/test db), který je pak parametrem všech dalších funkcí programu;
# parametr funkce rozhoduje o připojení k prod nebo test db, pokud se spustí funkce bez parametru, default připojení je na prod;
# naopak parametr u fixture pro PyTest (fix_test_conn) je definována s default hodnotou pro připojení na test db (test_db=True);
# volání funkce: pripojeni_db() / pripojeni_db(test_db=False) --- připojení na prod db (task_manager_prod);
# volání funkce: pripojeni_db(test_db=True) --- připojení na test db (task_manager_test)
def pripojeni_db(test_db=False):
    try:
        if test_db:                                      # připojení do testovací databáze: test_db
            db_name = os.getenv("DB_TEST_NAME")
            db_user = os.getenv("DB_TEST_USER")
            db_password = os.getenv("DB_TEST_PASSWORD")
        else:                                            # připojení do prod databáze: prod_db
            db_name = os.getenv("DB_NAME")
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")

        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=db_user,
            password=db_password,
            database=db_name
        )
        # Ověření, že připojení funguje
        if conn.is_connected():
            print(f"Připojení k databázi '{db_name}' bylo úspěšné.")
            return conn                         # připojení provedeno a vrací objekt conn

    except mysql.connector.Error as err:
        print(f"Chyba při připojování k databázi '{db_name}': {err}")
        return None                             # připojení neprovedeno, konec



# 2) Vytvoření tabulky (pokud neexistuje)
# funkce pro vytvoření tabulky v lokální databázi (test nebo prod);
# funkce bez návratu, provádí pouze efekt;
# s parametrem conn si vytvoří vlastní kurzor jen na dobu svého běhu;
# objekt conn obsahuje připojení k prod nebo test db, dle parametru funkce pripojeni_db();
# datový typ ENUM pro sloupec 'stav' zajišťuje pouze 3 povolené hodnoty s default hodnotou 'nezahájeno' 
# CHECK constraint u sloupců 'nazev', 'popis' zajišťuje, že hodnota nesmí být null (prázdná) a ani to nesmí být prázdný řetězec
def vytvoreni_tabulky(conn):   
    try:
        cursor = conn.cursor()     
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(30) NOT NULL CHECK (nazev <> ''),
                popis VARCHAR(100) NOT NULL CHECK (popis <> ''),
                stav ENUM('nezahájeno', 'probíhá', 'hotovo') NOT NULL DEFAULT 'nezahájeno', 
                datum_vytvoreni DATE
            )
        ''')
        conn.commit()                               
        print("Tabulka 'ukoly' již existuje nebo byla právě vytvořena.")

    except mysql.connector.Error as err:
        print(f"Chyba při vytváření tabulky: {err}")
    finally:
        cursor.close()



# 3) Přidání úkolu 
# funkce pro přidání úkolu do databázové tabulky 'ukoly' - volba 1 z hlavního menu;
# a) pridat_ukoly(): pouze načítá data z uživatelského vstupu, které pak předává svojí databázové variantě do jejích parametrů;
# b) pridat_ukol_db(): provádí insert nového úkolu do databázové tabulky 'ukoly'

# a) pridat_ukoly(): 
# funkce vrací True (volá db funkci) nebo False dle úspěšnosti 
# funkce vrací False při špatném vstupu nebo True (předá výsledek a zavolá db funkci)
def pridat_ukol(conn):  # získání hodnot z uživatelského vstupu ještě před voláním db funkce
    nazev = input("Zadejte název úkolu: ").strip()
    popis = input("Zadejte popis úkolu: ").strip()

    # validace uživatelského vstupu ještě před voláním db funkce
    if not nazev or not popis:
        print("Nebyl zadán název nebo popis úkolu. Prosím, zadejte obě tyto hodnoty (název, popis úkolu).")
        return False

    return pridat_ukol_db(nazev, popis, conn) # volání db funkce, předání validovaných hodnot z uživatelského vstupu (nazev, popis) a objektu conn do jejích parametrů

# b) pridat_ukol_db():
# funkce vrací True nebo False dle úspěšnosti provedení insertu
def pridat_ukol_db(nazev, popis, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ukoly (nazev, popis, stav, datum_vytvoreni) VALUES (%s, %s, 'nezahájeno', CURDATE())", (nazev, popis))
        conn.commit()
        cursor.close()
        print(f"Úkol '{nazev}' byl úspěšně přidán.")
        return True

    except mysql.connector.Error as err:
        print(f"Chyba při přidávání úkolu: {err}")
        return False



# 4) Zobrazení úkolů
# funkce pro zobrazení uložených úkolů
# a) zobrazit_ukoly(): funkce zobrazující výpis všech nedokončených úkolů z tabulky 'ukoly' (stav 'nezahájeno' nebo 'probíhá'), volba 2 z hlavního menu;
# b) zobrazit_vsechny_ukoly(): pomocná funkce pro aktualizovat_ukol(), odstranit_ukol() – zobrazuje všechny úkoly bez ohledu na jejich stav, není přístupná z hlavního menu

# a) zobrazit_ukoly():
# funkce vrací objekt nedokoncene_ukoly v podobě seznamu/slovníků s nedokončenými úkoly nebo prázdný seznam (prázdný seznam není chyba);
# conn.cursor(dictionary=True):
# i) row=ukol=dictionary, což umožní přistupovat v tisku k jednotlivým klíčům/sloupcům tabulky podle jejich názvu;
# ii) každý řádek/ukol/slovník má názvy sloupců jako klíče; 
# iii) bez parametru dictionary: row=ukol=n-tice a data by se musela tisknout na základě pozic, tzn. horší čitelnost kódu: print(f"{ukol[0]}. {ukol[1]} - {ukol[2]} ({ukol[3]})")
def zobrazit_ukoly(conn):
    try:
        cursor = conn.cursor(dictionary=True)   # každá řádka z tabulky bude načtena jako samostatný slovník, nikoliv n-tice
        cursor.execute("SELECT * FROM ukoly WHERE stav IN ('nezahájeno', 'probíhá')")
        nedokoncene_ukoly = cursor.fetchall()   # proměnná nedokoncene_ukoly - objekt potřebný pro automatizovaný test (PyTest)
        cursor.close()

        if not nedokoncene_ukoly:
            print("Neexistují žádné nedokončené úkoly.")
            return []       # funkce vrací prázdný seznam

        else:
            print("\nSEZNAM ÚKOLŮ:")
            for ukol in nedokoncene_ukoly:                                                 # row = ukol = slovník
                print(f"{ukol['id']}. {ukol['nazev']} - {ukol['popis']} ({ukol['stav']})") # tisk hodnot klíčů ze slovníků ukol
            return nedokoncene_ukoly  # funkce vrací pouze nedokončené úkoly
    
    except mysql.connector.Error as err:
        print(f"Chyba při načítání úkolů: {err}")
        return False           # konec funkce, návrat do hlavního menu

# b) zobrazit_vsechny_ukoly():
# pomocná funkce – zobrazení všech úkolů (bez filtru) pro aktualizovat_ukol(), odstranit_ukol()
# funkce vrací objekt ukoly v podobě seznamu/slovníků všech úkolů nebo prázdný seznam (prázdný seznam není chyba);
def zobrazit_vsechny_ukoly(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ukoly")
        ukoly = cursor.fetchall()
        cursor.close()

        if not ukoly:
            print("Tabulka 'ukoly' je prázdná.")
            return []       # funkce vrací prázdný seznam

        print("\nSEZNAM VŠECH ÚKOLŮ:")
        for ukol in ukoly:
            print(f"{ukol['id']}. {ukol['nazev']} - {ukol['popis']} ({ukol['stav']})")
        return ukoly                # funkce vrací všechny úkoly

    except mysql.connector.Error as err:
        print(f"Chyba při načítání úkolů: {err}")
        return False    # konec funkce, návrat do hlavního menu



# 5) Změna stavu úkolu
# funkce pro změnu stavu úkolu dle zadaného ID úkolu, volba 3 z hlavního menu;
# a) aktualizovat_ukol(): ověřuje prázdný seznam úkolů, načítá pouze data z uživatelského vstupu, částečně je validuje (int) a předává svojí databázové variantě do jejích parametrů;
# b) aktualizovat_ukol_db(): db varianta funkce, která provádí změnu stavu úkolu v databázové tabulce 'ukoly'

# a) aktualizovat_ukol():
# funkce pouze pro zjištění a validaci uživatelského vstupu a zjištění, zda seznam úkolů obsahuje data;
# vrací True/False dle úspěchu nebo prázdný seznam v případě prázdné tabulky 'ukoly' 
def aktualizovat_ukol(conn):
    # kontrola, zda v tabulce 'ukoly' vůbec existují nějaké úkoly (bez filtru, všechny úkoly)
    vsechny_ukoly = zobrazit_vsechny_ukoly(conn)
    if not vsechny_ukoly:
        print("Tabulka 'ukoly' je prázdná. Nejsou k dispozici žádné úkoly k aktualizaci.")    
        return []       # funkce vrací prázdný seznam      
    if vsechny_ukoly is False: # technická chyba při SELECTu
        return False                                                                                                                         

    # uživatelský vstup: ID úkolu
    vstup_id_ukolu = input("Zadejte ID úkolu, u kterého chcete měnit jeho stav: ").strip()   # string, bez převodu na int, odstranění mezer před a po stringu
    # kontrola hodnoty z uživatelského vstupu ještě před voláním db funkce;
    # kontrola správnosti datového typu (0–9) a konečný převod na integer;
    # kontrola rozsahu ID neprobíhá, musí provést až db funce s přístupem do MySQL databáze, jedná se o výpis jen některých (nedokončených) úkolů s různými ID
    if not vstup_id_ukolu.isdecimal():                                           
        print("Chybně zadaný datový typ. Zadejte pořadové ID úkolu ze seznamu (celé kladné číslo).")    
        return False                                                                                                                                         
    else:
        id_ukolu = int(vstup_id_ukolu)

    # uživatelský vstup: výběr stavu úkolu
    print("Zvolte nový stav daného úkolu:")
    print("1. probíhá\n2. hotovo")
    vstup_varianta = input("Zadejte číslo varianty (1-2): ").strip()

    if vstup_varianta == "1":
        novy_stav_ukolu = "probíhá"
    elif vstup_varianta == "2":
        novy_stav_ukolu = "hotovo"
    else:
        print("Zadáno neplatné číslo varianty.")
        return False                                                                                                                                           
            
    # volání db funkce, předání hodnot z uživatelského vstupu (id_ukolu, novy_stav) a objektu conn z pripojeni_db() do jejích parametrů   
    return aktualizovat_ukol_db(id_ukolu, novy_stav_ukolu, conn)     

# b) aktualizovat_ukol_db():
# funkce vrací True nebo False dle úspěšnosti provedení aktualizace stavu
def aktualizovat_ukol_db(id_ukolu, novy_stav, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
        if cursor.rowcount == 0:
            cursor.close()
            print("Úkol s tímto ID neexistuje.")
            return False
        else:
            conn.commit()
            cursor.close()
            print(f"Stav úkolu s ID {id_ukolu} byl změněn na '{novy_stav}'.")        
            return True
  
    except mysql.connector.Error as err:
        print(f"Chyba při změně stavu úkolu: {err}")
        return False



# 6) Odstranění úkolu
# funkce pro odstranění úkolu dle zadaného ID úkolu, volba 4 z hlavního menu;
# a) odstranit_ukol(): ověřuje prázdný seznam úkolů, načítá pouze data z uživatelského vstupu, částečně je validuje (int) a předává svojí db variantě do jejích parametrů;
# b) odstranit_ukol_db(): db varianta funkce, která provádí výmaz zadaného úkolu z databázové tabulky 'ukoly'

# a) odstranit_ukol():
# vrací True/False dle úspěchu nebo prázdný seznam v případě prázdné tabulky 'ukoly' 
def odstranit_ukol(conn):    
    # kontrola, zda v tabulce 'ukoly' vůbec existují nějaké úkoly (bez filtru, všechny úkoly)
    vsechny_ukoly = zobrazit_vsechny_ukoly(conn)
    if not vsechny_ukoly:
        print("Nejsou k dispozici žádné úkoly k odstranění.")    
        return []       # funkce vrací prázdný seznam                                                                                                                                     
    if vsechny_ukoly is False:         # technická chyba při SELECTu
        return False

    # uživatelský vstup: ID úkolu
    # získání hodnoty z uživatelského vstupu
    vstup_id_ukolu = input("Zadejte ID úkolu, u který chcete odstranit: ").strip()   # string, bez převodu na int, odstranění mezer před a po stringu
    # kontrola hodnoty z uživatelského vstupu ještě před voláním db funkce;
    # kontrola správnosti datového typu (0–9) a konečný převod na integer;
    # kontrola rozsahu ID neprobíhá, musí provést až db funce s přístupem do MySQL databáze, jedná se o výpis jen některých (nedokončených) úkolů s různými ID
    if not vstup_id_ukolu.isdecimal():                                           
        print("Chybně zadaný datový typ. Zadejte pořadové ID úkolu ze seznamu (celé kladné číslo).")    
        return False                                                                                                                                         
    else:
        id_ukolu = int(vstup_id_ukolu)
  
    # volání db funkce, předání hodnoty z uživatelského vstupu (id_ukolu) a objektu conn z pripojeni_db() do jejích parametrů   
    return odstranit_ukol_db(id_ukolu, conn)       

# b) odstranit_ukol_db(): 
# funkce vrací True nebo False dle úspěšnosti provedení výmazu
def odstranit_ukol_db(id_ukolu, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
        if cursor.rowcount == 0:
            print("Úkol s tímto ID neexistuje.")
            cursor.close()
            return False
        else:
            conn.commit()
            cursor.close()
            print(f"Úkol s ID {id_ukolu} byl odstraněn.")    
            return True
    
    except mysql.connector.Error as err:
        print(f"Chyba při výmazu úkolu: {err}")
        return False



# 7) Hlavní menu
def hlavni_menu(conn):
# pouze textové namapování volby s příslušnou funkcí;
# nekonečný cyklus, po dokončení běhu každé funkce se zobrazuje hlavní menu, dokud ho nepřeruší volba 5 s break
    while True:   
        print("\nSprávce úkolů - Hlavní nabídka")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")

        vstup_volba = input("Vyberte možnost (1-5): ").strip()        # string, bez převodu na int, odstranění mezer před a po stringu

        # kontrola dat z uživatelského vstupu ještě před voláním funkce;
        # 1) kontrola správnosti datového typu (celé číslo/integer) - místo vyvolávání výjimky ValueError
        if not vstup_volba.isdecimal():                                     # Pokud uživatel nezadal celé číslo,
            print("Chybně zadaný datový typ. Zadejte číslo v rozsahu 1-5.") # vytiskni mu hlášku
            continue  # a vráť ho do hl. menu a pokračuj další iterací.

        volba = int(vstup_volba) # převod už prověřené uživatelské hodnoty (čísla) na datový typ integer

        # 2) kontrola správnosti rozsahu zadaného čísla (1-5) - místo vyvolávání výjimky IndexError
        if volba < 1 or volba > 5:                        # Pokud uživatel nezadal číslo v rozsahu 1-5,
            print("Volba akce se zadaným číslem neexistuje. Zadejte číslo v rozsahu 1-5.")
            continue                                      # tak ho vrať do hl. menu a pokračuj další iterací.
        
        # namapování uživatelské volby s příslušnými funkcemi, pouze volba 5 není spojena s funkcí, ale s příkazem break;
        # funkce se volá s už jen ověřenými platnými vstupy (integer v rozsahu 1-5)
        if volba == 1:
            pridat_ukol(conn)
        elif volba == 2:
            zobrazit_ukoly(conn)
        elif volba == 3:
            aktualizovat_ukol(conn)
        elif volba == 4:
            odstranit_ukol(conn)
        elif volba == 5:
            print("Konec programu.")
            break                # ukončení věčného cyklu while true / zobrazování hl. menu, konec programu



# 8. Hlavní funkce pro spuštění programu
# v úvodu spustí příslušné funkce pro připojení do dané databáze, vytvoří či potvrdí existenci tabulky 'ukoly' a spustí hl. menu
def main():
    conn = pripojeni_db()
    if conn:
        vytvoreni_tabulky(conn)
        hlavni_menu(conn)
        conn.close()


if __name__ == "__main__":   # ochrana, při importu do test souborů pro PyTest se nespustí celý zdroják
    main()


"""
==============================================================
NÁVRATOVÉ HODNOTY FUNKCÍ 
--------------------------------------------------------------

Systémové funkce (DB připojení, tabulka)
    • pripojeni_db()            → conn / None
    • vytvoreni_tabulky()       → None

Zobrazovací funkce (SELECT)
    • zobrazit_ukoly()          → list[dict], [] (prázdná tabulka), False (SQL chyba)
    • zobrazit_vsechny_ukoly()  → list[dict], [] (prázdná tabulka), False (SQL chyba)

UI funkce (uživatelský vstup)
    • pridat_ukol()             → True / False
    • aktualizovat_ukol()       → True / [] (prázdná tabulka) / False
    • odstranit_ukol()          → True / [] (prázdná tabulka) / False

Databázové funkce (INSERT / UPDATE / DELETE)
    • pridat_ukol_db()          → True / False
    • aktualizovat_ukol_db()    → True / False
    • odstranit_ukol_db()       → True / False

Řídicí funkce
    • hlavni_menu()             → None
    • main()                    → None

--------------------------------------------------------------
Logika návratových hodnot
    • True / list[dict] / conn  → operace úspěšná
    • []                        → prázdná tabulka (není chyba)
    • False                     → neplatný vstup nebo SQL/technická chyba
    • None                      → pouze efekt, žádná návratová hodnota
==============================================================
"""


