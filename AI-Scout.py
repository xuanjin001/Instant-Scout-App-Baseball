import os
from google import genai
from google.genai import types
import pybaseball as pb
import pandas as pd
from datetime import datetime, timedelta

# 1. Initialize Client (Picks up key from environment variable)
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY environment variable not set. "
        "Please set it with: export GOOGLE_API_KEY='your-api-key'"
    )
client = genai.Client(api_key=api_key)

def get_last_100_pa(first_name, last_name):
    """Fetch the last 100 plate appearances for a player"""
    print(f"Searching for {first_name} {last_name}...")
    lookup = pb.playerid_lookup(last_name, first_name)

    if lookup.empty:
        print("Player not found.")
        return None

    mlb_id = lookup['key_mlbam'].values[0]
    
    today = datetime.today()
    start_date = (today - timedelta(days=730)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    print("Fetching Statcast data...")
    raw_data = pb.statcast_batter(start_date, end_date, mlb_id)

    pa_data = raw_data.dropna(subset=['events']).copy()
    pa_data = pa_data.sort_values(by=['game_date', 'at_bat_number'], ascending=False)
    last_100 = pa_data.head(100)

    return last_100

def generate_scouting_report(player_name, stats_df):
    # Convert the last 100 PAs into a summary string for the AI
    # We aggregate data to keep the prompt clean and concise
    avg_ev = stats_df['launch_speed'].mean()
    max_ev = stats_df['launch_speed'].max()
    hard_hit_rate = (stats_df['launch_speed'] >= 95).mean() * 100

    data_summary = f"""
    Player: {player_name}
    Last 100 PAs Summary:
    - Average Exit Velocity: {avg_ev:.1f} mph
    - Max Exit Velocity: {max_ev:.1f} mph
    - Hard Hit %: {hard_hit_rate:.1f}%
    - Recent Outcomes: {stats_df['events'].value_counts().to_dict()}
    """

    # 2. Define the Prompt (The "Brain")
    system_prompt = "You are a professional MLB Scout. Use the provided Statcast data to write a concise, 3-paragraph report. Focus on power profile, recent plate discipline, and a 'prospect outlook'. Use scouting lingo (e.g., 'plus-power', 'noise in the delivery')."

    # 3. Call Gemini
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        contents=data_summary
    )

    return response.text

# Test it with your DataFrame from Week 1
pb.cache.enable()
if __name__ == "__main__":
    # df = get_last_100_pa("Tim", "Lincecum")
    df = get_last_100_pa("Jung Hoo", "Lee")
    
    if df is not None:
        report = generate_scouting_report("Jung Hoo Lee", df)
        print("\n" + "="*60)
        print("SCOUTING REPORT")
        print("="*60)
        print(report)
    else:
        print("Could not fetch player data.")
