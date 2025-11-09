import streamlit as st
import pandas as pd
import io
from google import genai

# -------------------------------
# Streamlit page setup
# -------------------------------
st.set_page_config(page_title="Financial AI Advisor", layout="centered")

# -------------------------------
# Main app title
# -------------------------------
st.title(" SoundAdvice Recommendation Model", width="stretch")  # main title at the top
st.markdown("---")  # optional horizontal line for separatio

# -------------------------------
# Download buttons for existing CSVs
# -------------------------------
st.header("📥 Download Sample Financial Profiles")
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
client = genai.Client()  # GEMINI_API_KEY must be set in environment

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
# Streamlit UI: Logo and uploader
# -------------------------------
left_co, cent_co, right_co = st.columns(3)
with cent_co:
    st.image("logo.png", width=400)  # centered logo

uploaded_file = st.file_uploader("Upload financial profile CSV", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        csv_text = uploaded_file.read().decode("utf-8")

        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully.")

        # Dummy button for demo purposes
        if st.button("Send CSV to app"):
            st.info("CSV sent! (Demo button, no actual action)")

        # Generate AI recommendations
        with st.spinner("🤖 Generating personalized recommendations..."):
            recommendations_text = get_gemini_recommendations(csv_text)

        if recommendations_text.startswith("❌"):
            st.error(recommendations_text)
        else:
            st.markdown("## 💡 Personalized Recommendations")

            # Parse Gemini text into recommendations
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
                    <div style="
                        background-color:#f9fafb;
                        border:1px solid #e5e7eb;
                        border-radius:12px;
                        padding:20px;
                        margin-bottom:15px;
                        text-align:left;
                        box-shadow:0 2px 4px rgba(0,0,0,0.05);
                    ">
                        <div style="font-size:18px;font-weight:700;color:#1f2937;margin-bottom:5px;">{title}</div>
                        <div style="font-size:15px;color:#374151;">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
