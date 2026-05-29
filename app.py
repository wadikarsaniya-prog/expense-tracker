import database
import reports
import utils
import config

from flask import Flask, render_template, request, redirect
# __name__:  tells Flask where your project files, folders, and templates are located relative to this script
app = Flask(__name__)
database.create_tables()

@app.route('/')
def home(): #contains logic that executes only when user visits specific path /
    
    return render_template('index.html')
#view
@app.route('/expenses')
def view_expenses():
    real_expenses = database.get_all_expenses()

    return render_template('view_expenses.html', expenses=real_expenses)

#delete
@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    database.delete_expense(expense_id)
    return redirect('/expenses')

#add
@app.route('/add',methods=['GET','POST'])
def add_expenses():
    if request.method == 'GET':
        return render_template('add_expense.html',categories=config.CATEGORIES, error=None)

    if request.method=='POST':
        amount_input = request.form.get('amount')
        category_input = request.form.get('category')
        description_input = request.form.get('description')
        date_input = request.form.get('date')

        is_valid, validated_amount = utils.validate_amount(amount_input)

        if is_valid:
            database.add_expense(validated_amount, category_input,description_input,date_input)
            return redirect('/expenses')
        
        else: 
            error_msg = "Invalid amount string. Please enter a valid positive decimal number."
            return render_template(
                'add_expense.html', 
                categories=config.categories, 
                error=error_msg
            )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
