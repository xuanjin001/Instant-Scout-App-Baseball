import os
import streamlit as st
import pandas as pd
import pybaseball as pb
from datetime import datetime, timedelta
from google import genai
from dotenv import load_dotenv

from Last_100_PAs import get_last_100_pa
from AI_Scout import generate_scouting_report

# import plotly.graph_objects as go
from plot_graph import create_radar_chart

# Load variables from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# 1. Page Configuration
st.set_page_config(page_title="Instant Scout AI", layout="wide")

st.title("⚾ Instant Scout: AI-Powered MLB Analysis")
st.markdown("Enter a player's name to generate a professional Statcast scouting report.")

# 2. Search Bar Layout
# We use columns to put the search bar and button on the same line
col1, col2 = st.columns([4, 1])

with col1:
    # player_name = st.text_input("Player Name", placeholder="e.g., Shohei Ohtani", label_visibility="collapsed")
    player_name = st.text_input("Player Name", placeholder="e.g., Shohei Ohtani", label_visibility="collapsed")

with col2:
    search_button = st.button("Generate Report", use_container_width=True)


# 3. App Logic
if search_button and player_name:
    # Split player name into first and last name
    names = player_name.split()
    
    if len(names) >= 3:
        # If 3+ words: first 2 words = first name, last word = last name
        first_name = " ".join(names[:-1])
        last_name = names[-1]
    elif len(names) == 2:
        # If 2 words: first word = first name, second word = last name
        first_name = names[0]
        last_name = names[1]
    else:
        # If 1 word: same word for both
        first_name = names[0]
        last_name = names[0]
    
    with st.spinner(f"Scouting {player_name}..."):
        # This is where you would call your Week 1 & 2 functions
        df = get_last_100_pa(first_name, last_name)
        # report = generate_report(player_name, df)

        # Placeholder for visual feedback
        st.divider()

        # 4. Metrics Row (The "Quick Glance" stats)
        m1, m2, m3 = st.columns(3)
        # m1.metric("Avg Exit Velocity", "94.2 mph", delta="2.1 mph")
        # m2.metric("Hard Hit %", "52.4%", delta="-1.2%")
        # m3.metric("Barrel %", "15.8%", delta="3.4%")

        # "avg_exit_velo": round(df['launch_speed'].mean(), 1),
        m1.metric("Avg Exit Velocity", f"{df['launch_speed'].mean():.1f} mph")
        m2.metric("Max Exit Velocity", f"{df['launch_speed'].max():.1f} mph")
        m3.metric("Avg Launch Angle", f"{df['launch_angle'].mean():.1f}°")



        # 5. The Main AI Report
        st.subheader("📋 Scouting Analysis")
        st.info("AI-Generated Report based on last 100 Plate Appearances")
        # st.write("*(Your AI scouting report from Week 2 will appear here...)*")

        

        if df is not None:
                # Create stats dict for radar chart
                # Handle cases where specific columns might be missing
                barrel_rate = df['barrel'].mean() * 100 if 'barrel' in df.columns else 0
                
                my_stats = {
                    'ev': df['launch_speed'].mean(),
                    'la': df['launch_angle'].mean(),
                    'hh': (df['launch_speed'] >= 95).mean() * 100,
                    'br': barrel_rate,
                    'zc': df['zone_contact'].mean() if 'zone_contact' in df.columns else 50
                }
                
                report = generate_scouting_report(player_name, df)
                st.plotly_chart(create_radar_chart(my_stats), use_container_width=True)
                
                if report:
                    print("\n" + "="*60)
                    print("SCOUTING REPORT")
                    print("="*60)
                    print(report)
                    st.write(report)
                else:
                    print("\nCould not generate report - API quota exhausted.")
        else:
            print("Could not fetch player data.")
