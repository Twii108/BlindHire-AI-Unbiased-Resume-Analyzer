import sys
import json
import re
import pdfplumber

SKILL_KEYWORDS = [
    "python", "java", "c++", "c#", "javascript", "sql", "excel", "power bi",
    "tableau", "machine learning", "deep learning", "nlp", "pandas", "numpy",
    "streamlit", "django", "flask", "react", "node.js", "aws", "azure",
    "gcp", "docker", "kubernetes", "git", "html", "css", "data analysis",
    "data visualization", "statistics", "communication", "leadership",
]

TIER1_COLLEGES = [
    "iit", "indian institute of technology", "nit", "bits pilani",
    "mit", "stanford", "harvard", "iim", "carnegie mellon", "berkeley",
]

MALE_PRONOUNS = [" he ", " him ", " his ", "mr."]
FEMALE_PRONOUNS = [" she ", " her ", " hers ", "mrs.", "ms."]

BIAS_THRESHOLD = 5

def extract_text_from_pdf(file_path) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        pass
    return text

def extract_skills(text: str, skill_list=SKILL_KEYWORDS) -> list:
    text_lower = text.lower()
    found = [skill for skill in skill_list if skill.lower() in text_lower]
    return sorted(set(found))

def extract_experience(text: str) -> float:
    pattern = r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)"
    matches = re.findall(pattern, text.lower())
    if not matches:
        return 0.0
    return max(float(m) for m in matches)

def detect_tier1_college(text: str) -> bool:
    text_lower = text.lower()
    return any(college in text_lower for college in TIER1_COLLEGES)

def detect_gender_hint(text: str) -> str:
    padded = f" {text.lower()} "
    male_hits = sum(padded.count(p) for p in MALE_PRONOUNS)
    female_hits = sum(padded.count(p) for p in FEMALE_PRONOUNS)
    if male_hits > female_hits:
        return "Male"
    if female_hits > male_hits:
        return "Female"
    return "Unknown"

def calculate_fair_score(num_skills: int, experience_years: float) -> float:
    return (num_skills * 10) + (experience_years * 15)

def calculate_biased_score(num_skills: int, experience_years: float, is_tier1: bool, gender: str) -> float:
    score = calculate_fair_score(num_skills, experience_years)
    if is_tier1:
        score += 10
    if gender == "Male":
        score += 5
    return score

def recommend_skills(found_skills: list, skill_list=SKILL_KEYWORDS, top_n=5) -> list:
    missing = [s for s in skill_list if s not in found_skills]
    return missing[:top_n]

def analyze_resume(file_path: str):
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        return {"error": "Could not extract text from PDF."}

    skills_found = extract_skills(text)
    experience_years = extract_experience(text)
    auto_tier1 = detect_tier1_college(text)
    auto_gender = detect_gender_hint(text)

    fair_score = calculate_fair_score(len(skills_found), experience_years)
    biased_score = calculate_biased_score(len(skills_found), experience_years, auto_tier1, auto_gender)
    bias_detected = abs(biased_score - fair_score) > BIAS_THRESHOLD

    recommendations = recommend_skills(skills_found)

    return {
        "text_snippet": text[:500],
        "skills_found": skills_found,
        "experience_years": experience_years,
        "tier1_college": auto_tier1,
        "gender": auto_gender,
        "fair_score": round(fair_score, 1),
        "biased_score": round(biased_score, 1),
        "bias_detected": bias_detected,
        "skill_recommendations": recommendations
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided."}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = analyze_resume(file_path)
    print(json.dumps(result))
