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
