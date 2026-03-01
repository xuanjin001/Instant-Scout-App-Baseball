import streamlit as st
import pandas as pd
from Last_100_PAs import get_last_100_pa

# 1. Page Configuration
st.set_page_config(page_title="Instant Scout AI", layout="wide")

st.title("⚾ Instant Scout: AI-Powered MLB Analysis")
st.markdown("Enter a player's name to generate a professional Statcast scouting report.")

# 2. Search Bar Layout
# We use columns to put the search bar and button on the same line
col1, col2 = st.columns([4, 1])

with col1:
    player_name = st.text_input("Player Name", placeholder="e.g., Shohei Ohtani", label_visibility="collapsed")

with col2:
    search_button = st.button("Generate Report", use_container_width=True)

# 3. App Logic
if search_button and player_name:
    with st.spinner(f"Scouting {player_name}..."):
        # This is where you would call your Week 1 & 2 functions
        df = get_last_100_pa(player_name.split()[0], player_name.split()[1])
        # report = generate_report(player_name, df)

        if df is not None:
            avg_ev = df['launch_speed'].mean() if not df['launch_speed'].empty else 0
            max_ev = df['launch_speed'].max() if not df['launch_speed'].empty else 0
            hard_hit_rate = (df['launch_speed'] >= 95).mean() * 100 if not df['launch_speed'].empty else 0
            barrel_rate = (df['bb_type'] == 'pull_barrel').mean() * 100 if 'bb_type' in df.columns else 0 # Assuming 'bb_type' can indicate barrel


        # Placeholder for visual feedback
        st.divider()

        # 4. Metrics Row (The "Quick Glance" stats)
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Exit Velocity", "94.2 mph", delta="2.1 mph")
        m2.metric("Hard Hit %", "52.4%", delta="-1.2%")
        m3.metric("Barrel %", "15.8%", delta="3.4%")

        # 5. The Main AI Report
        st.subheader("📋 Scouting Analysis")
        st.info("AI-Generated Report based on last 100 Plate Appearances")
        st.write("*(Your AI scouting report from Week 2 will appear here...)*")
