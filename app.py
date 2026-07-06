"""
BlindHire AI - Unbiased Resume Analyzer
-----------------------------------------
A Streamlit app that extracts skills & experience from a resume PDF,
then compares a "Biased Score" (which factors in gender & college tier)
against a "Fair Score" (which strips identity factors out) to
demonstrate how bias can creep into automated hiring systems.

Run with:
    streamlit run app.py
"""

import re
import io

import streamlit as st
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Config / reference data
# ---------------------------------------------------------------------------

st.set_page_config(page_title="BlindHire AI - Unbiased Resume Analyzer", page_icon="🧠", layout="wide")

SKILL_KEYWORDS = [
    "python", "java", "c++", "c#", "javascript", "sql", "excel", "power bi",
    "tableau", "machine learning", "deep learning", "nlp", "pandas", "numpy",
    "streamlit", "django", "flask", "react", "node.js", "aws", "azure",
    "gcp", "docker", "kubernetes", "git", "html", "css", "data analysis",
    "data visualization", "statistics", "communication", "leadership",
]

# Sample "Tier 1" college keywords - used only to DEMONSTRATE how a biased
# model might unfairly reward pedigree. This is for educational purposes.
TIER1_COLLEGES = [
    "iit", "indian institute of technology", "nit", "bits pilani",
    "mit", "stanford", "harvard", "iim", "carnegie mellon", "berkeley",
]

MALE_PRONOUNS = [" he ", " him ", " his ", "mr."]
FEMALE_PRONOUNS = [" she ", " her ", " hers ", "mrs.", "ms."]

BIAS_THRESHOLD = 5  # difference above which we flag bias


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract raw text from an uploaded PDF resume."""
    text = ""
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_skills(text: str, skill_list=SKILL_KEYWORDS) -> list:
    """Return the list of known skills found in the resume text."""
    text_lower = text.lower()
    found = [skill for skill in skill_list if skill.lower() in text_lower]
    return sorted(set(found))


def extract_experience(text: str) -> float:
    """
    Extract years of experience using regex.
    Looks for patterns like '3 years', '5+ yrs', '2.5 years of experience'.
    Returns the maximum value found (assumed to be the total experience).
    """
    pattern = r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)"
    matches = re.findall(pattern, text.lower())
    if not matches:
        return 0.0
    return max(float(m) for m in matches)


def detect_tier1_college(text: str) -> bool:
    """Naively check whether the resume mentions a 'Tier 1' college."""
    text_lower = text.lower()
    return any(college in text_lower for college in TIER1_COLLEGES)


def detect_gender_hint(text: str) -> str:
    """
    Very naive pronoun-based heuristic used ONLY to illustrate how a biased
    system might infer gender from a resume and use it improperly.
    Returns 'Male', 'Female', or 'Unknown'.
    NOTE: this is a deliberately simplistic demo heuristic, not a reliable
    real-world signal, and should never be used for actual hiring decisions.
    """
    padded = f" {text.lower()} "
    male_hits = sum(padded.count(p) for p in MALE_PRONOUNS)
    female_hits = sum(padded.count(p) for p in FEMALE_PRONOUNS)
    if male_hits > female_hits:
        return "Male"
    if female_hits > male_hits:
        return "Female"
    return "Unknown"


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------

def calculate_fair_score(num_skills: int, experience_years: float) -> float:
    """Fair Score = skills x10 + experience x15 (identity-blind)."""
    return (num_skills * 10) + (experience_years * 15)


def calculate_biased_score(num_skills: int, experience_years: float,
                            is_tier1: bool, gender: str) -> float:
    """Biased Score = Fair Score + Tier1 bonus + Male bonus."""
    score = calculate_fair_score(num_skills, experience_years)
    if is_tier1:
        score += 10
    if gender == "Male":
        score += 5
    return score


def detect_bias(biased_score: float, fair_score: float) -> bool:
    """Flag bias if the two scores differ by more than the threshold."""
    return abs(biased_score - fair_score) > BIAS_THRESHOLD


def recommend_skills(found_skills: list, skill_list=SKILL_KEYWORDS, top_n=5) -> list:
    """Suggest a handful of in-demand skills missing from the resume."""
    missing = [s for s in skill_list if s not in found_skills]
    return missing[:top_n]


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def main():
    st.title("🧠 BlindHire AI – Unbiased Resume Analyzer")
    st.markdown(
        "Upload a resume to compare a **⚠️ Biased Score** (factors in gender & "
        "college prestige) against a **✅ Fair Score** (skills & experience only), "
        "and see how bias can silently creep into automated hiring."
    )

    with st.sidebar:
        st.header("⚙️ Settings")
        st.caption(
            "Gender and college-tier are demo-only signals used to illustrate "
            "bias. You can override the auto-detected values below."
        )
        bias_threshold = st.slider("Bias detection threshold", 1, 20, BIAS_THRESHOLD)

    uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

    if uploaded_file is None:
        st.info("Upload a PDF resume to get started.")
        return

    with st.spinner("Extracting text from resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if not resume_text.strip():
        st.error("Couldn't extract any text from this PDF. Try a different file.")
        return

    with st.expander("🔍 View extracted resume text"):
        st.text(resume_text)

    # --- Extraction ---
    skills_found = extract_skills(resume_text)
    experience_years = extract_experience(resume_text)
    auto_tier1 = detect_tier1_college(resume_text)
    auto_gender = detect_gender_hint(resume_text)

    st.subheader("🧾 Extracted Information")
    col1, col2, col3 = st.columns(3)
    col1.metric("Skills Found", len(skills_found))
    col2.metric("Experience (yrs)", experience_years)
    col3.metric("Tier 1 College Detected", "Yes" if auto_tier1 else "No")

    st.write("**Detected skills:**", ", ".join(skills_found) if skills_found else "None found")

    st.markdown("---")
    st.subheader("🧍 Demo Bias Inputs (override auto-detection)")
    demo_col1, demo_col2 = st.columns(2)
    with demo_col1:
        gender = st.selectbox(
            "Gender signal used by the biased model",
            options=["Male", "Female", "Unknown"],
            index=["Male", "Female", "Unknown"].index(auto_gender),
        )
    with demo_col2:
        is_tier1 = st.checkbox("Treat as Tier 1 college", value=auto_tier1)

    # --- Scoring ---
    fair_score = calculate_fair_score(len(skills_found), experience_years)
    biased_score = calculate_biased_score(len(skills_found), experience_years, is_tier1, gender)
    bias_detected = abs(biased_score - fair_score) > bias_threshold

    st.markdown("---")
    st.subheader("📊 Score Comparison")

    score_col1, score_col2, score_col3 = st.columns(3)
    score_col1.metric("⚠️ Biased Score", f"{biased_score:.1f}")
    score_col2.metric("✅ Fair Score", f"{fair_score:.1f}")
    score_col3.metric("Difference", f"{biased_score - fair_score:.1f}")

    if bias_detected:
        st.error("⚠️ Bias Detected — this candidate's score is being inflated by "
                  "identity factors that have nothing to do with their skills or experience.")
    else:
        st.success("✅ Fair Decision — no significant bias detected between the two scores.")

    # --- Chart ---
    fig, ax = plt.subplots(figsize=(5, 4))
    labels = ["Biased Score", "Fair Score"]
    values = [biased_score, fair_score]
    colors = ["#e74c3c", "#2ecc71"]
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel("Score")
    ax.set_title("Biased vs Fair Score")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5, f"{val:.1f}",
                 ha="center", va="bottom")
    st.pyplot(fig)

    # --- Recommendations ---
    st.markdown("---")
    st.subheader("💡 Skill Recommendations")
    suggestions = recommend_skills(skills_found)
    if suggestions:
        st.write("Consider adding these in-demand skills to strengthen the resume:")
        st.write(", ".join(suggestions))
    else:
        st.write("This resume already covers most of the tracked in-demand skills!")

    # --- Summary table ---
    st.markdown("---")
    st.subheader("📋 Summary")
    summary_df = pd.DataFrame({
        "Metric": ["Skills Found", "Experience (yrs)", "Tier 1 College",
                   "Gender Signal", "Biased Score", "Fair Score", "Bias Detected"],
        "Value": [len(skills_found), experience_years, is_tier1,
                  gender, round(biased_score, 1), round(fair_score, 1), bias_detected],
    })
    st.table(summary_df)


if __name__ == "__main__":
    main()
