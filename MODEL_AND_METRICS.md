# Model & Metrics Logic

This document explains the rigorous "Thinking Engine" behind the FPL Predictor. It details the exact mathematical formulas, weights, and assumptions used to grade players. This transparency allows contributors to audit and improve the model logic.

## 1. The Core Prediction (The "Reality Score")
The final `predicted_points` you see in the dashboard is a composite score, not just a raw regression output.

### The Formula
```python
Final Score = (M + P) * F * B
```

Where:
- **M (Model Prediction)**: The raw XGBoost output based on historical features.
- **P (Performance Boost)**: A reliability multiplier for proven assets.
- **F (Fixture Multiplier)**: Adjusts for opponent difficulty.
- **B (Position Bias)**: Adjusts for the "ceiling" of different positions.

#### Component Breakdown

**1. Performance Boost (P)**
Recognizes that high-performing players are more reliable than the model might predict (e.g., Palmer/Salah factors).
```python
P = (Form * 0.4) + (Total_Points / 60.0)
```
*Assumption*: Current form is weighted 40%, while season-long consistency provides a stable baseline.

**2. Fixture Multiplier (F)**
Based on FDR (Fixture Difficulty Rating from FPL API).
| FDR | Standard Multiplier | "Fixture Proof" Multiplier* |
| :--- | :--- | :--- |
| **1-2 (Easy)** | 1.15x | 1.15x |
| **3 (Medium)** | 1.00x | 1.00x |
| **4 (Hard)** | 0.75x | 0.90x |
| **5 (Hardest)** | 0.60x | 0.80x |

**Assumption*: A player is "Fixture Proof" if their `Explosivity Index >= 70`. This prevents us from benching elite assets like Haaland just because they play Man City.

**3. Position Bias (B)**
| Role | Multiplier | Rationale |
| :--- | :--- | :--- |
| **MID/FWD** | 1.05x | Higher point ceiling (goals = 5/4 pts) |
| **DEF/GK** | 0.90x | Lower ceiling, higher reliance on clean sheets |

---

## 2. Explosivity Index 🧨
A 0-100 score measuring a player's ability to deliver massive "Hauls" (double-digit points). 

**Formula:**
```python
Score = Historical_Score + Bonuses
```

**1. Historical Score (Base)**
```python
Frequency = (Total Hauls / Total Games Played)
Recent_Hauls = Count of hauls in last 6 GWs

Historical_Score = (Frequency * 30) + (Recent_Hauls * 10)
```

**2. Bonuses (For Elite Ceilings)**
| Metric | Threshold | Bonus Points |
| :--- | :--- | :--- |
| **Form** | >= 7.5 | +15 pts |
| **xGI/90** | >= 0.70 | +15 pts |
| **Super Hot** | *See below* | +25 pts |

**"Super Hot" Criteria (`is_super_hot`)**
A player receives the massive +25pt bump if *any* of the following are true:
1.  **Recent Form**: 5+ hauls in the last 10 games (Hot Streak).
2.  **Early Season (<= GW20)**: 5+ total hauls (Emerging Star).
3.  **Late Season (> GW20)**: 10+ total hauls (Proven Heavy Hitter).

*Assumption*: Consistent explosive returns define a premium asset. A player hitting these thresholds is "Fixture Proof".

---

## 3. Defcon Score 🛡️
A 0-100 hybrid score for identifying "The Fun One" (defenders with attacking threat).

**Formula:**
```python
Defcon = (Clean_Sheet_Prob * 60) + (Defensive_Work * 4) + (Attacking_Threat * 400)
```

**1. Clean Sheet Probability (Foundation)**
Derived inversely from FDR.
- Easy Fixture (FDR 2) ≈ 50% chance (0.5)

**2. Defensive Work Rate (BPS Magnet)**
Built directly from FPL's `defensive_contribution_per_90` API field (Clearances, Blocks, Interceptions).
- **Context**: Defenders with 10+ defensive actions (CBI + Tackles) in a match get **+2 additional points**.
- **Bonus**: High defensive work rate is the primary driver for Bonus Points (BPS) in low-scoring games.
- Weighted x4.0 to heavily reward players who hit this "monster" threshold (e.g., 12 actions * 4 = 48 pts).

**3. Attacking Threat**
```python
Threat = (xG_per_90 * 1.5) + (xA_per_90 * 1.2)
```
*Assumption*: Goals (xG) are weighted higher than assists (xA) for defenders because a defender goal is worth 6 points vs. 3 for an assist.

---

## 4. Squad Selection Algorithm (The "Knapsack")
We solve the problem: *Select 15 players within £100m that maximize predicted points.*

**The Greedy Strategy:**
1.  **Lock Minimums**: We enforce 1 starting GK.
2.  **Top-Down Selection**: We sort all players by `Final Score` and iterate.
3.  **Bench Optimization**: We explicitly look for "Starting fodder" (players costing £4.0-£4.5m who play >60 mins).
4.  **Formation Logic**:
    - We prefer a 3-4-3 or 3-5-2 (Attacking formations).
    - We rarely select 5 defenders unless their `predicted_points` overlap significantly with midfielders.
