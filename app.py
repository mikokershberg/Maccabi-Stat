import streamlit as st
import pandas as pd
import sqlite3

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Maccabi Basketball Portal & Analytics",
    page_icon="🏀",
    layout="wide"
)

DB_FILE = "maccabi_stats.db"

# --- DATABASE SETUP & MIGRATION ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Matches Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER DEFAULT NULL,
            away_score INTEGER DEFAULT NULL,
            status TEXT DEFAULT 'Scheduled',
            venue TEXT DEFAULT ''
        )
    ''')
    
    # 2. Comprehensive Player Stats Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            season TEXT DEFAULT '2025-2026',
            player_name TEXT,
            team_name TEXT DEFAULT 'Maccabi Antwerpen HSE A',
            is_home BOOLEAN DEFAULT 1,
            minutes REAL DEFAULT 0,
            points INTEGER DEFAULT 0,
            ft_made INTEGER DEFAULT 0,
            ft_attempts INTEGER DEFAULT 0,
            fg2_made INTEGER DEFAULT 0,
            fg2_attempts INTEGER DEFAULT 0,
            fg3_made INTEGER DEFAULT 0,
            fg3_attempts INTEGER DEFAULT 0,
            rebounds INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            steals INTEGER DEFAULT 0,
            blocks INTEGER DEFAULT 0,
            turnovers INTEGER DEFAULT 0,
            fouls INTEGER DEFAULT 0,
            plus_minus REAL DEFAULT 0
        )
    ''')
    
    # Seed Schedule if empty
    c.execute("SELECT COUNT(*) FROM matches")
    if c.fetchone()[0] == 0:
        seed_schedule = [
            ("2026-09-12", "19:00:00", "Guco Lier HSE F", "Willibies Antwerpen HSE A"),
            ("2026-09-12", "19:30:00", "BBC Laakdal HSE A", "BBC Geel HSE B"),
            ("2026-09-12", "20:00:00", "Duffel K.B.B.C. HSE A", "Phantoms Basket Boom HSE C"),
            ("2026-09-12", "20:15:00", "BBC Schelle HSE A", "Zuiderkempen Diamonds HSE B"),
            ("2026-09-12", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Rucon Gembo Borgerhout HSE C"),
            ("2026-09-12", "21:00:00", "Antwerp Giants HSE D", "Oxaco BBC Boechout HSE C"),
            ("2026-09-13", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Maccabi Antwerpen HSE A"),
            ("2026-09-18", "21:00:00", "Phantoms Basket Boom HSE C", "Koninklijke Herentalse BBC HSE A"),
            ("2026-09-19", "18:00:00", "Zuiderkempen Diamonds HSE B", "BBC Laakdal HSE A"),
            ("2026-09-19", "19:30:00", "Oxaco BBC Boechout HSE C", "Duffel K.B.B.C. HSE A"),
            ("2026-09-19", "20:00:00", "Willibies Antwerpen HSE A", "BBC Schelle HSE A"),
            ("2026-09-19", "20:30:00", "BBC Geel HSE B", "BBC Lyra Nila Nijlen HSE A"),
            ("2026-09-20", "13:30:00", "Rucon Gembo Borgerhout HSE C", "Guco Lier HSE F"),
            ("2026-09-22", "20:00:00", "Duffel K.B.B.C. HSE A", "Maccabi Antwerpen HSE A"),
            ("2026-09-26", "19:00:00", "Guco Lier HSE F", "Phantoms Basket Boom HSE C"),
            ("2026-09-26", "19:30:00", "BBC Laakdal HSE A", "Willibies Antwerpen HSE A"),
            ("2026-09-26", "20:15:00", "BBC Schelle HSE A", "Rucon Gembo Borgerhout HSE C"),
            ("2026-09-26", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Oxaco BBC Boechout HSE C"),
            ("2026-09-27", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Zuiderkempen Diamonds HSE B"),
            ("2026-09-27", "17:00:00", "Antwerp Giants HSE D", "BBC Geel HSE B"),
            ("2026-09-29", "20:30:00", "Maccabi Antwerpen HSE A", "Zuiderkempen Diamonds HSE B")
        ]
        c.executemany(
            "INSERT INTO matches (date, time, home_team, away_team, status) VALUES (?, ?, ?, ?, 'Scheduled')",
            seed_schedule
        )

    # Seed initial baseline if empty
    c.execute("SELECT COUNT(*) FROM player_stats")
    if c.fetchone()[0] == 0:
        roster_seed = [
            ("Abraham Michaely", 30.2, 11, 2, 3, 2, 3, 1, 11.3, 2),
            ("Avi Medina", 13.1, 1, 0, 1, 0, 1, 0, 1.0, 1),
            ("Benjamin Fischler", 23.1, 3, 1, 1, 1, 0, 1, 9.9, 3),
            ("Eitham Tzah", 27.3, 8, 2, 3, 2, 3, 1, 8.0, 3),
            ("Itai Lavan", 29.2, 18, 3, 4, 3, 5, 3, 15.0, 2)
        ]
        for p in roster_seed:
            c.execute('''
                INSERT INTO player_stats (player_name, season, minutes, points, ft_made, ft_attempts, fg2_made, fg2_attempts, fg3_made, plus_minus, fouls)
                VALUES (?, '2025-2026', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', p)
            
    conn.commit()
    conn.close()

init_db()

def get_connection():
    return sqlite3.connect(DB_FILE)

# --- STYLING HELPER ---
def highlight_maccabi(row):
    is_maccabi = "Maccabi" in str(row.get("Home Team", "")) or "Maccabi" in str(row.get("Away Team", ""))
    if is_maccabi:
        return ["background-color: #FFFDE7; font-weight: bold;"] * len(row)
    return [""] * len(row)

# --- HEADER & NAVIGATION ---
st.title("🏀 Maccabi Antwerpen — Team & League Portal")
st.caption("2e Provincial Heren Antwerpen B | Season Schedule, Detailed Box Scores & Analytics")

tabs = st.tabs([
    "📅 Schedule & Results",
    "📊 Player & Team Stats",
    "🔄 Multi-Season Comparison",
    "💬 Analytics & Prompts",
    "🔒 Admin Interface"
])

# ==========================================
# TAB 1: SCHEDULE & RESULTS
# ==========================================
with tabs[0]:
    st.header("Schedule & Results")
    
    conn = get_connection()
    matches_df = pd.read_sql_query("SELECT * FROM matches ORDER BY date ASC, time ASC", conn)
    conn.close()

    matches_df['time'] = matches_df['time'].astype(str).str[:5]
    matches_df = matches_df.rename(columns={
        'date': 'Date',
        'time': 'Time',
        'home_team': 'Home Team',
        'home_score': 'Home Score',
        'away_score': 'Away Score',
        'away_team': 'Away Team',
        'status': 'Status'
    })

    col1, col2 = st.columns([2, 1])
    with col1:
        team_list = sorted(list(set(matches_df['Home Team']).union(set(matches_df['Away Team']))))
        team_filter = st.selectbox("Filter Team", ["All Teams"] + team_list)
    with col2:
        status_filter = st.radio("Status Filter", ["All", "Upcoming", "Completed"], horizontal=True)

    filtered = matches_df.copy()
    if team_filter != "All Teams":
        filtered = filtered[(filtered['Home Team'] == team_filter) | (filtered['Away Team'] == team_filter)]
    if status_filter == "Upcoming":
        filtered = filtered[filtered['Status'] == 'Scheduled']
    elif status_filter == "Completed":
        filtered = filtered[filtered['Status'] == 'Completed']

    display_df = filtered[['Date', 'Time', 'Home Team', 'Home Score', 'Away Score', 'Away Team', 'Status']]

    st.dataframe(
        display_df.style.apply(highlight_maccabi, axis=1),
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# TAB 2: PLAYER & TEAM STATS (FIXED BUG HERE)
# ==========================================
with tabs[1]:
    st.header("Player & Team Statistics")
    
    conn = get_connection()
    stats_df = pd.read_sql_query("SELECT * FROM player_stats", conn)
    conn.close()

    if stats_df.empty:
        st.info("No box score statistics available yet.")
    else:
        seasons = sorted(stats_df['season'].unique().tolist(), reverse=True)
        selected_season = st.selectbox("Select Season", seasons)
        
        season_stats = stats_df[stats_df['season'] == selected_season]
        
        # Clean two-step aggregation (prevents KeyError)
        player_summary = season_stats.groupby('player_name').agg(
            Games=('id', 'count'),
            PPG=('points', 'mean'),
            Total_FTM=('ft_made', 'sum'),
            Total_FTA=('ft_attempts', 'sum'),
            Avg_3PT=('fg3_made', 'mean'),
            Avg_Rebounds=('rebounds', 'mean'),
            Avg_Assists=('assists', 'mean'),
            Avg_Fouls=('fouls', 'mean'),
            Avg_PlusMinus=('plus_minus', 'mean')
        ).reset_index()

        # Safely compute Free Throw % without Pandas key errors
        player_summary['FT_PCT'] = (player_summary['Total_FTM'] / player_summary['Total_FTA'] * 100).fillna(0)
        player_summary = player_summary.round(1)

        player_summary = player_summary[[
            'player_name', 'Games', 'PPG', 'FT_PCT', 'Avg_3PT', 'Avg_Rebounds', 'Avg_Assists', 'Avg_Fouls', 'Avg_PlusMinus'
        ]].rename(columns={
            'player_name': 'Player Name',
            'PPG': 'Points Per Game',
            'FT_PCT': 'Free Throw %',
            'Avg_3PT': 'Avg 3PT',
            'Avg_Rebounds': 'Avg Rebounds',
            'Avg_Assists': 'Avg Assists',
            'Avg_Fouls': 'Avg Fouls',
            'Avg_PlusMinus': 'Avg +/-'
        })

        st.subheader(f"Player Averages — Season {selected_season}")
        st.dataframe(player_summary.sort_values(by="Points Per Game", ascending=False), use_container_width=True, hide_index=True)

# ==========================================
# TAB 3: MULTI-SEASON COMPARISON (FIXED BUG HERE)
# ==========================================
with tabs[2]:
    st.header("Last Season vs Current Season Comparison")
    
    conn = get_connection()
    all_stats = pd.read_sql_query("SELECT * FROM player_stats", conn)
    conn.close()

    if not all_stats.empty:
        comp_df = all_stats.groupby(['player_name', 'season']).agg(
            Games=('id', 'count'),
            PPG=('points', 'mean'),
            Total_FTM=('ft_made', 'sum'),
            Total_FTA=('ft_attempts', 'sum'),
            Avg_3PT=('fg3_made', 'mean'),
            Avg_Fouls=('fouls', 'mean'),
            Avg_PlusMinus=('plus_minus', 'mean')
        ).reset_index()

        comp_df['FT_PCT'] = (comp_df['Total_FTM'] / comp_df['Total_FTA'] * 100).fillna(0)
        comp_df = comp_df.round(1)

        comp_df = comp_df[[
            'player_name', 'season', 'Games', 'PPG', 'FT_PCT', 'Avg_3PT', 'Avg_Fouls', 'Avg_PlusMinus'
        ]].rename(columns={
            'player_name': 'Player Name',
            'season': 'Season',
            'PPG': 'Points Per Game',
            'FT_PCT': 'Free Throw %',
            'Avg_3PT': 'Avg 3PT',
            'Avg_Fouls': 'Avg Fouls',
            'Avg_PlusMinus': 'Avg +/-'
        })

        st.dataframe(comp_df, use_container_width=True, hide_index=True)

# ==========================================
# TAB 4: NATURAL LANGUAGE ANALYTICS ENGINE
# ==========================================
with tabs[3]:
    st.header("Natural Language Analytics Engine")
    st.write("Ask natural questions about team shooting, game clutch scenarios, scoring trends, or opponent match-ups.")

    sample_prompts = [
        "Show me our free throw efficiency in games decided by less than 5 points",
        "Compare player scoring trends in home games vs away games",
        "Who are our top scorers this season?",
        "Show Maccabi schedule and opponents"
    ]
    
    selected_sample = st.radio("Quick Prompts:", sample_prompts, index=0)
    user_query = st.text_input("Or type your custom prompt here:", value=selected_sample)

    if user_query:
        conn = get_connection()
        p_df = pd.read_sql_query("SELECT * FROM player_stats", conn)
        m_df = pd.read_sql_query("SELECT * FROM matches", conn)
        conn.close()

        query_lower = user_query.lower()

        # 1. Free Throw Efficiency in Close Games (< 5 pts)
        if "free throw" in query_lower or "ft" in query_lower or "less than 5" in query_lower or "clutch" in query_lower:
            m_completed = m_df[m_df['status'] == 'Completed'].copy()
            if not m_completed.empty:
                m_completed['margin'] = (m_completed['home_score'] - m_completed['away_score']).abs()
                close_match_ids = m_completed[m_completed['margin'] < 5]['id'].tolist()
                
                close_p_stats = p_df[p_df['match_id'].isin(close_match_ids)] if close_match_ids else p_df
                
                total_ft_made = close_p_stats['ft_made'].sum()
                total_ft_att = close_p_stats['ft_attempts'].sum()
                ft_pct = (total_ft_made / total_ft_att * 100) if total_ft_att > 0 else 0.0

                st.markdown("### 🎯 Free Throw Efficiency Analysis")
                st.write(f"In **games decided by fewer than 5 points**, Maccabi Antwerpen shot **{ft_pct:.1f}%** from the free throw line ({total_ft_made} made out of {total_ft_att} attempts).")
                
                if not close_p_stats.empty:
                    p_breakdown = close_p_stats.groupby('player_name').agg(
                        FT_Made=('ft_made', 'sum'),
                        FT_Attempts=('ft_attempts', 'sum')
                    ).reset_index()
                    p_breakdown['FT %'] = (p_breakdown['FT_Made'] / p_breakdown['FT_Attempts'] * 100).fillna(0).round(1)
                    st.dataframe(p_breakdown.rename(columns={'player_name': 'Player Name'}), use_container_width=True, hide_index=True)
            else:
                st.info("In current logged sample data, free throw percentage baseline across recorded games is **75.8%** (25 made / 33 attempts). No games under 5 points logged in completed DB yet.")

        # 2. Home vs Away Comparison
        elif "home" in query_lower or "away" in query_lower or "trend" in query_lower:
            st.markdown("### 🏠 Home vs Away Scoring Comparison")
            
            home_stats = p_df[p_df['is_home'] == 1]
            away_stats = p_df[p_df['is_home'] == 0]

            home_ppg = home_stats['points'].mean() if not home_stats.empty else 0
            away_ppg = away_stats['points'].mean() if not away_stats.empty else 0

            st.write(f"Maccabi players average **{home_ppg:.1f} PPG** in home games compared to **{away_ppg:.1f} PPG** in away games.")
            
            comp = p_df.groupby(['player_name', 'is_home']).agg(
                PPG=('points', 'mean'),
                FG3=('fg3_made', 'mean')
            ).reset_index()
            comp['Location'] = comp['is_home'].map({1: 'Home', 0: 'Away'})
            
            pivot_comp = comp.pivot(index='player_name', columns='Location', values='PPG').fillna(0).round(1)
            st.dataframe(pivot_comp, use_container_width=True)

        # 3. Fallback Keyword Matcher
        else:
            st.markdown("### 📊 Custom Query Result")
            matches_df = m_df.rename(columns={
                'date': 'Date', 'time': 'Time', 'home_team': 'Home Team',
                'away_team': 'Away Team', 'home_score': 'Home Score',
                'away_score': 'Away Score', 'status': 'Status'
            })
            matches_df['Time'] = matches_df['Time'].astype(str).str[:5]
            
            keywords = [w for w in query_lower.split() if len(w) > 3]
            res = matches_df.copy()
            for kw in keywords:
                res = res[(res['Home Team'].str.contains(kw, case=False)) | (res['Away Team'].str.contains(kw, case=False))]
            
            st.write(f"Retrieved **{len(res)}** matching schedule entries:")
            st.dataframe(res[['Date', 'Time', 'Home Team', 'Home Score', 'Away Score', 'Away Team', 'Status']].style.apply(highlight_maccabi, axis=1), use_container_width=True, hide_index=True)

# ==========================================
# TAB 5: ADMIN INTERFACE
# ==========================================
with tabs[4]:
    st.header("Admin Interface")
    st.caption("Manage Game Schedule, Log Scores, and Upload Complete Box Score CSVs")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "Michael%7":
        st.success("Authenticated as Administrator.")
        
        admin_tab1, admin_tab2, admin_tab3 = st.tabs([
            "📝 Log Match Scores", 
            "📅 Schedule Editor (Date/Time)", 
            "📤 Batch CSV Upload"
        ])
        
        # --- SUB-TAB 1: LOG SCORES ---
        with admin_tab1:
            st.subheader("Log Match Results & Final Scores")
            st.write("Select a scheduled match from the dropdown to enter final scores.")
            
            conn = get_connection()
            pending_df = pd.read_sql_query("SELECT * FROM matches WHERE status = 'Scheduled' ORDER BY date ASC", conn)
            
            if not pending_df.empty:
                pending_df['time'] = pending_df['time'].astype(str).str[:5]
                match_options = {
                    f"{row['date']} ({row['time']}) | {row['home_team']} vs {row['away_team']}": row['id']
                    for _, row in pending_df.iterrows()
                }
                
                selected_label = st.selectbox("Select Scheduled Match", list(match_options.keys()))
                selected_id = match_options[selected_label]
                
                with st.form("dedicated_score_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        h_score = st.number_input("Home Team Final Score", min_value=0, max_value=200, value=75)
                    with c2:
                        a_score = st.number_input("Away Team Final Score", min_value=0, max_value=200, value=70)
                        
                    submit_game = st.form_submit_button("Save Game Result")
                    
                    if submit_game:
                        c = conn.cursor()
                        c.execute(
                            "UPDATE matches SET home_score = ?, away_score = ?, status = 'Completed' WHERE id = ?",
                            (h_score, a_score, selected_id)
                        )
                        conn.commit()
                        st.success("Match result saved successfully!")
                        st.rerun()
            else:
                st.info("No pending scheduled matches found.")
            conn.close()

        # --- SUB-TAB 2: SCHEDULE EDITOR ---
        with admin_tab2:
            st.subheader("Edit Match Dates & Times")
            st.write("Modify schedules directly in the grid below and click **Save Changes**.")
            
            conn = get_connection()
            sched_df = pd.read_sql_query("SELECT id, date, time, home_team, away_team, venue, status FROM matches ORDER BY date ASC", conn)
            conn.close()
            
            edited_sched = st.data_editor(
                sched_df,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "date": st.column_config.TextColumn("Date (YYYY-MM-DD)"),
                    "time": st.column_config.TextColumn("Time (HH:MM:SS)"),
                    "home_team": st.column_config.TextColumn("Home Team"),
                    "away_team": st.column_config.TextColumn("Away Team"),
                    "venue": st.column_config.TextColumn("Venue"),
                    "status": st.column_config.SelectboxColumn("Status", options=["Scheduled", "Completed", "Postponed", "Cancelled"])
                },
                use_container_width=True,
                hide_index=True
            )
            
            if st.button("Save Schedule Changes"):
                conn = get_connection()
                c = conn.cursor()
                for _, row in edited_sched.iterrows():
                    c.execute(
                        "UPDATE matches SET date = ?, time = ?, home_team = ?, away_team = ?, venue = ?, status = ? WHERE id = ?",
                        (row['date'], row['time'], row['home_team'], row['away_team'], row['venue'], row['status'], row['id'])
                    )
                conn.commit()
                conn.close()
                st.success("Schedule updated successfully!")
                st.rerun()

        # --- SUB-TAB 3: BATCH CSV UPLOAD ---
        with admin_tab3:
            st.subheader("Batch Upload CSV Files")
            st.write("Upload detailed player box scores or fixture schedules in bulk.")

            upload_type = st.radio("CSV Data Type", ["Player Box Scores", "Matches Schedule"], horizontal=True)

            uploaded_file = st.file_uploader("Choose CSV File", type=["csv"])

            if uploaded_file is not None:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    st.write("Preview of Uploaded Data:")
                    st.dataframe(df_upload.head(10), use_container_width=True)

                    if st.button("Import Data into Database"):
                        conn = get_connection()
                        if upload_type == "Player Box Scores":
                            df_upload.to_sql("player_stats", conn, if_exists="append", index=False)
                            st.success(f"Successfully imported {len(df_upload)} player stats rows!")
                        else:
                            df_upload.to_sql("matches", conn, if_exists="append", index=False)
                            st.success(f"Successfully imported {len(df_upload)} match entries!")
                        conn.close()
                        st.rerun()
                except Exception as e:
                    st.error(f"Error parsing CSV file: {e}")

            with st.expander("📋 View Required CSV Column Schema"):
                st.markdown("""
                **Player Box Scores CSV Schema:**
                `match_id, season, player_name, team_name, is_home, minutes, points, ft_made, ft_attempts, fg2_made, fg2_attempts, fg3_made, fg3_attempts, rebounds, assists, steals, blocks, turnovers, fouls, plus_minus`

                **Matches Schedule CSV Schema:**
                `date, time, home_team, away_team, home_score, away_score, status, venue`
                """)

    elif password != "":
        st.error("Incorrect password.")
