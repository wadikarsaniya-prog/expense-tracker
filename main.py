from database import create_tables, add_expense, get_all_expenses, delete_expense
from utils import get_current_date, validate_amount
from config import CATEGORIES, CURRENCY_SYMBOL
from reports import generate_monthly_report
from charts import generate_spending_pie_chart
def show_menu():
    print("\n" + "="*30)
    print("   Personal Expense Tracker   ")
    print("="*30)
    print("1. ➕ Add New Expense")
    print("2. 📋 View All Expenses")
    print("3. 🗑️ Delete An Expense")
    print("4. 📊 View Monthly Report")
    print("5. 🎨 Generate Spending Chart")
    print("6. ❌ Exit")
    print("="*30)

def handle_add_expense():
    print("\n------Add New Expense------")

    amount_input = input(f"Enter amount ({CURRENCY_SYMBOL}): ")
    amount = validate_amount(amount_input)
    if amount is None:
        print("❌ Expense creation cancelled due to invalid amount.")
        return
    
    #selection from category
    print("\n Select a category")
    for index, cat in enumerate(CATEGORIES, start=1):
        print(f"  {index}. {cat}")

    try:
        cat_choice=int(input(f"Choose number (1-{len(CATEGORIES)}): ").strip())
        if 1 <= cat_choice <= len(CATEGORIES):
            category = CATEGORIES[cat_choice-1]
        else:
            print("⚠ Out of range selection. Defaulting to 'Other'.")
            category = "Other"
    except ValueError:
        print("⚠ Invalid typing. Defaulting to 'Other'.")
        category = "Other"

    # Description
    description = input("Enter description (optional)").strip()
    date_today = get_current_date()

    add_expense(amount,category,description,date_today)
    print(f"Successfully added: {CURRENCY_SYMBOL}{amount:.2f} under {category}!")

def handle_view_expenses():
    print("-----All Expenses-----")
    expenses = get_all_expenses()

    if not expenses:
        print("No expenses recorded yet")
        return
    
    print(f"{'ID':<5} | {'Date':<12} | {'Category':<15} | {'Amount':<10} | {'Description'}")
    print("-" * 70)

    for row in expenses:
        exp_id, amount, category, description, date = row
        desc_display = description if description else "-"
        print(f"{exp_id:<5} | {date:<12} | {category:<15} | {CURRENCY_SYMBOL}{amount:<10.2f} | {desc_display}")

def handle_delete_expense():
    print("\n---Delete Expense---")
    handle_view_expenses()

    id_input = input("\nEnter id of expense to delete").strip()
    try:
        expense_id = int(id_input)
        was_deleted = delete_expense(expense_id)
        if was_deleted:
            print(f"🗑️ Expense ID {expense_id} has been completely erased.")
        else:
            print(f"❌ Could not find an expense matching ID {expense_id}.")
    except ValueError:
        print("❌ Invalid entry. ID must be a whole number index.")

def handle_monthly_report():
    print("\n---View Monthly Report---")
    year = input("Enter year (YYYY): ").strip()
    month = input("Enter month (MM): ").strip()

    if len(year) != 4 or len(month)!= 2:
        print("❌ Invalid format. Please use YYYY for year and MM for month.")
        return
    
    report = generate_monthly_report(year,month)

    if not report:
        print(f"No spending data found for {year}-{month}.")
        return
    
    print("\n" + "*"*35)
    print(f"      REPORT FOR {year}-{month}      ")
    print("*"*35)
    print(f"💰 Total Amount Spent: {CURRENCY_SYMBOL}{report['total_spent']:.2f}")
    print(f"🔢 Total Transactions: {report['transaction_count']}")
    
    print("\n📂 Spending Breakdown by Category:")
    for cat, total in report['category_totals'].items():
        print(f"  • {cat:<12}: {CURRENCY_SYMBOL}{total:.2f}")
        
    print("\n🏆 Single Largest Expense:")
    biggest = report['biggest_expense']
    print(f"  {CURRENCY_SYMBOL}{biggest['amount']:.2f} in '{biggest['category']}' ({biggest['description']})")
    print("*"*35)

def handle_generate_chart():
    print("\n---Generate Spending Chart---")
    year = input("Enter Year (YYYY, e.g., 2026): ").strip()
    month = input("Enter Month (MM, e.g., 05): ").strip()
    
    if len(year) != 4 or len(month) != 2:
        print("❌ Invalid format. Use YYYY and MM.")
        return
    
    print("Generating your visualization...")
    saved_path = generate_spending_pie_chart(year,month)

    if saved_path:
        print(f"📊 Success! Your chart has been generated and saved to:")
        print(f"   -> {saved_path}")
    else:
        print(f"❌ No data found for {year}-{month} to visualize.")

def main():
    create_tables()

    while True:
        show_menu()
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            handle_add_expense()
        elif choice == "2":
            handle_view_expenses()
        elif choice == "3":
            handle_delete_expense()
        elif choice == "4":
            handle_monthly_report()
        elif choice == "5":
            handle_generate_chart()
        elif choice == "6":
            print("\nThank you for tracking your expenses. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select from options 1-4.")

if __name__ == "__main__":
    main()
    
