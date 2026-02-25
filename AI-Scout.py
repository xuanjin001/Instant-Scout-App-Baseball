import os
from google import genai
from google.genai import types
import pybaseball as pb
import pandas as pd
from datetime import datetime, timedelta
import time

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
    system_prompt = f"""You are a Senior MLB Sabermetrics Analyst for a Major League Front Office.
Your goal is to provide a "Context-Inclusive" scouting report based on 100 Plate Appearances of Statcast data.

### EVALUATION FRAMEWORK:
1. Contact Quality: Prioritize "Barrels" and "Hard Hit %". If Hard Hit % > 45%, classify as "Elite Power Grade".
2. Plate Discipline: Analyze the relationship between K% and Whiff%. Distinguish between "Aggressive-Productive" and "Chasing".
3. Trend Analysis: Note if the player's recent Launch Angle (LA) suggests a "Launch Angle Revolution" adjustment or if they are "Topping" the ball (negative LA).

### TONE & STYLE:
- Use professional scouting lingo: "plus-plus raw power," "noise in the mechanics," "high-floor profile," "swing-and-miss profile."
- Be objective and clinical. Avoid fluff.
- Compare the current data to league averages (e.g., Average Exit Velo is ~89 mph).

### 1. Sample report

> _“Here is an example of a high-quality report for Aaron Judge: [
Scout Report: Aaron Judge (OF - NYY)
Based on 2024-2025 performance data
Overall Rating: 80 (Elite / Franchise Cornerstone)
Summary: A monumental talent and arguably the best right-handed hitter of his generation. Judge combines unprecedented raw power with elite plate discipline and high-IQ hitting, transforming from a high-strikeout prospect into a perennial MVP candidate who dominates all fields.
Hitting/Power (80/80):
Power: Top-of-the-scale raw power (70-80 grade) that translates fully to game scenarios, capable of hitting home runs to all fields, including opposite-field drives at Yankee Stadium.
Approach: Exceptionally patient. High walk rates paired with elite exit velocities (4th-fastest average bat speed in MLB at 77.0 MPH) and high barrel rates.
Refinement: Has matured from a pure slugger into a high-average hitter (hitting over .320 in 2024-2025) by improving contact rates and selectively attacking in-zone pitches.
Fielding/Defense (60/60):
Position: Capable of playing center field but is a elite defender in right field.
Metrics: Possesses gold glove caliber range and, despite his 6'7" frame, shows surprisingly fluid defensive actions.
Arm: Plus-plus arm strength and accuracy (60-70 grade), making him a premier defensive outfielder.
Baserunning (50/55):
Speed: Above-average speed for his size, especially once underway. While not a burner, he is a smart base runner with increasing efficiency in stealing bases (10+ steals in 2024-2025).
Weaknesses/Risks:
Health: Given his size and physicality, he carries historical injury risk, though he has proven durable over the past two seasons.
Strikeout Profile: While reduced, there is inherent swing-and-miss against high-end breaking stuff low in the zone.
Projected Outlook:
A 50+ home run threat with a .300+ batting average, elite discipline, and elite right-field defense, leading as the New York Yankees captain and providing a "rare total package" of skill and leadership.

]. Now, perform a similar analysis for the following data...”_


### 2. Guardrails Against "Hallucination"

> _“Strictly use the provided numbers. If a metric like 'Spin Rate' is not in the dataset, do not mention it. If the sample size is too small for a definitive conclusion, state 'Sample Size Warning'.”_

### 3. "Self-Critique" Loop

> _“After writing the report, review it for internal consistency. Does the 'Recommendation' match the 'Contact Profile'? Revise if necessary.”_



### OUTPUT STRUCTURE:
- [HEADING]: Player Name & Primary Tool Grade (20-80 Scale).
- [PARAGRAPH 1]: The Contact Profile (EV, LA, Barrels).
- [PARAGRAPH 2]: Plate Discipline & Decision Making (K/BB, Whiff%).
- [PARAGRAPH 3]: Front Office Recommendation (e.g., "Target in trade," "Adjust defensive positioning," "High-risk/High-reward").
"""
    # 3. Call Gemini with retry logic
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                #model="gemini-2.0-flash",
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(system_instruction=system_prompt),
                contents=data_summary
            )
            return response.text
        
        except Exception as e:
            error_str = str(e)
            
            if "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"\n⚠️  API Quota Exceeded. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print("\n❌ API Quota Exhausted (all retries failed)")
                    print("Options:")
                    print("  1. Wait 24 hours for daily quota to reset")
                    print("  2. Upgrade to paid plan: https://ai.google.dev")
                    print("  3. Check limits: https://console.cloud.google.com/")
                    return None
            else:
                # Re-raise other exceptions
                raise

# Test it with your DataFrame from Week 1
pb.cache.enable()
if __name__ == "__main__":
    # df = get_last_100_pa("Tim", "Lincecum")
    df = get_last_100_pa("Jung Hoo", "Lee")
    
    if df is not None:
        report = generate_scouting_report("Jung Hoo Lee", df)
        
        if report:
            print("\n" + "="*60)
            print("SCOUTING REPORT")
            print("="*60)
            print(report)
        else:
            print("\nCould not generate report - API quota exhausted.")
    else:
        print("Could not fetch player data.")
