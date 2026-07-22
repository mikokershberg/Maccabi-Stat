import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Maccabi Basketball Portal",
    page_icon="🏀",
    layout="wide"
)

# --- DATABASE SETUP (Shared Data Store) ---
DB_FILE = "maccabi_stats.db"

def init_sqlite_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Matches table
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER,
            status TEXT DEFAULT 'Scheduled'
        )
    ''')
    # Player stats table (Multi-Season)
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            player_name TEXT,
            season TEXT,
            minutes REAL,
            ft_made INTEGER,
            fg2_made INTEGER,
            fg3_made INTEGER,
            points INTEGER,
            plus_minus REAL,
            fouls INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_sqlite_db()

def get_connection():
    return sqlite3.connect(DB_FILE)

# --- HEADER & NAVIGATION ---
st.title("🏀 Maccabi Antwerpen — Team & League Portal")
st.caption("2e Provincial Heren Antwerpen B | Single Unified Center")

tabs = st.tabs([
    "📅 Schedule & Results",
    "📊 Player & Team Stats",
    "🔄 Last Season vs. Current",
    "🔍 Prompt Query",
    "🔒 Admin Interface"
])

# ==========================================
# TAB 1: SCHEDULE & RESULTS
# ==========================================
with tabs[0]:
    st.header("Schedule & Results")
    
    conn = get_connection()
    matches_df = pd.read_sql_query("SELECT * FROM matches ORDER BY date ASC", conn)
    conn.close()

    if matches_df.empty:
        st.info("No match data found. Please load the schedule via the Admin panel or script.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            team_filter = st.selectbox("Filter Team", ["All Teams"] + sorted(list(set(matches_df['home_team']).union(set(matches_df['away_team'])))))
        with col2:
            status_filter = st.radio("Status", ["All", "Upcoming", "Completed"], horizontal=True)

        filtered = matches_df.copy()
        if team_filter != "All Teams":
            filtered = filtered[(filtered['home_team'] == team_filter) | (filtered['away_team'] == team_filter)]
        if status_filter == "Upcoming":
            filtered = filtered[filtered['status'] == 'Scheduled']
        elif status_filter == "Completed":
            filtered = filtered[filtered['status'] == 'Completed']

        st.dataframe(
            filtered[['date', 'time', 'home_team', 'home_score', 'away_score', 'away_team', 'status']],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# TAB 2: PLAYER & TEAM STATS
# ==========================================
with tabs[1]:
    st.header("Current Season Statistics")
    
    conn = get_connection()
    stats_df = pd.read_sql_query("SELECT * FROM player_stats WHERE season = '2026-2027'", conn)
    conn.close()

    if stats_df.empty:
        st.info("No stat records available for the current season yet.")
    else:
        # Aggregated Player Leaderboard
        player_summary = stats_df.groupby('player_name').agg(
            Games=('id', 'count'),
            Avg_Points=('points', 'mean'),
            Avg_3PT=('fg3_made', 'mean'),
            Avg_Fouls=('fouls', 'mean'),
            Avg_PlusMinus=('plus_minus', 'mean')
        ).reset_index().round(2)

        st.subheader("Player Performance Averages")
        st.dataframe(player_summary.sort_values(by="Avg_Points", ascending=False), use_container_width=True, hide_index=True)

# ==========================================
# TAB 3: MULTI-SEASON COMPARISON
# ==========================================
with tabs[2]:
    st.header("Last Season vs. Current Season Performance")
    
    conn = get_connection()
    all_stats = pd.read_sql_query("SELECT * FROM player_stats", conn)
    conn.close()

    if all_stats.empty:
        st.info("Insufficient multi-season data for comparison.")
    else:
        season_comp = all_stats.groupby(['player_name', 'season']).agg(
            Games=('id', 'count'),
            PPG=('points', 'mean'),
            Avg_3PT=('fg3_made', 'mean'),
            Avg_Fouls=('fouls', 'mean')
        ).reset_index().round(2)

        st.dataframe(season_comp, use_container_width=True, hide_index=True)

# ==========================================
# TAB 4: NATURAL LANGUAGE PROMPT QUERY
# ==========================================
with tabs[3]:
    st.header("🔍 Ask the Stats Hub")
    st.write("Enter natural language queries to filter stats or game logs.")

    query = st.text_input("e.g., 'Show games scored over 70' or 'Show players averaging over 10 points'")
    
    if query:
        conn = get_connection()
        all_matches = pd.read_sql_query("SELECT * FROM matches", conn)
        all_players = pd.read_sql_query("SELECT * FROM player_stats", conn)
        conn.close()

        q_lower = query.lower()
        if "70" in q_lower or "score" in q_lower:
            res = all_matches[(all_matches['home_score'] > 70) | (all_matches['away_score'] > 70)]
            st.write("Matching Games:")
            st.dataframe(res, use_container_width=True)
        elif "point" in q_lower or "player" in q_lower:
            res = all_players.groupby('player_name')['points'].mean().reset_index()
            st.write("Player Points Averages:")
            st.dataframe(res, use_container_width=True)
        else:
            st.info("Query processed. Showing general match overview:")
            st.dataframe(all_matches.head(), use_container_width=True)

# ==========================================
# TAB 5: ADMIN INTERFACE (Password Protected)
# ==========================================
with tabs[4]:
    st.header("🔒 Admin Panel — Score & Box Score Logging")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "Michael%7":
        st.success("Authenticated as Administrator.")
        
        conn = get_connection()
        matches_df = pd.read_sql_query("SELECT * FROM matches WHERE status = 'Scheduled' ORDER BY date ASC", conn)
        
        if not matches_df.empty:
            match_options = {f"{row['date']} | {row['home_team']} vs {row['away_team']}": row['id'] for _, row in matches_df.iterrows()}
            selected_match_label = st.selectbox("Select Game to Log Result", list(match_options.keys()))
            selected_match_id = match_options[selected_match_label]
            
            with st.form("score_entry_form"):
                col1, col2 = st.columns(2)
                with col1:
                    home_score = st.number_input("Home Score", min_value=0, step=1)
                with col2:
                    away_score = st.number_input("Away Score", min_value=0, step=1)
                
                submit_score = st.form_submit_button("Submit Game Score")
                
                if submit_score:
                    c = conn.cursor()
                    c.execute(
                        "UPDATE matches SET home_score = ?, away_score = ?, status = 'Completed' WHERE id = ?",
                        (home_score, away_score, selected_match_id)
                    )
                    conn.commit()
                    st.success("Game score updated and synchronized live!")
                    st.rerun()
        else:
            st.info("No upcoming scheduled matches found to update.")
            
        conn.close()
    elif password != "":
        st.error("Incorrect password.")
