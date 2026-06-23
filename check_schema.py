import sqlite3

conn = sqlite3.connect('data/expenses.db')

tables_to_check = ['expense_splits', 'shared_expenses', 'friendships', 'users', 'expenses', 'categories']

for table in tables_to_check:
    result = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", 
        (table,)
    ).fetchone()
    print(f"--- {table} ---")
    print(result[0] if result else "TABLE DOES NOT EXIST")
    print()