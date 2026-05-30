import streamlit as st
import os
import re
from groq import Groq
from utils import get_supabase, load_css

def analyze_security(code, language):
    """VANGUARD AI: Penetration Testing and Secure Patching."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Error: GROQ_API_KEY not found.", "", 0
        
    client = Groq(api_key=api_key)
    
    system_prompt = f"""
    You are VANGUARD, an elite, merciless Cybersecurity AI Architect. Perform a Deep Security Penetration Test on this {language} code.
    
    STRICT FORMATTING RULES:
    1. You MUST start your response with the securely patched code wrapped securely in standard markdown blocks (e.g. ```{language.lower()} ... ```).
    2. Provide a Threat Intelligence Report formatted EXACTLY like this:

    ### 🚨 THREAT INTELLIGENCE REPORT
    (List vulnerabilities. Tag them with 🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🔵 LOW based on severity. Be concise and explain the attack vector).

    ### 🛡️ VANGUARD PATCH NOTES
    (List exactly what defenses you implemented to secure the code).
    
    3. STRICT VULNERABILITY SCORING:
       - 90-100: Extremely secure, no significant vulnerabilities.
       - 80-89: Safe, but minor misconfigurations or exposure risks.
       - 70-79: Moderate risk, standard bugs, lack of validation.
       - 0-69: High/Critical risk, Injection flaws, hardcoded secrets, memory leaks.
       DO NOT be generous. If there is SQL injection or secrets exposed, score it under 50.
    
    4. You MUST end the entire response with EXACTLY this line:
    FINAL_SCORE: <number>
    """
    
    try:
        with st.spinner("VANGUARD IS SCANNING NEURAL PATHWAYS FOR THREATS... 🛡️"):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"SCAN THIS PROTOCOL:\n{code}"}],
                temperature=0.1 
            )
            
            full_response = completion.choices[0].message.content or ""
            
            # Code Extraction
            matches = re.findall(r"```[^\n]*\n(.*?)```", full_response, re.DOTALL)
            secured_code = matches[0].strip() if matches else "# ⚠️ Code extraction failed. Check report."
            
            # Metric Extraction
            sc_matches = re.findall(r"FINAL_SCORE[^\d]*(\d+)", full_response, re.IGNORECASE)
            score = int(sc_matches[-1]) if sc_matches else 50  
            
            # Clean report view
            report = re.sub(r"```[^\n]*\n(.*?)```", "", full_response, flags=re.DOTALL)
            report = re.sub(r"FINAL_SCORE.*", "", report, flags=re.IGNORECASE | re.DOTALL).strip()

            return report, secured_code, score
            
    except Exception as e:
        return f"❌ System Error: {str(e)}", "", 0

def render_security_scan_page():
    load_css()
    
    st.markdown("""
        <style>
            .cyber-header {
                font-family: 'JetBrains Mono', monospace; 
                font-size: 3.2rem; 
                font-weight: 800; 
                background: linear-gradient(135deg, #10B981, #fff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
                text-align: center;
                text-transform: uppercase;
                margin-bottom: 0px;
                animation: textGlowGreen 3s infinite alternate;
            }
            @keyframes textGlowGreen {
                0% { text-shadow: 0 0 10px rgba(16, 185, 129, 0.4); }
                100% { text-shadow: 0 0 25px rgba(16, 185, 129, 0.8), 0 0 40px rgba(16, 185, 129, 0.4); }
            }
            .cyber-sub {
                text-align: center; color: #94A3B8; letter-spacing: 3px; font-family: monospace; font-size: 1rem; margin-bottom: 30px;
            }
            
            .tool-icon {
                display: inline-block;
                animation: toolActivity 2s infinite ease-in-out;
                -webkit-background-clip: border-box !important;
                -webkit-text-fill-color: initial !important;
            }
            @keyframes toolActivity {
                0%, 100% { transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.4)); }
                50% { transform: scale(1.15) rotate(-5deg); filter: drop-shadow(0 0 25px rgba(16, 185, 129, 1)); }
            }

            .glow-wrapper {
                border: 1px solid rgba(16, 185, 129, 0.4);
                box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
                padding: 30px;
                border-radius: 12px;
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(2, 6, 23, 0.1) 100%);
                margin-bottom: 30px;
                position: relative;
                overflow: hidden;
            }
            .glow-wrapper::after {
                content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(to right, transparent, rgba(16, 185, 129, 0.15), transparent);
                transform: translateX(-100%);
                animation: scanRightGreen 3s linear infinite;
                pointer-events: none;
            }
            @keyframes scanRightGreen { 100% { transform: translateX(100%); } }

            .editor-label { 
                font-size: 0.9rem; 
                color: #10B981; 
                font-family: 'JetBrains Mono', monospace; 
                font-weight: 800; 
                text-transform: uppercase; 
                margin-bottom: 5px; 
                letter-spacing: 2px; 
                animation: pulseTextGreen 3s infinite alternate; 
            }
            @keyframes pulseTextGreen { 0% { opacity: 0.8; text-shadow: 0 0 5px rgba(16, 185, 129, 0.3); } 100% { opacity: 1; text-shadow: 0 0 15px rgba(16, 185, 129, 0.8); } }

            div[data-baseweb="select"] > div {
                background: rgba(15, 23, 42, 0.8) !important;
                border: 2px solid rgba(16, 185, 129, 0.4) !important;
                border-radius: 8px !important;
                box-shadow: 0 0 15px rgba(16, 185, 129, 0.1);
                color: #10B981 !important;
            }

            .stTextArea textarea { 
                background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(15,23,42,0.8)) !important;
                border: 1px solid rgba(16, 185, 129, 0.3) !important; 
                border-left: 4px solid #F59E0B !important;
                color: #E2E8F0 !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                border-radius: 8px !important; 
                box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .stTextArea textarea:focus { 
                border-color: #10B981 !important; 
                border-left: 4px solid #10B981 !important;
                box-shadow: 0 0 25px rgba(16, 185, 129, 0.3), inset 0 0 15px rgba(16, 185, 129, 0.1) !important; 
                transform: scale(1.01);
            }
            
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(15,23,42,0.8));
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-left: 4px solid #F59E0B;
                border-radius: 8px;
                box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
                color: #E2E8F0;
                overflow-y: auto;
            }

            .export-tools {
                background: rgba(15, 23, 42, 0.6);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #F59E0B;
                box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                margin-top: 15px;
            }

            [data-testid="stFileUploader"] > div {
                background: rgba(2, 6, 23, 0.6) !important;
                border: 1px dashed rgba(16, 185, 129, 0.5) !important;
                border-radius: 8px;
                transition: all 0.3s;
            }
            [data-testid="stFileUploader"] > div:hover {
                border-color: #10B981 !important;
                background: rgba(16, 185, 129, 0.05) !important;
                box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
            }

            button[kind="primary"] {
                background: linear-gradient(90deg, #10B981, #F59E0B, #10B981) !important;
                background-size: 200% auto !important;
                color: #020617 !important;
                font-weight: 900 !important;
                border: none !important;
                animation: gradientShiftGreen 3s linear infinite !important;
                transition: all 0.3s !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                box-shadow: 0 0 20px rgba(16, 185, 129, 0.4) !important;
            }
            button[kind="primary"]:hover {
                transform: scale(1.01) !important;
                box-shadow: 0 0 30px rgba(16, 185, 129, 0.6) !important;
            }
            @keyframes gradientShiftGreen { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
            
            .threat-score-box { background: rgba(15, 23, 42, 0.8); border-left: 5px solid #EF4444; padding: 25px; margin-top: 15px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); animation: slideIn 0.5s ease-out; }
            @keyframes slideIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
            
            .report-box {
                background: rgba(2, 6, 23, 0.8);
                border: 1px solid rgba(16, 185, 129, 0.4);
                border-left: 5px solid #10B981;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(16, 185, 129, 0.1);
                animation: slideIn 0.6s ease-out;
                margin-top: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'><span class='tool-icon'>🛡️</span> VANGUARD SECURITY</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>DETECT AND NEUTRALIZE ZERO-DAY VULNERABILITIES IN REAL-TIME.</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="glow-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="editor-label">🎯 SCAN CONFIGURATION</div>', unsafe_allow_html=True)
    c_conf1, c_conf2 = st.columns(2)
    with c_conf1:
        language = st.selectbox("🌐 SELECT PROTOCOL LANGUAGE", ["Python", "JavaScript", "Java", "C++", "SQL", "Go", "PHP", "Ruby"], label_visibility="collapsed")
    with c_conf2:
        uploaded_file = st.file_uploader("UPLOAD DATA STREAM (.py, .js, etc.)", type=["py", "js", "java", "cpp", "ts", "html", "css", "sql", "go", "php", "rb"], key="sec_upload", label_visibility="collapsed")
        
        if uploaded_file is not None:
            if st.session_state.get("sec_last_file") != uploaded_file.name:
                try:
                    st.session_state["sec_input_text"] = uploaded_file.getvalue().decode("utf-8")
                    st.session_state["sec_last_file"] = uploaded_file.name
                    st.toast(f"Data Stream Loaded: {uploaded_file.name}", icon="✅")
                except:
                    st.error("Could not decode file.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)

    # --- TEXT WORKSPACE ---
    c_input, c_output = st.columns(2)
    
    with c_input:
        st.markdown('<div class="editor-label">🔴 RAW PROTOCOL STREAM</div>', unsafe_allow_html=True)
        default_text = st.session_state.get("sec_input_text", "")
        code_input = st.text_area("RAW_INPUT", value=default_text, height=550, label_visibility="collapsed", placeholder="// Paste target protocol here...")
        st.session_state["sec_input_text"] = code_input

    with c_output:
        st.markdown('<div class="editor-label">🟢 SECURED PROTOCOL</div>', unsafe_allow_html=True)
        secured_code = st.session_state.get("sec_code", "")
        if secured_code:
            with st.container(border=True, height=550):
                st.code(secured_code, language=language.lower())
        else:
            st.text_area("output", value="Awaiting security scan...", height=550, disabled=True, label_visibility="collapsed")

    st.write("<br>", unsafe_allow_html=True)

    if st.button("🚨 INITIATE DEEP SECURITY SCAN", type="primary", use_container_width=True):
        if not code_input.strip():
            st.warning("⚠️ DATA STREAM EMPTY. PROVIDE TARGET PROTOCOL.")
        else:
            report, sec_code, score = analyze_security(code_input, language)
            st.session_state["sec_report"] = report
            st.session_state["sec_code"] = sec_code
            st.session_state["sec_score"] = score
            
            # Gamification Drop
            earned_xp = 0
            if score >= 90: earned_xp = 3
            elif score >= 70: earned_xp = 2
            else: earned_xp = 1

            supabase = get_supabase()
            uid = st.session_state.get("user_id")
            if supabase and uid:
                try:
                    supabase.table("reviews").insert({"user_id": str(uid), "code_snippet": code_input, "language": language, "quality_score": score, "issues_found": 1 if score < 90 else 0, "ai_report": "VANGUARD SECURITY SCAN"}).execute()
                    
                    p_res = supabase.table("profiles").select("*").eq("id", uid).single().execute()
                    if p_res.data:
                        new_total = p_res.data.get("total_reviews", 0) + 1  
                        new_xp = p_res.data.get("lifetime_reviews", 0) + earned_xp  
                        supabase.table("profiles").update({"total_reviews": new_total, "lifetime_reviews": new_xp}).eq("id", uid).execute()
                        st.session_state["profile"] = supabase.table("profiles").select("*").eq("id", uid).single().execute().data
                    
                    st.toast(f"Vanguard Scan Complete! Score: {score}. Earned: +{earned_xp} XP!", icon="🛡️")
                except Exception as e: pass
                
            st.rerun()

    # --- DISPLAY RESULTS ---
    if "sec_report" in st.session_state:
        st.write("<br>", unsafe_allow_html=True)
        st.divider()
        
        score_val = st.session_state.get("sec_score", 0)
        border_color = "#10B981" if score_val >= 80 else "#F59E0B" if score_val >= 60 else "#EF4444"
        
        st.markdown(f"""
            <div class="threat-score-box" style="border-left-color: {border_color}; border-color: {border_color}; box-shadow: 0 0 15px {border_color}33;">
                <h3 style="margin-top:0; color:{border_color};">ORIGINAL THREAT SCORE: {score_val}/100</h3>
                <p style="color:#94A3B8; margin-bottom:0;">Lower scores indicate a highly exploitable environment. Review the Vanguard Patches below.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        st.markdown('<div class="editor-label">🚨 VANGUARD INTELLIGENCE REPORT</div>', unsafe_allow_html=True)
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.markdown(st.session_state["sec_report"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="export-tools">', unsafe_allow_html=True)
        st.markdown("**📥 EXTRACT INTEL:**")
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button("💾 DOWNLOAD SECURE PROTOCOL PATCH", data=st.session_state["sec_code"], file_name=f"secured_protocol.{language.lower()}", use_container_width=True)
        with dl2:
            st.download_button("📥 DOWNLOAD THREAT LOG", data=st.session_state["sec_report"], file_name=f"Vanguard_Threat_Log_{score_val}.md", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)
    if st.button("← ABORT & RETURN TO DASHBOARD", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()