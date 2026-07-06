# 🚀 BlindHire AI – Unbiased Resume Analyzer

## 🧠 Overview

BlindHire AI is a simple yet powerful AI-based web application that analyzes resumes and demonstrates how bias can affect hiring decisions. It compares **biased vs fair scoring** to highlight the importance of ethical AI.

---

## 🎯 Problem Statement

Many AI hiring systems unintentionally introduce bias based on:

* Gender
* College background
* Personal identity

This leads to **unfair hiring decisions**.

---

## 💡 Solution

BlindHire AI:

* Analyzes resumes
* Extracts skills and experience
* Calculates:

  * ⚠️ **Biased Score** (includes gender & college influence)
  * ✅ **Fair Score** (removes identity factors)
* Detects and highlights bias

---

## ⚙️ Features

* 📄 Resume PDF upload
* 🧾 Text extraction
* 🧠 Skill detection (Python, SQL, Excel, etc.)
* ⏳ Experience extraction using regex
* ⚖️ Bias vs Fair score comparison
* 📊 Visualization with charts
* 💡 Skill recommendations for improvement

---

## 🏗️ How It Works

1. Upload resume
2. Extract text
3. Identify skills & experience
4. Calculate:

   * Biased Score
   * Fair Score
5. Compare results
6. Display bias detection and chart

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **pdfplumber**
* **pandas**
* **matplotlib**
* **regex (re)**

---

## 📊 Scoring Logic

### Biased Score:

```
(score = skills × 10) + (experience × 15)
+10 if Tier1 college
+5 if Male
```

### Fair Score:

```
(score = skills × 10) + (experience × 15)
```

---

## ⚠️ Bias Detection

* If difference > 5 → ⚠️ Bias Detected
* Else → ✅ Fair Decision

---

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/your-username/blindhire-ai.git
cd blindhire-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run App

```bash
streamlit run app.py
```

---

## 📸 Demo

*Add screenshots of your app here*

---

## 🌍 Impact

* Promotes **fair hiring practices**
* Raises awareness about **AI bias**
* Encourages **ethical AI development**

---

## 🔮 Future Scope

* Advanced NLP for better resume parsing
* Integration with job portals
* Real AI fairness algorithms
* Multi-resume comparison

---

## 🏁 Conclusion

BlindHire AI shows that:

> AI is powerful, but it must also be fair.

---

## 🤝 Contributing

Feel free to fork this repo and improve the project!

---

## 📜 License

This project is open-source and available under the MIT License.
