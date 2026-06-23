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
        name text not null,
        id integer primary key autoincrement,
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

def add_user(name, email, password_hash) -> bool:
    query = "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?);"
    try:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, email, password_hash))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # Returns False if email is already taken
        return False
    
def get_user_by_email(email):
    """ Finds a user profile during login validation. """
    query = "SELECT id,name, email, password_hash FROM users WHERE email = ?;"
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (email,))
        return cursor.fetchone() # Returns tuple or None

def get_user_by_id(user_id):
    """ Flask-Login automatically invokes this to keep track of active sessions. """
    query = "SELECT id, name, email, password_hash FROM users WHERE id = ?;"
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
                SELECT friendships.id
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
                "update friendships set status = 'accepted' where id = ? and friend_id = ?",
                (friendship_id,current_user_id)
            )
            conn.commit()
            return "Success" if cursor.rowcount > 0 else "Request not found or not yours to accept."
        except sqlite3.Error:
            return "Failed to accept request."

def get_friends_list(user_id):
    with connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT users.id 
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

def create_shared_expenses(paid_by, amount, description, category, date, split_by):
    all_participants = split_by + [paid_by]
    num_people = len(all_participants)
    share_per_person = round(amount / num_people, 2)

    with connect() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "insert into shared_expenses (paid_by, amount, description, category, date) values (?, ?, ?, ?, ?)",
            (paid_by, amount, description, category, date)
        )
        shared_expense_id = cursor.lastrowid

        for user_id in all_participants:
            settled = 1 if user_id == paid_by else 0
            cursor.execute(
                "insert into expense_splits (shared_expense_id, user_id, amount_owed, settled) values (?, ?, ?, ?)",
                (shared_expense_id, user_id, share_per_person, settled)
            )
        
        conn.commit()
        return shared_expense_id

def get_balances(user_id):

    query = """
        SELECT 
            CASE WHEN se.paid_by = ? THEN es.user_id ELSE se.paid_by END as other_user_id,
            CASE WHEN se.paid_by = ? THEN es.amount_owed ELSE -es.amount_owed END as balance_contribution
        FROM expense_splits es
        JOIN shared_expenses se ON es.shared_expense_id = se.id
        WHERE es.settled = 0
        AND (se.paid_by = ? OR es.user_id = ?)
        AND es.user_id != se.paid_by
    """
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id, user_id, user_id, user_id))
        rows = cursor.fetchall()

    balances = {}
    for other_user_id, contribution in rows:
        balances[other_user_id] = balances.get(other_user_id, 0) + contribution

    result = []
    for other_user_id, net in balances.items():
        username_row = get_user_by_id(other_user_id)
        username = username_row[1] if username_row else "Unknown"
        result.append((other_user_id, username, round(net, 2)))

    return result

def settle_up (user_id, friend_id):
    query = """
        update expense_splits
        set settled = 1
        where settled = 0
        and user_id in (?,?)
        and shared_expense_id in (
            select if from shared_expenses where paid_by in (?,?)
        )
"""

    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id, friend_id, user_id, friend_id))
        conn.commit()
        return cursor.rowcount


if __name__ == "__main__":
    print("Testing shared expense creation...")
    new_id = create_shared_expenses(
        paid_by=1, 
        amount=600, 
        description="Test Dinner", 
        category="Food", 
        date="2026-06-22", 
        split_by=[2]
    )
    print(f"Created shared expense ID: {new_id}")

    print("\nBalances for user 1:")
    print(get_balances(1))

    print("\nBalances for user 2:")
    print(get_balances(2))