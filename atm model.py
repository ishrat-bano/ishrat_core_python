import os

BALANCE_FILE = "balance.txt"
PIN = "1234"


def read_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as file:
            return float(file.read())
    else:
        
        return 10000.0

def write_balance(balance):
    with open(BALANCE_FILE, "w") as file:
        file.write(str(balance))


entered_pin = input("Enter your 4-digit PIN: ")

if entered_pin == PIN:
    balance = read_balance()
    
    while True:
        print("\n===== ATM Menu =====")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            print(f"Your current balance is ₹{balance:.2f}")

        elif choice == "2":
            amount = float(input("Enter amount to deposit: ₹"))
            if amount > 0:
                balance += amount
                write_balance(balance)
                print(f"₹{amount:.2f} deposited successfully!")
                print(f"Updated balance: ₹{balance:.2f}")
            else:
                print("Invalid deposit amount.")

        elif choice == "3":
            amount = float(input("Enter amount to withdraw: ₹"))
            if 0 < amount <= balance:
                balance -= amount
                write_balance(balance)
                print(f"₹{amount:.2f} withdrawn successfully!")
                print(f"Remaining balance: ₹{balance:.2f}")
            elif amount > balance:
                print("Insufficient balance.")
            else:
                print("Invalid withdrawal amount.")

        elif choice == "4":
            print("Thank you for using the ATM. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")
else:
    print("Access Denied.")
