import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Digital Maturity Assessment", layout="wide")

# Title and Intro
st.title("📊 Digital Maturity Assessment (DMA)")
st.markdown("Assess your organization's digital readiness across **People**, **Process**, **Technology**, and **Data** dimensions using a 1–5 maturity scale.")

# Maturity scale dictionary
maturity_scale = {
    1: "Initial",
    2: "Developing",
    3: "Established",
    4: "Advanced",
    5: "Leading"
}

# Structure of the assessment
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

# Collecting scores
dimension_scores = {}
st.markdown("---")

for dimension, components in assessment_structure.items():
    st.header(f"📂 {dimension}")
    with st.expander(f"Rate each component in the **{dimension}** dimension"):
        scores = []
        for comp in components:
            score = st.slider(
                f"{comp} ({maturity_scale[1]} to {maturity_scale[5]})",
                1, 5, 3, key=f"{dimension}_{comp}"
            )
            st.write(f"➡️ Selected: **{score} - {maturity_scale[score]}**")
            scores.append(score)
        avg_score = round(sum(scores) / len(scores), 1)
        dimension_scores[dimension] = avg_score
        st.success(f"**{dimension} Average Score:** {avg_score} ({maturity_scale[round(avg_score)]})")

# Summary
st.markdown("---")
st.subheader("📈 Summary of Scores by Dimension")

score_df = pd.DataFrame({
    "Dimension": list(dimension_scores.keys()),
    "Average Score": list(dimension_scores.values()),
    "Maturity Level": [maturity_scale[round(score)] for score in dimension_scores.values()]
})
st.dataframe(score_df, use_container_width=True)

# Overall Score
overall_score = round(sum(dimension_scores.values()) / len(dimension_scores), 1)
st.markdown(f"### 🏁 **Overall Digital Maturity Score:** {overall_score} ({maturity_scale[round(overall_score)]})")

# Radar Chart
st.subheader("📊 Digital Maturity Radar Chart")

def plot_radar(scores_dict):
    labels = list(scores_dict.keys())
    values = list(scores_dict.values())
    values += values[:1]  # close the circle

    angles = np.linspace(0, 2 * np.pi, len(labels) + 1, endpoint=True)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, 'o-', linewidth=2, label='Maturity Score')
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels)
    ax.set_ylim(0, 5)
    ax.set_yticks(range(1, 6))
    ax.set_title('Digital Maturity Assessment Radar', fontsize=16)
    ax.grid(True)
    return fig

fig = plot_radar(dimension_scores)
st.pyplot(fig)

# PDF Generation
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
    label="📥 Download PDF",
    data=pdf_buffer,
    file_name="digital_maturity_assessment_report.pdf",
    mime="application/pdf"
)
