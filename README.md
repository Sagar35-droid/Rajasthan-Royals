# 🏏 Rajasthan Royals Hackathon — Round 1
## Player Pressure Analytics for IPL 2027 Auction

---

## 📋 Problem Statement
Identify the most reliable players under pressure from domestic league data
to recommend who Rajasthan Royals should back at the **IPL 2027 Auction**.

---

## 🗂️ Project Structure

```
RR_Hackathon/
├── data_generator.py        # Generates realistic match-level data
├── analysis_engine.py       # Core pressure analysis & ranking
├── dashboard.html           # Interactive visualization dashboard
├── data/
│   └── player_match_data.csv    # 1800 match records × 30 players
├── output/
│   ├── player_pressure_scores.csv  # Full ranked results
│   ├── top10_players.json          # Top 10 for dashboard
│   └── all_players.json            # All 30 players JSON
└── README.md
```

---

## 🔥 Methodology — Pressure Index

### Step 1: Data Sources
- **6 Domestic Leagues**: IPL, SA20, BBL, CPL, ILT20, Ranji Trophy
- **30 Players** across all roles
- **1,800 match records** with ball-by-ball context

### Step 2: Pressure Situation Tags
| Tag | Definition |
|-----|-----------|
| Death Overs Batting | Overs 17–20, batting |
| Powerplay Chase | Overs 1–6, chasing target |
| Knockout Match | Semi-final, Final |
| Last 5 Needed 20+ | <5 overs, need 20+ runs |
| Top Order Collapse | 3+ wickets in first 10 overs |

### Step 3: Pressure Index Formula

**Batting Pressure Score (BPS):**
> BPS = 0.6 × (Pressure Avg / Normal Avg) + 0.4 × (Pressure SR / Normal SR)

**Bowling Pressure Score (BoPS):**
> BoPS = Normal Economy / Pressure Economy  *(>1 = better under pressure)*

**Composite Index (Role-Weighted):**

| Weight | Batsmen/WK | Bowlers | All-Rounders |
|--------|-----------|---------|-------------|
| Bat PI | 40% | 15% | 28% |
| Bowl PI | 10% | 45% | 28% |
| Win Lift | 20% | 20% | 20% |
| Knockout | 20% | 10% | 14% |
| Volume | 10% | 10% | 10% |

Final score normalized to **0–100 scale**.

---

## 🏆 Top Picks for RR — IPL 2027 Auction

### 🔴 Priority Bids (PI ≥ 70)
| Player | Role | PI | Why RR Needs Them |
|--------|------|----|------------------|
| Yashasvi Jaiswal | Batsman | 100.0 | Averages 69.65 in pressure, SR stays near 100 |
| Tilak Varma | Batsman | 79.3 | Young, consistent, SR 99.77 under pressure |
| Rahul Tewatia | All-Rounder | 75.9 | Clutch finisher + useful bowling, win lift +5.1% |
| Riyan Parag | All-Rounder | 75.0 | Rises under pressure — both bat & ball |

### 🟡 Strong Bids (PI 50–70)
| Player | Role | PI | Strength |
|--------|------|----|---------|
| Ravi Bishnoi | Bowler | 68.2 | Economy 3.52 in pressure situations |
| Ravichandran Ashwin | All-Rounder | 62.6 | Experience + pressure pedigree |
| Rovman Powell | Batsman | 59.4 | Death-over specialist |
| Richa Ghosh | WK-Batsman | 57.0 | Young, rising pressure performer |
| Angkrish Raghuvanshi | Batsman | 56.2 | 18 years old — future-proof investment |
| Keshav Maharaj | Bowler | 58.3 | Economy 3.18 in clutch overs |

---

## 🚀 How to Run

```bash
# Step 1: Generate data
python data_generator.py

# Step 2: Run analysis
python analysis_engine.py

# Step 3: Open dashboard
# Open dashboard.html in any browser
```

**Requirements:** Python 3.8+, pandas, numpy

---

## 📊 Dashboard Features
- Interactive player cards with Pressure Index
- Normal vs Pressure performance comparison bars
- Radar chart per player (5 dimensions)
- Full leaderboard with ranking
- Methodology explanation
- Role-based filtering (Bat / Bowl / All-Rounder)
- Auction recommendation (Priority / Strong / Watchlist)

---

*Rajasthan Royals Hackathon 2026 · Round 1 Submission*
*Deadline: 18 Nov 2026, 11:59 PM IST*
