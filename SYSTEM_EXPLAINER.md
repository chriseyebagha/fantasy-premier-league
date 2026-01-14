# FPL Engine: System Explainer

This document explains the core metrics driving the FPL Predictor model, how they are calculated, and how to interpret them.

## Core Metrics

### 1. Haul Probability (`haul_prob`)
**What it is:** The probability that a player will score **11+ points** in the *upcoming* Gameweek.

**How it's calculated:**
- We simulate the match 10,000 times (Monte Carlo simulation) using the player's predicted event probabilities.
- **Inputs:**
  - Predicted Goals, Assists, Clean Sheets (Poisson/Binomial distributions).
  - **Clinicality Boost:** Multiplier based on the player's seasonal haul frequency (are they a "big game" player?).
  - **Matchup Boost:** Multiplier based on the opponent's **Vulnerability Score**.
- **Transformation:** The raw probability is boosted by these multipliers to get the final `%`.
- **Haul Alert:** Triggered if `haul_prob >= 20%`. This indicates a "Captainable" ceiling.

### 2. Explosivity Index (`explosivity`)
**What it is:** A historical "pedigree" score (0-100) measuring a player's *season-long* ability to deliver massive scores.

**How it's calculated:**
- **History:** Frequency of double-digit hauls over the season.
- **Form:** Specific bonus for hauls in the last 10 games.
- **Underlying Stats:** Bonus for high xGI (Expected Goal Involvement) per 90.
- **Fixture:** Slight adjustment for the upcoming fixture difficulty.

**Key Difference:**
> **Explosivity** is about *who the player is* (their ceiling).
> **Haul Probability** is about *what might happen this week* (the simulation).
>
> *Example:* A player like **Salah** has high Explosivity (always capable of a haul). But if he plays Man City away, his **Haul Probability** might be lower. Conversely, a mid-tier asset playing a chaotic defense might have a high Haul Probability this week despite lower seasonal Explosivity.

### 3. Opponent Vulnerability (`opponent_vulnerability`)
**What it is:** A score (0-100 scale) representing how "leaky" a team's defense is. Higher is worse for them (better for your attackers).

**How it's calculated:**
- It is a **50/50 Blend** of:
  1.  **Process (xGC):** Expected Goals Conceded per match (Rolling 7-game average).
  2.  **Reality (GC):** Actual Goals Conceded per match (Rolling 7-game average).
- **Scale:** The per-match value (e.g., 1.50) is multiplied by 25 to create a 0-100 index (e.g., 37.5).
- **Threshold:** Teams with a vulnerability score > 35 (approx 1.4 Goals Conceded/Game) are considered "Leaky" and trigger a Haul Boost for opposing attackers.

---

## Metric Verification (GW22 Example)

**Case Study: Chelsea's Defense**
- **Vulnerability Score:** 36.25 (implies ~1.45 Goals Conceded/Game).
- **Reality Check (Last 7 PL Games):**
  - vs Fulham (2 conceded)
  - vs Man City (1 conceded)
  - vs Bournemouth (2 conceded)
  - vs Aston Villa (2 conceded)
  - vs Newcastle (2 conceded)
  - vs Everton (0 conceded)
  - vs Bournemouth (0 conceded)
- **Average Conceded:** 1.29 Goals/Game.
- **Implied xGC:** ~1.61 xGC/Game (to reach the 1.45 average).
- **Conclusion:** Chelsea consistently conceding 2 goals in recent tough matches justifies the high vulnerability score, triggering Haul Alerts for Brentford attackers.
