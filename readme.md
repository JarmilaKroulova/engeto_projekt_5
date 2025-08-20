# Správce úkolů (MySQL + Python)

Tento repozitář obsahuje jednoduchou aplikaci pro správu úkolů pomocí databáze MySQL a skriptů v jazyce Python. Projekt zahrnuje také sadu automatizovaných testů pomocí knihovny `pytest`.

---

## 📁 Obsah repozitáře

- `main.py` – Hlavní skript pro práci s databází. Obsahuje funkce pro:
  - přidání úkolu
  - zobrazení úkolů
  - aktualizaci stavu úkolu
  - odstranění úkolu

- `test_main.py` – Automatizované testy k funkcím z `main.py`.
  - Pro každou funkci jsou připraveny dva testy: jeden pozitivní a jeden negativní.
  - Testy využívají `pytest` a pracují s testovací databází, která se po spuštění testů sama vytvoří a smaže.

- `testovaci_plan.txt` – Přehledný testovací plán s popisem testovacích případů (TC1–TC8), pokrytí CRUD funkcí.

- `testovaci_report.txt` – Report s výsledky posledního běhu testů.

- `requirements.txt` – Přehled potřebných knihoven pro spuštění projektu.

---

## ⚙️ Nastavení

Před spuštěním skriptů je nutné **doplnit platné heslo k databázi MySQL** ve funkci `pripojeni_db()` nebo v části, kde se navazuje připojení:

```python
pripojeni = mysql.connector.connect(
    host="localhost",
    user="root",
    password="VAŠE_HESLO",  # ← zde doplňte vaše heslo
    database="..."
)

✅ Spuštění testů

V terminálu zadejte:

pytest test_main.py


Testy:

vytvoří vlastní testovací databázi a tabulku,
provedou CRUD operace,
ověří správnou funkčnost jednotlivých částí,
a po dokončení databázi smažou.
📌 Nemění žádná ostrá data – testování je bezpečné.

🧰 Požadavky

Python 3.x
Lokální MySQL server


📦 Potřebné knihovny:

mysql-connector-python
pytest
Lze nainstalovat pomocí:

pip install -r requirements.txt


