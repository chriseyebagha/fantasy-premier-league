# FPL Predictor User Guide

Welcome to the **FPL Intelligence Engine**. This system uses a specialized 6-head probabilistic architecture to forecast player performance with higher accuracy than traditional points-based models.

## 1. Captaincy Personas
The engine recommends three distinct captaincy paths across different teams. Each uses a unique cross-section of probabilistic metrics:

| Persona | Best For... | Description |
| :--- | :--- | :--- |
| **⚽ The Obvious** | **Pure Dominance** | The algorithm's top pick, ranked by the **Brave Score** (70% Mean xP / 30% Haul Prob). Mathematically superior regardless of ownership. |
| **🃏 The Joker** | **High-Reward Differentials** | Targets high-explosivity players with low ownership (<15%) using the **Brave Score**. Chosen from a different team than the "Obvious" pick. |
| **🎢 The Fun One** | **Defensive Upside** | Strictly a Defender or Goalkeeper with elite attacking potential. Identified via the **Defcon Score** and targeting leaky defenses. |

## 2. Advanced Metrics & "The Brain"
*   **🧨 Explosivity Index**: A 0-100 rating measuring the probability of a "Haul" (10+ points). A score above 70 indicates a player is currently fixture-proof.
*   **🌋 Vesuvius Alert**: A premium status triggered by a **Monte Carlo Simulation**. It flags players with a **$\geq 20\%$ probability** of scoring **11 or more points** (a "Vesuvius Haul").
*   **🛡️ Defcon Score**: A specialized metric for defenders and GKs. High Defcon means high projected bonus points + goal/assist threat + clean sheet floor.
*   **🚀 Brave Target**: A label appearing on players whose xP has been boosted (+5%) because they are facing a "Leaky Defense."
*   **🧠 Model Brain**: You can now view the internal state of the engine. The **Confidence EMA** shows how much the model currently trusts each of its 6 specialized heads.

## 3. The Optimized Blueprint
The "Squad" view generates a 15-man roster (11 starters + 4 bench) following a strict **Max 3 Players Per Team** constraint.

- **Formation Optimization**: The engine automatically picks the formation with the highest cumulative xP.
- **Budget Management**: The squad is optimized within a standard £100m budget.
- **Rotation Resilience**: The engine uses a smart **2/3 Rule** (75+ mins in 2 of last 3 games) and **Talisman Protection** to ensure your starters are reliable even during busy festive fixture periods.
- **Data Heartbeat**: The system refreshes every 12 hours, with a deep-learning cycle triggered approximately 48 hours before the FPL deadline.

## 4. Strategic Usage
*   **Trust but Verify**: Use the "Brain" metrics to see if the engine is currently in a "Stability" phase (Noise Gate active) or in a high-confidence prediction phase.
*   **Transfer Shortlist**: If the engine suggests a player you don't own with high explosivity, they are a primary trade-in candidate.
*   **Bench Selection**: Follow the suggested bench order; it is calculated using a value-per-minute metric to ensure the most reliable backup plays first.
