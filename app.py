import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import requests
import hashlib
import base64
import secrets
import textwrap
import time
import pandas as pd
import altair as alt
import random
import calendar
import datetime

# --- IMPORTS FROM MODULES ---
from utils import load_css
import home
import features.ai_analysis 
import features.pending_tasks
import features.history
import features.translator
import features.leaderboard
import features.docs
import features.github_sync
import features.security_scan
import features.profile_page

# --- 1. CONFIGURATION ---
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    st.error("❌ API Keys missing. Check .env file.")
    st.stop()

supabase = create_client(url, key)
st.set_page_config(page_title="CodeSage", page_icon="🧠", layout="wide")

# --- 3. AUTH LOGIC ---
def get_auth_link():
    verifier = secrets.token_urlsafe(32)
    m = hashlib.sha256()
    m.update(verifier.encode())
    challenge = base64.urlsafe_b64encode(m.digest()).decode().rstrip('=')
    try: 
        with open(".verifier_temp", "w") as f: f.write(verifier)
    except: pass
    return f"{url}/auth/v1/authorize?provider=github&redirect_to=http://localhost:8501&code_challenge={challenge}&code_challenge_method=S256&scopes=repo"

def exchange_code(code):
    try: 
        with open(".verifier_temp", "r") as f: verifier = f.read().strip()
    except: return None
    res = requests.post(f"{url}/auth/v1/token?grant_type=pkce", json={
        "auth_code": code, "code_verifier": verifier, "redirect_uri": "http://localhost:8501"
    }, headers={"apikey": key, "Content-Type": "application/json"})
    return res.json() if res.status_code == 200 else None

def ensure_profile_exists(user_data, access_token):
    uid = user_data['id']
    meta = user_data.get('user_metadata', {})
    try: supabase.auth.set_session(access_token, "dummy_refresh_token")
    except: pass
    try:
        res = supabase.table("profiles").select("*").eq("id", uid).execute()
        if res.data: return res.data[0]
    except: pass 
    new_profile = {"id": uid, "username": meta.get("user_name", "Developer"), "full_name": meta.get("full_name", "CodeSage User"), "avatar_url": meta.get("avatar_url", "")}
    try: supabase.table("profiles").upsert(new_profile).execute(); return new_profile
    except: return None

# --- 4. NAVIGATION & VIEWS ---

def render_sidebar(profile):
    """Renders the Sidebar Navigation"""
    
    with st.sidebar:
        avatar_url = profile.get("avatar_url") or "https://api.dicebear.com/7.x/bottts/svg?seed=codesage"
        
        st.markdown(f"""
            <div style="width: 80px; height: 80px; margin: 0 auto; display: flex; justify-content: center; align-items: center;">
                <img src="{avatar_url}" style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid #00FFEA; box-shadow: 0 0 15px rgba(0,255,234,0.5); object-fit: cover; transition: 0.3s;" id="profile-avatar-img"/>
            </div>
            <style>
                /* Add hover animation via adjacent CSS to the actual image wrapper */
                #profile-avatar-img:hover {{
                    transform: scale(1.1); box-shadow: 0 0 25px rgba(0,255,234,0.8); border-color: #fff;
                }}
                /* Make the primary Python button invisible and pull it directly over the image */
                [data-testid="stSidebar"] button[kind="primary"] {{
                    margin-top: -85px !important; /* Pull up directly over the image */
                    width: 80px !important;
                    height: 80px !important;
                    margin-left: auto !important;
                    margin-right: auto !important;
                    border-radius: 50% !important;
                    opacity: 0 !important; /* Completely invisible */
                    cursor: pointer !important;
                    display: block !important;
                    z-index: 10 !important;
                }}
                [data-testid="stSidebar"] button[kind="primary"] p {{
                    display: none !important;
                }}
            </style>
        """, unsafe_allow_html=True)
        
        # CSS Hijacked into turning this primary button into the Profile Avatar Image!
        if st.button(" ", type="primary", use_container_width=False): 
            st.session_state["page"] = "profile_page"; st.rerun()

        st.markdown(f"<div style='text-align:center;'><b>{profile.get('full_name')}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;'><small style='color:#64748B'>@{profile.get('username')}</small></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        if st.button("🏠 Home", use_container_width=True): st.session_state["page"] = "home"; st.rerun()
        if st.button("🏆 Leaderboard", use_container_width=True): st.session_state["page"] = "leaderboard"; st.rerun()
        if st.button("🧠 AI Analysis", use_container_width=True): st.session_state["page"] = "ai_analysis"; st.rerun()
        if st.button("📊 Dashboard", use_container_width=True): st.session_state["page"] = "dashboard"; st.rerun()
        if st.button("🐙 GitHub Sync", use_container_width=True): st.session_state["page"] = "github_sync"; st.rerun()
        if st.button("📝 Docs", use_container_width=True): st.session_state["page"] = "docs"; st.rerun()

def render_dashboard_page():
    """Futuristic Analytics Dashboard"""
    # High-Tech Cyber CSS
    st.markdown("""
        <style>
            .cyber-header { text-align: center; color: #00FFEA; text-shadow: 0 0 15px rgba(0,255,234,0.6); font-family: 'Courier New', monospace; font-weight: 900; letter-spacing: 2px; }
            .cyber-sub { text-align: center; color: #94A3B8; letter-spacing: 4px; font-family: monospace; font-size: 0.9rem; margin-bottom: 30px; }
            
            .terminal-window {
                background: #020617; border: 1px solid #10B981; border-left: 4px solid #10B981;
                padding: 15px; border-radius: 4px; font-family: monospace; color: #10B981; font-size: 0.85rem; margin-bottom: 25px;
            }
            
            /* Real Python Calendar Grid CSS */
            .cal-table { width: 100%; border-collapse: separate; border-spacing: 8px; font-family: 'Courier New', monospace; margin-top: 15px; }
            .cal-th { color: #00FFEA; text-align: center; padding: 10px; font-weight: bold; text-transform: uppercase; font-size: 0.9rem; border-bottom: 1px solid rgba(0, 255, 234, 0.3); }
            .cal-td { 
                background: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 8px; 
                text-align: center; padding: 15px 5px; color: #475569; font-size: 1.1rem; 
                position: relative; transition: all 0.3s; width: 14.2%;
            }
            .cal-td:hover:not(.cal-empty) { border-color: #00FFEA; color: #00FFEA; transform: scale(1.08); z-index:10; cursor: pointer; }
            .cal-empty { background: transparent; border: none; }
            
            /* Streak Colors */
            .lvl-0 { color: #64748B; }
            .lvl-1 { background: rgba(0, 255, 234, 0.1); color: #00FFEA; border-color: rgba(0, 255, 234, 0.3); }
            .lvl-2 { background: rgba(0, 255, 234, 0.3); color: #fff; border-color: #00FFEA; box-shadow: 0 0 10px rgba(0, 255, 234, 0.3); }
            .lvl-3 { background: rgba(0, 255, 234, 0.7); color: #020617; border-color: #00FFEA; font-weight: bold; box-shadow: 0 0 15px rgba(0, 255, 234, 0.6); }
            
            /* Calendar Tooltip */
            .cal-tooltip { 
                visibility: hidden; background-color: #020617; color: #00FFEA; text-align: center; 
                border-radius: 4px; padding: 6px 10px; position: absolute; z-index: 100; 
                bottom: 110%; left: 50%; transform: translateX(-50%); border: 1px solid #00FFEA;
                opacity: 0; transition: opacity 0.3s; font-size: 0.75rem; white-space: nowrap;
            }
            .cal-td:hover:not(.cal-empty) .cal-tooltip { visibility: visible; opacity: 1; }
            
            /* High-Tech Chart Animations */
            [data-testid="stVegaLiteChart"] {
                position: relative;
                padding: 15px;
                background: linear-gradient(135deg, rgba(2, 6, 23, 0.8), rgba(15, 23, 42, 0.4));
                border-radius: 12px;
                border: 1px solid rgba(0, 255, 234, 0.2);
                border-top: 2px solid #00FFEA;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 255, 234, 0.05);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                animation: chartGlow 4s infinite alternate ease-in-out;
                z-index: 1;
            }
            
            [data-testid="stVegaLiteChart"]::after {
                content: "";
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(to bottom, transparent 40%, rgba(0, 255, 234, 0.05) 50%, transparent 60%);
                background-size: 100% 200%;
                animation: scanlineTracker 6s linear infinite;
                pointer-events: none;
                border-radius: 12px;
                z-index: 5;
            }

            [data-testid="stVegaLiteChart"]:hover {
                transform: translateY(-8px) scale(1.02);
                border-color: rgba(240, 18, 190, 0.5);
                border-top: 2px solid #F012BE;
                box-shadow: 0 15px 40px rgba(240, 18, 190, 0.2), inset 0 0 25px rgba(240, 18, 190, 0.1);
                z-index: 10;
            }
            
            /* Pie Chart specific fix so background matches container */
            [data-testid="stVegaLiteChart"] canvas { mix-blend-mode: screen; }

            @keyframes chartGlow {
                0% { box-shadow: 0 5px 20px rgba(0, 255, 234, 0.1), inset 0 0 10px rgba(0, 255, 234, 0.02); }
                100% { box-shadow: 0 15px 30px rgba(0, 255, 234, 0.2), inset 0 0 25px rgba(0, 255, 234, 0.08); }
            }
            @keyframes scanlineTracker {
                0% { background-position: 0% -100%; }
                100% { background-position: 0% 200%; }
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'>🌐 CYBER-NEXUS COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>SYSTEM ANALYTICS & TELEMETRY</p>", unsafe_allow_html=True)

    # Simulated Terminal Startup
    st.markdown("""
        <div class="terminal-window">
            > SYSTEM INITIALIZED... OK<br>
            > CONNECTING TO SUPABASE MAINFRAME... SECURE CONNECTION ESTABLISHED<br>
            > FETCHING TELEMETRY DATA & ANALYTICS... READY
        </div>
    """, unsafe_allow_html=True)

    # --- DATA FETCHING ---
    uid = st.session_state.get("user_id")
    
    try:
        res = supabase.table("reviews").select("quality_score, issues_found, created_at, language").eq("user_id", uid).execute()
        db_data = res.data
    except:
        db_data = []

    if db_data:
        df = pd.DataFrame(db_data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at')
        if 'language' not in df.columns:
            df['language'] = 'Python'
    else:
        # Futuristic Mock Data: Expanded to 180 days so navigating past months shows rich demo data
        now = datetime.datetime.now()
        dates = [now - pd.Timedelta(days=random.randint(0, 180)) for _ in range(200)]
        scores = [random.randint(55, 100) for _ in range(200)]
        issues = [random.randint(0, 15) for _ in range(200)]
        langs = [random.choice(["Python", "JavaScript", "TypeScript", "SQL", "C++", "Java", "Go"]) for _ in range(200)]
        df = pd.DataFrame({
            'created_at': dates,
            'quality_score': scores,
            'issues_found': issues,
            'language': langs
        })

    # Add Health Tier calculation
    def get_health_tier(score):
        if score >= 90: return 'Optimal (90+)'
        elif score >= 70: return 'Warning (70-89)'
        else: return 'Critical (<70)'
    
    df['health_tier'] = df['quality_score'].apply(get_health_tier)

    # Calculate 3 Threat Indicators mathematically based on issues_found for realistic distribution
    df['Critical (High)'] = df['issues_found'].apply(lambda x: x // 3 + (1 if x % 3 == 2 else 0))
    df['Warning (Med)'] = df['issues_found'].apply(lambda x: x // 3 + (1 if x % 3 >= 1 else 0))
    df['Info (Low)'] = df['issues_found'] - df['Critical (High)'] - df['Warning (Med)']
    df['Info (Low)'] = df['Info (Low)'].apply(lambda x: max(0, x))

    # Safely convert to naive datetime for clean streak math
    try:
        df['created_at'] = pd.to_datetime(df['created_at'], utc=True).dt.tz_localize(None)
    except:
        df['created_at'] = pd.to_datetime(df['created_at'])

    # STREAK CALCULATION
    df_dates = sorted(df['created_at'].dt.date.unique())
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    prev_date = None
    for d in df_dates:
        if prev_date is None or (d - prev_date).days == 1:
            temp_streak += 1
        else:
            temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak
        prev_date = d
    
    today = datetime.datetime.now().date()
    if df_dates and (today - df_dates[-1]).days <= 1:
        current_streak = temp_streak
    else:
        current_streak = 0

    st.write("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div style='border-left: 4px solid #00FFEA; padding-left: 15px; margin-bottom: 20px;'><div style='color: #94A3B8; font-size: 0.9rem; font-family: \"JetBrains Mono\";'>CURRENT STREAK</div><div style='color: #00FFEA; font-size: 1.8rem; font-weight: bold; text-shadow: 0 0 10px rgba(0,255,234,0.5);'>🔥 {current_streak} DAYS</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div style='border-left: 4px solid #F012BE; padding-left: 15px; margin-bottom: 20px;'><div style='color: #94A3B8; font-size: 0.9rem; font-family: \"JetBrains Mono\";'>MAXIMUM CONTINUOUS</div><div style='color: #F012BE; font-size: 1.8rem; font-weight: bold; text-shadow: 0 0 10px rgba(240,18,190,0.5);'>🏆 {longest_streak} DAYS</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div style='border-left: 4px solid #3B82F6; padding-left: 15px; margin-bottom: 20px;'><div style='color: #94A3B8; font-size: 0.9rem; font-family: \"JetBrains Mono\";'>LIFETIME REVIEWS</div><div style='color: #3B82F6; font-size: 1.8rem; font-weight: bold; text-shadow: 0 0 10px rgba(59,130,246,0.5);'>🧪 {len(df)}</div></div>", unsafe_allow_html=True)

    # --- 🗓️ ADVANCED PYTHON CALENDAR (REAL HTML GRID & DYNAMIC NAVIGATION) ---
    st.markdown("<h3 style='color: var(--accent-cyan); font-family: \"JetBrains Mono\"; margin-top: 30px; margin-bottom: 20px; text-align: center; text-shadow: 0 0 15px var(--glow-cyan);'>🗓️ CYBER-STREAK ENGAGEMENT</h3>", unsafe_allow_html=True)
    with st.container(border=True):
        st.caption("Real Calendar View: Navigate between months to trace your historical coding streaks.")
        
        # Initialize session state variables for dynamic calendar dates
        if "cal_year" not in st.session_state:
            st.session_state["cal_year"] = datetime.datetime.now().year
        if "cal_month" not in st.session_state:
            st.session_state["cal_month"] = datetime.datetime.now().month
            
        year = st.session_state["cal_year"]
        month = st.session_state["cal_month"]
        
        # UI controls for changing the month dynamically
        cal_col1, cal_col2, cal_col3 = st.columns([2, 4, 2])
        with cal_col1:
            if st.button("⬅️ PREVIOUS MONTH", use_container_width=True, key="prev_month", type="primary"):
                if st.session_state["cal_month"] == 1:
                    st.session_state["cal_month"] = 12
                    st.session_state["cal_year"] -= 1
                else:
                    st.session_state["cal_month"] -= 1
                st.rerun()
        
        with cal_col3:
            if st.button("NEXT MONTH ➡️", use_container_width=True, key="next_month", type="primary"):
                if st.session_state["cal_month"] == 12:
                    st.session_state["cal_month"] = 1
                    st.session_state["cal_year"] += 1
                else:
                    st.session_state["cal_month"] += 1
                st.rerun()

        # Filter dataframe for the SELECTED month
        df_curr_month = df[(df['created_at'].dt.year == year) & (df['created_at'].dt.month == month)]
        daily_counts = df_curr_month.groupby(df_curr_month['created_at'].dt.day).size().to_dict()

        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        with cal_col2:
            st.markdown(f"<h3 style='text-align:center; color:#00FFEA; letter-spacing:2px; font-family: monospace; margin-top:0;'>{month_name} {year}</h3>", unsafe_allow_html=True)
        
        # Build the HTML Table
        html_table = "<table class='cal-table'><tr>"
        for day_name in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            html_table += f"<th class='cal-th'>{day_name}</th>"
        html_table += "</tr>"
        
        for week in cal:
            html_table += "<tr>"
            for day in week:
                if day == 0:
                    html_table += "<td class='cal-empty'></td>"
                else:
                    count = daily_counts.get(day, 0)
                    if count == 0: lvl = "lvl-0"
                    elif count <= 2: lvl = "lvl-1"
                    elif count <= 4: lvl = "lvl-2"
                    else: lvl = "lvl-3"
                        
                    label = f"{count} Audits" if count != 1 else "1 Audit"
                    html_table += f"<td class='cal-td {lvl}'>{day}<span class='cal-tooltip'>{label}</span></td>"
            html_table += "</tr>"
        
        html_table += "</table>"
        
        st.markdown(html_table, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: var(--accent-cyan); font-family: \"JetBrains Mono\"; margin-top: 30px; margin-bottom: 20px; text-align: center; text-shadow: 0 0 15px var(--glow-cyan);'>📊 NEURAL ANALYTICS</h3>", unsafe_allow_html=True)
    
    # Advanced Altair Styling configuration to completely remove ugly artifacts
    def clean_chart(chart):
        return chart.configure_view(strokeOpacity=0).configure_axis(
            gridDash=[2,4], gridColor="rgba(255,255,255,0.05)", domainOpacity=0, ticks=False, labelColor="#94A3B8", titleColor="#00FFEA", titleFont="JetBrains Mono", labelFont="JetBrains Mono"
        ).configure_legend(
            labelColor="#E2E8F0", titleColor="#00FFEA", titleFont="JetBrains Mono", labelFont="JetBrains Mono", rowPadding=8, symbolStrokeWidth=0
        ).configure(background="transparent")

    r1c1, r1c2 = st.columns(2)
    
    with r1c1:
        st.markdown("<h5 style='color: #E2E8F0; text-align: center; font-family: \"JetBrains Mono\"; letter-spacing: 1px;'>HEALTH TIER DISTRIBUTION</h5>", unsafe_allow_html=True)
        pie = alt.Chart(df).mark_arc(innerRadius=0, cornerRadius=2).encode(
            theta=alt.Theta(field="health_tier", aggregate="count", type="quantitative"),
            color=alt.Color(field="health_tier", type="nominal",
                            scale=alt.Scale(domain=['Optimal (90+)', 'Warning (70-89)', 'Critical (<70)'],
                                            range=['#00FFEA', '#F59E0B', '#F012BE']),
                            legend=alt.Legend(title="", orient="bottom")),
            tooltip=['health_tier', 'count()']
        ).properties(height=300)
        st.altair_chart(clean_chart(pie), use_container_width=True)

    with r1c2:
        st.markdown("<h5 style='color: #E2E8F0; text-align: center; font-family: \"JetBrains Mono\"; letter-spacing: 1px;'>FRAMEWORK BREAKDOWN</h5>", unsafe_allow_html=True)
        pie_chart = alt.Chart(df).mark_arc(innerRadius=0, cornerRadius=2, padAngle=0.03).encode(
            theta=alt.Theta(field="language", aggregate="count", type="quantitative"),
            color=alt.Color(field="language", type="nominal", 
                            scale=alt.Scale(range=['#00FFEA', '#F012BE', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']), 
                            legend=alt.Legend(title="", orient="right")),
            tooltip=['language', 'count()']
        ).properties(height=300)
        st.altair_chart(clean_chart(pie_chart), use_container_width=True)

    st.write("<br>", unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    # Aggregate data by day for Candlestick & Threat Vectors
    df['date'] = df['created_at'].dt.date
    df['audit_count'] = 1
    df_daily = df.groupby('date').agg({
        'quality_score': ['first', 'max', 'min', 'last'],
        'audit_count': 'sum',
        'Critical (High)': 'sum',
        'Warning (Med)': 'sum',
        'Info (Low)': 'sum'
    })
    
    # Flatten MultiIndex columns created by groupby aggregation
    df_daily.columns = ['open', 'high', 'low', 'close', 'audit_count', 'Critical (High)', 'Warning (Med)', 'Info (Low)']
    df_daily = df_daily.reset_index()
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    
    # We display the aggregated daily data
    df_chart = df_daily.copy()

    with r2c1:
        st.markdown("<h5 style='color: #E2E8F0; text-align: center; font-family: \"JetBrains Mono\"; letter-spacing: 1px;'>CODE HEALTH TIMELINE (OHLC)</h5>", unsafe_allow_html=True)
        
        # Color condition: Cyber Cyan if close >= open (Bullish), Neon Pink if close < open (Bearish)
        color_condition = alt.condition("datum.open <= datum.close",
                                        alt.value("#00FFEA"),  
                                        alt.value("#F012BE"))  

        base = alt.Chart(df_chart).encode(
            x=alt.X('date:T', title='', axis=alt.Axis(format="%b %d", labelOverlap=True, tickCount=5)),
            color=color_condition,
            tooltip=[
                alt.Tooltip('date:T', format="%B %d, %Y", title="Date"),
                alt.Tooltip('open:Q', title="Open", format=".1f"),
                alt.Tooltip('high:Q', title="High", format=".1f"),
                alt.Tooltip('low:Q', title="Low", format=".1f"),
                alt.Tooltip('close:Q', title="Close", format=".1f"),
                alt.Tooltip('audit_count:Q', title="Total Scans")
            ]
        )

        # The 'wick' of the candle (Low to High)
        rule = base.mark_rule(strokeWidth=2).encode(
            y=alt.Y('low:Q', title='Health Score OHLC', scale=alt.Scale(domain=[0, 100])),
            y2=alt.Y2('high:Q')
        )

        # The 'body' of the candle (Open to Close)
        bar = base.mark_bar(size=14).encode(
            y='open:Q',
            y2='close:Q'
        )

        candlestick_chart = alt.layer(rule, bar).properties(height=280).interactive(bind_y=False)
        st.altair_chart(clean_chart(candlestick_chart), use_container_width=True)

    with r2c2:
        st.markdown("<h5 style='color: #E2E8F0; text-align: center; font-family: \"JetBrains Mono\"; letter-spacing: 1px;'>THREAT VECTOR VOLUME (DAILY)</h5>", unsafe_allow_html=True)
        df_threats = pd.melt(df_chart, id_vars=['date'], 
                             value_vars=['Critical (High)', 'Warning (Med)', 'Info (Low)'], 
                             var_name='Severity', value_name='Threat Count')
        line_chart_threats = alt.Chart(df_threats).mark_line(
            strokeWidth=3, 
            interpolate="monotone", 
            point=alt.OverlayMarkDef(filled=True, fill="#020617", strokeWidth=2, size=60)
        ).encode(
            x=alt.X('date:T', title='', axis=alt.Axis(format="%b %d", labelOverlap=True, tickCount=5)),
            y=alt.Y('Threat Count:Q', title=''),
            color=alt.Color('Severity:N', scale=alt.Scale(
                domain=['Critical (High)', 'Warning (Med)', 'Info (Low)'], 
                range=['#F012BE', '#F59E0B', '#3B82F6']
            ), legend=alt.Legend(title="", orient="bottom")),
            tooltip=[alt.Tooltip('date:T', format="%B %d, %Y", title="Date"), 'Severity', 'Threat Count']
        ).properties(height=280).interactive(bind_y=False)
        st.altair_chart(clean_chart(line_chart_threats), use_container_width=True)

    st.write("<br>", unsafe_allow_html=True)

def render_login_page():
    load_css()
    link = get_auth_link()
    
    # CSS styles moved to style.css
    
    # User's Original HTML structure successfully preserved!
    html_minified = f"""<div class="login-container"><div class="code-symbol sym-1">&lt;/&gt;</div><div class="code-symbol sym-2">&#123; &#125;</div><div class="code-symbol sym-3">def</div><div class="code-symbol sym-4">git</div><div class="code-symbol sym-5">01</div><div class="code-symbol sym-6">#</div><div class="login-card"><div class="brand-title"><span class="sage-text">CodeSage</span> <span class="brain-icon">🧠</span></div><p style="color: #94A3B8; margin-bottom: 2rem; font-family: monospace; letter-spacing: 1px;">AI-Powered Code Review Assistant</p><div class="feature-pills"><span class="pill">✨ AI Analysis</span><span class="pill">🛡️ Security</span><span class="pill">📈 Stats</span></div><div class="divider"></div><a href="{link}" target="_top" class="login-btn">Login with GitHub 🐙</a><div style="margin-top: 20px; font-size: 0.85rem; color: #475569; font-family: monospace;">v2.0 • Secure Authentication</div></div></div>"""
    st.markdown(html_minified, unsafe_allow_html=True)

def render_onboarding_page(profile):
    load_css()
    full_name = profile.get('full_name') or "Developer"
    user_name = full_name.split(' ')[0]
    
    st.markdown(f"""
        <div class="ob-header">WELCOME TO THE NEXUS, {user_name}</div>
        <div class="ob-sub">YOUR SECURE WORKSPACE IS READY FOR DEPLOYMENT</div>
        
        <div class="ob-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 800px; margin: 0 auto 40px auto;">
            <div class="ob-card c-cyan" style="display: flex; align-items: flex-start; gap: 15px; border-left: 4px solid var(--accent-cyan) !important;">
                <div class="ob-icon" style="font-size: 2.5rem;">🧠</div>
                <div><div class="ob-title" style="font-weight: bold; font-family: 'JetBrains Mono'; margin-bottom: 5px; color: var(--text-main);">AI Architect</div><div class="ob-desc" style="color: var(--text-muted); font-size: 0.9rem;">Deep code analysis and side-by-side neural refactoring.</div></div>
            </div>
            <div class="ob-card c-amber" style="display: flex; align-items: flex-start; gap: 15px; border-left: 4px solid #F59E0B !important;">
                <div class="ob-icon" style="font-size: 2.5rem;">🐙</div>
                <div><div class="ob-title" style="font-weight: bold; font-family: 'JetBrains Mono'; margin-bottom: 5px; color: var(--text-main);">GitHub Uplink</div><div class="ob-desc" style="color: var(--text-muted); font-size: 0.9rem;">Directly connect, patch, and push to remote repositories.</div></div>
            </div>
            <div class="ob-card c-purple" style="display: flex; align-items: flex-start; gap: 15px; border-left: 4px solid var(--accent-purple) !important;">
                <div class="ob-icon" style="font-size: 2.5rem;">🛡️</div>
                <div><div class="ob-title" style="font-weight: bold; font-family: 'JetBrains Mono'; margin-bottom: 5px; color: var(--text-main);">Vanguard Security</div><div class="ob-desc" style="color: var(--text-muted); font-size: 0.9rem;">Detect and neutralize critical vulnerabilities instantly.</div></div>
            </div>
            <div class="ob-card c-blue" style="display: flex; align-items: flex-start; gap: 15px; border-left: 4px solid var(--accent-blue) !important;">
                <div class="ob-icon" style="font-size: 2.5rem;">🏆</div>
                <div><div class="ob-title" style="font-weight: bold; font-family: 'JetBrains Mono'; margin-bottom: 5px; color: var(--text-main);">Code Arena</div><div class="ob-desc" style="color: var(--text-muted); font-size: 0.9rem;">Earn XP, climb the ranks, and become a Diamond Sage.</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c2.button("🚀 ENGAGE DASHBOARD PROTOCOL", type="primary", use_container_width=True):
        st.session_state["onboarding_complete"] = True
        st.rerun()

# --- 5. MAIN ---
def main():
    if "page" not in st.session_state: st.session_state["page"] = "home"
    
    # --- 🔗 STEP 1: CATCH REFERRAL LINK ---
    if "ref" in st.query_params:
        st.session_state["referred_by"] = st.query_params["ref"]
        st.query_params.clear() 

    if "code" in st.query_params:
        data = exchange_code(st.query_params["code"])
        if data:
            user = data.get("user")
            st.session_state["token"] = data["access_token"]
            st.session_state["provider_token"] = data.get("provider_token")
            st.session_state["user_raw"] = user
            st.session_state["onboarding_complete"] = False
            st.session_state["user_id"] = user["id"]
            st.query_params.clear(); st.rerun()

    if "token" not in st.session_state:
        render_login_page()
    else:
        if "profile" not in st.session_state:
            st.session_state["profile"] = ensure_profile_exists(st.session_state["user_raw"], st.session_state["token"])
        
        profile = st.session_state.get("profile")
        if not profile: st.error("Error loading profile"); st.stop()

        if "user_id" not in st.session_state:
            st.session_state["user_id"] = profile["id"]

        # --- 🔗 STEP 2: REWARD THE INVITER ---
        if "referred_by" in st.session_state:
            referrer = st.session_state["referred_by"]
            if referrer != profile.get("username"):
                try:
                    res = supabase.table("profiles").select("lifetime_reviews").eq("username", referrer).execute()
                    if res.data:
                        old_score = res.data[0].get("lifetime_reviews", 0)
                        supabase.table("profiles").update({"lifetime_reviews": old_score + 5}).eq("username", referrer).execute()
                        st.toast(f"🎉 You joined via {referrer}'s invite. They got +5 XP!", icon="🚀")
                except Exception as e:
                    print("Referral reward failed:", e)
            del st.session_state["referred_by"]

        if not st.session_state.get("onboarding_complete", False):
            render_onboarding_page(profile)
        else:
            load_css()
            render_sidebar(profile)
            
            page = st.session_state["page"]
            if page == "home": home.render_home_page(profile)
            elif page == "leaderboard": features.leaderboard.render_leaderboard_page()
            elif page == "docs": features.docs.render_docs_page()
            elif page == "ai_analysis": features.ai_analysis.render_ai_analysis_page()
            elif page == "pending_tasks": features.pending_tasks.render_pending_tasks_page()
            elif page == "history": features.history.render_history_page()
            elif page == "translator": features.translator.render_translator_page()
            elif page == "dashboard": render_dashboard_page()
            elif page == "github_sync": features.github_sync.render_github_page()
            elif page == "security_scan": features.security_scan.render_security_scan_page()
            elif page == "profile_page": features.profile_page.render_profile_page(profile)
            else: home.render_home_page(profile)

if __name__ == "__main__":
    main()