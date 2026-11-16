"""
Rajasthan Royals Hackathon — Round 1
Core Analysis Engine: Pressure Index Calculation & Player Ranking
"""

import pandas as pd
import numpy as np
import json, os

# ──────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
df = pd.read_csv("data/player_match_data.csv")
print(f"Loaded {len(df)} rows, {df['player_name'].nunique()} players.\n")

# ──────────────────────────────────────────────────────────────────────────────
# 2. HELPER: SAFE DIVISION
# ──────────────────────────────────────────────────────────────────────────────
def safe_div(a, b, default=0):
    return a / b if b != 0 else default

# ──────────────────────────────────────────────────────────────────────────────
# 3. SPLIT: NORMAL vs PRESSURE MATCHES
# ──────────────────────────────────────────────────────────────────────────────
normal  = df[~df["is_pressure_situation"]]
pressure= df[ df["is_pressure_situation"]]

# ──────────────────────────────────────────────────────────────────────────────
# 4. AGGREGATE STATS PER PLAYER
# ──────────────────────────────────────────────────────────────────────────────
def agg(subset):
    g = subset.groupby("player_name")
    return pd.DataFrame({
        "matches"      : g["match_id"].count(),
        "total_runs"   : g["runs_scored"].sum(),
        "avg_runs"     : g["runs_scored"].mean().round(2),
        "avg_sr"       : g["strike_rate"].mean().round(2),
        "total_wkts"   : g["wickets"].sum(),
        "avg_economy"  : g.apply(lambda x: round(x.loc[x["overs_bowled"]>0,"economy_rate"].mean(), 2) if (x["overs_bowled"]>0).any() else np.nan),
        "avg_catches"  : g["catches"].mean().round(3),
        "win_pct"      : (g["team_won"].sum() / g["team_won"].count() * 100).round(1),
        "avg_balls"    : g["balls_faced"].mean().round(1),
        "total_sixes"  : g["sixes"].sum(),
    }).reset_index()

normal_stats   = agg(normal).add_suffix("_normal").rename(columns={"player_name_normal":"player_name"})
pressure_stats = agg(pressure).add_suffix("_pressure").rename(columns={"player_name_pressure":"player_name"})

stats = normal_stats.merge(pressure_stats, on="player_name")
meta  = df[["player_name","role","age","country"]].drop_duplicates()
stats = stats.merge(meta, on="player_name")

# ──────────────────────────────────────────────────────────────────────────────
# 5. PRESSURE INDEX COMPONENTS
# ──────────────────────────────────────────────────────────────────────────────

# 5a. Batting Pressure Score  (for batting roles)
#     = (pressure_avg / normal_avg) * (pressure_sr / normal_sr)
#     Capped at 2.0 to avoid outliers

stats["bat_pressure_ratio"] = stats.apply(lambda r:
    safe_div(r["avg_runs_pressure"], r["avg_runs_normal"], 1.0), axis=1).clip(0, 2)

stats["sr_pressure_ratio"] = stats.apply(lambda r:
    safe_div(r["avg_sr_pressure"], r["avg_sr_normal"], 1.0), axis=1).clip(0, 2)

stats["batting_pressure_score"] = (
    0.6 * stats["bat_pressure_ratio"] + 0.4 * stats["sr_pressure_ratio"]
).round(4)

# 5b. Bowling Pressure Score (economy goes DOWN under pressure = better)
#     = normal_economy / pressure_economy   (>1 means better under pressure)
stats["bowl_pressure_ratio"] = stats.apply(lambda r:
    safe_div(r["avg_economy_normal"], r["avg_economy_pressure"], 1.0)
    if pd.notna(r["avg_economy_pressure"]) and r["avg_economy_pressure"] > 0
    else np.nan, axis=1)

stats["bowl_pressure_ratio"] = stats["bowl_pressure_ratio"].fillna(1.0).clip(0, 2)

# 5c. Win Contribution Under Pressure
stats["win_lift"] = (stats["win_pct_pressure"] - stats["win_pct_normal"]).fillna(0)

# 5d. Knockout match specialness  (extra weight for knockout games)
knockout = df[df["is_knockout"]==True]
ko_stats = knockout.groupby("player_name").agg(
    ko_avg_runs  = ("runs_scored","mean"),
    ko_win_pct   = ("team_won","mean"),
    ko_wkts      = ("wickets","mean"),
).reset_index()
stats = stats.merge(ko_stats, on="player_name", how="left")
stats["ko_avg_runs"]  = stats["ko_avg_runs"].fillna(stats["avg_runs_pressure"])
stats["ko_win_pct"]   = stats["ko_win_pct"].fillna(0.5)
stats["ko_wkts"]      = stats["ko_wkts"].fillna(0)

# ──────────────────────────────────────────────────────────────────────────────
# 6. COMPOSITE PRESSURE INDEX  (0–100 scale)
# ──────────────────────────────────────────────────────────────────────────────
# Weights:
#   30% Batting pressure score
#   25% Bowling pressure score (or batting for pure batsmen)
#   20% Win-lift under pressure
#   15% Knockout performance
#   10% Volume (matches × avg)

def normalize(series, lo=0, hi=1):
    mn, mx = series.min(), series.max()
    if mx == mn: return pd.Series([0.5]*len(series), index=series.index)
    return (series - mn) / (mx - mn) * (hi - lo) + lo

stats["n_bat"]      = normalize(stats["batting_pressure_score"])
stats["n_bowl"]     = normalize(stats["bowl_pressure_ratio"])
stats["n_win"]      = normalize(stats["win_lift"].clip(-30,30))
stats["n_ko"]       = normalize(stats["ko_avg_runs"])
stats["n_volume"]   = normalize(stats["total_runs_pressure"])

# Role-based weighting
def composite(row):
    if row["role"] in ("Batsman","WK-Batsman"):
        return (0.40*row["n_bat"] + 0.10*row["n_bowl"] +
                0.20*row["n_win"] + 0.20*row["n_ko"]  + 0.10*row["n_volume"])
    elif row["role"] == "Bowler":
        return (0.15*row["n_bat"] + 0.45*row["n_bowl"] +
                0.20*row["n_win"] + 0.10*row["n_ko"]  + 0.10*row["n_volume"])
    else:  # All-Rounder
        return (0.28*row["n_bat"] + 0.28*row["n_bowl"] +
                0.20*row["n_win"] + 0.14*row["n_ko"]  + 0.10*row["n_volume"])

stats["pressure_index_raw"] = stats.apply(composite, axis=1)
stats["pressure_index"]     = (normalize(stats["pressure_index_raw"]) * 100).round(1)
stats["rank"]               = stats["pressure_index"].rank(ascending=False).astype(int)

# ──────────────────────────────────────────────────────────────────────────────
# 7. TOP PICKS PER ROLE
# ──────────────────────────────────────────────────────────────────────────────
top_batsmen    = stats[stats["role"].isin(["Batsman","WK-Batsman"])].nlargest(5,"pressure_index")
top_bowlers    = stats[stats["role"]=="Bowler"].nlargest(5,"pressure_index")
top_allrounders= stats[stats["role"]=="All-Rounder"].nlargest(3,"pressure_index")

print("=" * 65)
print("🏏  TOP 5 BATSMEN / WK-BATSMEN UNDER PRESSURE")
print("=" * 65)
print(top_batsmen[["player_name","country","age","pressure_index","avg_runs_pressure","avg_sr_pressure"]].to_string(index=False))

print("\n" + "=" * 65)
print("🎳  TOP 5 BOWLERS UNDER PRESSURE")
print("=" * 65)
print(top_bowlers[["player_name","country","age","pressure_index","avg_economy_pressure","total_wkts_pressure"]].to_string(index=False))

print("\n" + "=" * 65)
print("🌟  TOP ALL-ROUNDERS UNDER PRESSURE")
print("=" * 65)
print(top_allrounders[["player_name","country","age","pressure_index","batting_pressure_score","bowl_pressure_ratio"]].to_string(index=False))

# ──────────────────────────────────────────────────────────────────────────────
# 8. SAVE RESULTS
# ──────────────────────────────────────────────────────────────────────────────
os.makedirs("output", exist_ok=True)
stats.sort_values("pressure_index", ascending=False).to_csv("output/player_pressure_scores.csv", index=False)

# Save top-10 as JSON for dashboard
top10 = stats.nlargest(10, "pressure_index")[
    ["player_name","role","country","age","pressure_index",
     "avg_runs_pressure","avg_sr_pressure","avg_economy_pressure",
     "batting_pressure_score","bowl_pressure_ratio","win_lift","matches_pressure"]
].rename(columns={
    "player_name":"name","avg_runs_pressure":"avg_runs","avg_sr_pressure":"avg_sr",
    "avg_economy_pressure":"avg_econ","batting_pressure_score":"bat_pi",
    "bowl_pressure_ratio":"bowl_pi","matches_pressure":"pressure_matches"
}).fillna(0)

top10.to_json("output/top10_players.json", orient="records", indent=2)

all_data = stats[[
    "player_name","role","country","age","pressure_index",
    "avg_runs_normal","avg_runs_pressure","avg_sr_normal","avg_sr_pressure",
    "avg_economy_normal","avg_economy_pressure","win_pct_normal","win_pct_pressure",
    "bat_pressure_ratio","bowl_pressure_ratio","win_lift","matches_normal","matches_pressure"
]].fillna(0)
all_data.to_json("output/all_players.json", orient="records", indent=2)

print(f"\n✅ Results saved to output/")
print(f"   • player_pressure_scores.csv")
print(f"   • top10_players.json")
print(f"   • all_players.json")
