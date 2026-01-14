# Contributing to FPL Predictor

Thank you for your interest in contributing to the FPL Intelligence Engine! This project aims to provide the most robust probabilistic model for Fantasy Premier League.

## 🏛 Architecture Overview

The project is divided into three main components:
1.  **Backend (Python)**: The intelligence engine that handles data ingestion, feature engineering, and training.
2.  **Frontend (Next.js)**: The dashboard for visualizing recommendations.
3.  **Automation (GitHub Actions)**: The periodic heartbeat that keeps the model updated.

## 🧠 The Vesuvius Layer

One of the unique features of this engine is the **Vesuvius Simulation Layer**. If you are looking to contribute to the predictive logic, keep these points in mind:

- **Monte Carlo Simulations**: We use 1,500+ iterations to predict "double-digit hauls" (11+ points).
- **Probabilistic Decomposition**: Instead of predicting total points, we predict discrete events (Goals, Assists, Clean Sheets, etc.) using Poisson and Binomial distributions.
- **Confidence Integration**: The model's self-assessed confidence scores are used as multipliers for event probabilities before simulation.

## 🛠 Setup for Development

### Backend
1. Create a virtual environment: `python -m venv venv`
2. Install requirements: `pip install -r backend/requirements.txt`
3. Run the generator with the force flag: `python backend/generate_static.py --force`

### Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run the dev server: `npm run dev`

## 🚀 How to Contribute

1.  **Fork the repository**.
2.  **Create a feature branch**: `git checkout -b feature/amazing-new-logic`.
3.  **Commit your changes**: `git commit -m 'Add some amazing logic'`.
4.  **Push to the branch**: `git push origin feature/amazing-new-logic`.
5.  **Open a Pull Request**.

Please ensure your code passes the existing validation checks by running `python backend/scripts/validate_deployment.py` before submitting.
