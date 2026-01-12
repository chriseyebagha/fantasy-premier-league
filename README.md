# Fantasy Premier League Predictor 🔮

**The "Oracle" used by `chriseyebagha.com/fantasy`.**

This project is an automated, data-driven engine that predicts FPL outcomes using machine learning. It runs daily in the cloud, determining the optimal squad and captaincy choices based on Form, Fixtures, and Expected Points (xP).

> **Live Demo**: This engine powers the fantasy section of my portfolio. Check it out at [chriseyebagha.com/fantasy](https://chriseyebagha.com/fantasy).

## 📚 Documentation
- **[User Guide](./USER_GUIDE.md)**: How to use the "Captaincy Personas" and optimized squad to win your mini-leagues.
- **[Technical Architecture](./TECHNICAL_ARCHITECTURE.md)**: A look under the hood. System diagrams, directory structure, and the logic behind the "Virtual Loop" automation.
- **[Model & Metrics](./MODEL_AND_METRICS.md)**: Deep dive into the XGBoost regression model, including exact formulas for the "Explosivity Index" and "Defcon Score".

## 🚀 Key Features
- **🤖 XGBoost Engine**: Uses gradient boosting to value player potential over hype.
- **☁️ Virtual Loop**: Runs on GitHub Actions every day at 3 AM UTC (`cron: 0 3 * * *`).
- **🧨 Explosivity Index**: A custom metric identifying high-ceiling differential players.
- **🛡️ Defcon Score**: A hybrid metric for defenders combining clean sheets with goal threat.
- **🧠 Squad Optimization**: Uses a knapsack-like greedy algorithm to build the mathematically "best" 15-man squad within budget (£100m).

## 🏗️ Portfolio Integration
This repository is designed as a standalone micro-frontend.
- **Repo**: `fantasy-premier-league` (This repo).
- **Host**: `chriseyebagha.com` (Main portfolio).
- **Integration**: The main portfolio serves the build output of this project at the `/fantasy` route, creating a seamless user experience while keeping the codebases distinct.

## 🛠️ Quick Start (for Contributors)
1.  **Clone & Install**:
    ```bash
    git clone https://github.com/chriseyebagha/fantasy-premier-league.git
    pip install -r backend/requirements.txt
    ```
2.  **Run the Engine**:
    ```bash
    python backend/generate_static.py --force
    ```
    *This generates a local `dashboard_data.json`.*

3.  **Run the Frontend**:
    ```bash
    cd frontend && npm run dev
    ```

---
*Built with Python 3.10 and Next.js.*
