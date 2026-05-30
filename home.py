import streamlit as st
from utils import get_supabase, load_css

def render_home_page(profile):
    load_css()
    
    # --- 1. DATA FETCHING (LIVE LOGIC) ---
    user_id = profile.get('id') or st.session_state.get("user_id")
    supabase = get_supabase()
    
    # Initialize all independent values to 0
    active_projects = 0
    total_xp = profile.get('lifetime_reviews', 0) # 'lifetime_reviews' acts as the permanent XP Score column
    live_code_score = 0 
    
    if supabase and user_id:
        try:
            # Active projects and Code Score depend on the live history
            res = supabase.table("reviews").select("quality_score").eq("user_id", user_id).execute()
            if res.data and len(res.data) > 0:
                active_projects = len(res.data) 
                total_points = sum(row.get('quality_score', 0) for row in res.data)
                live_code_score = total_points // active_projects
        except Exception as e:
            st.error(f"Error fetching stats: {e}")

    # --- 2. FUTURISTIC GRADE LOGIC ---
    if live_code_score == 0: 
        grade, color, shadow = "OFFLINE", "#94A3B8", "none"
    elif live_code_score >= 90: 
        grade, color, shadow = "OPTIMAL", "#00FFEA", "0 0 15px rgba(0,255,234,0.6)"
    elif live_code_score >= 80: 
        grade, color, shadow = "STABLE", "#3B82F6", "0 0 15px rgba(59,130,246,0.6)"
    else: 
        grade, color, shadow = "CRITICAL", "#F012BE", "0 0 15px rgba(240,18,190,0.6)"

    # --- 3. HIGH-TECH CYBER CSS ---
    # --- 3. HIGH-TECH CYBER CSS ---
    st.markdown(f"""
        <style>
            /* Hero Text Glow Animation */
            @keyframes neonPulse {{
                0%, 100% {{ text-shadow: 0 0 10px rgba(0, 255, 234, 0.4), 0 0 20px rgba(0, 255, 234, 0.2); }}
                50% {{ text-shadow: 0 0 20px rgba(0, 255, 234, 0.8), 0 0 40px rgba(0, 255, 234, 0.4); }}
            }}
            .cyber-hero-text {{ 
                font-family: 'JetBrains Mono', monospace; 
                font-size: 3.2rem; 
                font-weight: 800; 
                background: linear-gradient(135deg, #00FFEA, #fff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: neonPulse 3s infinite alternate;
                letter-spacing: 2px;
                text-transform: uppercase;
                margin-bottom: 0px;
                display: inline-block;
            }}
            
            /* Blinking Cyber Cursor */
            .cyber-cursor {{
                display: inline-block;
                width: 18px;
                height: 3rem;
                background-color: #00FFEA;
                vertical-align: text-bottom;
                animation: blink 1s step-end infinite;
                margin-left: 12px;
                box-shadow: 0 0 15px #00FFEA;
            }}
            @keyframes blink {{ 50% {{ opacity: 0; }} }}
            
            /* Stat Cards Enhancements */
            .cyber-stat-card {{
                background: linear-gradient(180deg, rgba(15,23,42,0.8) 0%, rgba(2,6,23,0.9) 100%);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-top: 4px solid #00FFEA;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                border-radius: 16px;
                padding: 20px 20px;
                text-align: center;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                min-height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                position: relative;
                overflow: hidden;
            }}
            .cyber-stat-card::after {{
                content: "";
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(to bottom, transparent 40%, rgba(0, 255, 234, 0.1) 50%, transparent 60%);
                background-size: 100% 200%;
                animation: cardScanline 4s linear infinite;
                pointer-events: none;
                z-index: 0;
            }}
            @keyframes cardScanline {{
                0% {{ background-position: 0% -100%; }}
                100% {{ background-position: 0% 200%; }}
            }}
            .cyber-stat-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 255, 234, 0.1);
                border-color: rgba(255,255,255,0.15);
            }}
            .cyber-stat-number {{ 
                font-size: 3.5rem; 
                font-weight: 800; 
                font-family: 'JetBrains Mono', monospace; 
                margin-bottom: 5px; 
                z-index: 2;
                position: relative;
                animation: floatNum 6s infinite ease-in-out;
            }}
            @keyframes floatNum {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-3px); }}
            }}
            .cyber-stat-label {{ 
                font-size: 0.85rem; 
                color: var(--text-muted); 
                text-transform: uppercase; 
                letter-spacing: 2px; 
                font-weight: 800;
                z-index: 2;
                position: relative;
            }}

            /* Tool Cards Enhancements */
            .cyber-tool-card {{
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.02) 0%, rgba(0, 0, 0, 0.2) 100%);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-left: 4px solid var(--accent-purple);
                border-radius: 12px;
                padding: 30px 20px;
                text-align: center;
                transition: all 0.3s;
                position: relative;
                overflow: hidden;
            }}
            .cyber-tool-card::before {{
                content: "";
                position: absolute;
                top: -50%; left: -50%; width: 200%; height: 200%;
                background: radial-gradient(circle, rgba(240, 18, 190, 0.1) 0%, transparent 70%);
                opacity: 0;
                transition: opacity 0.5s;
                z-index: 0;
                pointer-events: none;
            }}
            .cyber-tool-card:hover {{
                border-color: var(--text-main);
                box-shadow: 0 10px 30px rgba(0,0,0,0.4), 0 0 20px rgba(240, 18, 190, 0.2);
                transform: translateY(-4px);
            }}
            .cyber-tool-card:hover::before {{ opacity: 1; }}
            
            .tool-emoji {{
                display: inline-block;
                animation: hoverMatrix 4s infinite ease-in-out;
                z-index: 2;
                position: relative;
            }}
            @keyframes hoverMatrix {{
                0%, 100% {{ transform: translateY(0) rotate(0deg) scale(1); }}
                50% {{ transform: translateY(-5px) rotate(5deg) scale(1.1); filter: drop-shadow(0 0 10px rgba(255,255,255,0.5)); }}
            }}
            
            .tool-title {{
                color: var(--text-main);
                font-family: 'JetBrains Mono', monospace;
                letter-spacing: 1px;
                font-weight: 800;
                font-size: 1.1rem;
                margin-top: 15px;
                margin-bottom: 15px;
                text-transform: uppercase;
                z-index: 2; 
                position: relative;
            }}
        </style>
    """, unsafe_allow_html=True)

    # --- 4. TOP NAVIGATION ---
    nav_c1, nav_c2 = st.columns([7, 3])
    with nav_c1:
        raw_name = profile.get('full_name') or profile.get('username') or 'Developer'
        display_name = str(raw_name).split(' ')[0]
        st.markdown(f"<div><span class='cyber-hero-text'>UPLINK: {display_name}</span><span class='cyber-cursor'></span></div>", unsafe_allow_html=True)
    with nav_c2:
        st.write("<div style='padding-top: 25px;'></div>", unsafe_allow_html=True)
        if st.button("📂 ACCESS LOGS", use_container_width=True, key="history_nav_btn"):
            st.session_state["page"] = "history"; st.rerun()

    st.write("<br>", unsafe_allow_html=True)

    # --- 5. NEURAL SCOREBOARD ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.markdown(f'''
            <div class="cyber-stat-card" style="border-top-color: #3B82F6;">
                <div class="cyber-stat-number" style="color: #F8FAFC;">{active_projects}</div>
                <div class="cyber-stat-label">Active Scans</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with c2: 
        st.markdown(f'''
            <div class="cyber-stat-card" style="border-top-color: #F59E0B;">
                <div class="cyber-stat-number" style="color: #F59E0B; text-shadow: 0 0 10px rgba(245,158,11,0.4);">{total_xp}</div>
                <div class="cyber-stat-label">Total XP</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with c3: 
        st.markdown(f'''
            <div class="cyber-stat-card" style="border-top-color: #00FFEA;">
                <div class="cyber-stat-number" style="color: #00FFEA; text-shadow: 0 0 10px rgba(0,255,234,0.4);">{live_code_score}</div>
                <div class="cyber-stat-label">System Score</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with c4: 
        st.markdown(f'''
            <div class="cyber-stat-card" style="border-top-color: {color};">
                <div class="cyber-stat-number" style="color: {color}; text-shadow: {shadow}; font-size: 2rem;">{grade}</div>
                <div class="cyber-stat-label">Status</div>
            </div>
        ''', unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family: monospace; color: #94A3B8; letter-spacing: 2px;'>SYSTEM PROTOCOLS & TOOLS</h3>", unsafe_allow_html=True)
    
    # --- 6. FUTURISTIC TOOL BOX FUNCTION ---
    def tool_box(title, emoji, page_name, btn_label, is_primary=False, border_color="#F012BE"):
        unique_key = f"btn_{title.lower().replace(' ', '_')}_{page_name}"
        
        with st.container():
            st.markdown(f"""
                <div class="cyber-tool-card" style="border-left-color: {border_color};">
                    <h2 style='font-size: 2.2rem; margin-bottom: 0px;'><span class='tool-emoji'>{emoji}</span></h2>
                    <div class='tool-title'>{title.upper()}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(btn_label, key=unique_key, use_container_width=True, type="primary" if is_primary else "secondary"):
                st.session_state["page"] = page_name; st.rerun()

    # --- 7. TOOLSET GRID ---
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1: tool_box("AI Architect", "🧠", "ai_analysis", "INITIATE AUDIT", True, "#00FFEA")
    with r1_c2: tool_box("Task Solver", "🚀", "pending_tasks", "FIX LOGIC", False, "#F012BE")
    with r1_c3: tool_box("Doc Generator", "📝", "docs", "GENERATE DOCS", False, "#3B82F6")

    st.write("<br>", unsafe_allow_html=True)
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    with r2_c1: tool_box("Security Scan", "🛡️", "security_scan", "SCAN THREATS", False, "#10B981") 
    with r2_c2: tool_box("AI Polyglot", "🌐", "translator", "TRANSLATE CODE", False, "#F59E0B")
    with r2_c3: tool_box("Leaderboard", "🏆", "leaderboard", "VIEW RANKINGS", False, "#8B5CF6")
    
    st.write("<br>", unsafe_allow_html=True)
    r3_c1, r3_c2, r3_c3 = st.columns(3)
    with r3_c2: tool_box("GitHub Uplink", "🐙", "github_sync", "SYNC REPOS", False, "#E2E8F0")