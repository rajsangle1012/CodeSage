import streamlit as st
from utils import get_supabase, load_css

def render_history_page():
    load_css()
    
    # Get user context
    user_profile = st.session_state.get("profile", {})
    user_id = user_profile.get("id") or st.session_state.get("user_id")
    supabase = get_supabase()

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

            /* Style Expanders to look like Cyber-Panels */
            [data-testid="stExpander"] {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.95));
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-left: 4px solid #3B82F6;
                border-radius: 12px;
                box-shadow: inset 0 0 20px rgba(59, 130, 246, 0.05), 0 5px 15px rgba(0,0,0,0.5);
                margin-bottom: 15px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            [data-testid="stExpander"]:hover {
                border-color: rgba(59, 130, 246, 0.8);
                box-shadow: inset 0 0 30px rgba(59, 130, 246, 0.1), 0 10px 25px rgba(0,0,0,0.6);
                transform: translateX(8px);
            }
            
            /* Expander Title Text */
            [data-testid="stExpander"] p {
                font-family: 'JetBrains Mono', monospace !important;
                font-weight: bold !important;
                color: #60A5FA !important;
                letter-spacing: 1px;
            }
            
            /* Delete/Primary Button Styling */
            button[kind="primary"] {
                background: linear-gradient(90deg, #EF4444, #F43F5E, #EF4444) !important;
                background-size: 200% auto !important;
                color: #fff !important;
                font-weight: 900 !important;
                border: none !important;
                animation: gradientShiftRed 3s linear infinite !important;
                transition: all 0.3s !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                box-shadow: 0 0 20px rgba(239, 68, 68, 0.4) !important;
            }
            button[kind="primary"]:hover { transform: scale(1.02) !important; box-shadow: 0 0 30px rgba(239, 68, 68, 0.7) !important; }
            @keyframes gradientShiftRed { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
            
            /* Secondary Buttons */
            button[kind="secondary"] {
                background: rgba(30, 41, 59, 0.5) !important;
                border: 1px solid rgba(59, 130, 246, 0.4) !important;
                color: #60A5FA !important;
                font-family: 'JetBrains Mono', monospace !important;
                font-weight: bold !important;
                transition: all 0.3s !important;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            button[kind="secondary"]:hover {
                background: rgba(59, 130, 246, 0.1) !important;
                border-color: #3B82F6 !important;
                color: #fff !important;
                box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
                transform: translateY(-2px);
            }

            /* Stats Bar */
            .history-stats {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid #1E293B;
                border-radius: 8px;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                border-left: 4px solid #FBBF24;
            }
            .stats-text {
                font-family: 'JetBrains Mono', monospace;
                color: #FBBF24;
                font-size: 1.1rem;
                font-weight: bold;
                letter-spacing: 1px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'><span class='tool-icon'>📜</span> ARCHIVE MATRIX</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>REVIEW PAST ANALYSES, RE-EXECUTE TARGETS, AND MANAGE DATA LOGS.</p>", unsafe_allow_html=True)
    st.divider()

    if not supabase:
        st.error("Database connection failed.")
        return

    # --- DELETE HISTORY LOGIC ---
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear History", type="primary", use_container_width=True):
            try:
                # Delete all rows in the reviews table for this specific user
                supabase.table("reviews").delete().eq("user_id", user_id).execute()
                st.success("History successfully cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to clear history: {e}")

    # --- FETCH AND DISPLAY HISTORY ---
    try:
        # Fetch records sorted by newest first
        res = supabase.table("reviews").select("*").eq("user_id", user_id).order("id", desc=True).execute()
        records = res.data

        if not records:
            st.markdown("<div class='history-stats'><span class='stats-text'>📭 MAINFRAME ARCHIVES EMPTY. NO DATA LOGGED.</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='history-stats'><span class='stats-text'>📡 EXTRACTED {len(records)} NEURAL PACKETS</span></div>", unsafe_allow_html=True)
            for idx, record in enumerate(records):
                lang = record.get("language", "Code")
                snippet = record.get("code_snippet", "")
                
                # Create an expander for each piece of code
                with st.expander(f"🕰️ Analysis #{len(records) - idx} - {lang} Snippet"):
                    st.code(snippet, language=lang.lower() if lang else "python")
                    
                    # Optional: Add a button to instantly send this code back to the Task Solver!
                    if st.button("⚡ RE-ROUTE TO TASK SOLVER", key=f"solve_{record['id']}"):
                        st.session_state["latest_analyzed_code"] = snippet
                        st.session_state["latest_analyzed_language"] = lang
                        st.session_state["page"] = "pending_tasks"
                        st.rerun()

    except Exception as e:
        st.error(f"Error fetching history: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ DASHBOARD MAIN UPLINK"):
        st.session_state["page"] = "home"
        st.rerun()