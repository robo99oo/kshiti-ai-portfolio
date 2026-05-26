import streamlit as st
import google.generativeai as genai

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO
from collections import Counter
from pathlib import Path
import tempfile
from streamlit_mic_recorder import mic_recorder

st.set_page_config(
    page_title="Kshiti AI Portfolio",
    page_icon="🤖",
    layout="wide"
)

st.sidebar.title("🤖 Kshiti AI")

section = st.sidebar.radio(
    "Navigation",
    ["Home", "Projects", "AI Assistant", "Contact"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Core Focus")
st.sidebar.markdown("""
- GenAI Systems
- RAG Pipelines
- MCP Workflows
- AI Automation
- Enterprise AI
""")

with st.sidebar.expander("Admin"):
    admin_code = st.text_input("Admin Code", type="password")

show_analytics = admin_code == st.secrets.get("ADMIN_CODE", "")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")


def safe_generate(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_text = str(e)
        if "429" in error_text or "quota" in error_text.lower():
            return "⚠️ Gemini API quota limit reached for today. Please try again later."
        return "⚠️ Something went wrong while generating the AI response. Please try again."



def transcribe_recruiter_voice(audio_data):
    """Convert recruiter voice recording into text using Gemini audio understanding."""
    try:
        if not audio_data:
            return ""

        # streamlit-mic-recorder returns a dictionary containing recorded audio bytes
        audio_bytes = audio_data.get("bytes") if isinstance(audio_data, dict) else None

        if not audio_bytes:
            return "⚠️ Voice was recorded, but audio bytes were not received. Please try recording again."

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        uploaded_audio = genai.upload_file(temp_audio_path)

        transcription_response = model.generate_content([
            uploaded_audio,
            "Transcribe this recruiter voice question exactly into clean English text. Return only the question, no extra explanation."
        ])

        Path(temp_audio_path).unlink(missing_ok=True)
        return transcription_response.text.strip()

    except Exception as e:
        error_text = str(e)
        if "429" in error_text or "quota" in error_text.lower():
            return "⚠️ Gemini API quota limit reached while transcribing voice. Please type the question instead."
        return "⚠️ Could not transcribe the voice clearly. Please try again or type the question."


with open("resume_data.txt", "r", encoding="utf-8") as file:
    resume_data = file.read()

if "analytics" not in st.session_state:
    st.session_state.analytics = {
        "questions": [],
        "skills": [],
        "ats_downloads": 0,
        "total_interactions": 0
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_question_processed" not in st.session_state:
    st.session_state.last_question_processed = ""

if "last_role_processed" not in st.session_state:
    st.session_state.last_role_processed = ""

if "match_text" not in st.session_state:
    st.session_state.match_text = ""

if "tailored_text" not in st.session_state:
    st.session_state.tailored_text = ""

if "tailored_pdf" not in st.session_state:
    st.session_state.tailored_pdf = None

if "voice_transcript" not in st.session_state:
    st.session_state.voice_transcript = ""

if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None


def create_pdf_from_text(text):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    content.append(
        Paragraph("<b>Kshiti Tyagi - ATS Tailored Resume</b>", styles["Title"])
    )
    content.append(Spacer(1, 12))

    safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_text = safe_text.replace("\n", "<br/>")

    content.append(Paragraph(safe_text, styles["BodyText"]))
    doc.build(content)
    pdf_buffer.seek(0)

    return pdf_buffer


st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

body {
    background: #0B0F19;
}

.main {
    background: linear-gradient(135deg, #0B0F19 0%, #111827 50%, #0F172A 100%);
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #27272A;
}

.hero-title {
    font-size: 64px;
    font-weight: 800;
    color: white;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 24px;
    color: #A78BFA;
    margin-bottom: 22px;
    font-weight: 600;
}

.hero-text {
    font-size: 17px;
    color: #CBD5E1;
    line-height: 1.7;
}

.info-box {
    background: rgba(17, 24, 39, 0.88);
    border: 1px solid rgba(167, 139, 250, 0.22);
    padding: 25px;
    border-radius: 22px;
    margin-top: 20px;
    box-shadow: 0px 0px 30px rgba(167, 139, 250, 0.08);
}

.metric-card {
    background: linear-gradient(145deg, rgba(17,24,39,0.95), rgba(30,41,59,0.92));
    border: 1px solid rgba(167,139,250,0.18);
    padding: 22px;
    border-radius: 20px;
    text-align: center;
}

.metric-number {
    font-size: 34px;
    font-weight: 800;
    color: #C084FC;
}

.metric-label {
    font-size: 14px;
    color: #CBD5E1;
}

.project-card {
    background: rgba(17,24,39,0.94);
    border: 1px solid rgba(167,139,250,0.18);
    padding: 24px;
    border-radius: 24px;
    min-height: 420px;
    margin-top: 12px;
}

.project-card img {
    border-radius: 14px;
    transition: 0.3s ease;
    box-shadow: 0px 0px 20px rgba(147,51,234,0.12);

}

.project-card img:hover {
    transform: scale(1.02);
}

.badge {
    display: inline-block;
    background: rgba(147, 51, 234, 0.18);
    color: #DDD6FE;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    margin: 4px 4px 4px 0;
    border: 1px solid rgba(167,139,250,0.28);
}

.profile-wrapper {
    display: flex;
    justify-content: center;
    margin-bottom: 18px;
}

.profile-wrapper img {
    border-radius: 26px !important;
    border: 1px solid rgba(167,139,250,0.18);
    box-shadow: 0px 0px 25px rgba(147,51,234,0.12);
}

.open-badge {
    background: rgba(17,24,39,0.96);
    border: 1px solid rgba(167,139,250,0.22);
    color: white;
    padding: 16px;
    border-radius: 20px;
    text-align: center;
    margin-top: 16px;
    margin-bottom: 22px;
    line-height: 1.8;
    font-size: 15px;
}

.stButton>button,
.stDownloadButton>button {
    background: linear-gradient(90deg, #9333EA, #7C3AED);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.7rem 1.4rem;
    font-weight: 600;
}

.stTextInput input {
    background-color: #111827;
    border: 1px solid #374151;
    color: white;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


if section == "Home":

    left, right = st.columns([1.25, 1])

    with left:
        st.markdown('<div class="hero-title">Kshiti Tyagi</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="hero-subtitle">GenAI Engineer | Data Analyst | AI Systems Builder</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="hero-text">
        Hands-on experience developing GenAI applications using RAG pipelines,
        MCP-based AI workflows, FastAPI, Streamlit, and intelligent automation
        systems focused on real-world enterprise use cases.
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        col1, col2 = st.columns(2)

        with col1:
            st.link_button("LinkedIn", "https://www.linkedin.com/in/kshiti-tyagi/")

        with col2:
            st.link_button("GitHub", "https://github.com/robo99oo")

        st.write("")

        with open("Kshiti_Tyagi_AI_Data_Analyst_..pdf", "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.download_button(
            label="📄 Download Original Resume",
            data=PDFbyte,
            file_name="Kshiti_Tyagi_Original_Resume.pdf",
            mime="application/pdf"
        )

        st.markdown("""
        <div class="info-box">
        <h3>🚀 AI Portfolio Experience</h3>
        <p>
        This AI-powered portfolio is designed to go beyond a static resume.
        Recruiters can explore my work through a dedicated AI assistant that understands
        my GenAI projects, enterprise AI experience, technical background, and project impact.
        </p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown('<div class="metric-card"><div class="metric-number">2</div><div class="metric-label">Years Experience</div></div>', unsafe_allow_html=True)

        with m2:
            st.markdown('<div class="metric-card"><div class="metric-number">94%</div><div class="metric-label">Extraction Accuracy</div></div>', unsafe_allow_html=True)

        with m3:
            st.markdown('<div class="metric-card"><div class="metric-number">60%</div><div class="metric-label">Manual Effort Reduced</div></div>', unsafe_allow_html=True)

        with m4:
            st.markdown('<div class="metric-card"><div class="metric-number">500+</div><div class="metric-label">Users Supported</div></div>', unsafe_allow_html=True)

        st.write("")
        st.write("")

        st.markdown("""
        <div class="info-box">
        <h3>🧠 Tech Stack</h3>
        <span class="badge">Python</span>
        <span class="badge">RAG</span>
        <span class="badge">MCP</span>
        <span class="badge">FastAPI</span>
        <span class="badge">Streamlit</span>
        <span class="badge">LangChain</span>
        <span class="badge">FAISS</span>
        <span class="badge">HuggingFace</span>
        <span class="badge">SQL</span>
        <span class="badge">Azure Data Lake</span>
        <span class="badge">AWS Bedrock</span>
        <span class="badge">Power BI</span>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="profile-wrapper">', unsafe_allow_html=True)
        st.image("Kshiti Tyagi.png", width=520)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="open-badge">
        🟢 Open to Opportunities <br>
        GenAI • RAG • MCP • AI Automation
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
        <h3>🤖 Try the AI Assistant</h3>
        <p>
        Visit the <b>AI Assistant</b> section from the sidebar to ask questions,
        match hiring requirements, and generate an ATS-tailored resume version.
        </p>
        </div>
        """, unsafe_allow_html=True)


elif section == "Projects":

    st.markdown("## 🚀 Featured Projects")

    p1, p2, p3 = st.columns(3)

    with p1:

        st.image(
            "Images/hr_ai_architecture.png",
            use_container_width=True
        )

        st.markdown("""
        <div class="project-card">

        <h3>HR AI Hybrid Assistant</h3>

        <p>
        Enterprise-style HR assistant combining RAG retrieval
        with MCP-based action execution for intelligent routing,
        HR policy retrieval, and workflow automation.
        </p>

        <span class="badge">Python</span>
        <span class="badge">RAG</span>
        <span class="badge">MCP</span>
        <span class="badge">LangChain</span>
        <span class="badge">FAISS</span>
        <span class="badge">FastAPI</span>

        </div>
        """, unsafe_allow_html=True)

    with p2:

        st.image(
            "Images/OCR_architecture.png",
            use_container_width=True
        )

        st.markdown("""
        <div class="project-card">

        <h3>OCR Aadhaar Verification</h3>

        <p>
        OCR-based identity verification system using preprocessing, text extraction, validation, masking, and FastAPI backend workflows.
        </p>

        <span class="badge">OCR</span>
        <span class="badge">OpenCV</span>
        <span class="badge">Tesseract</span>
        <span class="badge">FastAPI</span>
        <span class="badge">SQLite</span>

        </div>
        """, unsafe_allow_html=True)

    with p3:

        st.image(
            "Images/Bosch_architecture.png",
            use_container_width=True
        )

        st.markdown("""
        <div class="project-card">

        <h3>Bosch GenAI CoPilot</h3>

        <p>
        Enterprise document intelligence platform using RAG,
        embeddings, vector search, and LLM orchestration
        for real-time plant document understanding.
        </p>

        <span class="badge">RAG</span>
        <span class="badge">Vector DB</span>
        <span class="badge">Azure Data Lake</span>
        <span class="badge">AWS Bedrock</span>
        <span class="badge">Streamlit</span>

        </div>
        """, unsafe_allow_html=True)


elif section == "AI Assistant":

    st.markdown("## 🤖 Kshiti AI Assistant")

    st.markdown("""
    <div class="info-box">
    <h4>👋 Welcome Recruiter</h4>
    <p>
    Hi, I’m Kshiti AI — an interactive recruiter assistant designed to explain
    Kshiti’s GenAI systems, RAG pipelines, MCP workflows, enterprise AI projects,
    technical strengths, and role alignment through conversational AI.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <h4> 🎤 Recruiter Voice Input</h4>
    <p>
    Recruiters can use voice-assisted interaction to explore Kshiti’s
GenAI experience, enterprise AI projects, RAG pipelines, MCP workflows,
technical strengths, and ATS-tailored resume generation.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("### 🎙️ Voice Recruiter Assistant")

    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹️ Stop Recording",
        just_once=True,
        use_container_width=True,
        key="voice_input"
    )

    if audio:
        audio_id = audio.get("id") or audio.get("bytes")[:30] if isinstance(audio, dict) and audio.get("bytes") else str(audio)

        if audio_id != st.session_state.last_audio_id:
            with st.spinner("🎧 Listening to recruiter voice and converting it into text..."):
                st.session_state.voice_transcript = transcribe_recruiter_voice(audio)
                st.session_state.last_audio_id = audio_id

        if st.session_state.voice_transcript.startswith("⚠️"):
            st.warning(st.session_state.voice_transcript)
        else:
            st.success("✅ Voice captured and converted into recruiter question.")
            st.markdown(f"""
            <div class="info-box">
            <h4>🗣️ Recruiter asked:</h4>
            <p>{st.session_state.voice_transcript}</p>
            </div>
            """, unsafe_allow_html=True)

    question = st.text_input(
        "Ask something about Kshiti:",
        value=st.session_state.voice_transcript if st.session_state.voice_transcript and not st.session_state.voice_transcript.startswith("⚠️") else "",
        placeholder="Recruiter can speak or type here..."
    )

    quick_questions = [
        "Tell me about Kshiti",
        "What did Kshiti build at Bosch?",
        "Why should we hire Kshiti?",
        "How does she align with Microsoft AI?",
        "How can her HR AI Assistant help JPMorgan?",
        "What are her strongest technical skills?",
        "How would she help enterprise AI teams?"
    ]

    selected_question = st.selectbox(
        "Or choose a recruiter question:",
        [""] + quick_questions
    )

    final_question = question if question else selected_question

    if (
            final_question
            and final_question.strip()
            and final_question != st.session_state.last_question_processed
    ):
        prompt = f"""
You are Kshiti Tyagi's professional AI portfolio assistant.

Answer like a sharp recruiter-facing AI assistant.

Rules:
- Keep answer under 90 words
- Sound human, concise, and recruiter-friendly
- Use bullet points when useful
- Keep responses highly skimmable
- Avoid repeating the same metrics or experience repeatedly
- Mention statistics only when directly relevant
- Avoid exaggerated or unsupported claims
- Explain technical systems clearly in business language
- Refer to Kshiti as "she"
- Keep a premium enterprise-AI tone
- End responses with concise executive-style conclusions
- Avoid robotic or repetitive phrasing
- Do not overpraise
- Prefer shorter responses over highly detailed explanations
- Avoid repeating the same examples, metrics, or wording from previous answers.
- Use varied response styles.

Use this information:

{resume_data}

Recruiter Question:
{final_question}

If the same recruiter asks similar questions repeatedly, vary the response style and avoid repeating identical examples or metrics.
"""

        with st.spinner("🤖 Analyzing recruiter query..."):
            ai_text = safe_generate(prompt)

        st.session_state.analytics["questions"].append(final_question)
        st.session_state.analytics["total_interactions"] += 1
        st.session_state.chat_history.append(("Recruiter", final_question))
        st.session_state.chat_history.append(("Kshiti AI", ai_text))
        st.session_state.last_question_processed = final_question

    for sender, message in st.session_state.chat_history:

        if sender == "Recruiter":
            st.markdown(f"""
            <div style="
            background: rgba(147,51,234,0.18);
            padding:16px;
            border-radius:18px;
            margin-top:14px;
            margin-left:60px;
            text-align:right;
            border:1px solid rgba(167,139,250,0.25);
            ">
            <b>👔 Recruiter:</b><br>
            {message}
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div style="
            background: rgba(17,24,39,0.92);
            padding:16px;
            border-radius:18px;
            margin-top:14px;
            margin-right:60px;
            border:1px solid rgba(167,139,250,0.18);
            ">
            <b>🤖 Kshiti AI Assistant:</b><br>
            {message}
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.markdown("### 🎯 Recruiter Requirement Matcher")

    role_need = st.text_input(
        "What skills or role are you hiring for?",
        placeholder="Example: RAG, FastAPI, LLMs, Python, AI agents"
    )

    st.caption(
        "Example: Hiring for RAG engineers, FastAPI developers, AI agents, GenAI systems, or NLP-focused roles."
    )

    if role_need and role_need != st.session_state.last_role_processed:

        st.session_state.analytics["skills"].append(role_need)
        st.session_state.analytics["total_interactions"] += 1

        matcher_prompt = f"""
You are Kshiti Tyagi's AI portfolio assistant.

A recruiter is hiring for:
{role_need}

Using Kshiti's resume data below, explain clearly:
1. ✅ Skills Match
2. 🚀 Relevant Projects
3. 📈 Key Impact
4. 💡 Hiring Fit

Rules:
- Keep answer under 75 words
- Sound human, concise, and recruiter-friendly
- Use bullet points when useful
- Keep responses highly skimmable
- Avoid repeating the same metrics or experience repeatedly
- Mention statistics only when directly relevant
- Avoid exaggerated or unsupported claims
- Explain technical systems clearly in business language
- Refer to Kshiti as "she"
- Keep a premium enterprise-AI tone
- End responses with concise executive-style conclusions
- Avoid robotic or repetitive phrasing
- Do not overpraise
- Prefer shorter responses over highly detailed explanations

Resume Data:
{resume_data}
"""

        with st.spinner("🔍 Matching recruiter requirements with AI profile intelligence..."):
            st.session_state.match_text = safe_generate(matcher_prompt)

        st.session_state.last_role_processed = role_need

    if role_need and st.session_state.match_text:

        st.markdown(f"""
        <div class="info-box">
        <h4>🎯 Match Summary</h4>
        <p>{st.session_state.match_text}</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button("✨ Generate ATS Tailored Resume"):

            st.session_state.analytics["ats_downloads"] += 1
            st.session_state.analytics["total_interactions"] += 1

            resume_prompt = f"""
You are an ATS resume tailoring assistant for Kshiti Tyagi.

Recruiter requirement:
{role_need}

Using the resume data below, generate an ATS-friendly tailored resume version.

Important:
- Do NOT invent experience.
- Do NOT change company names, dates, education, or facts.
- Do NOT exaggerate seniority.
- Optimize keywords naturally for ATS.
- Keep it concise and recruiter-readable.
- Focus on relevant skills, projects, and measurable impact.
- Prioritize GenAI, RAG, FastAPI, MCP, Streamlit, Python, AI systems when relevant.
- Avoid repeating the same examples, metrics, or wording from previous answers.
- Use varied response styles.

Format with clear sections:
1. ✅ Professional Summary
2. ⚡ Core Skills
3. 💼 Relevant Experience
4. 🚀 Relevant Projects
5. 📈 Key Achievements

Resume Data:
{resume_data}
"""

            with st.spinner("⚡ Optimizing ATS keywords and generating tailored resume..."):
                st.session_state.tailored_text = safe_generate(resume_prompt)

            st.session_state.tailored_pdf = create_pdf_from_text(st.session_state.tailored_text)

    if st.session_state.tailored_text:

        st.markdown(f"""
        <div class="info-box">
        <h4>📄 ATS Tailored Resume Preview</h4>
        <pre style="white-space: pre-wrap; color: white; font-family:Segoe UI; line-height:1.7;">
{st.session_state.tailored_text}
        </pre>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.tailored_pdf:
            st.download_button(
                label="📥 Download ATS Tailored Resume",
                data=st.session_state.tailored_pdf,
                file_name="Kshiti_ATS_Tailored_Resume.pdf",
                mime="application/pdf"
            )

            st.success("✅ ATS-tailored resume generated successfully.")

    if show_analytics:

        st.write("")
        st.write("")
        st.markdown("## 📊 Recruiter Analytics Dashboard")

        analytics = st.session_state.analytics

        q_counter = Counter(analytics["questions"])
        s_counter = Counter(analytics["skills"])

        a1, a2, a3 = st.columns(3)

        with a1:
            st.metric("Recruiter Questions", len(analytics["questions"]))

        with a2:
            st.metric("ATS Resume Generations", analytics["ats_downloads"])

        with a3:
            st.metric("Total Interactions", analytics["total_interactions"])

        st.write("")

        left, right = st.columns(2)

        with left:
            st.markdown("### 🔥 Most Asked Questions")

            if q_counter:
                for question_item, count in q_counter.most_common(5):
                    st.markdown(f"- {question_item} ({count})")
            else:
                st.info("No recruiter questions yet.")

        with right:
            st.markdown("### ⚡ Most Searched Skills")

            if s_counter:
                for skill_item, count in s_counter.most_common(5):
                    st.markdown(f"- {skill_item} ({count})")
            else:
                st.info("No recruiter skill searches yet.")


elif section == "Contact":

    st.markdown("## 📬 Contact")

    st.markdown("""
    <div class="info-box">
    <p><b>Email:</b> kshiti392000@gmail.com</p>
    <p><b>Contact No.:</b> +91 9412830537</p>
    <p><b>LinkedIn:</b> <a href="https://linkedin.com/in/kshiti-tyagi" target="_blank">linkedin.com/in/kshiti-tyagi</a></p>
    <p><b>GitHub:</b> <a href="https://github.com/robo99oo" target="_blank">github.com/robo99oo</a></p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

st.markdown("""
<hr style="border:1px solid rgba(167,139,250,0.2);">

<div style="
text-align:center;
padding:18px;
color:#CBD5E1;
font-size:14px;
">

Built with ❤️ using Streamlit • Gemini AI • Python • RAG Concepts • MCP Workflows

</div>
""", unsafe_allow_html=True)