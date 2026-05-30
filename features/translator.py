import streamlit as st
import os
import re
from groq import Groq
from utils import get_supabase, load_css

def translate_code(code, source_lang, target_lang):
    """Translates code from one language to another using Groq."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Error: GROQ_API_KEY not found."
        
    client = Groq(api_key=api_key)
    system_prompt = f"""
    You are an expert Polyglot Developer. Translate the following {source_lang} code into highly optimized {target_lang} code.
    Ensure that you use the best practices, standard libraries, and correct syntax for {target_lang}.
    You MUST wrap the output code in standard markdown code blocks (```).
    Do not explain the code, JUST output the translated code block.
    """
    
    try:
        with st.spinner(f"Translating to {target_lang}... 🌍"):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": code}],
                temperature=0.1
            )
            response = completion.choices[0].message.content or ""
            matches = re.findall(r"```[^\n]*\n(.*?)```", response, re.DOTALL)
            return matches[0].strip() if matches else response.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

def render_translator_page():
    load_css()
    st.markdown("""
        <style>
            .cyber-header {
                font-family: 'JetBrains Mono', monospace; 
                font-size: 3.2rem; 
                font-weight: 800; 
                background: linear-gradient(135deg, #14B8A6, #fff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 20px rgba(20, 184, 166, 0.5);
                text-align: center;
                text-transform: uppercase;
                margin-bottom: 0px;
                animation: textGlowTeal 3s infinite alternate;
            }
            @keyframes textGlowTeal {
                0% { text-shadow: 0 0 10px rgba(20, 184, 166, 0.4); }
                100% { text-shadow: 0 0 25px rgba(20, 184, 166, 0.8), 0 0 40px rgba(20, 184, 166, 0.4); }
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
                0%, 100% { transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 10px rgba(20, 184, 166, 0.4)); }
                50% { transform: scale(1.15) rotate(-5deg); filter: drop-shadow(0 0 25px rgba(20, 184, 166, 1)); }
            }

            .glow-wrapper {
                border: 1px solid rgba(20, 184, 166, 0.4);
                box-shadow: 0 0 20px rgba(20, 184, 166, 0.3);
                padding: 30px;
                border-radius: 12px;
                background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(14, 165, 233, 0.1) 100%);
                margin-bottom: 30px;
                position: relative;
                overflow: hidden;
            }
            .glow-wrapper::after {
                content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(to right, transparent, rgba(20, 184, 166, 0.15), transparent);
                transform: translateX(-100%);
                animation: scanRightTeal 3s linear infinite;
                pointer-events: none;
            }
            @keyframes scanRightTeal { 100% { transform: translateX(100%); } }

            .editor-label { 
                font-size: 0.9rem; 
                color: #14B8A6; 
                font-family: 'JetBrains Mono', monospace; 
                font-weight: 800; 
                text-transform: uppercase; 
                margin-bottom: 5px; 
                letter-spacing: 2px; 
                animation: pulseTextTeal 3s infinite alternate; 
            }
            @keyframes pulseTextTeal { 0% { opacity: 0.8; text-shadow: 0 0 5px rgba(20, 184, 166, 0.3); } 100% { opacity: 1; text-shadow: 0 0 15px rgba(20, 184, 166, 0.8); } }

            div[data-baseweb="select"] > div {
                background: rgba(15, 23, 42, 0.8) !important;
                border: 2px solid rgba(20, 184, 166, 0.4) !important;
                border-radius: 8px !important;
                box-shadow: 0 0 15px rgba(20, 184, 166, 0.1);
                color: #5EEAD4 !important;
            }

            .stTextArea textarea { 
                background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(15,23,42,0.8)) !important;
                border: 1px solid rgba(20, 184, 166, 0.3) !important; 
                border-left: 4px solid #0EA5E9 !important;
                color: #E2E8F0 !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                border-radius: 8px !important; 
                box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .stTextArea textarea:focus { 
                border-color: #14B8A6 !important; 
                border-left: 4px solid #14B8A6 !important;
                box-shadow: 0 0 25px rgba(20, 184, 166, 0.3), inset 0 0 15px rgba(20, 184, 166, 0.1) !important; 
                transform: scale(1.01);
            }
            
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(15,23,42,0.8));
                border: 1px solid rgba(20, 184, 166, 0.3);
                border-left: 4px solid #0EA5E9;
                border-radius: 8px;
                box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
                color: #E2E8F0;
                overflow-y: auto;
            }

            .export-tools {
                background: rgba(15, 23, 42, 0.6);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #0EA5E9;
                box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                margin-top: 15px;
            }

            [data-testid="stFileUploader"] > div {
                background: rgba(2, 6, 23, 0.6) !important;
                border: 1px dashed rgba(20, 184, 166, 0.5) !important;
                border-radius: 8px;
                transition: all 0.3s;
            }
            [data-testid="stFileUploader"] > div:hover {
                border-color: #0EA5E9 !important;
                background: rgba(14, 165, 233, 0.05) !important;
                box-shadow: 0 0 15px rgba(14, 165, 233, 0.3);
            }

            button[kind="primary"] {
                background: linear-gradient(90deg, #14B8A6, #0EA5E9, #14B8A6) !important;
                background-size: 200% auto !important;
                color: #fff !important;
                font-weight: 900 !important;
                border: none !important;
                animation: gradientShiftTeal 3s linear infinite !important;
                transition: all 0.3s !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                box-shadow: 0 0 20px rgba(20, 184, 166, 0.4) !important;
            }
            button[kind="primary"]:hover {
                transform: scale(1.01) !important;
                box-shadow: 0 0 30px rgba(20, 184, 166, 0.6) !important;
            }
            @keyframes gradientShiftTeal { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'><span class='tool-icon'>🌍</span> AI Polyglot Translator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>TRANSLATE AND RE-COMPILE PROTOCOLS ACROSS LANGUAGE BOUNDARIES.</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="glow-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="editor-label">🎯 TRANSLATION MATRIX</div>', unsafe_allow_html=True)
    langs = ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "TypeScript", "Ruby", "PHP"]
    
    colA, colB, colC = st.columns([1,1,2])
    with colA: source_lang = st.selectbox("📤 Source Language", langs, index=0)
    with colB: target_lang = st.selectbox("📥 Target Language", langs, index=1)
    with colC:
        uploaded_file = st.file_uploader("Upload Script", type=["py", "js", "java", "cpp", "ts", "cs", "go", "rs", "rb", "php"], key="trans_upload")
        if uploaded_file is not None:
            if st.session_state.get("trans_last_file") != uploaded_file.name:
                try:
                    file_contents = uploaded_file.getvalue().decode("utf-8")
                    st.session_state["trans_input"] = file_contents
                    st.session_state["trans_last_file"] = uploaded_file.name
                    st.toast(f"Loaded {uploaded_file.name}", icon="✅")
                except: st.error("Error reading file.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    c_input, c_output = st.columns(2)
    
    with c_input:
        st.markdown(f'<div class="editor-label">🔴 RAW {source_lang}</div>', unsafe_allow_html=True)
        def_val = st.session_state.get("trans_input", "")
        code_input = st.text_area("in", value=def_val, height=550, label_visibility="collapsed", placeholder=f"Paste {source_lang} code here...")
        st.session_state["trans_input"] = code_input

    with c_output:
        st.markdown(f'<div class="editor-label">🟢 COMPILED {target_lang}</div>', unsafe_allow_html=True)
        res = st.session_state.get("trans_result", "")
        if res:
            with st.container(border=True, height=550):
                st.code(res, language=target_lang.lower() if target_lang.lower() != 'c++' else 'cpp')
        else:
            st.text_area("out", value="Translated code will appear here...", height=550, disabled=True, label_visibility="collapsed")

    st.write("<br>", unsafe_allow_html=True)

    if st.button("🪄 INITIATE TRANSLATION MATRIX", type="primary", use_container_width=True):
        if not code_input.strip(): st.warning("⚠️ Provide code first!")
        else:
            st.session_state["trans_result"] = translate_code(code_input, source_lang, target_lang)
            
            supabase = get_supabase()
            uid = st.session_state.get("user_id")
            if supabase and uid:
                try:
                    p = supabase.table("profiles").select("lifetime_reviews").eq("id", uid).single().execute()
                    supabase.table("profiles").update({"lifetime_reviews": p.data.get("lifetime_reviews",0) + 1}).eq("id", uid).execute()
                except: pass
            st.rerun()

    if res:
        st.markdown('<div class="export-tools">', unsafe_allow_html=True)
        st.markdown("**📥 EXTRACT INTEL:**")
        dl1, dl2, dl3 = st.columns(3)
        with dl2:
             st.download_button("💾 Download Translation Source", data=res, file_name=f"translated_code.txt", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)
    if st.button("← Return to Dashboard", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()