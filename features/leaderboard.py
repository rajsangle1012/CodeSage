import streamlit as st
import pandas as pd
import altair as alt
from utils import get_supabase, load_css
import streamlit.components.v1 as components

# --- GAMIFICATION LOGIC ---
def get_rank_tier(score):
    if score < 10: return "🥉 Bronze Novice"
    elif score < 25: return "🥈 Silver Hacker"
    elif score < 50: return "🥇 Gold Architect"
    else: return "💎 Diamond Sage"

def get_xp_progress(score):
    if score < 10: return (score / 10.0) * 100, 10
    elif score < 25: return ((score - 10) / 15.0) * 100, 25
    elif score < 50: return ((score - 25) / 25.0) * 100, 50
    else: return 100, "MAX"

def render_leaderboard_page():
    try: load_css()
    except: pass
    
    # --- 1. GAME UI CSS ---
    st.markdown("""
        <style>
            .cyber-header {
                font-family: 'JetBrains Mono', monospace; 
                font-size: 3.2rem; 
                font-weight: 800; 
                background: linear-gradient(135deg, #FBBF24, #fff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
                text-align: center;
                text-transform: uppercase;
                margin-bottom: 0px;
                animation: textGlowGold 3s infinite alternate;
            }
            @keyframes textGlowGold {
                0% { text-shadow: 0 0 10px rgba(251, 191, 36, 0.4); }
                100% { text-shadow: 0 0 25px rgba(251, 191, 36, 0.8), 0 0 40px rgba(251, 191, 36, 0.4); }
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
                0%, 100% { transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 10px rgba(251, 191, 36, 0.4)); }
                50% { transform: scale(1.15) rotate(-5deg); filter: drop-shadow(0 0 25px rgba(251, 191, 36, 1)); }
            }

            /* Leaderboard elements */
            .glow-podium { border: 1px solid rgba(59, 130, 246, 0.5); box-shadow: 0 0 20px rgba(0, 0, 0, 0.8); border-radius: 12px; background: linear-gradient(180deg, rgba(30,41,59,0.8), rgba(15,23,42,0.9)); text-align: center; backdrop-filter: blur(10px); transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); padding: 20px 10px; margin-top: 20px; overflow: hidden; position: relative;}
            .glow-podium::before { content: ""; position: absolute; top:0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, transparent, rgba(255,255,255,0.05), transparent); transform: translateY(100%); transition: all 0.5s; }
            .glow-podium:hover::before { transform: translateY(-100%); }
            
            .glow-podium:hover { transform: translateY(-10px) scale(1.02); box-shadow: 0 15px 35px rgba(59, 130, 246, 0.5), inset 0 0 20px rgba(59, 130, 246, 0.2); }
            .rank-1 { height: 260px; border: 2px solid #FBBF24; box-shadow: 0 0 35px rgba(251, 191, 36, 0.3), inset 0 0 20px rgba(251, 191, 36, 0.1); }
            .rank-1:hover { box-shadow: 0 15px 45px rgba(251, 191, 36, 0.6), inset 0 0 30px rgba(251, 191, 36, 0.3); }
            .rank-2 { height: 210px; border-color: #94A3B8; margin-top: 70px; }
            .rank-3 { height: 180px; border-color: #B45309; margin-top: 100px; }
            .rank-badge { font-size: 4rem; margin-bottom: 5px; animation: float 3s ease-in-out infinite; display: inline-block; }
            @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
            
            .dev-name { font-size: 1.3rem; font-weight: 900; color: #F1F5F9; margin-bottom: 5px; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 1px;}
            .dev-score { font-size: 1.1rem; color: #60A5FA; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 10px rgba(96, 165, 250, 0.5);}
            .rank-1 .dev-score { color: #FBBF24; text-shadow: 0 0 15px rgba(251, 191, 36, 0.6); }

            .rules-box { background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(59, 130, 246, 0.3); border-left: 4px solid #3B82F6; padding: 25px; border-radius: 8px; margin-bottom: 30px; font-size: 1rem; color: #E2E8F0; box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: all 0.3s; }
            .rules-box:hover { border-left: 4px solid #FBBF24; box-shadow: 0 15px 40px rgba(59, 130, 246, 0.2); }
            
            .editor-label { 
                font-size: 1rem; 
                color: #3B82F6; 
                font-family: 'JetBrains Mono', monospace; 
                font-weight: 800; 
                text-transform: uppercase; 
                margin-bottom: 15px; 
                letter-spacing: 2px; 
                text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
            }
            
            button[kind="primary"] {
                background: linear-gradient(90deg, #FBBF24, #3B82F6, #FBBF24) !important;
                background-size: 200% auto !important;
                color: #020617 !important;
                font-weight: 900 !important;
                border: none !important;
                animation: gradientShiftGold 3s linear infinite !important;
                transition: all 0.3s !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                box-shadow: 0 0 20px rgba(251, 191, 36, 0.4) !important;
            }
            button[kind="primary"]:hover {
                transform: scale(1.02) !important;
                box-shadow: 0 0 30px rgba(251, 191, 36, 0.6) !important;
            }
            @keyframes gradientShiftGold { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
            
            [data-testid="stVegaLiteChart"] {
                background: linear-gradient(180deg, rgba(15,23,42,0.95), rgba(2,6,23,1)) !important;
                border: 1px solid rgba(59, 130, 246, 0.4) !important;
                border-left: 4px solid #FBBF24 !important;
                border-radius: 12px;
                padding: 20px;
                box-shadow: inset 0 0 50px rgba(59, 130, 246, 0.1), 0 10px 30px rgba(0,0,0,0.6);
                position: relative;
                overflow: hidden;
            }
            [data-testid="stVegaLiteChart"]::after {
                content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(59, 130, 246, 0.05) 2px, rgba(59, 130, 246, 0.05) 4px);
                pointer-events: none;
            }

            .arena-scoreboard { width: 100%; border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 12px; padding: 15px; grid-gap: 8px; display: grid; background: linear-gradient(180deg, rgba(15,23,42,0.95), rgba(2,6,23,1)); position: relative; overflow: hidden; box-shadow: inset 0 0 50px rgba(59, 130, 246, 0.1), 0 10px 30px rgba(0,0,0,0.6); }
            .arena-scoreboard::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(59, 130, 246, 0.05) 2px, rgba(59, 130, 246, 0.05) 4px); pointer-events: none; }
            .arena-row { display: flex; justify-content: space-between; align-items: center; padding: 13px 20px; background: linear-gradient(90deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9)); border-left: 4px solid #3B82F6; border-radius: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); animation: slideInRight 0.5s ease-out forwards; opacity: 0; position: relative; z-index: 2;}
            .arena-row:nth-child(1) { animation-delay: 0.1s; border-left: 4px solid #FBBF24; box-shadow: 0 0 15px rgba(251, 191, 36, 0.2); }
            .arena-row:nth-child(2) { animation-delay: 0.15s; border-left: 4px solid #94A3B8; }
            .arena-row:nth-child(3) { animation-delay: 0.2s; border-left: 4px solid #B45309; }
            .arena-row:nth-child(4) { animation-delay: 0.25s; }
            .arena-row:nth-child(5) { animation-delay: 0.3s; }
            .arena-row:nth-child(6) { animation-delay: 0.35s; }
            .arena-row:nth-child(7) { animation-delay: 0.4s; }
            .arena-row:nth-child(8) { animation-delay: 0.45s; }
            .arena-row:nth-child(9) { animation-delay: 0.5s; }
            .arena-row:nth-child(10) { animation-delay: 0.55s; }

            @keyframes slideInRight { 0% { transform: translateX(50px); opacity: 0; } 100% { transform: translateX(0); opacity: 1; } }

            .arena-row:hover { transform: scale(1.02) translateX(10px); border-left: 4px solid #FBBF24; background: linear-gradient(90deg, rgba(59, 130, 246, 0.3), rgba(2, 6, 23, 0.9)); box-shadow: 0 0 25px rgba(59, 130, 246, 0.5); z-index: 10;}
            .arena-row.current-user { border-left: 4px solid #10B981 !important; background: linear-gradient(90deg, rgba(16, 185, 129, 0.15), rgba(2, 6, 23, 0.9)); }
            .arena-row.current-user .arena-name { color: #10B981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.6); }

            .arena-rank { width: 50px; font-weight: 900; color: #94A3B8; font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; }
            .arena-row:nth-child(1) .arena-rank { color: #FBBF24; text-shadow: 0 0 10px rgba(251,191,36,0.6);}
            .arena-name { flex-grow: 1; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #F1F5F9; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 2px; }
            .arena-tier { color: #FBBF24; font-size: 0.9rem; margin-right: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
            .arena-score { font-family: 'JetBrains Mono', monospace; color: #60A5FA; font-weight: 900; font-size: 1.2rem; text-shadow: 0 0 10px rgba(96, 165, 250, 0.5); width: 100px; text-align: right; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='cyber-header'><span class='tool-icon'>🎮</span> Code Arena Leaderboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='cyber-sub'>COMPETE, ANALYZE, AND CLIMB THE CORE MAINFRAME RANKS.</p>", unsafe_allow_html=True)
    st.divider()

    # --- 2. FETCH DATA ---
    supabase = get_supabase()
    current_user_profile = st.session_state.get("profile", {})
    current_username = current_user_profile.get("username", "developer")
    current_score = current_user_profile.get("lifetime_reviews", 0)
    
    if not supabase:
        st.error("⚠️ Database connection failed.")
        return

    with st.spinner("Loading Live Arena Stats..."):
        try:
            res = supabase.table("profiles").select("full_name, username, lifetime_reviews").order("lifetime_reviews", desc=True).limit(50).execute()
            leaderboard_data = res.data
        except Exception as e:
            leaderboard_data = []

    # --- 4. TOP 3 GLOWING PODIUM ---
    if leaderboard_data:
        top_3 = leaderboard_data[:3]
        st.markdown('<div class="editor-label" style="text-align: center; color: #FBBF24; font-size: 1.3rem;">🏆 HALL OF FAME</div>', unsafe_allow_html=True)
        
        c2, c1, c3 = st.columns([1, 1.2, 1])
        
        def render_podium_card(col, data, medal, css_class):
            name = data.get('full_name') or data.get('username') or 'Unknown Dev'
            score = data.get('lifetime_reviews', 0)
            with col:
                st.markdown(f"""
                    <div class="glow-podium {css_class}">
                        <div class="rank-badge">{medal}</div>
                        <div class="dev-name">{name}</div>
                        <div class="dev-score">{score} XP</div>
                    </div>
                """, unsafe_allow_html=True)

        if len(top_3) > 1: render_podium_card(c2, top_3[1], "🥈", "rank-2")
        if len(top_3) > 0: render_podium_card(c1, top_3[0], "🥇", "rank-1")
        if len(top_3) > 2: render_podium_card(c3, top_3[2], "🥉", "rank-3")
        
        st.write("<br><br>", unsafe_allow_html=True)

    # --- 3. THE REAL INVITE SYSTEM & STATS ---
    col_stats, col_invite = st.columns([1, 1])
    
    with col_stats:
        current_tier = get_rank_tier(current_score)
        progress_pct, next_goal = get_xp_progress(current_score)
        
        st.markdown('<div class="rules-box">', unsafe_allow_html=True)
        st.markdown('<div class="editor-label">🛡️ YOUR NEURAL COMBAT STATS</div>', unsafe_allow_html=True)
        st.markdown(f"**Current Rank Node:** <span style='color:#FBBF24;'>{current_tier}</span>", unsafe_allow_html=True)
        st.markdown(f"**System XP Output:** <span style='color:#60A5FA; font-weight: bold;'>{current_score} 🚀</span>", unsafe_allow_html=True)
        if next_goal != "MAX":
            st.caption(f"Progress to next rank ({int(progress_pct)}%) - {current_score} / {next_goal} XP")
            st.progress(int(progress_pct))
        else:
            st.success("🎉 MAXIMUM OVERDRIVE ACHIEVED!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_invite:
        st.markdown('<div class="rules-box" style="border-left-color: #8B5CF6;">', unsafe_allow_html=True)
        st.markdown('<div class="editor-label" style="color: #8B5CF6;">🤝 XP BOUNTY SYSTEM</div>', unsafe_allow_html=True)
        st.markdown("**How to earn XP inside the Mainframe:**<br/>", unsafe_allow_html=True)
        st.markdown("• **Standard Outputs (AI Architect / Solutions):** +1 to +3 XP<br/>", unsafe_allow_html=True)
        st.markdown("• **Vanguard Security Scans:** Earn Bounties based on Threat Detection.<br/><br/>", unsafe_allow_html=True)
        st.markdown("Invite peers. When they register via link, **you instantly bypass firewall for +5 XP!**")
        base_url = "http://localhost:8501" 
        real_invite_link = f"{base_url}/?ref={current_username}"
        st.code(real_invite_link, language="text")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # --- MINIGAME WIDGET ---
    st.markdown('<div class="editor-label" style="text-align: center; font-size: 1.2rem;">🕹️ NEURAL BOT ARENA (MINI-GAME)</div>', unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; text-align: center; font-family: monospace; font-size: 0.85rem;'>TARGET AND ELIMINATE ROGUE NEURONS. Click to neutralize them. Warning: system will spawn reinforcements.</p>", unsafe_allow_html=True)
    
    components.html("""
        <canvas id='gameCanvas' style='width: 100%; height: 350px; background: linear-gradient(180deg, rgba(15,23,42,0.9), rgba(2,6,23,0.95)); border-radius: 12px; border: 1px solid rgba(59,130,246,0.4); box-shadow: inset 0 0 30px rgba(0,0,0,0.8); cursor: none;'></canvas>
        <script>
            const canvas = document.getElementById('gameCanvas');
            const ctx = canvas.getContext('2d');
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            
            let bots = [];
            let particles = [];
            let score = 0;
            let particleColors = ['#3B82F6', '#10B981', '#FBBF24', '#EF4444', '#8B5CF6', '#14B8A6'];
            
            function spawnBot() {
                bots.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * 6,
                    vy: (Math.random() - 0.5) * 6,
                    color: particleColors[Math.floor(Math.random() * particleColors.length)],
                    radius: Math.random() * 5 + 4,
                    alive: true
                });
            }
            
            for(let i=0; i<25; i++) spawnBot();

            let mouseX = canvas.width/2;
            let mouseY = canvas.height/2;

            canvas.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                mouseX = e.clientX - rect.left;
                mouseY = e.clientY - rect.top;
            });
            canvas.addEventListener('touchmove', (e) => {
                const rect = canvas.getBoundingClientRect();
                mouseX = e.touches[0].clientX - rect.left;
                mouseY = e.touches[0].clientY - rect.top;
                e.preventDefault();
            });

            canvas.addEventListener('mousedown', (e) => {
                const rect = canvas.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const clickY = e.clientY - rect.top;
                
                // Blast flash effect
                ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                for(let i = bots.length - 1; i >= 0; i--) {
                    let bot = bots[i];
                    let dist = Math.hypot(bot.x - clickX, bot.y - clickY);
                    
                    if(dist < 35) { // Hitbox detection
                        bot.alive = false;
                        score += 10;
                        
                        // Spawn explosion fragments
                        for(let p=0; p<10; p++) {
                            particles.push({
                                x: bot.x, y: bot.y,
                                vx: (Math.random() - 0.5) * 15,
                                vy: (Math.random() - 0.5) * 15,
                                life: 1.0, color: bot.color
                            });
                        }
                        
                        // Spawn 1 or 2 new bots as reinforcements
                        spawnBot();
                        if(Math.random() > 0.4) spawnBot();
                    }
                }
                bots = bots.filter(b => b.alive);
            });

            function draw() {
                ctx.fillStyle = 'rgba(2, 6, 23, 0.5)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw Sniper Targeter
                ctx.strokeStyle = 'rgba(239, 68, 68, 0.8)'; // Red crosshair
                ctx.beginPath();
                ctx.arc(mouseX, mouseY, 20, 0, Math.PI*2);
                ctx.moveTo(mouseX-30, mouseY); ctx.lineTo(mouseX-10, mouseY);
                ctx.moveTo(mouseX+10, mouseY); ctx.lineTo(mouseX+30, mouseY);
                ctx.moveTo(mouseX, mouseY-30); ctx.lineTo(mouseX, mouseY-10);
                ctx.moveTo(mouseX, mouseY+10); ctx.lineTo(mouseX, mouseY+30);
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.beginPath();
                ctx.arc(mouseX, mouseY, 3, 0, Math.PI*2);
                ctx.fillStyle = 'rgba(239, 68, 68, 1)';
                ctx.fill();
                
                // Draw Player Score
                ctx.fillStyle = '#60A5FA';
                ctx.font = 'bold 18px "JetBrains Mono", monospace';
                ctx.fillText(`NEURONS NEUTRALIZED: ${score}`, 20, 30);

                // Update and draw live bots
                bots.forEach(bot => {
                    bot.x += bot.vx;
                    bot.y += bot.vy;
                    
                    if(bot.x < 0 || bot.x > canvas.width) bot.vx *= -1;
                    if(bot.y < 0 || bot.y > canvas.height) bot.vy *= -1;

                    ctx.beginPath();
                    ctx.arc(bot.x, bot.y, bot.radius, 0, Math.PI*2);
                    ctx.fillStyle = bot.color;
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = bot.color;
                    ctx.fill();
                    ctx.shadowBlur = 0;
                });
                
                // Update and draw explosion particles
                for(let i = particles.length - 1; i >= 0; i--) {
                    let p = particles[i];
                    p.x += p.vx; 
                    p.y += p.vy;
                    p.life -= 0.04; // Fade out
                    
                    if(p.life <= 0) { 
                        particles.splice(i, 1); 
                        continue; 
                    }
                    
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, 2, 0, Math.PI*2);
                    ctx.fillStyle = p.color;
                    ctx.globalAlpha = p.life;
                    ctx.fill();
                    ctx.globalAlpha = 1.0;
                }
                
                requestAnimationFrame(draw);
            }
            draw();
        </script>
    """, height=370)

    st.write("<br><br>", unsafe_allow_html=True)

    # --- 5. COMPETITIVE ANALYTICS GRAPHS ---
    if leaderboard_data:
        st.markdown('<div class="editor-label">📈 ARENA DATA ANALYTICS</div>', unsafe_allow_html=True)
        df_data = [{"Developer": r.get('full_name') or r.get('username') or 'Dev', "XP": r.get('lifetime_reviews', 0), "Tier": get_rank_tier(r.get('lifetime_reviews', 0))} for r in leaderboard_data]
        df = pd.DataFrame(df_data)

        tab1, tab2 = st.tabs(["🔥 Top 10 Power Rankings", "📊 Score Distribution"])
        
        with tab1:
            top_10 = leaderboard_data[:10]
            
            html_rows = "<div class='arena-scoreboard'>"
            for idx, p in enumerate(top_10):
                name = p.get('full_name') or p.get('username') or 'Unknown Dev'
                score = p.get('lifetime_reviews', 0)
                tier = get_rank_tier(score)
                is_current = "current-user" if name == current_user_profile.get("full_name", "") else ""
                
                html_rows += f"""
                    <div class='arena-row {is_current}'>
                        <div class='arena-rank'>#{idx+1}</div>
                        <div class='arena-name'>{name}</div>
                        <div class='arena-tier'>[{tier}]</div>
                        <div class='arena-score'>{score} XP</div>
                    </div>
                """
            html_rows += "</div>"
            st.markdown(html_rows, unsafe_allow_html=True)

        with tab2:
            neon_scale = alt.Scale(
                domain=["🥉 Bronze Novice", "🥈 Silver Hacker", "🥇 Gold Architect", "💎 Diamond Sage"],
                range=["#94A3B8", "#3B82F6", "#FBBF24", "#A855F7"]
            )
            
            base = alt.Chart(df).encode(
                x=alt.X('Developer:N', sort='-y', axis=alt.Axis(labels=False, title=None, grid=True, gridColor='rgba(59, 130, 246, 0.15)', gridDash=[4,4])),
                y=alt.Y('XP:Q', title="DATA PACKETS (XP)", axis=alt.Axis(grid=True, gridColor='rgba(59, 130, 246, 0.15)', tickColor='transparent', labelColor='#60A5FA', titleColor='#FBBF24', titleFont='JetBrains Mono'))
            )
            
            area = base.mark_area(opacity=0.15, interpolate='monotone').encode(
                color=alt.value('#3B82F6')
            )
            
            lines = base.mark_line(strokeWidth=2, opacity=0.5, interpolate='monotone').encode(
                color=alt.value('#60A5FA')
            )
            
            circles = base.mark_circle(size=400, opacity=0.9, strokeWidth=2, stroke='#fff').encode(
                color=alt.Color('Tier:N', legend=alt.Legend(title="RANK TIER", titleColor='#FBBF24', labelColor='#94A3B8', titleFont='JetBrains Mono'), scale=neon_scale),
                tooltip=['Developer', 'XP', 'Tier']
            )

            scatter_chart = (area + lines + circles).properties(height=380).configure_view(
                strokeOpacity=0
            ).configure(
                background='transparent'
            ).interactive()
            
            st.altair_chart(scatter_chart, use_container_width=True)

    # --- NAVIGATION ---
    st.write("<br>", unsafe_allow_html=True)
    if st.button("← RETURN TO CORE DASHBOARD", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()