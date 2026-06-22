import sqlite3
import os
import config

DB_PATH = os.path.join("data","expenses.db")

def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    
    users_query = """
    create table if not exists users (
        id integer primary key autoincrement,
        username text not null unique,
        email text not null unique,
        password_hash text not null
    );
"""

    expenses_query = """
    create table if not exists expenses(
        id integer primary key autoincrement,
        user_id integer not null,
        amount real not null,
        category text not null,
        description text,
        date text not null,
        foreign key (user_id) references users (id)
);
"""
    budgets_query = """
    CREATE TABLE IF NOT EXISTS budgets (
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        PRIMARY KEY (user_id, category),
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """

    categories_query = """
    create table if not exists categories(
        id integer primary key autoincrement,
        category text not null,
        user_id integer not null,
        unique(user_id, category)
    ); """
    
    friendship_query = """
    create table if not exists friendships(
            id integer primary key autoincrement,
            user_id integer not null,
            friend_id integer not null,
            status text check(status in ('pending','accepted','rejected')),
            created_at text default current_timestamp,
            foreign key (user_id) references users(id),
            foreign key (friend_id) references users(id)
        );
    """
    shared_expenses_query = """
    create table if not exists shared_expenses(
        id integer primary key autoincrement,
        paid_by integer not null,
        amount real,
        description text,
        category text,
        date text not null,
        FOREIGN KEY (paid_by) REFERENCES users (id)
    );  
"""

    expense_split_query = """
    create table if not exists expense_splits(
        id integer primary key autoincrement,
        shared_expense_id integer not null,
        user_id integer not null, 
        amount_owed real,
        settled integer check(settled in (1,0)),
        FOREIGN KEY (shared_expense_id) REFERENCES shared_expenses (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
"""


    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(users_query)
        cursor.execute(expenses_query)
        cursor.execute(budgets_query)
        cursor.execute(categories_query)
        cursor.execute(friendship_query)
        cursor.execute(shared_expenses_query)
        cursor.execute(expense_split_query)
    conn.commit()

def add_user(username, email, password_hash) -> bool:
    """ Inserts a new user. Expects a pre-hashed password string. """
    query = "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?);"
    try:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username, email, password_hash))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # Returns False if username or email is already taken
        return False
    
def get_user_by_email(email):
    """ Finds a user profile during login validation. """
    query = "SELECT id, username, email, password_hash FROM users WHERE email = ?;"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (email,))
        return cursor.fetchone() # Returns tuple or None

def get_user_by_id(user_id):
    """ Flask-Login automatically invokes this to keep track of active sessions. """
    query = "SELECT id, username, email, password_hash FROM users WHERE id = ?;"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        return cursor.fetchone()

def get_all_budgets(user_id: int) -> dict:
    """ Fetches all categories and their assigned budgets as a clean dictionary. """
    query = "SELECT category, amount FROM budgets where user_id=?;"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query,(user_id,))
        rows = cursor.fetchall()
        # Converts [( 'Food', 300.00 ), ( 'Transport', 150.00 )] into { 'Food': 300.00, ... }
        return {row[0]: row[1] for row in rows}


def set_budget(user_id: int, category: str, amount: float):
    """ Inserts or updates a budget allocation threshold for a specific user. """
    query = "INSERT OR REPLACE INTO budgets (user_id, category, amount) VALUES (?, ?, ?);"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id, category, amount))
        conn.commit()

def add_expense(user_id: int,amount: float, category: str, description: str, date: str):
    query = """
    insert into expenses (user_id, amount, category, description, date)
    values (?,?,?,?,?);
"""
# ? tells the database to treat that input strictly as harmless text, never as executable code
    with connect() as conn:
        cursor = conn.cursor()
        # Using placeholder tuples (?) protects your application from SQL Injection attacks.
        cursor.execute(query, (user_id,amount,category,description,date))
        conn.commit()

def get_all_expenses(user_id: int):
    """ Fetches all expenses from a specific user, sorted from newest to oldest. """
    query = "SELECT id, amount, category, description, date FROM expenses WHERE user_id = ? ORDER BY date DESC"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
        
def delete_expense(expense_id: int,user_id: int)->bool:
    #return true if row was del, false if id not found
    query = "delete from expenses where id = ? and user_id=?;"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (expense_id,user_id))
        conn.commit()
        # rowcount returns how many rows were affected by the query
        return cursor.rowcount > 0
    
def get_expenses_by_month(user_id:int,year: str, month: str):
    query = "Select id, amount, category, description, date from expenses where user_id = ? and date like ?;"
    target_date = f"{year}-{month}%"

    with connect() as conn:
        cursor=conn.cursor()
        cursor.execute(query,(user_id,target_date))
        return cursor.fetchall()

def add_category(user_id, category):
    query = "insert into categories(user_id,category) values (?,?)"

    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query,(user_id,category))
        conn.commit()
        return cursor.rowcount > 0
    
def get_user_categories(user_id):
    query = "SELECT category FROM categories WHERE user_id = ?"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        return [row[0] for row in rows]

def delete_category(user_id, category_name):
    with connect() as conn:
        conn.execute("DELETE FROM categories WHERE user_id = ? AND category = ?", (user_id, category_name))
        conn.commit()
    
def send_friend_request(user_id, friend_email):
    query = "select id from users where email = ?"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (friend_email,))
        result = cursor.fetchone()

        if result is None:
            return "Sent"

        friend_id = result[0]

        if friend_id == user_id:
            return "Self"

        try:
            cursor.execute(
                "insert into friendships (user_id, friend_id, status) values (?, ?, 'pending')",
                (user_id, friend_id)
            )
            conn.commit()
            return "Sent"
        except sqlite3.IntegrityError:
            return "Sent"
       
def get_pending_requests(user_id):
    with connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT friendships.id, users.username 
                FROM friendships 
                JOIN users ON friendships.user_id = users.id 
                WHERE friendships.friend_id = ? AND friendships.status = 'pending'
            """, (user_id,))
            return cursor.fetchall()
        except sqlite3.Error:
            return []
        

def accept_friend_request(friendship_id,current_user_id):
    with connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "update friendships set status = 'accepted' where id = ?",
                (friendship_id,current_user_id)
            )
            conn.commit()
            return "Success"
        except sqlite3.Error:
            return "Failed to accept request."

def get_friends_list(user_id):
    with connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT users.id, users.username 
                FROM users 
                JOIN friendships ON (friendships.user_id = users.id OR friendships.friend_id = users.id)
                WHERE (friendships.user_id = ? OR friendships.friend_id = ?) 
                AND friendships.status = 'accepted'
                AND users.id != ?
                """,(user_id,user_id,user_id))
            result = cursor.fetchall()
            return result
        except sqlite3.Error:
            return []
        
def reject_friend_request(friendship_id, current_user_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE friendships SET status = 'rejected' WHERE id = ? AND friend_id = ?",
            (friendship_id, current_user_id)
        )
        conn.commit()
        return cursor.rowcount > 0

if __name__ == "__main__":
    print("Initializing database tables...")
    create_tables()
    
    TEST_USER_ID = 1
    print(f"Seeding baseline database budgets for Test User ID: {TEST_USER_ID}...")
    
    default_split = round(config.TOTAL_MONTHLY_BUDGET / len(config.CATEGORIES), 2)
    
    for category_name in config.CATEGORIES:
        set_budget(TEST_USER_ID, category_name, default_split)
    
    print("Default baseline allocations seeded successfully!")
    print("Current Budgets in DB for Test User:", get_all_budgets(TEST_USER_ID))