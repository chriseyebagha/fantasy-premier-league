# FPL Predictor: The Brain (Engine Documentation)

This document explains the logic behind the FPL Predictor's "Thinking Engine," including player scoring, recommendation categories, and the "Explosivity Index."

## Core Prediction Logic

The engine uses a multi-layered approach to predict player performance for the upcoming gameweek:

1.  **ML Prediction**: A trained `XGBoost` model analyzes historical player data, form, ICT index, and team strength to provide a baseline projected score.
2.  **Performance Boost**: Adds a reliability factor based on seasonal total points and current form.
3.  **Fixture Adjustment (FDR)**: Applies a multiplier based on the Official FPL Fixture Difficulty Rating:
    *   **FDR 2**: 1.15x boost (Easy fixture)
    *   **FDR 3**: 1.0x (Neutral)
    *   **FDR 4**: 0.75x penalty (Hard fixture) / **0.90x** if Fixture-Proof
    *   **FDR 5**: 0.6x penalty (Extreme difficulty) / **0.80x** if Fixture-Proof
4.  **Position Bias**:
    *   **Attackers (MID/FWD)**: Receive a 5% premium to favor potential goal involvements.
    *   **Defensive (DEF/GKP)**: Receive a 10% discount to account for clean-sheet volatility and "bench fodder" risk.

## Recommendation Categories (The Captains)

The dashboard presents four distinct recommendation tiers, each with strict selection criteria:

### 1. The Easy Choice
*   **Position**: Strictly Midfielders or Forwards.
*   **Ownership**: Must be > 25% (Highly owned).
*   **Performance**: Prioritizes players with the highest number of double-digit hauls (10+ points) in the current season.

### 2. The Obvious One
*   **Position**: Strictly Midfielders or Forwards.
*   **Metric**: The player with the highest final `predicted_points` score after all multipliers are applied.

### 3. The Joker (The Differential)
*   **Position**: Strictly Midfielders or Forwards.
*   **Ownership**: Must be < 15% (Low ownership).
*   **Metric**: Prioritizes the highest **Explosivity Index**.

### 4. The Fun One
*   **Position**: Strictly Defenders or Goalkeepers.
*   **Metric**: Prioritizes players with high **DEFCON** (Defensive Concentration Index), focusing on clean-sheet security and offensive participation.

## The Explosivity Index (Unified High Performance Metric)
The "Explosivity Index" is the master indicator of current performance and haul potential. 

### Elite Bonuses (The Fixture-Proof Path)
Players earn bonus points towards their index based on unbiased output:
*   **Elite Form**: +15 pts if current form is >= 7.5.
*   **Elite Underlying Stats**: +15 pts if xGI per 90 is >= 0.70.
*   **Elite Reliability**: +20 pts if they have achieved 5+ double-digit hauls this season.

### Fixture-Proof Status
Any player who achieves an **Explosivity Index >= 70** is codified as **Fixture-Proof**. This removes heavy biases and ensures the model respects world-class performers in world-class form, regardless of their opponent.

### Selection Floor
To be considered for the top 3 recommendation categories (Easy Choice, Obvious, Joker), a player must meet an **Explosivity Floor of 33**.

## Open Source Contribution
We welcome contributors to refine the `fixture_multiplier` constants or the `XGBoost` hyper-parameters in `backend/engine/trainer.py`.
