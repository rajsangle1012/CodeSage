import streamlit as st
import os
import re
from groq import Groq
from utils import get_supabase, load_css

def analyze_code_with_groq(code, language):
    """Senior Architect: Bulletproof extraction and beautifully formatted reports."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Error: GROQ_API_KEY not found.", "API Key missing.", 0, 0
        
    client = Groq(api_key=api_key)
    
    # Highly structured prompt for a beautiful, readable, free-flowing Audit Report
    system_prompt = f"""
    You are an elite, brutally honest Senior Software Architect mentoring a developer. Analyze this {language} code.
    
    STRICT FORMATTING RULES:
    1. You MUST start your response with the refactored code wrapped securely in standard markdown code blocks (e.g. ```{language.lower()} ... ```).
    2. The refactored code MUST be a complete, production-ready, error-free replacement.
    3. After the code block, provide a highly readable, attractive Audit Report structured EXACTLY like this:

    ### 📝 Executive Summary
    (Write 1-2 sentences explaining the overall state of the original code and what you fixed.)

    ### 🚨 Key Issues Discovered
    (Use bullet points and emojis like 🐛, 🔓, 🐢)

    ### 💡 CodeSage Improvements
    (Use bullet points and emojis like ✨, ⚡, 🧹)

    ### 🎓 The Architect's Advice
    (One short, encouraging tip.)
    
    4. STRICT SCORING RUBRIC (BE BRUTALLY HONEST):
       - 90-100: Flawless, highly secure, optimized.
       - 80-89: Good, but has minor stylistic or performance issues.
       - 70-79: Functional, but has noticeable bugs, bad practices, or lacks error handling.
       - 0-69: Broken, contains severe security vulnerabilities, or terrible performance.
       CRITICAL: If the code contains SQL Injection, hardcoded secrets, or severe vulnerabilities, YOU MUST GIVE A SCORE BELOW 60. Do NOT be polite. Do NOT default to a high score. Calculate it honestly.
    
    5. You MUST end the entire response with EXACTLY these two lines at the very bottom:
    TOTAL_ISSUES: <number>
    FINAL_SCORE: <number>
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": f"AUDIT THIS:\n{code}"}],
            temperature=0.2 
        )
        
        full_response = completion.choices[0].message.content or ""
        
        # 1. Code Extraction
        matches = re.findall(r"```[^\n]*\n(.*?)```", full_response, re.DOTALL)
        refactored_code = matches[0].strip() if matches else "# ⚠️ Code extraction failed.\n# Check the report below."
        
        # 2. BULLETPROOF METRIC EXTRACTION (Grab the LAST match to prevent grabbing prompt echoes)
        is_matches = re.findall(r"TOTAL_ISSUES[^\d]*(\d+)", full_response, re.IGNORECASE)
        sc_matches = re.findall(r"FINAL_SCORE[^\d]*(\d+)", full_response, re.IGNORECASE)
        
        issues = int(is_matches[-1]) if is_matches else 0
        score = int(sc_matches[-1]) if sc_matches else 0  
        
        # 3. Clean the report reading view (Cut off the raw metrics block at the end)
        readable_report = re.sub(r"```[^\n]*\n(.*?)```", "", full_response, flags=re.DOTALL)
        readable_report = re.sub(r"TOTAL_ISSUES.*", "", readable_report, flags=re.IGNORECASE | re.DOTALL)
        readable_report = re.sub(r"FINAL_SCORE.*", "", readable_report, flags=re.IGNORECASE | re.DOTALL)
        readable_report = readable_report.strip()

        return readable_report, refactored_code, issues, score
        
    except Exception as e:
        error_msg = f"❌ System Error: {str(e)}"
        return error_msg, "# Error generating refactored code.", 0, 0


def render_ai_analysis_page():
    load_css()
    
    # --- 1. WORKBENCH GLOW CSS ---
    st.markdown("""
        <style>
            .cyber-header {
                font-family: 'JetBrains Mono', monospace; 
                font-size: 3.2rem; 
                font-weight: 800; 
                background: linear-gradient(135deg, #00FFEA, #fff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 20px rgba(0, 255, 234, 0.5);
                text-align: center;
                text-transform: uppercase;
                margin-bottom: 0px;
                animation: textGlow 3s infinite alternate;
            }
            @keyframes textGlow {
                0% { text-shadow: 0 0 10px rgba(0, 255, 234, 0.4); }
                100% { text-shadow: 0 0 25px rgba(0, 255, 234, 0.8), 0 0 40px rgba(0, 255, 234, 0.4); }
            }
            .cyber-sub {
                text-align: center; color: #94A3B8; letter-spacing: 3px; font-family: monospace; font-size: 1rem; margin-bottom: 30px;
            }
            
            /* Realistic Brain Animation */
            .brain-icon {
                display: inline-block;
                animation: neuralActivity 2s infinite ease-in-out;
                -webkit-background-clip: border-box !important;
                -webkit-text-fill-color: initial !important;
            }
            @keyframes neuralActivity {
                0%, 100% { 
                    transform: scale(1) translateY(0); 
                    filter: drop-shadow(0 0 10px rgba(240, 18, 190, 0.4)); 
                }
                50% { 
                    transform: scale(1.2) translateY(-5px); 
                    filter: drop-shadow(0 0 25px rgba(0, 255, 234, 1)); 
                }
            }
            .editor-label { 
                font-size: 0.9rem; 
                color: #00FFEA; 
                font-family: 'JetBrains Mono', monospace; 
                font-weight: 800; 
                text-transform: uppercase; 
                margin-bottom: 5px; 
                letter-spacing: 2px; 
                animation: pulseText 3s infinite alternate; 
            }
            @keyframes pulseText { 0% { opacity: 0.8; text-shadow: 0 0 5px rgba(0, 255, 234, 0.3); } 100% { opacity: 1; text-shadow: 0 0 15px rgba(0, 255, 234, 0.8); } }
            
            /* High Tech Form Elements */
            div[data-baseweb="select"] > div {
                background: rgba(15, 23, 42, 0.8) !important;
                border: 2px solid rgba(0, 255, 234, 0.4) !important;
                border-radius: 8px !important;
                box-shadow: 0 0 15px rgba(0, 255, 234, 0.1);
                color: #00FFEA !important;
            }
            
            .stTextArea textarea { 
                background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(15,23,42,0.8)) !important;
                border: 1px solid rgba(0, 255, 234, 0.3) !important; 
                border-left: 4px solid #F012BE !important;
                color: #00FFEA !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                border-radius: 8px !important; 
                box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .stTextArea textarea:focus { 
                border-color: #00FFEA !important; 
                border-left: 4px solid #00FFEA !important;
                box-shadow: 0 0 25px rgba(0, 255, 234, 0.3), inset 0 0 15px rgba(0, 255, 234, 0.1) !important; 
                transform: scale(1.01);
            }
            
            /* File Uploader Glow */
            .stFileUploader > div {
                background: rgba(2, 6, 23, 0.6) !important;
                border: 1px dashed rgba(0, 255, 234, 0.5) !important;
                border-radius: 8px;
                transition: all 0.3s;
            }
            .stFileUploader > div:hover {
                border-color: #F012BE !important;
                background: rgba(240, 18, 190, 0.05) !important;
                box-shadow: 0 0 15px rgba(240, 18, 190, 0.3);
            }

            /* Report Panel */
            .report-box {
                background: rgba(2, 6, 23, 0.8);
                border: 1px solid rgba(0, 255, 234, 0.4);
                border-left: 5px solid #00FFEA;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0, 255, 234, 0.1);
                animation: slideUpFade 0.6s ease-out;
            }
            @keyframes slideUpFade {
                0% { opacity: 0; transform: translateY(20px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            
            /* Primary Button Glow Animation */
            button[kind="primary"] {
                background: linear-gradient(90deg, #F012BE, #00FFEA, #F012BE) !important;
                background-size: 200% auto !important;
                color: #020617 !important;
                font-weight: 900 !important;
                border: none !important;
                animation: gradientShift 3s linear infinite !important;
                transition: all 0.3s !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                box-shadow: 0 0 20px rgba(240, 18, 190, 0.4) !important;
            }
            button[kind="primary"]:hover {
                transform: scale(1.02) !important;
                box-shadow: 0 0 30px rgba(0, 255, 234, 0.6) !important;
            }
            @keyframes gradientShift { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'><span class='brain-icon'>🧠</span> AI Workbench</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>PROFESSIONAL AUDIT & SIDE-BY-SIDE NEURAL REFACTORING</p>", unsafe_allow_html=True)
    st.divider()

    # --- 2. GLOWING LANGUAGE SELECTOR ---
    with st.container():
        st.markdown('<div class="editor-label">🎯 Target Programming Language</div>', unsafe_allow_html=True)
        language = st.selectbox("Language", ["Python", "JavaScript", "Java", "C++", "SQL", "HTML/CSS"], label_visibility="collapsed")
        st.write("<br>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="editor-label">📂 Upload Script Instance</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload script to auto-fill Original Snippet", type=["py", "js", "java", "cpp", "ts", "html", "css", "sql"], key="ai_upload")
        if uploaded_file is not None:
            if st.session_state.get("ai_last_file") != uploaded_file.name:
                try:
                    st.session_state["ai_input_text"] = uploaded_file.getvalue().decode("utf-8")
                    st.session_state["ai_last_file"] = uploaded_file.name
                    st.toast(f"Loaded {uploaded_file.name}", icon="✅")
                except:
                    st.error("Could not read file.")
                    
    st.write("<br>", unsafe_allow_html=True)

    # --- 3. DUAL CODE WORKSPACE ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="editor-label">🔴 Original Snippet</div>', unsafe_allow_html=True)
        default_val = st.session_state.get("ai_input_text", "")
        code_input = st.text_area("input_area", value=default_val, height=550, label_visibility="collapsed", placeholder="Paste dirty code or upload file...")
        st.session_state["ai_input_text"] = code_input

    with col2:
        st.markdown('<div class="editor-label">🟢 CodeSage Refactored</div>', unsafe_allow_html=True)
        refactored_val = st.session_state.get("current_refactor", "")
        st.text_area("output_area", value=refactored_val, height=550, label_visibility="collapsed", placeholder="Optimized code will appear here...")
        
        if refactored_val and refactored_val != "# Error generating refactored code.":
            st.download_button(label="💾 Download Refactored Code", data=refactored_val, file_name=f"refactored_solution.{language.lower()}", mime="text/plain", use_container_width=True)

    st.write("<br>", unsafe_allow_html=True)

    # --- 4. ACTION BUTTON ---
    if st.button("🚀 Analyze & Rewrite Code", type="primary", use_container_width=True):
        if not code_input.strip():
            st.warning("⚠️ Please provide code to analyze.")
            return

        with st.spinner("Senior Architect is auditing your logic..."):
            report, refactored, issues, score = analyze_code_with_groq(code_input, language)
            
            st.session_state["current_refactor"] = refactored
            st.session_state["latest_report"] = report
            st.session_state["latest_score"] = score
            st.session_state["latest_issues"] = issues

            # --- STRICT GAMIFICATION LOGIC ---
            earned_xp = 0
            if score >= 90: earned_xp = 3
            elif score >= 80: earned_xp = 2
            elif score >= 70: earned_xp = 1

            # --- DATABASE SYNC ---
            supabase = get_supabase()
            uid = st.session_state.get("user_id")
            if supabase and uid:
                try:
                    supabase.table("reviews").insert({"user_id": str(uid), "code_snippet": code_input, "language": language, "quality_score": score, "issues_found": issues, "ai_report": report}).execute()
                    
                    p_res = supabase.table("profiles").select("*").eq("id", uid).single().execute()
                    if p_res.data:
                        new_total_reviews = p_res.data.get("total_reviews", 0) + 1  
                        new_xp = p_res.data.get("lifetime_reviews", 0) + earned_xp  
                        
                        supabase.table("profiles").update({"total_reviews": new_total_reviews, "lifetime_reviews": new_xp}).eq("id", uid).execute()
                        st.session_state["profile"] = supabase.table("profiles").select("*").eq("id", uid).single().execute().data
                    
                    if earned_xp > 0:
                        st.toast(f"Audit Complete! AI Score: {score}. You earned +{earned_xp} XP!", icon="🎯")
                    else:
                        st.toast(f"Audit Complete! AI Score: {score}. Code needs work (0 XP).", icon="⚠️")

                except Exception as db_err:
                    print(f"Database error: {db_err}")
            
            st.rerun()

    # --- 5. REPORT DISPLAY ---
    if "latest_report" in st.session_state:
        st.write("<br>", unsafe_allow_html=True)
        st.divider()
        
        score_val = st.session_state.get("latest_score", 0)
        
        col_hdr, col_btn = st.columns([7, 3])
        with col_hdr:
            st.markdown(f"## 📋 CodeSage Audit Report")
            st.markdown(f"**Performance Score: {score_val}/100**")
        with col_btn:
            st.download_button(label="📥 Download Audit (.md)", data=st.session_state["latest_report"], file_name=f"Audit_{score_val}.md", mime="text/markdown", use_container_width=True)
        
        st.write("<br>", unsafe_allow_html=True)
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.markdown(st.session_state["latest_report"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("<br><br>", unsafe_allow_html=True)
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()