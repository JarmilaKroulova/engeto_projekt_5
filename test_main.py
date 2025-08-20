import pytest
import mysql.connector
from main import pridat_ukol, zobrazit_ukoly, aktualizovat_ukol, odstranit_ukol, ChybaUkolu

@pytest.fixture(scope="function")
def dtb_priprava():
    """
    Fixture pro připojení k databázi a nastavení testovacího prostředí.
    """
    # Připojení k MySQL
    pripojeni = mysql.connector.connect(
        host="localhost",
        user="root",
        # password="", # zadejte vaše platné heslo
    ) 
    
    kurzor = pripojeni.cursor()
    kurzor.execute("CREATE DATABASE IF NOT EXISTS test_spravce_ukolu")
    kurzor.close()
    pripojeni.close()
    # Připojení k testovací databázi
    pripojeni = mysql.connector.connect(
        host="localhost",
        user="root",
        # password="", # zadejte vaše platné heslo
        database="test_spravce_ukolu"
    )
    kurzor = pripojeni.cursor()

    # Vytvoření testovací tabulky
    kurzor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(100) NOT NULL,
            popis VARCHAR(500) NOT NULL,
            stav VARCHAR(50) DEFAULT 'Nezahájeno',
            datum_vytvoreni DATE NOT NULL
        );
    """)
    pripojeni.commit()

    # Předání připojení a kurzoru testům
    yield pripojeni

    # Úklid po testech: Smazání tabulky
    kurzor = pripojeni.cursor()
    kurzor.execute("DROP TABLE IF EXISTS ukoly")
    pripojeni.commit()

    # Uzavření připojení
    kurzor.close()
    pripojeni.close()


# TC 1
def test_pridat_ukol_pozitivni(dtb_priprava):
    ukol = "Skleník"
    popis = "Zalít skleník a truhlíky"
    pripojeni = dtb_priprava
    pridat_ukol(pripojeni, ukol, popis) 
    kurzor = pripojeni.cursor()
    kurzor.execute("SELECT nazev, popis FROM ukoly WHERE nazev = %s", (ukol,))
    vysledek = kurzor.fetchone()
    kurzor.close()
    assert vysledek == (ukol, popis)


# TC 2
def test_pridat_ukol_negativni(dtb_priprava):                   # zachycení výjimky při nezadání popisu úkolu
    with pytest.raises(ChybaUkolu, match="Popis nebyl zadán, opakujte prosím zadání úkolu."):
        pridat_ukol(dtb_priprava, "Skleník", "") 


# TC 3
def test_zobrazit_ukoly_pozitivni(dtb_priprava):
    ukol = "Cvičit"
    popis = "Zacvičit si HIIT"
    pripojeni = dtb_priprava
    pridat_ukol(pripojeni, ukol, popis) 
    vysledek = zobrazit_ukoly(pripojeni)
    assert isinstance(vysledek, list), "Funkce by měla vrátit seznam"
    assert len(vysledek) > 0, "Funkce by měla vrátit alespoň jeden úkol"


# TC 4
def test_zobrazit_ukoly_negativni(dtb_priprava):                    # zachycení výjimky při prázdném seznamu úkolů
    with pytest.raises(ChybaUkolu, match="Žádné úkoly k zobrazení."):
        zobrazit_ukoly(dtb_priprava)


# TC 5
def test_aktualizovat_ukol_pozitivni(dtb_priprava):
    ukol = "Nákup"
    popis = "Koupit mléko, chleba, mleté maso"
    pripojeni = dtb_priprava
    kurzor = pripojeni.cursor()
    pridat_ukol(pripojeni, ukol, popis)
    kurzor.execute("SELECT id FROM ukoly WHERE nazev = %s", (ukol,)) 
    volba_id = kurzor.fetchone()[0]
    volba_stavu = "H"
    aktualizovat_ukol(pripojeni, str(volba_id), volba_stavu)
    kurzor.execute(f"SELECT stav FROM ukoly WHERE id = {volba_id}")
    vysledek = kurzor.fetchone()
    kurzor.close()
    assert vysledek[0] == "Hotovo"


# TC 6
def test_aktualizovat_ukol_negativni(dtb_priprava):                 # zachycení výjimky při zadání čísla ID do prázdné tabulky
    with pytest.raises(ChybaUkolu, match="Úkol s tímto ID neexistuje."):
        aktualizovat_ukol(dtb_priprava, "1", "H")


# TC 7
def test_odstranit_ukol_pozitivni(dtb_priprava):
    pripojeni = dtb_priprava
    kurzor = pripojeni.cursor()
    ukol = "Knihovna"
    popis = "Vrátit knížky do knihovny"
    pridat_ukol(pripojeni, ukol, popis)
    kurzor.execute("SELECT id FROM ukoly WHERE nazev = %s", (ukol,)) 
    volba_odstraneni = kurzor.fetchone()[0]
    odstranit_ukol(pripojeni, str(volba_odstraneni))
    kurzor.execute("SELECT * FROM ukoly WHERE id = %s", (volba_odstraneni,))
    vysledek = kurzor.fetchone()
    kurzor.close()
    assert vysledek is None, "Úkol nebyl správně smazán."


# TC 8
def test_odstranit_ukol_negativni(dtb_priprava):                 # zachycení výjimky při zadání písmena místo čísla
    with pytest.raises(ChybaUkolu, match="Neplatné číslo úkolu."):
        odstranit_ukol(dtb_priprava,"K")
