import sqlite3
import os
import config

DB_PATH = os.path.join("data","expenses.db")

def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    #query is a variable that will connect to sql
    query = """
    create table if not exists expenses(
    id integer primary key autoincrement,
    amount real not null,
    category text not null,
    description text,
    date text not null
);
"""
    budgets_query = """
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            amount REAL NOT NULL
        );
        """

    with connect() as conn:
        #create cursor obj, sends commands to db
        cursor = conn.cursor()
        cursor.execute(query)
        cursor.execute(budgets_query)
        conn.commit()

def get_all_budgets() -> dict:
    """ Fetches all categories and their assigned budgets as a clean dictionary. """
    query = "SELECT category, amount FROM budgets;"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        # Converts [( 'Food', 300.00 ), ( 'Transport', 150.00 )] into { 'Food': 300.00, ... }
        return {row[0]: row[1] for row in rows}


def set_budget(category: str, amount: float):
    """ Inserts or updates a budget allocation threshold for a category. """
    # INSERT OR REPLACE handles updating an existing row if the category already exists
    query = "INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?);"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (category, amount))
        conn.commit()

def add_expense(amount: float, category: str, description: str, date: str):
    query = """
    insert into expenses (amount, category, description, date)
    values (?,?,?,?);
"""
# ? tells the database to treat that input strictly as harmless text, never as executable code
    with connect() as conn:
        cursor = conn.cursor()
        # Using placeholder tuples (?) protects your application from SQL Injection attacks.
        cursor.execute(query, (amount,category,description,date))
        conn.commit()

def get_all_expenses():
    """ Fetches all expenses from the database, sorted from newest to oldest. """
    query = "SELECT id, amount, category, description, date FROM expenses ORDER BY date DESC"
    
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows # Using a 'with' block auto-closes the connection safely!
    
def delete_expense(expense_id: int)->bool:
    #return true if row was del, false if id not found
    query = "delete from expenses where id = ?;"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (expense_id,))
        conn.commit()
        # rowcount returns how many rows were affected by the query
        return cursor.rowcount > 0
    
def get_expenses_by_month(year: str, month: str):
    query = "Select id, amount, category, description, date from expenses where date like ?;"
    target_date = f"{year}-{month}%"

    with connect() as conn:
        cursor=conn.cursor()
        cursor.execute(query,(target_date,))
        return cursor.fetchall()
    
# At the bottom of database.py
# At the bottom of database.py
if __name__ == "__main__":
    print("Initializing database tables...")
    create_tables()
    
    print("Seeding baseline database budgets...")
    # Calculate a balanced split default budget per category (4000 / 7 categories ≈ 571)
    default_split = round(config.TOTAL_MONTHLY_BUDGET / len(config.CATEGORIES), 2)
    
    # 💡 LOOP THROUGH THE LIST: Since config.CATEGORIES is a list, we loop over it directly
    for category_name in config.CATEGORIES:
        set_budget(category_name, default_split)
    
    print("Default baseline allocations seeded successfully!")
    print("Current Budgets in DB:", get_all_budgets())