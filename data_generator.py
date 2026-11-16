"""
Rajasthan Royals Hackathon - Round 1
Player Performance Data Generator
Simulates realistic domestic cricket data for pressure analysis
"""

import pandas as pd
import numpy as np
import json
import os

np.random.seed(42)

# ─────────────────────────────────────────────────────────────
# PLAYER POOL — 30 realistic domestic cricket players
# ─────────────────────────────────────────────────────────────
players = [
    # (name, role, age, country)
    ("Yashasvi Jaiswal",      "Batsman",       22, "India"),
    ("Dhruv Jurel",           "WK-Batsman",    23, "India"),
    ("Riyan Parag",           "All-Rounder",   22, "India"),
    ("Shimron Hetmyer",       "Batsman",       27, "West Indies"),
    ("Jos Buttler",           "WK-Batsman",    33, "England"),
    ("Rovman Powell",         "Batsman",       29, "West Indies"),
    ("Nitish Rana",           "Batsman",       29, "India"),
    ("Tilak Varma",           "Batsman",       21, "India"),
    ("Abdul Samad",           "All-Rounder",   22, "India"),
    ("Shubman Gill",          "Batsman",       24, "India"),
    ("Sanju Samson",          "WK-Batsman",    29, "India"),
    ("Tushar Deshpande",      "Bowler",        28, "India"),
    ("Avesh Khan",            "Bowler",        27, "India"),
    ("Sandeep Sharma",        "Bowler",        30, "India"),
    ("Kuldeep Sen",           "Bowler",        25, "India"),
    ("Nandre Burger",         "Bowler",        25, "South Africa"),
    ("Wanindu Hasaranga",     "All-Rounder",   26, "Sri Lanka"),
    ("Ravichandran Ashwin",   "All-Rounder",   37, "India"),
    ("Yuzvendra Chahal",      "Bowler",        33, "India"),
    ("Keshav Maharaj",        "Bowler",        33, "South Africa"),
    ("Trent Boult",           "Bowler",        34, "New Zealand"),
    ("Obed McCoy",            "Bowler",        28, "West Indies"),
    ("Adam Zampa",            "Bowler",        32, "Australia"),
    ("Rahul Tewatia",         "All-Rounder",   30, "India"),
    ("Dhruv Shorey",          "Batsman",       29, "India"),
    ("Richa Ghosh",           "WK-Batsman",    20, "India"),
    ("Sai Sudharsan",         "Batsman",       22, "India"),
    ("Angkrish Raghuvanshi",  "Batsman",       18, "India"),
    ("Kumar Kartikeya",       "Bowler",        24, "India"),
    ("Ravi Bishnoi",          "Bowler",        24, "India"),
]

# ─────────────────────────────────────────────────────────────
# GENERATE MATCH-LEVEL DATA  (each player × 60 matches)
# ─────────────────────────────────────────────────────────────
records = []
match_id = 1

leagues = ["IPL", "SA20", "BBL", "CPL", "ILT20", "Ranji Trophy"]
pressure_situations = [
    "Death Overs Batting",   # 17-20
    "Powerplay Chase",       # 1-6, chasing
    "Knockout Match",
    "Last 5 Needed 20+",
    "Top Order Collapse",    # 3+ wickets in first 10 overs
    "Normal"
]

for name, role, age, country in players:
    # Base talent multiplier per role
    if "Batsman" in role or "WK" in role:
        bat_base = np.random.uniform(28, 55)
        bowl_base = 0
    elif role == "Bowler":
        bat_base = np.random.uniform(5, 18)
        bowl_base = np.random.uniform(20, 32)
    else:  # All-Rounder
        bat_base = np.random.uniform(20, 38)
        bowl_base = np.random.uniform(18, 28)

    # Pressure trait: how well does the player perform under pressure?
    pressure_trait = np.random.uniform(0.60, 1.40)   # >1 = clutch, <1 = folds

    for m in range(60):
        is_pressure = np.random.choice([True, False], p=[0.35, 0.65])
        situation = np.random.choice(pressure_situations[:-1]) if is_pressure else "Normal"
        is_knockout = situation == "Knockout Match"
        league = np.random.choice(leagues)

        # Batting stats
        if "Batsman" in role or "WK" in role or "All" in role:
            base_runs = bat_base * np.random.uniform(0.5, 2.0)
            if is_pressure:
                runs = base_runs * pressure_trait * np.random.uniform(0.7, 1.3)
            else:
                runs = base_runs * np.random.uniform(0.7, 1.3)
            runs = max(0, int(runs))

            balls = max(runs, int(runs / np.random.uniform(0.9, 2.2))) if runs > 0 else int(np.random.uniform(0, 8))
            balls = max(balls, 1)
            sr = round((runs / balls) * 100, 2)
            fours = int(runs * np.random.uniform(0.05, 0.15))
            sixes = int(runs * np.random.uniform(0.02, 0.10))
            dismissed = np.random.choice([True, False], p=[0.65, 0.35])
        else:
            runs, balls, sr, fours, sixes, dismissed = 0, 0, 0, 0, 0, False

        # Bowling stats
        if "Bowler" in role or "All" in role:
            overs_bowled = np.random.choice([2, 3, 4], p=[0.2, 0.3, 0.5])
            base_econ = bowl_base / 6
            if is_pressure:
                econ = base_econ * (2 - pressure_trait) * np.random.uniform(0.85, 1.15)
            else:
                econ = base_econ * np.random.uniform(0.85, 1.15)
            econ = round(max(3.0, min(14.0, econ)), 2)
            wickets = np.random.choice([0, 1, 2, 3, 4], p=[0.45, 0.30, 0.15, 0.07, 0.03])
            dots = int(overs_bowled * 6 * np.random.uniform(0.2, 0.5))
        else:
            overs_bowled, econ, wickets, dots = 0, 0, 0, 0

        # Fielding
        catches = np.random.choice([0, 1, 2], p=[0.65, 0.28, 0.07])
        run_outs = np.random.choice([0, 1], p=[0.92, 0.08])

        # Match result
        team_won = np.random.choice([True, False])

        records.append({
            "match_id": match_id,
            "player_name": name,
            "role": role,
            "age": age,
            "country": country,
            "league": league,
            "is_pressure_situation": is_pressure,
            "pressure_type": situation,
            "is_knockout": is_knockout,
            "runs_scored": runs,
            "balls_faced": balls,
            "strike_rate": sr,
            "fours": fours,
            "sixes": sixes,
            "dismissed": dismissed,
            "overs_bowled": overs_bowled,
            "economy_rate": econ,
            "wickets": wickets,
            "dot_balls": dots,
            "catches": catches,
            "run_outs": run_outs,
            "team_won": team_won,
            "_pressure_trait": round(pressure_trait, 3),   # hidden ground truth
        })
        match_id += 1

df = pd.DataFrame(records)
os.makedirs("data", exist_ok=True)
df.to_csv("data/player_match_data.csv", index=False)
print(f"✅ Generated {len(df)} match records for {len(players)} players.")
print(df.head(3))
