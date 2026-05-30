import streamlit as st
import requests
import time
import os
import re
import base64
from groq import Groq
from utils import load_css, get_supabase

# --- GITHUB API HELPERS ---
def fetch_github_repos(token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        res = requests.get("https://api.github.com/user/repos?sort=updated&per_page=9", headers=headers)
        if res.status_code == 200: return res.json()
    except: pass
    return []

def fetch_repo_contents(token, owner, repo, path=""):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200: return res.json()
    except: pass
    return []

def fetch_file_content(token, download_url):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(download_url, headers=headers)
        if res.status_code == 200: return res.text
    except: return "# Error loading file."

def push_to_github(token, owner, repo, path, sha, new_content, commit_message):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    encoded_content = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha
    }
    try:
        res = requests.put(url, headers=headers, json=data)
        if res.status_code in [200, 201]:
            return True, ""
        else:
            err_data = res.json()
            return False, err_data.get('message', 'Unknown GitHub API Error')
    except Exception as e:
        return False, str(e)

# --- AI PROCESSING LOGIC ---
def process_github_task(code, task_type, filename):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return None, "API Key Missing"
    client = Groq(api_key=api_key)
    
    prompts = {
        "refactor": "Refactor and optimize this code for better performance and readability.",
        "docs": "Add professional docstrings and inline comments explaining the logic.",
        "security": "Scan for and fix any security vulnerabilities, bugs, or bad practices."
    }
    
    sys_prompt = f"""
    You are CodeSage, an elite AI developer. {prompts[task_type]}
    IMPORTANT RULES:
    1. You MUST return ONLY the fully updated, working code.
    2. Wrap the output securely in standard markdown code blocks (e.g. ```python ... ```).
    3. Do NOT add any conversational text before or after the code block. 
    4. Make sure it is ready to be committed directly to GitHub.
    """
    
    try:
        comp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": f"FILE: {filename}\n\n{code}"}],
            temperature=0.1
        )
        response = comp.choices[0].message.content or ""
        matches = re.findall(r"```[^\n]*\n(.*?)```", response, re.DOTALL)
        return matches[0].strip() if matches else response.strip(), None
    except Exception as e:
        return None, str(e)


# --- UI VIEWS ---
def render_review_page():
    repo = st.session_state.get("active_repo")
    if not repo:
        st.session_state["page"] = "github_sync"
        st.rerun()

    token = st.session_state.get("provider_token")
    owner = repo['owner']['login']
    repo_name = repo['name']

    # --- MASSIVE UI/UX CSS INJECTION ---
    st.markdown("""
        <style>
            /* File Selector Hacker Styling -> Acts as the panel tall box */
            div[data-testid="stRadio"] {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.95));
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-top: 4px solid #3B82F6;
                border-radius: 12px;
                padding: 25px;
                box-shadow: inset 0 0 30px rgba(59, 130, 246, 0.05), 0 10px 30px rgba(0,0,0,0.6);
                height: 600px;
                overflow-y: auto;
            }
            div[data-testid="stRadio"]::-webkit-scrollbar { width: 6px; }
            div[data-testid="stRadio"]::-webkit-scrollbar-thumb { background: #3B82F6; border-radius: 3px; }

            div[data-testid="stRadio"] > div { gap: 12px; }
            div[data-testid="stRadio"] label {
                background: rgba(2, 6, 23, 0.8);
                border: 1px solid #334155;
                border-left: 3px solid transparent;
                padding: 12px 15px;
                border-radius: 6px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                font-family: 'JetBrains Mono', monospace;
                color: #94A3B8;
                cursor: pointer;
            }
            div[data-testid="stRadio"] label:hover {
                border-left-color: #3B82F6;
                background: rgba(59, 130, 246, 0.15);
                color: #E2E8F0;
                transform: translateX(8px);
                box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
            }
            div[data-testid="stRadio"] label[data-checked="true"] {
                border-left-color: #00FFEA !important;
                background: linear-gradient(90deg, rgba(0, 255, 234, 0.2), transparent) !important;
                color: #00FFEA !important;
                text-shadow: 0 0 10px rgba(0, 255, 234, 0.5);
                box-shadow: inset 0 0 10px rgba(0,255,234,0.1);
            }
            
            /* Glowing Protocol Task Buttons via universal selection inside column 2 */
            div[data-testid="column"]:nth-child(2) div[data-testid="column"]:nth-child(1) button {
                border: 1px solid #00FFEA; color: #00FFEA; background: rgba(0,255,234,0.05); height: 80px; font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 900; letter-spacing: 1px; transition: 0.3s;
            }
            div[data-testid="column"]:nth-child(2) div[data-testid="column"]:nth-child(1) button:hover {
                background: rgba(0,255,234,0.2); box-shadow: 0 0 25px rgba(0,255,234,0.5); transform: translateY(-3px) scale(1.02);
            }
            
            div[data-testid="column"]:nth-child(2) div[data-testid="column"]:nth-child(2) button {
                border: 1px solid #3B82F6; color: #3B82F6; background: rgba(59,130,246,0.05); height: 80px; font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 900; letter-spacing: 1px; transition: 0.3s;
            }
            div[data-testid="column"]:nth-child(2) div[data-testid="column"]:nth-child(2) button:hover {
                background: rgba(59,130,246,0.2); box-shadow: 0 0 25px rgba(59,130,246,0.5); transform: translateY(-3px) scale(1.02);
            }
            
            div[data-testid="column"]:nth-child(2) div[data-testid="column"]:nth-child(3) button {
                border: 1px solid #F012BE; color: #F012BE; background: rgba(240,18,190,0.05); height: 80px; font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 900; letter-spacing: 1px; transition: 0.3s;
            }
            div[data-testid="column"]:nth-child(2) div[data-testid="column"]:nth-child(3) button:hover {
                background: rgba(240,18,190,0.2); box-shadow: 0 0 25px rgba(240,18,190,0.5); transform: translateY(-3px) scale(1.02);
            }
            
            /* Mac/Linux Terminal Window for Code */
            .cyber-terminal-header {
                background: linear-gradient(90deg, #0f172a, #1e293b);
                padding: 12px 20px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border: 1px solid #334155;
                border-bottom: none;
                display: flex;
                align-items: center;
                font-family: 'JetBrains Mono', monospace;
                color: #94a3b8;
                font-weight: bold;
                letter-spacing: 1px;
                margin-bottom: -1rem; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            }
            .cyber-terminal-header .dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: inset 0 0 5px rgba(0,0,0,0.8); }
            .dot.red { background-color: #FF5F56; }
            .dot.yellow { background-color: #FFBD2E; }
            .dot.green { background-color: #27C93F; }
            .terminal-title { margin-left: 15px; color: #3B82F6; font-size: 0.9rem;}
            
            /* Commit Override Widget */
            .commit-widget {
                background: linear-gradient(135deg, rgba(2,6,23,0.95), rgba(16,185,129,0.15));
                border: 1px solid rgba(16, 185, 129, 0.4);
                border-left: 5px solid #10B981;
                padding: 30px;
                border-radius: 12px;
                margin-top: 30px;
                box-shadow: 0 10px 30px rgba(16,185,129,0.2), inset 0 0 40px rgba(16,185,129,0.05);
                animation: slideUpFade 0.5s ease-out;
            }
            @keyframes slideUpFade { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
            
            .commit-btn-wrapper [data-testid="stButton"] button {
                background: linear-gradient(90deg, #10B981, #059669) !important; color: #020617 !important; height: 50px; font-weight: 900 !important; letter-spacing: 2px; border: none !important; box-shadow: 0 0 15px rgba(16,185,129,0.4) !important; transition: all 0.3s !important;
            }
            .commit-btn-wrapper [data-testid="stButton"] button:hover {
                transform: scale(1.02) !important; box-shadow: 0 0 30px rgba(16,185,129,0.8) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- TOP NAVIGATION BREADCRUMBS ---
    col_title, col_back = st.columns([8, 2])
    with col_title:
        st.markdown(f"<h2 style='font-family: \"JetBrains Mono\", monospace; margin-top:0; text-transform: uppercase;'><span style='color:#00FFEA; text-shadow: 0 0 10px rgba(0,255,234,0.5);'>{owner}</span> <span style='color:#64748B;'>/</span> <span style='color:#E2E8F0;'>{repo_name}</span> <span style='color:#F012BE; font-size:1.2rem; text-shadow: 0 0 10px rgba(240,18,190,0.5);'>// TARGET_LOCKED</span></h2>", unsafe_allow_html=True)
    with col_back:
        if st.button("⬅️ DISCONNECT UPLINK", use_container_width=True):
            st.session_state["active_repo"] = None
            st.session_state["gh_modified_code"] = None
            st.rerun()
    st.divider()

    # --- FILE EXPLORER & EDITOR ---
    c_files, c_code = st.columns([1, 3])
    
    with c_files:
        st.markdown("<h4 style='color:#60A5FA; font-family: \"JetBrains Mono\", monospace; margin-top:0;'>📁 DIRECTORY TREE</h4>", unsafe_allow_html=True)
        files = fetch_repo_contents(token, owner, repo_name)
        code_files = [f for f in files if f['name'].endswith(('.py', '.js', '.ts', '.tsx', '.css', '.html', '.java', '.sql', '.cpp', '.go', '.md'))]
        
        if code_files:
            file_names = [f['name'] for f in code_files]
            
            # Reset modified code if file changes
            selected_file_name = st.radio("Select Target:", file_names, label_visibility="collapsed")
            if st.session_state.get("gh_last_file") != selected_file_name:
                st.session_state["gh_modified_code"] = None
                st.session_state["gh_last_file"] = selected_file_name
                
            selected_node = next((f for f in code_files if f['name'] == selected_file_name), None)
        else:
            selected_node = None
            st.info("No standard code files found in the root directory.")

    with c_code:
        if selected_node:
            # 1. Fetch File Content
            raw_code = fetch_file_content(token, selected_node['download_url'])
            
            # 2. PROTOCOL EXECUTION MATRIX (Task Bar)
            st.markdown("<h4 style='color:#F012BE; font-family: \"JetBrains Mono\", monospace; margin-top:0; letter-spacing:2px; font-weight: bold;'>⚡ PROTOCOL EXECUTION MATRIX</h4>", unsafe_allow_html=True)
            
            t1, t2, t3 = st.columns(3)
            with t1:
                if st.button("🧠\nREFACTOR & OPTIMIZE", use_container_width=True):
                    with st.spinner("Rewriting Neural Pathways..."):
                        mod_code, err = process_github_task(raw_code, "refactor", selected_node['name'])
                        if not err: st.session_state["gh_modified_code"] = mod_code
                        else: st.error(err)
            with t2:
                if st.button("📝\nADD AUTO-DOCS", use_container_width=True):
                    with st.spinner("Generating Documentation..."):
                        mod_code, err = process_github_task(raw_code, "docs", selected_node['name'])
                        if not err: st.session_state["gh_modified_code"] = mod_code
                        else: st.error(err)
            with t3:
                if st.button("🛡️\nPATCH VULNERABILITIES", use_container_width=True):
                    with st.spinner("Securing System Architecture..."):
                        mod_code, err = process_github_task(raw_code, "security", selected_node['name'])
                        if not err: st.session_state["gh_modified_code"] = mod_code
                        else: st.error(err)
            
            st.write("<br>", unsafe_allow_html=True)

            # 3. View Code (Terminal Window)
            modified_code = st.session_state.get("gh_modified_code")
            
            if modified_code:
                st.markdown("<h4 style='color:#10B981; font-family:monospace;'>🟢 SYSTEM UPGRADE PREVIEW</h4>", unsafe_allow_html=True)
                tab1, tab2 = st.tabs(["[ PREVIEW ]", "[ ORIGINAL ]"])
                with tab1:
                    st.markdown(f"<div class='cyber-terminal-header'><span class='dot red'></span><span class='dot yellow'></span><span class='dot green'></span><span class='terminal-title'>~/codesage/optimized/{selected_node['name']}</span></div>", unsafe_allow_html=True)
                    st.code(modified_code, language="python") 
                with tab2:
                    st.markdown(f"<div class='cyber-terminal-header'><span class='dot red'></span><span class='dot yellow'></span><span class='dot green'></span><span class='terminal-title'>~/github/raw/{selected_node['name']}</span></div>", unsafe_allow_html=True)
                    st.code(raw_code, language="python")
                    
                # 4. COMMIT TO GITHUB WIDGET
                st.markdown('<div class="commit-widget">', unsafe_allow_html=True)
                st.markdown("<h3 style='color:#10B981; margin-top:0; font-family:monospace; letter-spacing:2px;'>🚀 SYSTEM OVERRIDE: PUSH TO GITHUB</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color:#94A3B8; font-size:0.9rem; margin-bottom:20px;'>Commit these optimized changes directly to the remote repository.</p>", unsafe_allow_html=True)
                
                commit_msg = st.text_input("COMMIT MESSAGE:", value=f"CodeSage AI Update: Optimized {selected_node['name']}")
                
                st.markdown("<div class='commit-btn-wrapper'>", unsafe_allow_html=True)
                if st.button("CONFIRM UPLINK OVERRIDE", type="primary", use_container_width=True):
                    with st.spinner("Transmitting data to GitHub Mainframe..."):
                        success, err_msg = push_to_github(
                            token=token, 
                            owner=owner, 
                            repo=repo_name, 
                            path=selected_node['path'], 
                            sha=selected_node['sha'], 
                            new_content=modified_code, 
                            commit_message=commit_msg
                        )
                        if success:
                            st.toast("Success! Neural pathways successfully merged with GitHub.", icon="✅")
                            st.session_state["gh_modified_code"] = None # Reset after successful push
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Uplink Failed: {err_msg}")
                            st.info("💡 Fix: Did you add `&scopes=repo` to your login URL in `app.py`? Make sure to Logout and Log back in!")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.markdown("<h4 style='color:#60A5FA; font-family:monospace;'>🔴 RAW DATA STREAM</h4>", unsafe_allow_html=True)
                st.markdown(f"<div class='cyber-terminal-header'><span class='dot red'></span><span class='dot yellow'></span><span class='dot green'></span><span class='terminal-title'>~/github/raw/{selected_node['name']}</span></div>", unsafe_allow_html=True)
                st.code(raw_code, language="python")


def render_github_page():
    load_css()
    
    # Switch to the Review Interface if a repo is currently targeted
    if st.session_state.get("active_repo"):
        render_review_page()
        return

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
                animation: textGlowCyan 3s infinite alternate;
            }
            @keyframes textGlowCyan {
                0% { text-shadow: 0 0 10px rgba(0, 255, 234, 0.4); }
                100% { text-shadow: 0 0 25px rgba(0, 255, 234, 0.8), 0 0 40px rgba(0, 255, 234, 0.4); }
            }
            .cyber-sub { text-align: center; color: #94A3B8; letter-spacing: 4px; font-family: 'JetBrains Mono', monospace; font-size: 1rem; margin-bottom: 30px; }
            
            .tool-icon {
                display: inline-block;
                animation: float 3s ease-in-out infinite;
                -webkit-background-clip: border-box !important;
                -webkit-text-fill-color: initial !important;
            }
            @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

            .repo-cyber-card {
                background: linear-gradient(180deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-left: 4px solid #00FFEA;
                padding: 25px; border-radius: 12px; margin-bottom: 15px;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 10px 20px rgba(0,0,0,0.5), inset 0 0 20px rgba(0, 255, 234, 0.05);
                position: relative;
                overflow: hidden;
                animation: slideUpFade 0.5s ease-out forwards;
            }
            .repo-cyber-card::before {
                content: ""; position: absolute; top:0; left: 0; width: 100%; height: 100%; 
                background: linear-gradient(135deg, transparent, rgba(255,255,255,0.05), transparent); 
                transform: translateY(100%); transition: all 0.6s; pointer-events: none;
            }
            .repo-cyber-card:hover::before { transform: translateY(-100%); }
            .repo-cyber-card:hover { 
                border-color: #00FFEA; 
                background: linear-gradient(180deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 1)); 
                box-shadow: 0 15px 35px rgba(0, 255, 234, 0.3), inset 0 0 30px rgba(0, 255, 234, 0.1); 
                transform: translateY(-5px) scale(1.02);
            }
            
            button[kind="primary"] {
                background: linear-gradient(90deg, #00FFEA, #3B82F6, #00FFEA) !important;
                background-size: 200% auto !important;
                color: #020617 !important;
                font-weight: 900 !important;
                border: none !important;
                animation: gradientShiftCyan 3s linear infinite !important;
                transition: all 0.3s !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                box-shadow: 0 0 20px rgba(0, 255, 234, 0.4) !important;
            }
            button[kind="primary"]:hover { transform: scale(1.02) !important; box-shadow: 0 0 30px rgba(0, 255, 234, 0.6) !important; }
            @keyframes gradientShiftCyan { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
            @keyframes slideUpFade { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'><span class='tool-icon'>🐙</span> GITHUB COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>SYNC, ANALYZE, AND PUSH UPDATES IN REAL-TIME</p>", unsafe_allow_html=True)
    st.divider()

    c_head, c_btn = st.columns([4, 1])
    with c_head:
        st.markdown("<span style='color:#94A3B8; font-family:monospace;'>ESTABLISH CONNECTION TO TARGET REPOSITORIES...</span>", unsafe_allow_html=True)
    with c_btn:
        if st.button("🔄 INITIALIZE UPLINK", use_container_width=True, type="primary"):
            token = st.session_state.get("provider_token")
            if token: st.session_state["repos"] = fetch_github_repos(token)
            else: st.warning("Uplink failed: GitHub token missing.")

    repos = st.session_state.get("repos", [])
    if repos:
        st.write("<br>", unsafe_allow_html=True)
        for i in range(0, len(repos), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(repos):
                    repo = repos[i+j]
                    with cols[j]:
                        lang_color = "#F012BE" if repo.get('language') == "Python" else "#F59E0B" if repo.get('language') == "JavaScript" else "#3B82F6"
                        
                        st.markdown(f'''
                            <div class="repo-cyber-card" style="border-left-color: {lang_color};">
                                <h3 style="color: #F1F5F9; margin-bottom: 5px; font-family:monospace;">{repo['name']}</h3>
                                <p style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 15px;">
                                    <span style="color:{lang_color}; font-weight:bold;">{repo.get('language', 'Data')}</span> • ⭐ {repo['stargazers_count']}
                                </p>
                            </div>
                        ''', unsafe_allow_html=True)
                        if st.button(f"⚡ TARGET PROTOCOL", key=f"btn_{repo['id']}", use_container_width=True):
                            st.session_state["active_repo"] = repo
                            st.session_state["gh_modified_code"] = None # Reset state
                            st.rerun()
    else:
        st.info("Click 'INITIALIZE UPLINK' to securely fetch your repositories.")