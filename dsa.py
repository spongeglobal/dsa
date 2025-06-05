import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import os
from datetime import datetime

# ------------------ THEME STYLES ------------------
st.set_page_config(page_title="Digital Maturity Assessment", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #01497c;
    }
    .stSlider > div {
        background-color: #f0f4f8;
        padding: 0.5rem 1rem;
        border-radius: 10px;
    }
    .stDownloadButton button {
        background-color: #01497c !important;
        color: white !important;
    }
    .footer {
        text-align: center;
        font-size: 0.9rem;
        color: #888888;
        margin-top: 4rem;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ TITLE AND INTRO ------------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Streamlit_logo_mark.svg/1200px-Streamlit_logo_mark.svg.png", width=80)
with col2:
    st.title("📊 Digital Maturity Assessment (DMA)")

st.markdown("Assess your organization's digital readiness across **People**, **Process**, **Technology**, and **Data** using a 1–5 maturity scale.")

maturity_scale = {
    1: "Initial",
    2: "Developing",
    3: "Established",
    4: "Advanced",
    5: "Leading"
}

assessment_structure = {
    "People": [
        "Leadership awareness and commitment",
        "Digital skills and competencies",
        "Change readiness and innovation mindset",
        "Training and development programs",
        "Digital champions/ambassadors",
        "Organizational alignment with digital goals"
    ],
    "Process": [
        "Degree of process digitization",
        "Process standardization and documentation",
        "Agility and responsiveness",
        "Integration of digital tools in workflows",
        "Use of KPIs and metrics",
        "Governance and compliance"
    ],
    "Technology": [
        "IT infrastructure maturity",
        "Adoption of digital tools (ERP, CRM, etc.)",
        "System integration and interoperability",
        "Cybersecurity readiness",
        "Cloud adoption and flexibility",
        "Availability of AI/analytics tools"
    ],
    "Data": [
        "Data availability and accessibility",
        "Data quality and consistency",
        "Data-driven decision making",
        "Data governance policies",
        "Reporting and analytics capabilities",
        "AI/ML readiness"
    ]
}

# ------------------ DIMENSIONAL RATINGS ------------------
dimension_scores = {}
st.markdown("---")
st.header("🧮 Rate Your Digital Maturity")

for dimension, components in assessment_structure.items():
    st.subheader(f"📂 {dimension}")
    with st.expander(f"Rate components in the **{dimension}** dimension", expanded=False):
        scores = []
        cols = st.columns(2)
        for i, comp in enumerate(components):
            with cols[i % 2]:
                score = st.slider(
                    f"{comp} ({maturity_scale[1]}–{maturity_scale[5]})",
                    1, 5, 3, key=f"{dimension}_{comp}"
                )
                st.caption(f"➡️ Selected: **{score} - {maturity_scale[score]}**")
                scores.append(score)
        avg_score = round(sum(scores) / len(scores), 1)
        dimension_scores[dimension] = avg_score
        st.success(f"**{dimension} Average Score:** {avg_score} ({maturity_scale[round(avg_score)]})")

# ------------------ SCORE SUMMARY ------------------
st.markdown("---")
st.subheader("📈 Summary of Scores by Dimension")

score_df = pd.DataFrame({
    "Dimension": list(dimension_scores.keys()),
    "Average Score": list(dimension_scores.values()),
    "Maturity Level": [maturity_scale[round(score)] for score in dimension_scores.values()]
})

st.table(score_df.set_index("Dimension"))

overall_score = round(sum(dimension_scores.values()) / len(dimension_scores), 1)
st.markdown(f"### 🏁 **Overall Digital Maturity Score:** {overall_score} ({maturity_scale[round(overall_score)]})")

# ------------------ RADAR CHART ------------------
st.subheader("📊 Digital Maturity Radar Chart")

def plot_radar(scores_dict):
    labels = list(scores_dict.keys())
    values = list(scores_dict.values())
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels) + 1)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color="#01497c", alpha=0.25)
    ax.plot(angles, values, 'o-', color="#01497c", linewidth=2)
    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels)
    ax.set_ylim(0, 5)
    ax.set_yticks(range(1, 6))
    ax.set_title("Digital Maturity Radar", fontsize=16, color="#01497c")
    ax.grid(True)
    return fig

st.pyplot(plot_radar(dimension_scores))

# ------------------ PDF GENERATION ------------------
st.subheader("📄 Download Assessment Report")

def generate_pdf(score_df, overall_score, maturity_scale):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Digital Maturity Assessment Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=11)
    pdf.cell(60, 10, "Dimension", border=1)
    pdf.cell(40, 10, "Avg Score", border=1)
    pdf.cell(60, 10, "Maturity Level", border=1)
    pdf.ln()

    pdf.set_font("Arial", size=11)
    for _, row in score_df.iterrows():
        pdf.cell(60, 10, str(row["Dimension"]), border=1)
        pdf.cell(40, 10, str(row["Average Score"]), border=1)
        pdf.cell(60, 10, str(row["Maturity Level"]), border=1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, f"Overall Score: {overall_score} ({maturity_scale[round(overall_score)]})", ln=True)

    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

pdf_buffer = generate_pdf(score_df, overall_score, maturity_scale)

st.download_button(
    label="📥 Download PDF Report",
    data=pdf_buffer,
    file_name="digital_maturity_assessment_report.pdf",
    mime="application/pdf"
)

# ------------------ CSV LOGGING ------------------
st.subheader("📇 Save Your Results")

user_name = st.text_input("Enter your name or email to log your assessment (optional):")

if st.button("💾 Save Assessment to History"):
    history_file = "dma_history.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_row = {
        "Timestamp": now,
        "User": user_name if user_name else "Anonymous",
        **{f"{dim} Score": score for dim, score in dimension_scores.items()},
        "Overall Score": overall_score
    }

    new_row_df = pd.DataFrame([data_row])

    if os.path.exists(history_file):
        new_row_df.to_csv(history_file, mode='a', header=False, index=False)
    else:
        new_row_df.to_csv(history_file, mode='w', header=True, index=False)

    st.success("✅ Your assessment has been saved to history.")

# ------------------ VIEW HISTORY ------------------
with st.expander("📜 View Past Assessments"):
    if os.path.exists("dma_history.csv"):
        history_df = pd.read_csv("dma_history.csv")
        st.dataframe(history_df, use_container_width=True)

        st.download_button(
            label="📥 Download Full History",
            data=history_df.to_csv(index=False),
            file_name="digital_maturity_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No assessments saved yet.")

# ------------------ FOOTER ------------------
st.markdown('<div class="footer">© 2025 Your Company Name | All rights reserved.</div>', unsafe_allow_html=True)
