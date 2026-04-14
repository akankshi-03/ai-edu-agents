import streamlit as st
from groq import Groq
import json
import re

# ── CONFIG ──────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ── HELPER ──────────────────────────────────────────────
def call_groq(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a JSON API. Always respond with valid, compact JSON only. No newlines inside string values. No markdown. No extra text."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content

def parse_json(text: str) -> dict:
    # Backticks hatao
    text = re.sub(r"```json|```", "", text).strip()
    # JSON block nikalo
    start = text.find('{')
    end = text.rfind('}') + 1
    text = text[start:end]
    # Saare control characters hatao except newline aur tab
    text = ''.join(ch for ch in text if ord(ch) >= 32 or ch in '\n\t')
    # Newlines strings ke andar se hatao
    text = re.sub(r'(?<="):.*?(?=")', lambda m: m.group().replace('\n', ' ').replace('\r', ''), text)
    return json.loads(text)

# ── AGENT 1 : GENERATOR ─────────────────────────────────
def generator_agent(grade: int, topic: str, feedback: list = None) -> dict:
    feedback_block = ""
    if feedback:
        feedback_block = f"""
Previously a reviewer rejected this content. Fix these issues:
{chr(10).join(f'- {f}' for f in feedback)}
"""
    prompt = f"""
You are an educational content generator.
Generate content for Grade {grade} students on the topic: "{topic}".
{feedback_block}

Return ONLY valid JSON in this exact format:
{{
  "explanation": "2-3 paragraph explanation suitable for Grade {grade}",
  "mcqs": [
    {{
      "question": "question text",
      "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
      "answer": "A"
    }},
    {{
      "question": "question text",
      "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
      "answer": "B"
    }},
    {{
      "question": "question text",
      "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
      "answer": "C"
    }}
  ]
}}

Rules:
- Language must match Grade {grade} level
- Concepts must be accurate
- MCQs must test what is explained above
- No extra text outside JSON
"""
    raw = call_groq(prompt)
    return parse_json(raw)

# ── AGENT 2 : REVIEWER ──────────────────────────────────
def reviewer_agent(grade: int, content: dict) -> dict:
    prompt = f"""
You are a strict educational content reviewer.
Review this content meant for Grade {grade} students.

Content:
{json.dumps(content, indent=2)}

Evaluate on:
1. Age appropriateness (language, vocabulary for Grade {grade})
2. Conceptual correctness
3. Clarity of explanation
4. MCQ quality (are questions testing what was explained?)

Return ONLY valid JSON in this exact format:
{{
  "status": "pass",
  "feedback": []
}}

OR if there are issues:
{{
  "status": "fail",
  "feedback": [
    "specific issue 1",
    "specific issue 2"
  ]
}}

Be strict. If anything is even slightly inappropriate for Grade {grade}, return fail.
No extra text outside JSON.
"""
    raw = call_groq(prompt)
    return parse_json(raw)

# ── UI ───────────────────────────────────────────────────
st.set_page_config(page_title="AI Edu Agents", page_icon="🎓", layout="wide")

st.title("🎓 AI Educational Content Generator")
st.caption("Two-agent pipeline: Generator → Reviewer → Refiner")

# Input
col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("Select Grade", list(range(1, 13)), index=3)
with col2:
    topic = st.text_input("Enter Topic", placeholder="e.g. Types of Angles")

run = st.button("🚀 Generate Content", type="primary", use_container_width=True)

if run and topic.strip():
    # ── STEP 1: GENERATOR ──
    with st.status("⚙️ Generator Agent is working...", expanded=True) as status:
        st.write("Generating explanation and MCQs...")
        try:
            generated = generator_agent(grade, topic)
            status.update(label="✅ Generator Agent — Done", state="complete")
        except Exception as e:
            st.error(f"Generator failed: {e}")
            st.stop()

    # Show Generator Output
    st.markdown("---")
    st.subheader("📝 Generator Agent Output")
    with st.expander("View Raw JSON", expanded=False):
        st.json(generated)

    st.markdown(f"**📖 Explanation:**")
    st.info(generated.get("explanation", ""))

    st.markdown("**❓ MCQs:**")
    for i, mcq in enumerate(generated.get("mcqs", []), 1):
        with st.container(border=True):
            st.markdown(f"**Q{i}. {mcq['question']}**")
            for opt in mcq["options"]:
                st.markdown(f"- {opt}")
            st.success(f"✅ Correct Answer: {mcq['answer']}")

    # ── STEP 2: REVIEWER ──
    st.markdown("---")
    with st.status("🔍 Reviewer Agent is evaluating...", expanded=True) as status:
        st.write("Checking age appropriateness, correctness, clarity...")
        try:
            review = reviewer_agent(grade, generated)
            status.update(label="✅ Reviewer Agent — Done", state="complete")
        except Exception as e:
            st.error(f"Reviewer failed: {e}")
            st.stop()

    st.subheader("🔍 Reviewer Agent Feedback")
    if review["status"] == "pass":
        st.success("✅ Status: PASS — Content is appropriate for this grade!")
    else:
        st.error("❌ Status: FAIL — Issues found, refining content...")
        with st.container(border=True):
            st.markdown("**Issues found:**")
            for fb in review.get("feedback", []):
                st.markdown(f"- ⚠️ {fb}")

        # ── STEP 3: REFINER ──
        st.markdown("---")
        with st.status("🔧 Refining content based on feedback...", expanded=True) as status:
            st.write("Re-running Generator with reviewer feedback...")
            try:
                refined = generator_agent(grade, topic, feedback=review["feedback"])
                status.update(label="✅ Refined Content Ready", state="complete")
            except Exception as e:
                st.error(f"Refinement failed: {e}")
                st.stop()

        st.subheader("✨ Refined Output")
        with st.expander("View Raw JSON", expanded=False):
            st.json(refined)

        st.markdown(f"**📖 Refined Explanation:**")
        st.info(refined.get("explanation", ""))

        st.markdown("**❓ Refined MCQs:**")
        for i, mcq in enumerate(refined.get("mcqs", []), 1):
            with st.container(border=True):
                st.markdown(f"**Q{i}. {mcq['question']}**")
                for opt in mcq["options"]:
                    st.markdown(f"- {opt}")
                st.success(f"✅ Correct Answer: {mcq['answer']}")

elif run and not topic.strip():
    st.warning("⚠️ Please enter a topic first!")