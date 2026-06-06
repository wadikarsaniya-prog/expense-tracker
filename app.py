import database
import reports
import utils
import config
import time
from datetime  import datetime
import charts 
from flask import Flask, render_template, request, redirect
import os
from dotenv import load_dotenv
from flask_login import LoginManager, current_user, login_required

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-fallback-key')

database.create_tables()

login_manager = LoginManager()
login_manager.init_app(app) #connects to flask app
login_manager.login_view = 'auth.login'#if sm1 tries to access page wo login send them to login

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

@login_manager.user_loader
def load_user(user_id):
    user_data = database.get_user_by_id(user_id)
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    return None

@app.route('/')
@login_required
def home():
    from datetime import datetime
    year_str = datetime.today().strftime('%Y')
    month_str = datetime.today().strftime('%m')
    current_month_name = datetime.today().strftime('%B')
    
    report_data = reports.generate_monthly_report(year_str, month_str)
    
    # 💡 ONE MASTERS TOTAL: Pull the single 4000.00 budget directly from config
    global_budget = config.TOTAL_MONTHLY_BUDGET
    total_spent = 0.0
    
    if report_data:
        total_spent = report_data.get('total_spent', 0.0)
        
    # Calculate one overall spending percentage for the entire month
    global_percentage = (total_spent / global_budget) * 100 if global_budget > 0 else 0
    
    summary_data = {
        'total_spent': total_spent,
        'budget': global_budget,
        'percentage': round(global_percentage, 1)
    }
        
    recent_expenses = database.get_all_expenses(current_user.id)[:5]
    return render_template('index.html', summary=summary_data, recent=recent_expenses, month=current_month_name)

@app.route('/expenses')
@login_required
def view_expenses():
    real_expenses = database.get_all_expenses()
    return render_template('view_expenses.html', expenses=real_expenses)


@app.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    try:
        database.delete_expense(expense_id, current_user.id)
    except Exception:
        pass  # Gracefully ignore invalid IDs or connection dropouts silently
    return redirect('/expenses')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    error_msg = None

    if request.method == 'POST':
        amount_input = request.form.get('amount')
        category_input = request.form.get('category')
        description_input = request.form.get('description')
        date_input = request.form.get('date')

        is_valid, validated_amount = utils.validate_amount(amount_input)

        if is_valid:
            database.add_expense(current_user.id, validated_amount, category_input, description_input, date_input)
            return redirect('/expenses')
        else: 
            error_msg = "Invalid amount string. Please enter a valid positive decimal number."
            
    return render_template('add_expense.html', 
                         categories=config.CATEGORIES, 
                         error=error_msg)

@app.route('/analytics')
@login_required
def view_analytics():
    selected_month = request.args.get('month')

    if not selected_month:
        selected_month = datetime.today().strftime('%Y-%m')

    try:
        year_str, month_str = selected_month.split('-')

    except ValueError:
        year_str = datetime.today().strftime('%Y')
        month_str = datetime.today().strftime('%m')
        selected_month = f"{year_str}-{month_str}"

    pie_file = charts.generate_spending_pie_chart(year_str, month_str)
    bar_file = charts.generate_spending_bar_chart(year_str, month_str)
    trend_file = charts.generate_spending_trend_chart(year_str, month_str)

    charts_dir = "static/charts"

    pie_path = f"charts/{pie_file}" if pie_file and os.path.exists(os.path.join(charts_dir, pie_file)) else None
    bar_path = f"charts/{bar_file}" if bar_file and os.path.exists(os.path.join(charts_dir, bar_file)) else None
    trend_path = f"charts/{trend_file}" if trend_file and os.path.exists(os.path.join(charts_dir, trend_file)) else None

    return render_template(
        'charts.html',
        selected_month=selected_month,
        pie_path=pie_path,
        bar_path=bar_path,
        trend_path=trend_path
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)