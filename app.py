from flask import Flask, render_template
# __name__:  tells Flask where your project files, folders, and templates are located relative to this script
app = Flask(__name__)

@app.route('/')
def home(): #contains logic that executes only when user visits specific path /
    mock_expenses = [
        {"id": 1, "amount": 45.50, "category": "Food", "description": "Grocery run", "date": "2026-05-25"},
        {"id": 2, "amount": 12.00, "category": "Transport", "description": "Bus fare", "date": "2026-05-26"},
        {"id": 3, "amount": 120.00, "category": "Utilities", "description": "Internet Bill", "date": "2026-05-27"},
        {"id": 4, "amount": 8.50, "category": "Entertainment", "description": "Movie rental", "date": "2026-05-28"}
    ]

    total_spent = sum(item["amount"]for item in mock_expenses)

    return render_template(
        'index.html',
        expenses=mock_expenses,
        total=total_spent,
        month='May'
    )
if __name__ == '__main__':
    app.run(debug=True, port=5000)
