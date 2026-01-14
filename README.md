# ⚽ FPL Predictor Engine

A sophisticated, self-learning intelligence system for Fantasy Premier League. This engine uses a multi-head probabilistic architecture and a reinforcement learning feedback loop to provide state-of-the-art player projections.

[**Read the Full System Spec**](./SYSTEM_SPEC.md)

---

## 🚀 Key Features

- **6-Head Specialized Brain**: Poisson/Logistic regression models for goals, assists, clean sheets, saves, bonus, and defcon points.
- **Stability Sentinel**: Automated noise reduction and confidence scoring that protects the model during chaotic gameweeks.
- **Deadline-Aware Automation**: Dynamic synchronization that adjusts to FPL rescheduling, delivering optimized squads exactly 2 days before every deadline.
- **Vesuvius Haul Alert**: A simulation-based probabilistic layer that identifies "high-ceiling" captains with a >20% chance of double-digit returns (11+ points).
- **Budget Optimization**: Integrated LP solver that builds the highest-value squad within your team's bank constraints.

---

## 🛠 Project Structure

- `backend/`: Python intelligence engine (XGBoost + Scikit-Learn).
- `frontend/`: Next.js dashboard for visualizing predictions.
- `.github/workflows/`: Automated 12-hour heartbeat and deployment pipelines.

---

## 🎯 Target Audiences

This project is built for three distinct groups:

| Audience | What's in it for you? | Key Files |
| :--- | :--- | :--- |
| **FPL Managers** | High-performance team tips and captain picks. | `dashboard_data.json` |
| **ML Engineers** | A real-world example of 6-head probabilistic XGBoost with reinforcement feedback. | `backend/engine/trainer.py` |
| **Open Source Contributors** | A modular FPL pipeline ready for new features (e.g., chip strategy). | `CONTRIBUTING.md` |

## 🧠 AI Intelligence (How to Read the Model)

The FPL Predictor isn't just a static heuristic; it's a self-improving engine. Every week, it updates its "Brain" based on performance:

- **Confidence Scores**: The model tracks its accuracy for 6 different targets (Goals, Assists, etc.) and adjusts its trust in each.
- **Stability Sentinel**: A noise gate that prevents the model from overreacting to single-week anomalies.
- **Vesuvius Simulation**: The engine runs 1,500+ Monte Carlo simulations per player using Poisson distributions to move beyond simple "expected points" into "explosivity probability."
- **Dynamic Hysteresis**: The engine maintains "momentum," requiring significant evidence before shifting its long-term player valuations.

You can view these live metrics in the `weights.brain` section of the dashboard report.

## 📦 Quick Start

### Local Setup
1. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Run the engine**:
   ```bash
   python backend/generate_static.py --force
   ```

3. **Start the dashboard**:
   ```bash
   cd frontend && npm install && npm run dev
   ```

---

## 🔗 Portfolio Integration
This project is automatically integrated into my [main portfolio](https://chriseyebagha.com/fantasy).

The CI/CD pipeline uses `repository_dispatch` to sync data from this engine to the live website, ensuring zero-latency updates whenever predictions are refreshed.
