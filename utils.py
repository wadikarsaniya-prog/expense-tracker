from datetime import datetime 

def get_current_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def validate_amount(input_string: str):
    try:
        # Clean up any accidental spaces or dollar signs
        cleaned_input = input_string.strip().replace("$", "")
        amount = float(cleaned_input)

        if amount <= 0:
            print("⚠ Amount must be greater than zero.")
            # 💡 RETURN A PAIR: (False, None)
            return False, None
            
        # 💡 RETURN A PAIR: (True, the rounded amount)
        return True, round(amount, 2)
        
    except ValueError:
        print("⚠ Invalid input. Please enter a valid decimal number.")
        # 💡 RETURN A PAIR: (False, None)
        return False, None

if __name__ == "__main__":
    # Test your utilities locally here before moving to main.py
    # Ensures that specific code runs only when the script is executed directly
    print(f"Testing current date: {get_current_date()}")
    print(f"Testing valid amount: {validate_amount(' 150.50 ')}")
    print(f"Testing invalid amount: {validate_amount('abc')}")
