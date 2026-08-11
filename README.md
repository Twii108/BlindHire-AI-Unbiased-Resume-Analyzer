# 🧠 BlindHire AI - Unbiased Resume Analyzer

BlindHire AI is a full-stack web application designed to demonstrate how automated hiring systems (Applicant Tracking Systems) can inadvertently introduce bias into the recruitment process. 

The application analyzes a candidate's uploaded PDF resume and compares a **Fair Score** (based purely on technical skills and experience) against a **Biased Score** (which is artificially inflated by identity proxies like gender and college pedigree).

## ✨ Features
- **PDF Resume Parsing**: Extracts raw text from resumes using Python's `pdfplumber`.
- **Fairness Engine**: Calculates scores based on objective metrics vs. biased heuristics.
- **Modern UI**: A premium, responsive frontend built with React, featuring drag-and-drop uploads, glassmorphism design, and micro-animations.
- **Interactive Dashboards**: Visualizes the score discrepancies using interactive charts (`recharts`).
- **History Tracking**: Saves past resume analysis records into a local MongoDB database.

## 🛠️ Technology Stack
- **Frontend**: React (Vite), CSS3, Lucide Icons, Recharts
- **Backend**: Node.js, Express.js, Multer (for file uploads)
- **AI / Processing Engine**: Python, `pdfplumber`, `pandas`
- **Database**: MongoDB & Mongoose

---

## 🚀 Getting Started

### Prerequisites
Make sure you have the following installed on your machine:
- [Node.js](https://nodejs.org/) (v16+)
- [Python](https://www.python.org/) (3.8+)
- [MongoDB](https://www.mongodb.com/) (Optional, but required if you want to save analysis history)

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd BlindHire
```

### 2. Backend Setup (Node & Python)
Navigate to the backend folder:
```bash
cd backend
```

Install the Node.js dependencies:
```bash
npm install
```

Set up the Python virtual environment and install dependencies:
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install pdfplumber pandas
```

Start the Backend server:
```bash
node index.js
```
The server will run on `http://localhost:5000`. 
*(Note: If MongoDB is not running locally, the server will still work but will skip saving history).*

### 3. Frontend Setup (React)
Open a new terminal and navigate to the frontend folder:
```bash
cd frontend
```

Install the React dependencies:
```bash
npm install
```

Start the Vite development server:
```bash
npm run dev
```
The frontend will run on `http://localhost:5173`.

---

## ⚖️ How the Scoring Works

**✅ Fair Score:**
Evaluates the candidate purely on objective, job-related criteria.
- `+10 points` for every relevant technical skill found (e.g., Python, React, AWS).
- `+15 points` for every year of professional experience detected.

**⚠️ Biased Score:**
Simulates a biased algorithm by taking the Fair Score and adding artificial bonuses for pedigree and demographic proxies.
- `+10 points` if a "Tier 1" university (e.g., IIT, MIT, Stanford) is detected.
- `+5 points` if the resume contains more male pronouns than female pronouns (simulating a model trained on skewed historical hiring data).

*Disclaimer: The demographic and pedigree detection logic in this app uses naive keyword matching. It is built strictly for educational demonstration purposes to highlight algorithmic bias, and should never be used in a real-world hiring environment.*
