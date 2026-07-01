import database
import reports
import utils
import config
import time
from datetime  import datetime
import charts 
from flask import Flask, render_template, request, redirect, flash
import os
from dotenv import load_dotenv
from flask_login import LoginManager, current_user, login_required
from models import User
from flask import jsonify
from friends import friends_bp
from authlib.integrations.flask_client import OAuth

load_dotenv()
database.create_tables()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-fallback-key')
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

app.register_blueprint(friends_bp)


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
    year_str = datetime.today().strftime('%Y')
    month_str = datetime.today().strftime('%m')
    current_month_name = datetime.today().strftime('%B')
    
    report_data = reports.generate_monthly_report(current_user.id,year_str, month_str)
    
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
    real_expenses = database.get_all_expenses(current_user.id)
    return render_template('view_expenses.html', expenses=real_expenses)


@app.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    try:
        database.delete_expense(expense_id, current_user.id)
    except Exception as e:
        app.logger.error(f"Failed to delete expense {expense_id}: {e}")
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
    user_cats = database.get_user_categories(current_user.id)
    return render_template('add_expense.html', 
                         categories=user_cats, 
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

    pie_file = charts.generate_spending_pie_chart(current_user.id,year_str, month_str)
    bar_file = charts.generate_spending_bar_chart(current_user.id,year_str, month_str)
    trend_file = charts.generate_spending_trend_chart(current_user.id,year_str, month_str)

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
@app.route('/api/add-category', methods=['POST'])
@login_required
def api_add_category():
    category_input = request.form.get('category')
    
    if category_input and category_input.strip():
        cleaned_category = category_input.strip()
        database.add_category(current_user.id, cleaned_category)
        return jsonify({"status": "success", "category": cleaned_category}), 200
        
    return jsonify({"status": "error", "message": "Category cannot be empty"}), 400

@app.route('/api/delete-category', methods=['POST'])
@login_required
def api_delete_category():
    category_name = request.form.get('category_name')
    if category_name:
        database.delete_category(current_user.id, category_name)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "No category specified"}), 400        

@app.route('/split-expense', methods = ['GET','POST'])
@login_required
def split_expense():
    error_msg = None

    if request.method == 'POST':
        amount_input = request.form.get('amount')
        description_input = request.form.get('description')
        category_input = request.form.get('category')
        date_input = request.form.get('date')
        selected_friend_ids = request.form.getlist('friends')
        split_mode = request.form.get('split_mode', 'equal')

        is_valid, validated_amount = utils.validate_amount(amount_input)

        if not is_valid:
            error_msg = "Invalid amount. Please enter a valid positive number."
        elif not selected_friend_ids:
            error_msg = "Please select at least one friend to split with."
        else:
            friend_ids_int = [int(fid) for fid in selected_friend_ids]
            all_participants = friend_ids_int + [current_user.id]

            if split_mode == 'equal':
                share = round(validated_amount / len(all_participants), 2)
                split_details = [(uid, share) for uid in all_participants]
            else:
                # Custom split - read each person's specific amount from the form
                split_details = []
                total_entered = 0.0
                for uid in all_participants:
                    custom_amount = request.form.get(f'custom_amount_{uid}')
                    is_valid_custom, validated_custom = utils.validate_amount(custom_amount)
                    if not is_valid_custom:
                        error_msg = "Please enter valid amounts for everyone."
                        break
                    split_details.append((uid, validated_custom))
                    total_entered += validated_custom

            if not error_msg and round(total_entered, 2) != round(validated_amount, 2):
                    error_msg = f"Custom amounts (₹{total_entered:.2f}) must add up to the total (₹{validated_amount:.2f})."

            if not error_msg:
                database.create_shared_expenses(
                    paid_by=current_user.id,
                    amount=validated_amount,
                    description=description_input,
                    category=category_input,
                    date=date_input,
                    split_details=split_details
                )
                return redirect('/balances')
            
    friends_list = database.get_friends_list(current_user.id)
    user_cats = database.get_user_categories(current_user.id)

    return render_template('split_expense.html', 
                         friends=friends_list, 
                         categories=user_cats, 
                         error=error_msg)

@app.route('/balances')
@login_required
def view_balances():
    balances = database.get_balances(current_user.id)
    return render_template('balances.html', balances=balances)

@app.route('/settle/<int:friend_id>', methods=['POST'])
@login_required
def settle(friend_id):
    rows_updated = database.settle_up(current_user.id, friend_id)
    if rows_updated > 0:
        flash("Settled up successfully!", "success")
    else:
        flash("Nothing to settle.", "info")
    return redirect('/balances')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)