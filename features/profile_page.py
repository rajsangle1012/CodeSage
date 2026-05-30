import streamlit as st
from utils import load_css, get_supabase

def render_profile_page(profile):
    load_css()
    
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

            .profile-card {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.95));
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-top: 4px solid #3B82F6;
                border-radius: 12px;
                padding: 40px 30px;
                box-shadow: inset 0 0 30px rgba(59, 130, 246, 0.05), 0 10px 30px rgba(0,0,0,0.6);
                text-align: center;
                position: relative;
                overflow: hidden;
                animation: slideUpFade 0.5s ease-out;
            }
            @keyframes slideUpFade { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }

            .profile-card::after {
                content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(59, 130, 246, 0.05) 2px, rgba(59, 130, 246, 0.05) 4px);
                pointer-events: none;
                z-index: 1;
            }
            
            .content-wrapper { position: relative; z-index: 2; }
            
            .profile-avatar {
                width: 140px; height: 140px;
                border-radius: 50%;
                border: 4px solid #00FFEA;
                box-shadow: 0 0 35px rgba(0, 255, 234, 0.6);
                margin: 0 auto 20px auto;
                object-fit: cover;
                animation: pulseAvatar 2s infinite alternate;
                display: block;
            }
            @keyframes pulseAvatar {
                0% { box-shadow: 0 0 20px rgba(0, 255, 234, 0.4); transform: scale(1); border-color: #00FFEA;}
                100% { box-shadow: 0 0 45px rgba(0, 255, 234, 0.8); transform: scale(1.05); border-color: #fff;}
            }

            .info-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 40px;
                text-align: left;
            }
            .info-box {
                background: rgba(2, 6, 23, 0.6);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-left: 4px solid #00FFEA;
                padding: 18px;
                border-radius: 6px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.4);
                transition: transform 0.3s;
            }
            .info-box:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.6); border-left-color: #fff;}
            
            .info-label { color: #64748B; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; margin-bottom: 5px; }
            .info-value { color: #F1F5F9; font-size: 1.2rem; font-weight: bold; font-family: 'JetBrains Mono', monospace; }
            .info-value.cyan { color: #00FFEA; text-shadow: 0 0 10px rgba(0,255,234,0.4); }

            /* Logout Button completely hijacked CSS */
            .logout-container [data-testid="stButton"] button {
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
                height: 55px;
                margin-top: 50px;
                width: 100% !important;
            }
            .logout-container [data-testid="stButton"] button:hover { transform: scale(1.02) !important; box-shadow: 0 0 35px rgba(239, 68, 68, 0.8) !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'><span class='tool-icon'>🤖</span> DEPLOYMENT ID</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>IDENTITY VERIFICATION AND SYSTEM CLEARANCE</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        avatar = profile.get('avatar_url') or "https://api.dicebear.com/7.x/bottts/svg?seed=codesage"
        
        html_content = f"""
<div class="profile-card">
<div class="content-wrapper">
<img src="{avatar}" class="profile-avatar" />
<h2 style='color:#F1F5F9; font-family: "JetBrains Mono", monospace; margin:0; text-transform: uppercase; letter-spacing: 2px;'>{profile.get('full_name', 'Unknown User')}</h2>
<p style='color:#60A5FA; font-family: "JetBrains Mono", monospace; margin-top:5px; margin-bottom: 0;'>@{profile.get('username', 'developer')}</p>

<div class="info-grid">
<div class="info-box">
<div class="info-label">System User ID</div>
<div class="info-value" style="font-size: 1rem;">{str(profile.get('id'))[:13]}...</div>
</div>
<div class="info-box" style="border-left-color: #F012BE;">
<div class="info-label">Clearance Level</div>
<div class="info-value cyan" style="color: #F012BE; text-shadow: 0 0 10px rgba(240,18,190,0.5);">DIAMOND SAGE</div>
</div>
<div class="info-box" style="border-left-color: #FBBF24;">
<div class="info-label">Total Neural Audits</div>
<div class="info-value" style="color: #FBBF24; text-shadow: 0 0 10px rgba(251,191,36,0.3);">{profile.get('lifetime_reviews', 0)} XP</div>
</div>
<div class="info-box" style="border-left-color: #10B981;">
<div class="info-label">Account Status</div>
<div class="info-value" style="color: #10B981; text-shadow: 0 0 10px rgba(16,185,129,0.3);">ACTIVE UPLINK</div>
</div>
</div>
</div>
</div>
"""
        st.markdown(html_content, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        with st.expander("⚙️ CONFIGURE SYSTEM IDENTITY"):
            new_name = st.text_input("Display Name", value=profile.get('full_name', ''))
            new_username = st.text_input("Network Alias", value=profile.get('username', ''))
            
            if st.button("⚡ SYNCHRONIZE IDENTITY", use_container_width=True):
                try:
                    supabase = get_supabase()
                    supabase.table("profiles").update({
                        "full_name": new_name,
                        "username": new_username
                    }).eq("id", profile.get("id")).execute()
                    
                    # Update local state cache to immediately reflect
                    st.session_state["profile"]["full_name"] = new_name
                    st.session_state["profile"]["username"] = new_username
                    st.success("✅ Neural Identity Synchronization Complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Sync Failed: {e}")

        st.write("<br>", unsafe_allow_html=True)
        if st.button("⬅️ DASHBOARD MAIN UPLINK", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()

        st.markdown('<div class="logout-container">', unsafe_allow_html=True)
        if st.button("TERMINATE CONNECTION (LOGOUT)", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)
