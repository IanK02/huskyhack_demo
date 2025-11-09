import streamlit as st
import pandas as pd
import io
from datetime import datetime
from google import genai
import os

# -------------------------------
# Streamlit page setup
# -------------------------------
st.set_page_config(page_title="Financial AI Advisor", layout="centered")

# -------------------------------
# Streamlit UI: download buttons for existing CSVs
# -------------------------------
st.header("📥 Download Sample Financial Profiles")

# Map of people to file paths (these CSV files should already exist in your project folder)

sample_files = {
    "Alice Johnson": "sample_csvs/alice_johnson_profile.csv",
    "Bob Smith": "sample_csvs/bob_smith_profile.csv",
    "Carol Lee": "sample_csvs/carol_lee_profile.csv"
}

for person, file_path in sample_files.items():
    try:
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"Download sample CSV for {person}",
                data=f,
                file_name=file_path.split("/")[-1],
                mime="text/csv"
            )
    except FileNotFoundError:
        st.warning(f"CSV file for {person} not found at {file_path}")
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
        csv_text = uploaded_file.read().decode("utf-8")

        # Split by sections
        sections = csv_text.split("\n# ")
        df_personal, df_transactions, df_investments, df_benefits = None, None, None, None

        for section in sections:
            section = section.strip()
            if section.startswith("Personal Info"):
                df_personal = pd.read_csv(io.StringIO(section.replace("Personal Info\n", "")))
            elif section.startswith("Bank Transactions"):
                df_transactions = pd.read_csv(io.StringIO(section.replace("Bank Transactions\n", "")))
            elif section.startswith("Investment Portfolio"):
                df_investments = pd.read_csv(io.StringIO(section.replace("Investment Portfolio\n", "")))
            elif section.startswith("Benefits / Rewards"):
                df_benefits = pd.read_csv(io.StringIO(section.replace("Benefits / Rewards\n", "")))

        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully.")
        st.markdown("### Personal Info")
        st.dataframe(df_personal)
        st.markdown("### Bank Transactions")
        st.dataframe(df_transactions.head(10))  # preview only first 10
        st.markdown("### Investment Portfolio")
        st.dataframe(df_investments)
        st.markdown("### Benefits / Rewards")
        st.dataframe(df_benefits)

        # Here you can still send the entire CSV text to Gemini for recommendations
        # ...
        
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
