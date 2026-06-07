from database import get_expenses_by_month

def generate_monthly_report(user_id, year: str, month: str) -> dict:
        
    raw_data= get_expenses_by_month(user_id, year,month)

    if not raw_data:
        return {}

    total_spent = 0.0
    category_totals = {}
    biggest_expense = {"amount":0.0,"category":"None","description":""}

    for row in raw_data:
        _,amount,category,description,_=row

        total_spent+=amount

        if category in category_totals:
            category_totals[category]+=amount
        else:
            category_totals[category]=amount

        # larget expense
        if amount>biggest_expense["amount"]:
            biggest_expense["amount"] = amount
            biggest_expense["category"] = category
            biggest_expense["description"] = description if description else "-"

    return {
        "total_spent": round(total_spent,2),
        "category_totals": category_totals,
        "biggest_expense": biggest_expense,
        "transaction_count":len(raw_data)
    }

