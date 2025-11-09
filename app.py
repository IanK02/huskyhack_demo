import streamlit as st
import pandas as pd
import io
from datetime import datetime
from google import genai

# -------------------------------
# Streamlit page setup
# -------------------------------
st.set_page_config(page_title="Financial AI Advisor", layout="centered")

# Hide default Streamlit UI and set background image
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Make container scrollable */
.block-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start; /* change from center */
    text-align: center;
    padding-top: 40px;
}

/* Background image */
body {
    background-image: url('background.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

/* Recommendation boxes */
.recommendation-box {
    background-color: rgba(255,255,255,0.9);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    text-align: left;
    width: 90%;
    max-width: 700px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.recommendation-title {
    font-size: 18px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 5px;
}
.recommendation-desc {
    font-size: 15px;
    color: #374151;
}
</style>
""", unsafe_allow_html=True)

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
