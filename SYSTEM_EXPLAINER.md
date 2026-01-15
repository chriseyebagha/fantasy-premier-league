# FPL Engine: System Explainer

This document explains the core metrics driving the FPL Projections (xP Predictor), how they are calculated, and how to interpret them.

## Core Metrics

### 1. Haul Probability (`haul_prob`)
**What it is:** The probability that a player will score **11+ points** in the *upcoming* Gameweek.

**How it's calculated:**
- **Monte Carlo Simulation:** We simulate the match 1,500 times using the player's predicted event probabilities.
- **Advanced Prediction (Vesuvius Layer):** Before simulation, the model's base probabilities (lambdas) for Goals, Assists, Bonus, and Clean Sheets are adjusted by **Vesuvius Multipliers**:
  - **Clinicality Boost:** Up to **+15%** for players with a high seasonal frequency of 10+ point hauls.
  - **Matchup Boost:** **+10%** if the opponent's **Vulnerability Score** exceeds the "Leaky Defense" threshold.
- **Output:** The percentage of simulations where the player's total points reach 11 or higher.
- **Vesuvius Alert:** Triggered if `haul_prob >= 20%`. This indicates a significant ceiling and a prime captaincy candidate.

### 2. Explosivity Index (`explosivity`)
**What it is:** A historical "pedigree" score (0-100) measuring a player's ability to deliver massive scores over the season.

**How it's calculated:**
- **Haul Frequency:** Ratio of 10+ point hauls across all played games.
- **Recent Pedigree:** Bonus for hauls delivered in the last 10 gameweeks.
- **Underlying Stats:** Weighted bonus for high xGI (Expected Goal Involvement) per 90.
- **"Super Hot" Status:** A major bonus (25 pts) for players maintaining an elite haul rate (e.g., 5+ hauls in the last 10 games).
- **FDR Adjustment:** Easy fixtures (FDR 2) boost the index by 10%, as they provide the best opportunity to unlock a player's ceiling.

### 3. Defensive Contribution (`defcon`)
**What it is:** A specialized metric for Defenders and Goalkeepers (0-100) predicting the likelihood of clean sheets and bonus-point-generating defensive work.

**Calculation Components:**
- **Clean Sheet Process:** Historic CS probability adjusted by the upcoming fixture difficulty.
- **Work Rate:** Based on `defensive_contribution_per_90` (tackles, interceptions, clearances, blocks).
- **Attacking upside:** Defenders with high xG/xA (e.g., set-piece threats or attacking full-backs) receive a significant "Defcon" boost.

> [!NOTE]
> **24/25 FPL Rule Update:** Outfield players now earn **+2 points** for reaching defensive action thresholds (10 for Defenders, 12 for Midfielders/Forwards). Our model trains specifically on these "Defcon Points."

### 4. Opponent Vulnerability (`opponent_vulnerability`)
**What it is:** A score (0-100) representing how likely a team is to concede big chances. Higher is better for your attackers.

**Analysis:**
- It is a **50/50 Blend** of **Process (xGC)** and **Reality (GC)** over a rolling 7-game window.
- **Scale:** A raw vulnerability score of 1.40 (average goals/xgc conceded per game) translates to a 35 on the index.
- **Threshold:** Scores > 35 trigger **Matchup Boosts** for all opposing attackers in the Vesuvius Layer.

---

## Case Study: GW22 Target (Arsenal vs Crystal Palace)

**Context:** Arsenal (H) vs Crystal Palace (A)
- **Opponent (Palace) Vulnerability:** Expected to be high (~38.0) due to recent defensive inconsistencies.
- **Player: Gabriel (DEF)**
  - **Defcon Alert:** High defensive work rate + Arsenal's strong CS odds + goal threat from corners.
  - **Prediction:** High xP driven by Clean Sheet potential + "Defcon Points."
- **Player: Saka (MID)**
  - **Vesuvius Alert:** Likely to trigger a **Matchup Boost** (+10%) and possibly a **Clinicality Boost** based on recent hauls. 
  - **Haul Probability:** Expecting >25% given Palace's vulnerability.

---
**Verification Logic:**
The system uses a **Stability Sentinel** feedback loop. After each Gameweek, actual results are compared to predictions. If the model's Mean Absolute Error (MAE) exceeds 3.0, the learning rate is throttled (Noise Gate) to prevent over-reactions to chaotic weeks. Conversely, high accuracy (7/11 predicted starters hitting 4+ points) boosts model confidence.
