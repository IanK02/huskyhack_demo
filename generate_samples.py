import pandas as pd
import io
import numpy as np
from datetime import datetime, timedelta
import os

# -------------------------
# Function to generate one large CSV per person
# -------------------------
def generate_large_person_csv(name, age):
    np.random.seed(hash(name) % 2**32)  # reproducibility per person

    # Personal info
    personal_info = pd.DataFrame({
        "Field": [
            "Name", "Age", "Monthly_Income", "Monthly_Expenses", "Primary_Bank", 
            "Credit_Cards", "Loans", "Memberships", "Insurance_Policies"
        ],
        "Value": [
            name, age, np.random.randint(4000, 12000), np.random.randint(2000, 9000),
            np.random.choice(["Chase", "Bank of America", "Wells Fargo", "Citi", "Capital One"]),
            ", ".join(np.random.choice(["Chase Sapphire", "Amex Blue", "Discover", "CapitalOne Venture", "Citi Double Cash"], size=3, replace=False)),
            ", ".join(np.random.choice(["Car Loan", "Student Loan", "Mortgage", "Personal Loan"], size=2, replace=False)),
            ", ".join(np.random.choice(["Gym", "Netflix", "Spotify", "Amazon Prime", "Airline Club", "Costco"], size=4, replace=False)),
            ", ".join(np.random.choice(["Health", "Auto", "Home", "Life"], size=2, replace=False))
        ]
    })

    # Bank transactions (150 entries)
    start_date = datetime(2025,1,1)
    transactions = pd.DataFrame({
        "Date": [start_date + timedelta(days=i) for i in range(150)],
        "Description": np.random.choice(
            ["Grocery", "Restaurant", "Utilities", "Online Shopping", "Gas", "Subscription", "Rent", "Travel", "Coffee", "Electronics", "Medical", "Insurance", "Gym"], 
            size=150),
        "Amount": np.round(np.random.uniform(5,2000, size=150),2),
        "Category": np.random.choice(
            ["Food", "Bills", "Shopping", "Transport", "Housing", "Entertainment", "Travel", "Health", "Subscriptions", "Insurance"], 
            size=150)
    })

    # Investment portfolio (30 assets)
    investments = pd.DataFrame({
        "Investment_Type": np.random.choice(["Stock", "ETF", "Bond", "Crypto", "Mutual Fund", "REIT"], size=30),
        "Ticker": [f"TICK{i}" for i in range(30)],
        "Shares": np.round(np.random.uniform(1,200, size=30),2),
        "Value_USD": np.round(np.random.uniform(100,10000, size=30),2),
        "Annual_Return": np.round(np.random.uniform(2,20, size=30),2)
    })

    # Benefits / rewards (20 entries)
    benefits = pd.DataFrame({
        "Benefit": np.random.choice(
            ["Airline Miles", "Cashback", "Gym Discount", "Streaming Service", "Hotel Points", "Fuel Discount", "Retail Coupons", "Travel Vouchers", "Dining Discounts", "Membership Perks"], 
            size=20),
        "Provider": np.random.choice(["Chase", "Amex", "Bank of America", "Netflix", "Marriott", "Shell", "Amazon"], size=20),
        "Estimated_Savings_USD": np.round(np.random.uniform(10,500, size=20),2),
        "Frequency": np.random.choice(["Monthly", "Yearly"], size=20)
    })

    # Combine into a single CSV-like string
    csv_buffer = io.StringIO()
    csv_buffer.write("# Personal Info\n")
    personal_info.to_csv(csv_buffer, index=False)
    csv_buffer.write("\n# Bank Transactions\n")
    transactions.to_csv(csv_buffer, index=False)
    csv_buffer.write("\n# Investment Portfolio\n")
    investments.to_csv(csv_buffer, index=False)
    csv_buffer.write("\n# Benefits / Rewards\n")
    benefits.to_csv(csv_buffer, index=False)

    return csv_buffer.getvalue()


# -------------------------
# Generate and save 3 sample CSVs
# -------------------------
output_folder = "sample_csvs"
os.makedirs(output_folder, exist_ok=True)

people = [("Alice Johnson", 30), ("Bob Smith", 42), ("Carol Lee", 28)]

for name, age in people:
    csv_data = generate_large_person_csv(name, age)
    file_path = os.path.join(output_folder, f"{name.replace(' ','_').lower()}_profile.csv")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(csv_data)
    print(f"Generated CSV for {name} -> {file_path}")

print("✅ All sample CSV files generated!")
