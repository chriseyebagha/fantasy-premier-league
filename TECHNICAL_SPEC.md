# FPL Predictor: Technical Specification

## System Architecture

The FPL Predictor is a decoupled analytics engine designed to transform raw Premier League data into actionable transfer and captaincy insights, powered by a self-improving machine learning workflow.

```mermaid
graph TD
    API[FPL API] --> DM[Data Manager]
    DM --> History[Historic Data / Feedback Loop]
    History --> Trainer[Model Trainer (Self-Learning)]
    Trainer --> Model[XGBoost Matrix]
    
    API --> FF[Feature Factory]
    FF --> FF_Explo[Explosivity Index (FDR Adjusted)]
    FF --> FF_Defcon[Defcon Score (FDR Adjusted)]
    FF --> FF_Meta[Element Type / Form / xGI]
    
    FF --> Model
    Model --> Commander[Engine Commander]
    
    Commander --> Squad[15-Man Optimized Squad]
    Commander --> Captains[Tiered Captain Recommendations]
    
    Captains --> Dashboard[dashboard_data.json]
    Squad --> Dashboard
```

## 1. Predictive Modeling Strategy
The system has evolved from a hybrid heuristic/ML model to a **pure Machine Learning** pipeline.

- **Primary Model**: XGBoost Regressor.
- **Self-Training**: The `generate_static.py` pipeline includes a feedback loop. Before generating predictions, it checks the previous Gameweek's actual points, evaluates the model's error, and retrains the model to adapt to the latest trends.
- **No Manual Multipliers**: We removed manual "fixture multipliers" and "position biases" from the final score. Instead, **Fixture Difficulty (FDR)** and **Element Type (Position)** are fed directly into the XGBoost model as features, allowing the AI to learn the non-linear relationships between opponent strength, position, and output.

## 2. Advanced Metrics

### Explosivity Index (0 - 100)
A proprietary metric measuring a player's ceiling and haul potential.
- **Base inputs**: Haul Frequency + Recent Haul Density.
- **Context Awareness**:
    - **Boost**: +10% if FDR <= 2 (Easy fixture unlocks ceiling).
    - **Penalty**: -10% if FDR >= 5 (Hard fixture caps ceiling).
- **Bonuses**:
    - **Elite Form**: +15 pts.
    - **Elite Underlying**: +15 pts.
    - **Super Hot**: +25 pts for proven haul streaks.

### Defcon Score
A hybrid reliability/potential metric for GKs and DEFs.
- **Goal**: Identify the "Fun" defensive pick—someone reliable but with attacking upside.
- **Formula**: `((Historic Clean Sheet % * 60) * FDR_Modifier) + (Defensive Work * 4.0) + (Attacking Threat * 400)`
- **Components**:
    - **Reliability**: Historic Clean Sheet percentage, modulated by the upcoming opponent's difficulty (FDR).
    - **Work Rate**: Defensive actions (Blocks/Interceptions/Tackles) which drive Bonus Points (BPS).
    - **Threat**: Expected Goals (xG) and Assists (xA).

## 3. Selection Logic (The Engine Commander)

### The Optimized Squad (The Knapsack)
The algorithm selects a 15-man squad within a £100.0m budget using a "Value-Weighted Greedy" approach:
1.  **Metric**: Players are ranked by their **Reality Score** (Pure XGBoost Prediction).
2.  **Constraints**:
    - 2 GK, 5 DEF, 5 MID, 3 FWD.
    - Max 3 players per PL team.
3.  **Bench Strategy**: The algorithm attempts to minimize spending on the 4 bench slots to maximize funds for the Starting XI.

### Tiered Captain Recommendations
Players are categorized into three tactical tiers:
- **The Obvious**: The highest predicted point scorer (The model's favorite).
- **The Joker**: Low ownership differentials (<15%) with high Explosivity.
- **The Fun One**: Defensive assets with the highest Defcon scores.

## 4. Automation & Pipeline
The engine is updated daily via **GitHub Actions** (`update_fpl.yml`):
- **Schedule**: `0 3 * * *` (3 AM UTC).
- **Execution**: 
    1.  Scrapes FPL API.
    2.  **Self-Correction**: Evaluates last GW predictions vs actuals.
    3.  **Retraining**: Updates model weights.
    4.  **Prediction**: Calculates new Reality Scores and advanced metrics.
    5.  **Build**: Updates `dashboard_data.json` and pushes to main.
