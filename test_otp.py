import database

TEST_USER_ID = 1

print("--- Testing OTP Save and Verify ---")

print("\n1. Saving OTP code '123456' for user 1...")
database.save_otp(TEST_USER_ID, '123456')
print("Saved.")

print("\n2. Verifying with CORRECT code '123456'...")
result = database.verify_otp(TEST_USER_ID, '123456')
print(f"Result: {result} (should be True)")

print("\n3. Saving a NEW OTP code '654321' for user 1...")
database.save_otp(TEST_USER_ID, '654321')
print("Saved.")

print("\n4. Verifying with WRONG code '000000'...")
result = database.verify_otp(TEST_USER_ID, '000000')
print(f"Result: {result} (should be False)")

print("\n5. Verifying with CORRECT code '654321'...")
result = database.verify_otp(TEST_USER_ID, '654321')
print(f"Result: {result} (should be True)")

print("\n--- Test Complete ---")