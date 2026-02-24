
import pybaseball as pb
import pandas as pd
from datetime import datetime, timedelta

def get_last_100_pa(first_name, last_name):
    # 1. Lookup the player's unique MLB ID
    print(f"Searching for {first_name} {last_name}...")
    lookup = pb.playerid_lookup(last_name, first_name)

    if lookup.empty:
        print("Player not found.")
        return None

    # Grab the MLBAM ID (the one Statcast uses)
    mlb_id = lookup['key_mlbam'].values[0]

    # 2. Define the date range (fetching the last ~2 years to ensure we find 100 PAs)
    today = datetime.today()
    start_date = (today - timedelta(days=730)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    # 3. Fetch pitch-by-pitch data
    print("Fetching Statcast data (this may take a few seconds)...")
    raw_data = pb.statcast_batter(start_date, end_date, mlb_id)

    # 4. Filter for the END of a Plate Appearance
    # In Statcast data, the 'events' column is only populated on the final pitch of a PA.
    pa_data = raw_data.dropna(subset=['events']).copy()

    # Sort by date and game time to ensure we have the most recent data
    pa_data = pa_data.sort_values(by=['game_date', 'at_bat_number'], ascending=False)

    # 5. Extract the 100 most recent rows
    last_100 = pa_data.head(500)

    return last_100

# --- EXECUTION ---
pb.cache.enable()
# df = get_last_100_pa("Tim", "Lincecum")
df = get_last_100_pa("Jung Hoo", "Lee")

if df is not None:
    print(f"Successfully retrieved {len(df)} Plate Appearances.")
    # Show the most relevant columns for your AI Scout
    print(df[['game_date', 'events', 'launch_speed', 'launch_angle']].head(10))
    df.to_csv('last_100_pas.csv', index=False)
    print("Saved to last_100_pas.csv")
else:
    print("Error: Could not fetch player data. Check the player name or internet connection.")