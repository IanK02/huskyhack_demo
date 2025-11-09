import streamlit as st
import pandas as pd
import io
from datetime import datetime
from google import genai

# -------------------------------
# Streamlit page setup
# -------------------------------
st.set_page_config(page_title="Financial AI Advisor", layout="centered")

# -------------------------------
# Sample CSV generation
# -------------------------------

import pandas as pd
import io
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

# -------------------------------
# Function to generate one rich sample CSV per person
# -------------------------------
def generate_person_csv(name, age):
    np.random.seed(hash(name) % 2**32)  # reproducibility per person

    # Personal info
    personal_info = pd.DataFrame({
        "Field": ["Name", "Age", "Monthly_Income", "Monthly_Expenses", "Primary_Bank", "Credit_Cards", "Memberships"],
        "Value": [name, age, np.random.randint(4000,10000), np.random.randint(2000,8000),
                  np.random.choice(["Chase", "Bank of America", "Wells Fargo", "Citi"]),
                  ", ".join(np.random.choice(["Chase Sapphire", "Amex Blue", "Discover", "CapitalOne Venture"], size=2, replace=False)),
                  ", ".join(np.random.choice(["Gym", "Airline Club", "Netflix", "Spotify", "Amazon Prime"], size=3, replace=False))
                 ]
    })

    # Bank transactions (50+ entries)
    start_date = datetime(2025,1,1)
    transactions = pd.DataFrame({
        "Date": [start_date + timedelta(days=i) for i in range(50)],
        "Description": np.random.choice(["Grocery", "Restaurant", "Utilities", "Online Shopping", "Gas", "Subscription", "Rent", "Travel", "Coffee"], size=50),
        "Amount": np.round(np.random.uniform(5,1500, size=50),2),
        "Category": np.random.choice(["Food", "Bills", "Shopping", "Transport", "Housing", "Entertainment", "Travel"], size=50)
    })

    # Investment portfolio (10+ assets)
    investments = pd.DataFrame({
        "Investment_Type": np.random.choice(["Stock", "ETF", "Bond", "Crypto"], size=10),
        "Ticker": [f"TICK{i}" for i in range(10)],
        "Shares": np.round(np.random.uniform(1,100, size=10),2),
        "Value_USD": np.round(np.random.uniform(100,5000, size=10),2),
        "Annual_Return": np.round(np.random.uniform(2,15, size=10),2)
    })

    # Benefits / rewards (10+ entries)
    benefits = pd.DataFrame({
        "Benefit": np.random.choice(["Airline Miles", "Cashback", "Gym Discount", "Streaming Service", "Hotel Points", "Fuel Discount", "Retail Coupons"], size=10),
        "Provider": np.random.choice(["Chase", "Amex", "Bank of America", "Netflix", "Marriott", "Shell", "Amazon"], size=10),
        "Estimated_Savings_USD": np.round(np.random.uniform(10,500, size=10),2),
        "Frequency": np.random.choice(["Monthly", "Yearly"], size=10)
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

# -------------------------------
# Generate 3 sample CSVs
# -------------------------------
sample_csvs = {
    "Alice Johnson": generate_person_csv("Alice Johnson", 30),
    "Bob Smith": generate_person_csv("Bob Smith", 42),
    "Carol Lee": generate_person_csv("Carol Lee", 28)
}

# -------------------------------
# Streamlit UI: download buttons
# -------------------------------
st.header("📥 Download Sample Financial Profiles")
for person, csv_data in sample_csvs.items():
    st.download_button(
        label=f"Download sample CSV for {person}",
        data=csv_data.encode("utf-8"),
        file_name=f"{person.replace(' ','_').lower()}_profile.csv",
        mime="text/csv"
    )
# -------------------------------
# Gemini client setup
# -------------------------------
client = genai.Client()  # GEMINI_API_KEY must be in environment variable

def get_gemini_recommendations(csv_text: str) -> str:
    prompt = f"""
You are a friendly financial assistant.
Given the following CSV describing one person's financial profile, produce 5 actionable recommendations that the person can do immediately to save money or optimize finances.
The recommendations should follow the goal of "helping the user easily discover, organize, and maximize the benefits available to them - whether from financial products, service providers, or everyday memberships.
So give the user quick recommendations of how they could use easily accesible or already available benefits to them to help them save money.

Each recommendation should include:
- Concise title (2-6 words)
- Clear description
- Quantitative estimate of savings (monthly or annual)

Format each recommendation like this:
**Title**
Description of the recommendation and estimated savings.

CSV contents:
{csv_text}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ Gemini API error: {e}"

# -------------------------------
# Streamlit UI
# -------------------------------
left_co, cent_co, right_co = st.columns(3)
with cent_co:
    st.image("logo.png", width=400)  # smaller, centered logo

uploaded_file = st.file_uploader("Upload financial profile CSV", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        csv_bytes = uploaded_file.read()
        csv_text = csv_bytes.decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_text))

        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully.")

        # Dummy button for demo purposes
        if st.button("Send CSV to app"):
            st.info("CSV sent! (Demo button, no actual action)")

        with st.spinner("🤖 Generating personalized recommendations..."):
            recommendations_text = get_gemini_recommendations(csv_text)

        if recommendations_text.startswith("❌"):
            st.error(recommendations_text)
        else:
            st.markdown("## 💡 Personalized Recommendations")

            # Split Gemini text into recommendations
            recs = []
            current_title = None
            current_desc = []

            for line in recommendations_text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("**") and line.endswith("**"):
                    if current_title:
                        recs.append((current_title, " ".join(current_desc)))
                    current_title = line.strip("*")
                    current_desc = []
                else:
                    current_desc.append(line)
            if current_title:
                recs.append((current_title, " ".join(current_desc)))

            # Display recommendations
            for i, (title, desc) in enumerate(recs[:10]):
                st.markdown(f"""
                    <div class="recommendation-box">
                        <div class="recommendation-title">{title}</div>
                        <div class="recommendation-desc">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
