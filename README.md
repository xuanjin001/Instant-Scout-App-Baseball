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

In Week 2, we transition from collecting raw data to building the "Intelligence" of the app. This involves setting up your API access and, more importantly, **Prompt Engineering**—crafting the persona that turns numbers into a story.

---

## 🔑 1. Setup Your Gemini API Key

For this project, I recommend using the **Gemini 3 Flash** model. It's incredibly fast, cost-effective (with a generous free tier), and specialized for tasks like summarizing data.

1. **Get the Key:** Go to [Google AI Studio](https://aistudio.google.com/).
2. **Create Key:** Click "Get API key" in the sidebar and create a key in a new project.
3. **Secure It:** In your terminal, set it as an environment variable so you don't accidentally share it:

- **Windows (PowerShell):** `$env:GEMINI_API_KEY="your_key_here"`
- **Mac/Linux:** `export GEMINI_API_KEY="your_key_here"`

---

## 🧠 2. The "AI Scout" Script

This script takes the DataFrame from Week 1, converts it to a readable string, and sends it to Gemini with a "System Instruction" that defines its personality.

```python
import os
from google import genai
from google.genai import types

# 1. Initialize Client (Picks up key from environment variable)
client = genai.Client()

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
# report = generate_scouting_report("Shohei Ohtani", df)
# print(report)

```

---

## 🧪 3. Basic Prompt Testing (What to tweak)

To get the best reports, experiment with the `system_prompt`. Try adding these instructions to see how the tone changes:

- **"The Skeptic":** "Identify one statistical red flag that might suggest a future decline in performance."
- **"The Fantasy Guru":** "Analyze this specifically for a fantasy baseball owner. Should they Buy, Sell, or Hold?"
- **"The Comp Specialist":** "Based on the exit velocity and launch angle profile, compare this player to a historical MLB great."

### ✅ Success Metric for Week 2

You have a script where you can input a player's name and, within 5 seconds, receive a 3-paragraph scouting report that sounds like it was written by a human scout.

**Would you like me to show you how to structure the output as JSON so it's easier to display in your web app later?**

## Week 2: Prompt Engineering - Refine system message for MLB Sabermetrics expert analysis

To move from a "basic chatbot" to a professional **MLB Sabermetrics Expert**, your prompt needs to do more than just summarize—it needs to interpret data through the lens of modern baseball theory.

In 2026, scouts don't just look at "Home Runs"; they look at **Barrels**, **Whiff Rates**, and **Expected Run Values (xRA)**. Here is how to refine your system message to achieve that "Front Office" feel.

---

## 🛠️ The Refined "Expert" System Prompt

Copy and paste this into your Week 2 script. This uses a "Chain of Thought" structure to force the AI to reason through the data before writing.

```text
You are a Senior MLB Sabermetrics Analyst for a Major League Front Office.
Your goal is to provide a "Context-Inclusive" scouting report based on 100 Plate Appearances of Statcast data.

### EVALUATION FRAMEWORK:
1. Contact Quality: Prioritize "Barrels" and "Hard Hit %". If Hard Hit % > 45%, classify as "Elite Power Grade".
2. Plate Discipline: Analyze the relationship between K% and Whiff%. Distinguish between "Aggressive-Productive" and "Chasing".
3. Trend Analysis: Note if the player's recent Launch Angle (LA) suggests a "Launch Angle Revolution" adjustment or if they are "Topping" the ball (negative LA).

### TONE & STYLE:
- Use professional scouting lingo: "plus-plus raw power," "noise in the mechanics," "high-floor profile," "swing-and-miss profile."
- Be objective and clinical. Avoid fluff.
- Compare the current data to league averages (e.g., Average Exit Velo is ~89 mph).

### OUTPUT STRUCTURE:
- [HEADING]: Player Name & Primary Tool Grade (20-80 Scale).
- [PARAGRAPH 1]: The Contact Profile (EV, LA, Barrels).
- [PARAGRAPH 2]: Plate Discipline & Decision Making (K/BB, Whiff%).
- [PARAGRAPH 3]: Front Office Recommendation (e.g., "Target in trade," "Adjust defensive positioning," "High-risk/High-reward").

```

---

## 🔬 Advanced Prompting Techniques

To take this to the next level, consider these three "Pro" adjustments:

### 1. The "Few-Shot" Method

LLMs learn best by example. Add a "Sample Report" to your prompt.

> _“Here is an example of a high-quality report for Aaron Judge: [Paste a short, high-quality report here]. Now, perform a similar analysis for the following data...”_

### 2. Guardrails Against "Hallucination"

AI sometimes makes up stats if the data is missing. Add this line:

> _“Strictly use the provided numbers. If a metric like 'Spin Rate' is not in the dataset, do not mention it. If the sample size is too small for a definitive conclusion, state 'Sample Size Warning'.”_

### 3. "Self-Critique" Loop

Ask the AI to review its own work before showing it to you.

> _“After writing the report, review it for internal consistency. Does the 'Recommendation' match the 'Contact Profile'? Revise if necessary.”_

---

## 📊 Week 2 Success Checklist

- [x] **API Connectivity:** Your Python script successfully calls the Gemini/OpenAI API.
- [x] **Variable Injection:** The script dynamically inserts the player's name and stats into the prompt template.
- [x] **Output Quality:** The report uses terms like "Barrel Rate" and "Whiff%" correctly.

**Would you like me to help you create a "Scouting Lingo Glossary" in Python to help the AI map raw numbers to "20-80 Scale" grades?**

## Week 2: Connect Python script to AI API to generate 3-paragraph report

In Week 2, we bridge the gap between "raw data" and "human insight." This is where your Python script takes the data from Week 1, cleans it, and feeds it to the AI.

---

## 🛠️ Step 1: Secure Your API Key

Before writing code, ensure your API key is stored safely. Never "hard-code" it directly into your script.

1. Create a file named `.env` in your project folder.
2. Add your key: `GEMINI_API_KEY=your_actual_key_here`
3. Install the handler: `pip install python-dotenv google-genai`

## 🧠 Step 2: The "Bridge" Script

This script performs three jobs: it summarizes your DataFrame, sends it to the AI, and prints the 3-paragraph report.

```python
import os
import pandas as pd
from google import genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_report(player_name, df):
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
    """

    # 3. Call the API
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text

# --- TEST IT ---
# df = pd.read_csv('last_100_pas.csv') # Use the data from Week 1
# print(generate_report("Shohei Ohtani", df))

```

---

## 🔬 Step 3: Prompt Refinement

If the AI is being too "chatty" or getting stats wrong, use a **System Instruction**. This acts as a permanent personality for the AI that stays consistent across every report.

- **The Goal:** Tell the AI _how_ to think before it sees the data.
- **The Lingo:** Encourage it to use "scouting grades" (the 20-80 scale).

> **Success Metric:** By the end of this week, you should be able to run one command and see a perfectly formatted, 3-paragraph scouting report for any player in your dataset.

**Would you like me to help you format the AI's output into a clean JSON structure so it's ready for your website in Week 3?**

[Connect Python to Gemini API](https://www.youtube.com/watch?v=cd_2NXuTGlQ)
This video provides a clear walkthrough of setting up the Google GenAI library and making your first text generation request.

## Week 3: Building the Interface (Frontend) - Build Streamlit layout with search bar and button

In Week 3, we move from the terminal to the web browser. **Streamlit** is the industry standard for this because it allows you to build a professional-looking interface using only Python—no HTML or CSS required.

---

## 🛠️ The "Instant Scout" App Blueprint

This script creates a "Wide Mode" layout with a search bar and three high-impact "KPI cards" (Key Performance Indicators) at the top.

```python
import streamlit as st
import pandas as pd

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
        # df = get_last_100_pa(player_name)
        # report = generate_report(player_name, df)

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

```

---

## 🏗️ Key Streamlit Components Explained

| Component    | Why we use it in a Baseball App                                                                           |
| ------------ | --------------------------------------------------------------------------------------------------------- |
| `st.columns` | Keeps your layout from looking like a long, boring list. Good for comparing stats side-by-side.           |
| `st.metric`  | Perfect for "Big Numbers" like Exit Velo or Home Runs. The `delta` parameter shows if they are improving. |
| `st.spinner` | Essential for AI. It tells the user "The AI is thinking" so they don't think the app is frozen.           |
| `st.divider` | Cleanly separates the search area from the results.                                                       |

## 🚀 Pro-Tip: The "Sidebar" Option

If you want to add filters (like "Season," "Home vs. Away," or "Pitch Type"), move the search bar to the sidebar using `with st.sidebar:`. This keeps the main screen dedicated solely to the scouting report and charts.

### ✅ Success Metric for Week 3

You can run `streamlit run app.py` in your terminal and see a website that actually reacts when you click the "Generate" button.

**Would you like me to show you how to add a "Spray Chart" or "Radar Chart" using Plotly to make the report look even more professional?**

[Build Interactive Data Apps with Streamlit](https://www.youtube.com/watch?v=JozICuAZMIw)
This tutorial walks through the exact components used above, including layout mastery with columns and interactive widgets.

Adding visualizations is the "secret sauce" that makes your app look like a professional scouting tool rather than a simple chatbot. We’ll use **Plotly**, which integrates natively with Streamlit to provide interactive, hoverable charts.

---

-- stopped here, need to do the following still

## 🛰️ 1. The Radar Chart (Percentile Rankings)

A radar chart is the best way to show a player's "tools" at a glance. In this version, we’ll plot a player's stats against league averages (or your own custom grades).

```python
import plotly.graph_objects as go

def create_radar_chart(stats_dict):
    # Standard MLB tools on a 0-100 scale (percentiles)
    categories = ['Exit Velo', 'Launch Angle', 'Hard Hit%', 'Barrel%', 'Zone Contact']

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[stats_dict['ev'], stats_dict['la'], stats_dict['hh'], stats_dict['br'], stats_dict['zc']],
        theta=categories,
        fill='toself',
        name='Player Profile',
        line_color='#1f77b4'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title="Player Tool Percentiles"
    )
    return fig

# Display in Streamlit:
# st.plotly_chart(create_radar_chart(my_stats), use_container_width=True)

```

---

## ⚾ 2. The Spray Chart (Hit Locations)

To build a spray chart, we have to convert Statcast's raw `hc_x` and `hc_y` pixels into a format that looks like a baseball field. We’ll also color-code the points by the "Event" (e.g., Home Run vs. Single).

```python
import plotly.express as px

def create_spray_chart(df):
    # Statcast coordinate transformation to center home plate
    # Formula: x = (hc_x - 125.42), y = (198.27 - hc_y)
    df['plot_x'] = df['hc_x'] - 125.42
    df['plot_y'] = 198.27 - df['hc_y']

    fig = px.scatter(
        df, x='plot_x', y='plot_y',
        color='events',
        hover_data=['launch_speed', 'launch_angle', 'des'],
        title="Recent Batted Ball Profile",
        labels={'events': 'Outcome'}
    )

    # Make it look like a field: remove grid lines and fix axes
    fig.update_layout(
        xaxis=dict(visible=False, range=[-150, 150]),
        yaxis=dict(visible=False, range=[0, 300]),
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background
        height=500
    )

    # Optional: Add a 'Home Run' boundary line
    fig.add_shape(type="path", path="M -100,100 Q 0,300 100,100", line_color="Gray")

    return fig

# Display in Streamlit:
# st.plotly_chart(create_spray_chart(df), use_container_width=True)

```

---

## 🚀 Pro-Tip: Integrating with AI

In your **Week 2** prompt, you can now ask the AI to "Comment on the spray chart patterns." Since the AI has the raw `hc_x` and `hc_y` data, it can tell if a player is a "Dead-Pull Hitter" or an "All-Fields Threat" by looking at the distribution of those coordinates!

### ✅ Week 3 Success Checklist

- [ ] **Interactive Plots:** Users can hover over a dot on the spray chart to see the exact Exit Velocity.
- [ ] **Responsive Design:** Use `st.columns([1, 1])` to show the Radar Chart and Spray Chart side-by-side.
- [ ] **Visual Consistency:** Ensure your Plotly charts use the same color palette as your Streamlit theme.

**Would you like me to help you write the code that "re-maps" the Statcast events into a custom color scale (e.g., making Home Runs bright red and Outs light gray)?**

[Generating Plotly Charts in Streamlit](https://www.youtube.com/watch?v=KmcoofohV64)
This video demonstrates how to take interactive Plotly visualizations and embed them seamlessly into a Streamlit dashboard.

## Week 3: Add visual elements (st.metric for stats, Plotly for spray charts)

## Week 4: Polishing & Deployment - Implement @st.cache_data for performance

## Week 4: Deploy to Streamlit Community Cloud

## Week 4: Portfolio Update - Record screen capture and update resume/LinkedIn

**Next Step:** Run that script by typing `python test_data.py` in your terminal. If you see Aaron Judge's MLB ID, you're ready for Phase 1!

**Would you like me to show you how to pull the specific "Statcast" metrics (Exit Velocity, etc.) for your first report?**

## Errors and Fixes

Please note, sometimes within python virtual environment pip run sometimes is not recognized, in that case, please run the following:
`python3.13 -m pip install -q -U google-genai`
