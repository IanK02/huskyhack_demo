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

def generate_sample_csvs():
    sample_csvs = {}

    # Sample 1: Basic financial profile
    df1 = pd.DataFrame({
        "Name": ["Alice"],
        "Age": [30],
        "Monthly_Income": [5000],
        "Monthly_Expenses": [3200],
        "Credit_Card_Reward": ["2% cashback"],
        "Bank_Accounts": ["Bank of America, Chase"],
        "Investments": ["Vanguard ETF, Robinhood Stocks"],
        "Membership_Benefits": ["Gym membership discount, Airline miles"]
    })
    csv_buffer1 = io.StringIO()
    df1.to_csv(csv_buffer1, index=False)
    sample_csvs["Basic Financial Profile"] = csv_buffer1.getvalue()

    # Sample 2: More transactions
    df2 = pd.DataFrame({
        "Date": pd.date_range(start="2025-01-01", periods=10, freq='D'),
        "Description": ["Grocery", "Restaurant", "Utilities", "Online Shopping", "Coffee", "Gas", "Subscription", "Rent", "Gym", "Travel"],
        "Amount": [120, 45, 150, 200, 5, 60, 15, 1200, 40, 500],
        "Category": ["Food","Food","Bills","Shopping","Food","Transport","Subscription","Housing","Health","Travel"]
    })
    csv_buffer2 = io.StringIO()
    df2.to_csv(csv_buffer2, index=False)
    sample_csvs["Recent Transactions"] = csv_buffer2.getvalue()

    # Sample 3: Investment portfolio
    df3 = pd.DataFrame({
        "Investment_Type": ["Stocks", "ETF", "Bonds", "Crypto"],
        "Ticker": ["AAPL", "VOO", "US10Y", "BTC"],
        "Shares": [10, 20, 5, 0.1],
        "Value_USD": [1500, 6000, 500, 3000],
        "Annual_Return": ["8%", "7%", "3%", "12%"]
    })
    csv_buffer3 = io.StringIO()
    df3.to_csv(csv_buffer3, index=False)
    sample_csvs["Investment Portfolio"] = csv_buffer3.getvalue()

    # Sample 4: Benefits / rewards
    df4 = pd.DataFrame({
        "Benefit": ["Airline Miles", "Cashback", "Gym Discount", "Streaming Service", "Hotel Points"],
        "Provider": ["Chase Sapphire", "Amex Blue", "Local Gym", "Netflix", "Marriott"],
        "Estimated_Savings_USD": [300, 50, 20, 15, 200],
        "Frequency": ["Yearly", "Monthly", "Monthly", "Monthly", "Yearly"]
    })
    csv_buffer4 = io.StringIO()
    df4.to_csv(csv_buffer4, index=False)
    sample_csvs["Available Benefits"] = csv_buffer4.getvalue()

    return sample_csvs

sample_csvs = generate_sample_csvs()

# -------------------------------
# Display download buttons
# -------------------------------
st.header("📥 Download Sample CSVs to Try Out")

for name, csv_data in sample_csvs.items():
    st.download_button(
        label=f"Download '{name}'",
        data=csv_data.encode("utf-8"),
        file_name=f"{name.replace(' ','_').lower()}.csv",
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
