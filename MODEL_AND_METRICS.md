# Model & Metrics Logic

This document explains the "Thinking Engine" behind the FPL Predictor. It details why we chose XGBoost, how we process data, and the mathematical formulas behind our custom metrics.

## 1. The Model: XGBoost
We use **XGBoost (Extreme Gradient Boosting)** as our core regression model.

### Why XGBoost?
- **Tabular Mastery**: Gradient boosting trees historically outperform neural networks on structured, tabular data like FPL statistics.
- **Feature Importance**: It allows us to easily see *which* stats matter (e.g., does `xG` impact points more than `minutes_played`?).
- **Speed**: It trains and predicts in milliseconds, making our daily automation efficient.

### Training Strategy
- **Target**: We predict `total_points` for the *upcoming* gameweek.
- **Features**: We feed the model a rolling window of:
    - Recent Form (last 5 GWs).
    - Expected Goals (xG) & Assists (xA).
    - Opponent Difficulty (FDR).
    - Minutes played reliability.

## 2. Key Metrics & Formulas
The model provides a raw prediction, but we layer custom metrics on top to create "human-readable" strategy.

### 🧨 Explosivity Index
Measures a player's ceiling—how likely are they to score big?

**Formula:**
```python
Explosivity = (Form * 0.4) + (Points_Per_Game / 60.0) + (Bonus_Points)
```
- **Bonus**: We apply a multiplier if they have multiple double-digit hauls.
- **Position Bias**: Midfielders and Forwards get a 5% boost to Explosivity, as they benefit more from goals.
- **Threshold**: A player needs an Explosivity score `> 33` to be considered for captaincy.

### 🛡️ Defcon Score
A hybrid metric for defenders, combining clean sheet probability with attacking threat.

**Formula:**
```python
Defcon = (Clean_Sheet_Odds * 0.6) + (xA_Threat * 0.4)
```
- Used to identify "The Fun One"—a defender who might get a 10+ pointer.

## 3. Squad Optimization
We don't just pick the top 15 players. We build a valid FPL squad using a **Knapsack-style Greedy Algorithm**.

1.  **Constraints**:
    - Budget: £100.0m.
    - Max 3 players per EPL team.
    - Formation rules (e.g., min 3 Defenders, 1 GK).
2.  **Selection**:
    - We lock in a budget Goalkeeper first.
    - We iterate through the highest `predicted_points` candidates.
    - We dynamically balance the budget to ensure we can afford a full bench.
