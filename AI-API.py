

# Install the handler: `pip install python-dotenv google-genai`

import os
import json
import time
import pandas as pd
from google import genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Cache file to store generated reports
CACHE_FILE = "reports_cache.json"

def load_cache():
    """Load cached reports from file"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save reports to cache file"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def generate_report(player_name, df):
    # Check cache first
    cache = load_cache()
    if player_name in cache:
        print(f"✓ Found cached report for {player_name}")
        return cache[player_name]
    
    # 1. Summarize the data so the AI isn't overwhelmed
    stats_summary = {
        "avg_exit_velo": round(df['launch_speed'].mean(), 1),
        "max_exit_velo": df['launch_speed'].max(),
        "avg_launch_angle": round(df['launch_angle'].mean(), 1),
        "outcomes": df['events'].value_counts().to_dict()
    }

    # 2. Construct the specific request
    prompt = f"""
    Analyze the following Statcast data for {player_name}:
    {stats_summary}

    Write a 3-paragraph professional scouting report:
    - Para 1: Physical tools and contact quality.
    - Para 2: Plate discipline and outcome trends.
    - Para 3: Future outlook and 'pro comparison'.

- [PARAGRAPH 1]: The Contact Profile (EV, LA, Barrels).
- [PARAGRAPH 2]: Plate Discipline & Decision Making (K/BB, Whiff%).
- [PARAGRAPH 3]: Front Office Recommendation (e.g., "Target in trade," "Adjust defensive positioning," "High-risk/High-reward").
    """

    # 3. Call the API with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            report = response.text
            
            # Cache the result
            cache[player_name] = report
            save_cache(cache)
            print(f"✓ Generated and cached report for {player_name}")
            return report
        
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    wait_time = 50 + (attempt * 10)  # 50s, 60s, 70s
                    print(f"\n⏳ Quota exceeded. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print("\n❌ API quota exhausted after all retries")
                    print("Options:")
                    print("  1. Upgrade to paid plan: https://ai.google.dev")
                    print("  2. Wait for quota reset (daily limit)")
                    print("  3. Use cached reports: check reports_cache.json")
                    return None
            else:
                raise

# --- TEST IT ---
# df = pd.read_csv('last_100_pas.csv') # Use the data from Week 1
df = pd.read_csv('./jung-hoo-lee.csv')
report = generate_report("Jung-Hoo Lee", df)
if report:
    print("\n" + "="*60)
    print("SCOUTING REPORT")
    print("="*60)
    print(report)