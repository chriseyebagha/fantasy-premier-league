# FPL Predictor: The Brain (Engine Documentation)

This document explains the logic behind the FPL Predictor's "Thinking Engine," including player scoring, recommendation categories, and the "Explosivity Index."

## Core Prediction Logic

The engine uses a multi-layered approach to predict player performance for the upcoming gameweek. The final "Reality Score" is arguably the most advanced metric in the system.

### 1. The Core Prediction ("Reality Score")
The **Reality Score** is the engine's primary output for each player. It is a direct prediction from the **XGBoost Regressor model**, which is trained on historical data including form, fixture difficulty, and xGI.

**Formula**:
`Reality Score = XGBoost_Prediction`

> **Note**: Previous versions used manual multipliers for fixtures and position. These have been removed to avoid double-counting, as the model now natively learns these factors from the feature set (including FDR and Element Type).

## Recommendation Categories (The Captains)

The dashboard presents three distinct recommendation tiers, each with strict selection criteria:

### 1. The Obvious One
*   **Position**: Strictly Midfielders or Forwards.
*   **Metric**: The player with the highest final `predicted_points` score.

### 2. The Joker (The Differential)
*   **Position**: Strictly Midfielders or Forwards.
*   **Ownership**: Must be < 15% (Low ownership).
*   **Metric**: Prioritizes the highest **Explosivity Index**.

### 3. The Fun One
*   **Position**: Strictly Defenders or Goalkeepers.
*   **Metric**: Prioritizes players with high **Defcon Score**, identifying defenders who generate points through activity and reliability.
*   **Formula**: `((Historic Clean Sheet % * 60) * FDR_Modifier) + (Defensive Work * 4.0) + (Attacking Threat * 400)`
*   **Why**: Proves Reliability (History) + Opportunity (Fixture) + Work Rate (BPS).

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
We welcome contributors to refine the `XGBoost` hyper-parameters in `backend/engine/trainer.py`.
