import sqlite3

conn = sqlite3.connect('data/expenses.db')

for table in ['users', 'otp_codes']:
    result = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table,)
    ).fetchone()
    print(f"--- {table} ---")
    print(result[0] if result else "TABLE DOES NOT EXIST")
    print()