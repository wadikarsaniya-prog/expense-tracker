print("File is running...")
from datetime import datetime 
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def validate_amount(input_string):
    try:
        value = float(input_string)
        if value > 0:
            return value
        else:
            return None
    except ValueError:
        return None

def format_currency(amount):
    return f"₹{amount:.2f}"

if __name__ == "__main__":
    print("Testing utils.py...\n")

    print("Date:", get_current_date())

    print("\nValid amount:", validate_amount("100"))
    print("Invalid amount (text):", validate_amount("abc"))
    print("Invalid amount (negative):", validate_amount("-50"))

    print("\nFormatted currency:", format_currency(149.5))