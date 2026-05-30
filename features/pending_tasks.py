import streamlit as st
import os
import re
from groq import Groq
from utils import get_supabase, load_css

def solve_task(task_desc, code_context):
    """Uses Groq to fix bugs or implement features requested by the user."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Error: GROQ_API_KEY not found."
        
    client = Groq(api_key=api_key)
    system_prompt = """
    You are an elite Senior Developer. The user will provide a TASK/BUG description, and a CODE CONTEXT.
    Your job is to write the completed, fixed, or updated code.
    
    1. First, briefly explain how you solved the problem in 2-3 sentences.
    2. Then, provide the COMPLETE, working code wrapped in a markdown code block (```).
    """
    
    try:
        with st.spinner("CodeSage is solving the issue... 🛠️"):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, 
                          {"role": "user", "content": f"TASK:\n{task_desc}\n\nCODE CONTEXT:\n{code_context}"}],
                temperature=0.2
            )
            return completion.choices[0].message.content or ""
    except Exception as e:
        return f"❌ Error: {str(e)}"

def render_pending_tasks_page():
    load_css()
    st.markdown("""
        <style>
            .cyber-header {
                font-family: 'JetBrains Mono', monospace; 
                font-size: 3.2rem; 
                font-weight: 800; 
                background: linear-gradient(135deg, #F43F5E, #fff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 20px rgba(244, 63, 94, 0.5);
                text-align: center;
                text-transform: uppercase;
                margin-bottom: 0px;
                animation: textGlowRed 3s infinite alternate;
            }
            @keyframes textGlowRed {
                0% { text-shadow: 0 0 10px rgba(244, 63, 94, 0.4); }
                100% { text-shadow: 0 0 25px rgba(244, 63, 94, 0.8), 0 0 40px rgba(244, 63, 94, 0.4); }
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
                0%, 100% { transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 10px rgba(244, 63, 94, 0.4)); }
                50% { transform: scale(1.15) rotate(-5deg); filter: drop-shadow(0 0 25px rgba(244, 63, 94, 1)); }
            }

            .task-header { 
                background: linear-gradient(135deg, rgba(244, 63, 94, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%); 
                border: 1px solid rgba(244, 63, 94, 0.4); 
                box-shadow: 0 0 20px rgba(244, 63, 94, 0.3); 
                padding: 30px; 
                border-radius: 12px; 
                margin-bottom: 30px;
                position: relative;
                overflow: hidden;
            }
            .task-header::after {
                content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(to right, transparent, rgba(244, 63, 94, 0.15), transparent);
                transform: translateX(-100%);
                animation: scanRight 3s linear infinite;
                pointer-events: none;
            }
            @keyframes scanRight { 100% { transform: translateX(100%); } }

            .editor-label { 
                font-size: 0.9rem; 
                color: #F43F5E; 
                font-family: 'JetBrains Mono', monospace; 
                font-weight: 800; 
                text-transform: uppercase; 
                margin-bottom: 5px; 
                letter-spacing: 2px; 
                animation: pulseTextRed 3s infinite alternate; 
            }
            @keyframes pulseTextRed { 0% { opacity: 0.8; text-shadow: 0 0 5px rgba(244, 63, 94, 0.3); } 100% { opacity: 1; text-shadow: 0 0 15px rgba(244, 63, 94, 0.8); } }
            
            .stTextArea textarea { 
                background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(15,23,42,0.8)) !important;
                border: 1px solid rgba(244, 63, 94, 0.3) !important; 
                border-left: 4px solid #8B5CF6 !important;
                color: #E2E8F0 !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                border-radius: 8px !important; 
                box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .stTextArea textarea:focus { 
                border-color: #F43F5E !important; 
                border-left: 4px solid #F43F5E !important;
                box-shadow: 0 0 25px rgba(244, 63, 94, 0.3), inset 0 0 15px rgba(244, 63, 94, 0.1) !important; 
                transform: scale(1.01);
            }
            
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(15,23,42,0.8));
                border: 1px solid rgba(244, 63, 94, 0.3);
                border-left: 4px solid #8B5CF6;
                border-radius: 8px;
                box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
                color: #E2E8F0;
                overflow-y: auto;
            }

            [data-testid="stFileUploader"] > div {
                background: rgba(2, 6, 23, 0.6) !important;
                border: 1px dashed rgba(244, 63, 94, 0.5) !important;
                border-radius: 8px;
                transition: all 0.3s;
            }
            [data-testid="stFileUploader"] > div:hover {
                border-color: #8B5CF6 !important;
                background: rgba(139, 92, 246, 0.05) !important;
                box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
            }

            button[kind="primary"] {
                background: linear-gradient(90deg, #F43F5E, #8B5CF6, #F43F5E) !important;
                background-size: 200% auto !important;
                color: #fff !important;
                font-weight: 900 !important;
                border: none !important;
                animation: gradientShiftRed 3s linear infinite !important;
                transition: all 0.3s !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                box-shadow: 0 0 20px rgba(244, 63, 94, 0.4) !important;
            }
            button[kind="primary"]:hover {
                transform: scale(1.01) !important;
                box-shadow: 0 0 30px rgba(244, 63, 94, 0.6) !important;
            }
            @keyframes gradientShiftRed { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'><span class='tool-icon'>🛠️</span> AI Task & Bug Solver</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>DESCRIBE THE BUG, UPLOAD YOUR SCRIPT, AND LET CODESAGE EXECUTE THE FIX.</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="task-header">', unsafe_allow_html=True)
    st.markdown('<div class="editor-label">🎯 Mission Directives</div>', unsafe_allow_html=True)
    task_description = st.text_input("task", label_visibility="collapsed", placeholder="e.g. 'Fix the NullReferenceException' or 'Add a sorting algorithm to this logic'")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="editor-label">📂 Attached System Logs / Snippet</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload broken script", type=["py", "js", "java", "cpp", "ts", "html", "css", "sql"], key="task_upload", label_visibility="collapsed")
        if uploaded_file is not None:
            if st.session_state.get("task_last_file") != uploaded_file.name:
                try:
                    file_contents = uploaded_file.getvalue().decode("utf-8")
                    st.session_state["task_input"] = file_contents
                    st.session_state["task_last_file"] = uploaded_file.name
                    st.toast(f"Loaded {uploaded_file.name}", icon="✅")
                except: st.error("Error reading file.")
                
    st.write("<br>", unsafe_allow_html=True)

    c_input, c_output = st.columns(2)
    with c_input:
        st.markdown('<div class="editor-label">🔴 Buggy Environment Context</div>', unsafe_allow_html=True)
        def_val = st.session_state.get("task_input", "")
        code_input = st.text_area("in", value=def_val, height=500, label_visibility="collapsed", placeholder="Paste the code that needs to be fixed here...")
        st.session_state["task_input"] = code_input

    with c_output:
        st.markdown('<div class="editor-label">🟢 Compiled AI Solution</div>', unsafe_allow_html=True)
        res = st.session_state.get("task_result", "")
        if res:
            with st.container(height=500, border=True):
                st.markdown(res)
        else:
            st.text_area("out", value="The explanation and fixed code will appear here...", height=500, disabled=True, label_visibility="collapsed")

    st.write("<br>", unsafe_allow_html=True)

    # Solve execution logic bound tightly to highly visible interface block
    if st.button("🚀 INITIATE BUG FIX PROTOCOL", type="primary", use_container_width=True):
        if not task_description.strip() or not code_input.strip():
            st.warning("⚠️ Please provide both a task description and code context!")
        else:
            st.session_state["task_result"] = solve_task(task_description, code_input)
            
            # Gamification Drop
            supabase = get_supabase()
            uid = st.session_state.get("user_id")
            if supabase and uid:
                try:
                    p = supabase.table("profiles").select("lifetime_reviews").eq("id", uid).single().execute()
                    supabase.table("profiles").update({"lifetime_reviews": p.data.get("lifetime_reviews",0) + 3}).eq("id", uid).execute()
                except: pass
            st.rerun()

    if res:
        st.write("<br>", unsafe_allow_html=True)
        col_pad1, col_dl, col_pad2 = st.columns([1,2,1])
        with col_dl:
            st.download_button("💾 Export Verified Solution Source", data=res, file_name="solved_code.txt", use_container_width=True)

    st.write("<br><br>", unsafe_allow_html=True)
    if st.button("← Return to Dashboard", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()