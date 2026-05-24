# database.py
import sqlite3
import os 

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
    with connect() as conn:
        #create cursor obj, sends commands to db
        cursor = conn.cursor()
        cursor.execute(query)
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
    query = """select id, amount, category, description,
    date from expenses
    order by date desc;""" 
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
if __name__ == "__main__":
    print("Initializing database and testing insertion...")
    create_tables()
    add_expense(250.00, "Food", "Dinner with team", "2026-05-17")
    print("Current data in DB:", get_all_expenses())