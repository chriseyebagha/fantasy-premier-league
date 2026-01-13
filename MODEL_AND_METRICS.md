# Model & Metrics Logic

This document explains the rigorous "Thinking Engine" behind the FPL Predictor. It details the exact mathematical formulas, weights, and assumptions used to grade players. This transparency allows contributors to audit and improve the model logic.

## 1. Core Prediction ("Reality Score")
The primary metric used for ranking players and selecting the squad.

**Formula**:
`Score = XGBoost_Model_Output`

**Key Features utilized by the Model**:
- **Form**: Recent points average.
- **Fixture Difficulty**: FDR of the upcoming opponent.
- **Position**: (New) Explicit element type filtering.
- **xGI**: Expected Goal Involvement.
- **Explosivity**: Likelihood of hauling.

*Manual multipliers for Fixture and Position have been removed to ensure the model learns these weights optimally via self-training.*

---

## 2. Explosivity Index 🧨
A 0-100 score measuring a player's ability to deliver massive "Hauls" (double-digit points). 

**Formula:**
```python
Score = Historical_Score + Bonuses
Score = Score * FDR_Bonus (if applicable)
```

**1. Historical Score (Base)**
```python
Historical_Score = (Haul_Frequency * 30) + (Recent_10_Hauls * 10)
```
*Frequency is total_hauls / total_games.*

**2. Bonuses (For Elite Ceilings)**
| Metric | Threshold | Bonus Points |
| :--- | :--- | :--- |
| **Form** | >= 7.5 | +15 pts |
| **xGI/90** | >= 0.70 | +15 pts |
| **Super Hot** | *See below* | +25 pts |

**3. FDR Adjustment**
- **Easy Fixtures (FDR <= 2)**: Score boosted by **10%** (x1.10) to reward potential ceiling in easy games.
- **Hard Fixtures (FDR >= 5)**: Score penalized by **10%** (x0.90).

**"Super Hot" Criteria (`is_super_hot`)**
A player receives the massive +25pt bump if *any* of the following are true:
1.  **Recent Form**: 5+ hauls in the last 10 games (Hot Streak).
2.  **Early Season (<= GW20)**: 5+ total hauls (Emerging Star).
3.  **Late Season (> GW20)**: 10+ total hauls (Proven Heavy Hitter).

*Assumption*: Consistent explosive returns define a premium asset. A player hitting these thresholds is "Fixture Proof".

---

## 3. Title Contender (Defcon Score) 🛡️
A 0-100 hybrid score for identifying "The Fun One" (defenders with attacking threat).

**Formula**:
`Defcon = ((Historic_CS_Prob * 60) * FDR_Modifier) + (Defensive_Work * 4) + (Attacking_Threat * 400)`

1. **Historic Clean Sheet Probability** (Reliability)
   - Calculated from the player's seasonal history (`Total Clean Sheets / Total Games`).
   - Weighted heavily (x60) to ensure the foundation of the pick is reliability.
   - **FDR Modifier**:
     - Easy (FDR ≤ 2): **1.15x**
     - Hard (FDR = 4): **0.85x**
     - Hardest (FDR = 5): **0.70x**

2. **Defensive Work Rate** (BPS Magnet)
   - Built directly from FPL's `defensive_contribution_per_90` API field (Clearances, Blocks, Interceptions).
   - Weighted x4.0.

3. **Attacking Threat**
   - `Threat = (xG_per_90 * 1.5) + (xA_per_90 * 1.2)`
   - *Assumption*: Goals (xG) are weighted higher than assists (xA) for defenders because a defender goal is worth 6 points vs. 3 for an assist. The high 400x multiplier scales these small per-90 decimals (e.g., 0.10) into meaningful score components (40 pts).

---

## 4. Squad Selection Algorithm (The "Knapsack")
We solve the problem: *Select 15 players within £100m that maximize predicted points.*

**The Greedy Strategy:**
1.  **Lock Minimums**: We enforce 1 starting GK.
2.  **Top-Down Selection**: We sort all players by `Final Score` and iterate.
3.  **Formation Logic**:
    - We prefer a 3-4-3 or 3-5-2 (Attacking formations).
    - We rarely select 5 defenders unless their `predicted_points` overlap significantly with midfielders.
4.  **Bench Strategy**: We minimize bench spend (£17.5m approx) to maximize starting XI value, picking the cheapest viable players who play minutes.
