# 🎓 AI Educational Content Generator

A two-agent AI pipeline that generates and reviews educational content for any grade and topic.

## 🔗 Live Demo
[Click here to open the app]([https://ai-edu-agents-jvfbxpyzdbcueebvpd72ax.streamlit.app/])

## 🤖 Agent Pipeline
User Input (Grade + Topic)
↓
Generator Agent
(Explanation + MCQs)
↓
Reviewer Agent
(Pass / Fail + Feedback)
↓
Pass → Show Result
Fail → Refiner (Generator + Feedback) → Show Refined Result

## 🧠 Agents

### 1. Generator Agent
- **Input:** Grade (1-12), Topic (string)
- **Output:** Explanation + 3 MCQs in JSON
- **Model:** Llama 3.3 70B via Groq API

### 2. Reviewer Agent
- **Input:** Generated content JSON + Grade
- **Output:** `pass/fail` status + feedback list
- **Checks:** Age appropriateness, conceptual correctness, clarity

### 3. Refiner (Inline)
- Triggered only when Reviewer returns `fail`
- Re-runs Generator with feedback embedded
- Limited to one refinement pass

## 🗂️ Project Structure
ai-edu-agents/
├── app.py              # Main Streamlit app + all agents
├── requirements.txt    # Dependencies
└── .streamlit/
└── secrets.toml    # API key (not uploaded to GitHub)

## ⚙️ Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/(https://github.com/akankshi-03)/ai-edu-agents.git
cd ai-edu-agents
```

### 2. Install dependencies
```bash
pip install streamlit groq
```

### 3. Add API key
Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```
Get your free API key at [console.groq.com](https://console.groq.com)

### 4. Run
```bash
streamlit run app.py
```
Open `http://localhost:8501`

## 📦 Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | UI Framework |
| Groq API | LLM inference (free) |
| Llama 3.3 70B | Language Model |
| Python | Backend logic |

## 📊 Output Format

### Generator Output
```json
{
  "explanation": "...",
  "mcqs": [
    {
      "question": "...",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "A"
    }
  ]
}
```

### Reviewer Output
```json
{
  "status": "pass | fail",
  "feedback": ["issue 1", "issue 2"]
}
```

Banane ke baad terminal mein:
bashgit add README.md
git commit -m "add README"
git push
