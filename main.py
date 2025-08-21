"""
main.py: pátý projekt do Engeto Online Python Akademie

author: Jarmila Kroulová
email: jarmilxxx@seznam.cz
""" 

import mysql.connector

def pripojeni_db():
    """
    Vytvoří databázi a připojí se k ní. Vrací připojení.
    """
    try:
        #pripojeni bez dtb
        pripojeni = mysql.connector.connect(
            host="localhost",
            user="root",
            # password="",  # zadejte své heslo pro připojení k MySQL Workbench

        )
        if pripojeni.is_connected():
            kurzor = pripojeni.cursor()
            kurzor.execute("CREATE DATABASE IF NOT EXISTS spravce_ukolu")
            #pripojeni s dtb
            pripojeni = mysql.connector.connect(
                host="localhost",
                user="root",
                # password="",  # zadejte své heslo pro připojení k MySQL Workbench
                database="spravce_ukolu"
            )
            print("Jste úspěšně připojen k databázi Správce úkolů.")
            return  pripojeni
    except mysql.connector.Error as e:
        print(f"Chyba při připojování: {e}")
    return None


def vytvoreni_tabulky(pripojeni):
    """
    Pokud neexistuje tabulka 'ukoly', vytvoří ji.
    """
    kurzor = pripojeni.cursor()
    try:
        kurzor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(100) NOT NULL,
            popis VARCHAR(500) NOT NULL,
            stav VARCHAR(50) DEFAULT 'Nezahájeno',
            datum_vytvoreni DATE NOT NULL DEFAULT CURRENT_DATE
        );
    """)
        print("Byla vytvořena tabulka pro správu úkolů.")
    except mysql.connector.Error as err:
        print(f"Chyba při vytváření tabulky: {err}")
    finally:
        kurzor.close()


class ChybaUkolu(Exception):
    """Vlastní výjimka pro chyby spojené s úkolem."""
    pass


def pridat_ukol(pripojeni, nazev_ukolu, popis_ukolu):
    """
    Zapíše úkol do tabulky 'ukoly' v databázi 'spravce_ukolu'.
    """
    ukol = nazev_ukolu.strip()
    popis = popis_ukolu.strip()

    if not ukol:
        raise ChybaUkolu("Úkol nebyl zadán, opakujte prosím zadání úkolu.")
    if not popis:
        raise ChybaUkolu("Popis nebyl zadán, opakujte prosím zadání úkolu.")
    if len(ukol) > 100:
        raise ChybaUkolu("Úkol je moc dlouhý (max. 100 znaků).")
    if len(popis) > 500:
        raise ChybaUkolu("Popis je moc dlouhý (max. 500 znaků).")
    kurzor = pripojeni.cursor()
    try:
        kurzor.execute("""
            INSERT INTO ukoly (nazev, popis) 
            VALUES (%s, %s);
            """,(ukol, popis))
        pripojeni.commit()
        print(f"Úkol '{ukol}' byl zadán.")
    except mysql.connector.Error as err:
        raise ChybaUkolu(f"Chyba při vkládání dat: {err}")
    finally:
        kurzor.close()


def vytisknout_ukoly(ukoly: list):
    print("Seznam úkolů:")
    if not ukoly:
        print("Žádné úkoly k zobrazení.")
        return
    for id, nazev, popis, stav in ukoly:
        print(f"{id}. - {nazev} - {popis} - {stav}")


def zobrazit_ukoly(pripojeni):
    """
    Zobrazí všechny úkoly v databázi, pokud nejsou, zobrazí hlášku o neexistenci úkolů. 
    Vrací list s načtenými úkoly.
    """
    kurzor = pripojeni.cursor()
    try:
        kurzor.execute("""
            SELECT id, nazev, popis, stav FROM ukoly;
            """)
        vysledky = kurzor.fetchall()
        return vysledky
    except mysql.connector.Error as err:
        print(f"Chyba při zobrazení dat: {err}")
        return []
    finally:
        kurzor.close()


def zobrazit_filtrovane_ukoly(pripojeni, volba_filtru):
    """
    Zobrazí filtrované úkoly v databázi dle výběru uživatele. 
    Možnosti výběru jsou Nezahájeno, Probíhá, Hotovo.
    Pokud nejsou ve filtru žádné úkoly,zobrazí hlášku o neexistenci úkolů.
    Vrací list s načtenými úkoly.
    """
    kurzor = pripojeni.cursor()
    try:
        if volba_filtru == "N":
            kurzor.execute("""
            SELECT id, nazev, popis, stav FROM ukoly WHERE stav = 'Nezahájeno';
            """)
        elif volba_filtru == "P":
            kurzor.execute("""
            SELECT id, nazev, popis, stav FROM ukoly WHERE stav = 'Probíhá';
            """)
        elif volba_filtru == "H":
            kurzor.execute("""
            SELECT id, nazev, popis, stav FROM ukoly WHERE stav = 'Hotovo';
            """)
        vysledky = kurzor.fetchall()
        return vysledky
    except mysql.connector.Error as err:
        print(f"Chyba při vkládání dat: {err}")
        return []
    finally:
        kurzor.close()



def aktualizovat_ukol(pripojeni, volba_id, volba_stavu):
    """
    Umožňuje změnit stav úkolu z Nezahájeno = defaultní hodnota 
    na Probíhá nebo Hotovo."""
    kurzor = pripojeni.cursor()
    try:
        if not volba_id.isdigit():
            raise ChybaUkolu("Neplatné číslo úkolu.")
        kurzor.execute("SELECT 1 FROM ukoly WHERE id = %s", (int(volba_id),))
        if kurzor.fetchone() is None:
            raise ChybaUkolu("Úkol s tímto ID neexistuje.")
        if volba_stavu == "P":
            kurzor.execute("UPDATE ukoly SET stav = 'Probíhá' WHERE id = %s", (int(volba_id),))
            pripojeni.commit()
            print(f"Úkol '{volba_id}' byl aktualizován na 'Probíhá'.")
        elif volba_stavu == "H":
            kurzor.execute("UPDATE ukoly SET stav = 'Hotovo' WHERE id = %s", (int(volba_id),))
            pripojeni.commit()
            print(f"Úkol '{volba_id}' byl aktualizován na 'Hotovo'.")
                
        else:
            print("Neplatná volba stavu.")
    except mysql.connector.Error as err:
        print(f"Chyba při aktualizaci dat: {err}")  
    finally:
        kurzor.close()


def odstranit_ukol(pripojeni, volba_odstraneni):
    """
    Umožňuje odstranit úkol z databáze pomocí zvoleného id.
    """
    kurzor = pripojeni.cursor()
    try:
        if not volba_odstraneni.isdigit() :
            raise ChybaUkolu("Neplatné číslo úkolu.")
        kurzor.execute("SELECT 1 FROM ukoly WHERE id = %s", (int(volba_odstraneni),))
        if kurzor.fetchone() is None:
            raise ChybaUkolu("Úkol s tímto číslem neexistuje.")
        kurzor.execute("DELETE FROM ukoly WHERE id=%s",(int(volba_odstraneni),))
        pripojeni.commit()
        print(f"Úkol '{volba_odstraneni}' byl smazán.")
            
    except mysql.connector.Error as err:
        print(f"Chyba při mazání dat: {err}")
    finally:
        kurzor.close()


def zpracovat_volbu(volba: int, pripojeni):
    """
    Získává a zpracovává vstupy od uživatele.
    """
    if volba == 1:
        nazev_ukolu = input("Zadejte název úkolu - max. 100 znaků:  ")
        popis_ukolu = input("Zadejte popis úkolu - max. 500 znaků:  ")
        try:
            pridat_ukol(pripojeni, nazev_ukolu, popis_ukolu)
        except ChybaUkolu as chyba:
            print(f"Chyba při vkládání úkolu: {chyba}")
    elif volba == 2:
        chce_filtrovat = input("Přejete si úkoly filtrovat? A/N:  ").upper().strip()
        while chce_filtrovat not in ("N", "A"):
            print("Neplatný výběr.")
            chce_filtrovat = input("Přejete si úkoly filtrovat? A/N:  ").upper().strip()
        if chce_filtrovat == "N":
            vysledky = zobrazit_ukoly(pripojeni)
            vytisknout_ukoly(vysledky)
        elif chce_filtrovat == "A":
            volba_filtru = input("Vyberte požadovaný filtr - Nezahájeno = N, Probíhá = P, Hotovo = H:  ").upper().strip()
            while volba_filtru not in ("N", "P", "H"):
                print("Neplatný filtr. Zadejte N, P nebo H.")
                volba_filtru = input("Vyberte požadovaný filtr - Nezahájeno = N, Probíhá = P, Hotovo = H:  ").upper().strip()
            vysledky = zobrazit_filtrovane_ukoly(pripojeni, volba_filtru)
            vytisknout_ukoly(vysledky)
    elif volba == 3:
        vysledky = zobrazit_ukoly(pripojeni)
        vytisknout_ukoly(vysledky)
        volba_id = input("Zadejte číslo úkolu, který si přejete aktualizovat:  ").strip()
        while not volba_id.isdigit():
            print("Neplatné číslo úkolu.")
            volba_id = input("Zadejte číslo úkolu, který si přejete aktualizovat: ").strip()
        
        volba_stavu = input("Zadejte nový stav - Probíhá = P, Hotovo = H:  ").strip().upper()
        while volba_stavu not in ("P", "H"):
            print("Neplatná volba stavu.")
            volba_stavu = input("Zadejte nový stav - Probíhá = P, Hotovo = H: ").strip().upper()
       
        aktualizovat_ukol(pripojeni, volba_id, volba_stavu)
    elif volba == 4:
        vysledky = zobrazit_ukoly(pripojeni)
        vytisknout_ukoly(vysledky)
        volba_odstraneni = input("Zadejte číslo úkolu, který chcete odstranit (Tento krok je nevratný!):  ").strip()
        while not volba_odstraneni.isdigit():
            print("Neplatné číslo úkolu.")
            volba_odstraneni = input("Zadejte číslo úkolu, který chcete odstranit (Tento krok je nevratný!):  ").strip()
        potvrzeni = input(f"Opravdu chcete smazat úkol {volba_odstraneni}? A/N: ").upper().strip()
        if potvrzeni == "A":
            odstranit_ukol(pripojeni, volba_odstraneni)
        else:
            print("Mazání zrušeno.")
   

def hlavni_menu():
     """
     Slouží jako hlavní menu pro správce úkolů.
     Zpracovává prvotní vstup od uživatele.
     """
     oddelovac = "_"*40
     pripojeni = pripojeni_db()
     if not pripojeni:
         print("Nepodařilo se připojit k databázi.")
         return
     vytvoreni_tabulky(pripojeni)
     try:
        while True:
            print(oddelovac)
            print("""
    Správce úkolů - Hlavní menu
    ___________________________
    1. Přidat úkol
    2. Zobrazit úkoly
    3. Aktualizovat úkol
    4. Odstranit úkol
    5. Ukončit program
    ___________________________
    """)
            vyber = input("Vyberte možnost (1 - 5):  ").strip()
            print(oddelovac)
            if not vyber.isdigit() or int(vyber) not in range(1,6): 
                print("Neplatná volba")
                continue

            volba = int(vyber)
            if volba == 5:
                print(oddelovac)
                print("Program ukončen.")
                break
            zpracovat_volbu(volba, pripojeni)
     finally:
            # Uzavření připojení
            pripojeni.close()
            print("Připojení k databázi bylo uzavřeno.")      

        

if __name__ == "__main__":
    hlavni_menu()
