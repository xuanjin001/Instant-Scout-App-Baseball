# Instant-Scout-App-Baseball

Instant Scout App Baseball

To set up your "Instant Scout" environment, we’ll focus on creating a **clean, isolated workspace**. In the world of Python, the "best" way is to use a **Virtual Environment**. This ensures that the libraries you install for your baseball app don't interfere with other projects on your computer.

## Week 1: Data Infrastructure & 'The Pipeline' - Setup environment (VS Code, Python, pybaseball, pandas)

---

## 🛠️ Step 1: Create Your Workspace

Before touching any code, give your project a home.

1. Create a new folder on your computer named `instant-scout`.
2. Open **VS Code**.
3. Go to `File > Open Folder...` and select your `instant-scout` folder.

## 🐍 Step 2: Set Up the Virtual Environment (Venv)

This is the "pro" way to manage your tools.

1. Open the **Terminal** in VS Code (Press `Ctrl + ~` or `Cmd + ~` on Mac).
2. Type the following command and hit Enter:

```bash
python -m venv venv

```

3. **Activate it:**

- **Windows:** `.\venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

4. _Look for `(venv)` to appear at the start of your terminal line. This means you're "inside" the environment._

## 📦 Step 3: Install the "Big Three" Libraries

Now that your environment is active, install the specific tools we need:

```bash
pip install pybaseball pandas streamlit

```

- **pybaseball:** Your data straw—it sucks the stats out of MLB databases.
- **pandas:** Your data blender—it organizes and cleans the stats.
- **streamlit:** Your display case—it turns your code into a website.

## ✅ Step 4: The Connection Test

Create a new file called `test_data.py` and paste this code to see if everything is working:

```python
import pybaseball as pb

# Search for a player (Let's use Aaron Judge)
data = pb.playerid_lookup('judge', 'aaron')
print("Connection Successful!")
print(data)

```

Please Note:

- VS Code alternative: open Command Palette → Python: Select Interpreter → choose the python interpreter, then click the green “Run Python File in Terminal” play button

- Use `deactivate` to get out of `(venv)`

<br>

## Week 1: Write script to fetch last 100 plate appearances via pybaseball

To fetch the last 100 plate appearances, we have to navigate a specific quirk of the `pybaseball` library: it primarily returns **pitch-by-pitch** data. To get 100 "Plate Appearances" (PAs), we have to filter for the pitches that actually ended the turn (hits, strikeouts, walks, etc.).

Here is the refined script to handle the lookup, the fetch, and the filtering logic.

---

### 💻 The "Last 100 PAs" Script

```python
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
    last_100 = pa_data.head(100)

    return last_100

# --- EXECUTION ---
df = get_last_100_pa('Shohei', 'Ohtani')

if df is not None:
    print(f"Successfully retrieved {len(df)} Plate Appearances.")
    # Show the most relevant columns for your AI Scout
    print(df[['game_date', 'events', 'launch_speed', 'launch_angle']].head(10))

```

---

### 🔑 Why this specific logic?

- **The `events` Filter:** If you don't filter by `events`, you'll get every single 0-1 foul ball and 1-1 take. By dropping rows where `events` is empty, you're left only with the "outcomes" (Home Run, Groundout, etc.).
- **The Date Window:** `statcast_batter` requires a date range. Since players have off-seasons, we use a rolling 2-year window to make sure the script doesn't return an empty set if you run it in January.
- **Data Preparation for AI:** For Phase 2 (the AI Brain), the columns `launch_speed` (Exit Velocity) and `launch_angle` are the most important. They tell the AI how hard and at what angle the player is hitting the ball, regardless of whether it was caught.

### 💡 Pro-Tip: Avoid the "Rate Limit"

If you run this script 50 times in an hour while debugging, MLB's servers might temporarily block your IP. I recommend saving your data to a CSV while you work on the AI prompt:

```python
df.to_csv('last_100_pas.csv', index=False)

```

**Would you like me to help you write the "Aggregator" next? This would calculate metrics like "Hard Hit %" and "Average Exit Velocity" from this data to feed into your AI.**

## Week 1: Test printing average Exit Velocity and Launch Angle to console

## Week 2: The 'AI Scout' Brain - API Setup (Gemini or OpenAI) and basic prompt testing

## Week 2: Prompt Engineering - Refine system message for MLB Sabermetrics expert analysis

## Week 2: Connect Python script to AI API to generate 3-paragraph report

## Week 3: Building the Interface (Frontend) - Build Streamlit layout with search bar and button

## Week 3: Add visual elements (st.metric for stats, Plotly for spray charts)

## Week 4: Polishing & Deployment - Implement @st.cache_data for performance

## Week 4: Deploy to Streamlit Community Cloud

## Week 4: Portfolio Update - Record screen capture and update resume/LinkedIn

**Next Step:** Run that script by typing `python test_data.py` in your terminal. If you see Aaron Judge's MLB ID, you're ready for Phase 1!

**Would you like me to show you how to pull the specific "Statcast" metrics (Exit Velocity, etc.) for your first report?**
