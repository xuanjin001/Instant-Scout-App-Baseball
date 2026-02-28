import streamlit as st
from AI_Scout import get_last_100_pa, generate_scouting_report

# 1. Page Configuration
st.set_page_config(page_title="Instant Scout AI", layout="wide")

st.title("⚾ Instant Scout: AI-Powered MLB Analysis")
st.markdown("Enter a player's name to generate a professional Statcast scouting report.")

# 2. Search Bar Layout
col1, col2 = st.columns([4, 1])

with col1:
    player_name = st.text_input("Player Name", placeholder="e.g., Shohei Ohtani", label_visibility="collapsed")

with col2:
    search_button = st.button("Generate Report", use_container_width=True)

# 3. App Logic
if search_button and player_name:
    with st.spinner(f"Scouting {player_name}..."):
        # Split name for the pybaseball lookup
        name_parts = player_name.split()
        if len(name_parts) < 2:
            st.error("Please enter a full name (First Last).")
        else:
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])

            # Fetch Data
            df = get_last_100_pa(first_name, last_name)

            if df is not None and not df.empty:
                # Calculate Quick Metrics
                avg_ev = df['launch_speed'].mean()
                hard_hit = (df['launch_speed'] >= 95).mean() * 100
                
                # Display Metrics
                m1, m2 = st.columns(2)
                m1.metric("Avg Exit Velocity", f"{avg_ev:.1f} mph")
                m2.metric("Hard Hit %", f"{hard_hit:.1f}%")

                st.divider()

                # Generate and Display AI Report
                report = generate_scouting_report(player_name, df)
                st.subheader("📋 Scouting Analysis")
                st.markdown(report)
            else:
                st.error("Player not found or insufficient data.")
