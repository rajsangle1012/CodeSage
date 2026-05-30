# 🧠 CodeSage — AI-Powered Code Review Assistant

> [!NOTE]
> ### 📄 Looking for the Project Overview?
> Because **[Overview.pdf](Overview.pdf)** is a high-resolution file (~12.4 MB), GitHub's web preview might fail to render it directly in the browser. 
> 
> **[👉 Click here to download and view the PDF directly](https://github.com/rajsangle1012/CodeSage/blob/main/Overview.pdf?raw=true)**

---

**CodeSage** is a futuristic, high-tech AI-powered code auditing and refactoring workspace built with Streamlit, Supabase, and Groq. It lets you analyze, refactor, generate documentation, patch security vulnerabilities, and sync changes directly to your GitHub repositories in real-time.

---

## ⚡ Core Features

- 🧠 **AI Architect**: Direct code quality scoring and side-by-side smart refactoring using LLMs.
- 🛡️ **Vanguard Security Scan**: Identify syntax flaws, hardcoded secrets, and patch logical security exploits instantly.
- 🐙 **GitHub Uplink**: Connect directly to your repos, explore files, run AI transformations, and push commits in one click.
- 📝 **Doc Generator**: Inject professional docstrings and clear comments into complex modules.
- 🌐 **AI Polyglot**: Instantly translate code between Python, JavaScript, TypeScript, SQL, Go, Java, and C++.
- 🚀 **Task Solver**: Create checklists and let the AI resolve individual coding tasks automatically.
- 📊 **Cyber-Nexus Dashboard**: Track audits, daily streak counts, threat severity levels, and code quality timelines via charts.
- 🏆 **Arena Leaderboard**: Climb the coding rank tiers based on completed code quality audits.

---

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (with cyber-nexus custom HTML/CSS styling)
- **Database & Auth**: [Supabase](https://supabase.com/) (PostgreSQL & GitHub OAuth)
- **Inference Engine**: [Groq API](https://groq.com/) (utilizing high-speed `llama-3.3-70b-versatile` model)
- **Charts & Visuals**: Altair & Pandas

---

## 🚀 Setup & Installation

### 1. Prerequisites
- Python 3.10+
- A Supabase account
- A GitHub developer account (for OAuth login)
- A Groq API key

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a `.env` file in the root directory:
```env
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_KEY="your-anon-public-key"
GROQ_API_KEY="gsk_your-groq-key"
```

### 4. Database Schema Setup
Run the following SQL in your **Supabase SQL Editor** to create the required tables:
```sql
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY,
  username TEXT,
  full_name TEXT,
  avatar_url TEXT,
  lifetime_reviews INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  quality_score INT,
  issues_found INT,
  language TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_stats (
  user_id UUID PRIMARY KEY REFERENCES profiles(id),
  reviews_done INT DEFAULT 0,
  active_projects INT DEFAULT 0,
  quality_score INT DEFAULT 80,
  last_updated TIMESTAMP DEFAULT NOW()
);
```

### 5. Running CodeSage
```bash
python -m streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser to begin!
