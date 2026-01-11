# FPL Predictor ⚽️

A Fantasy Premier League prediction app that helps you find the best players to buy each gameweek based on upcoming fixtures, form, and expected performance metrics.

![FPL Predictor Demo](https://img.shields.io/badge/FPL-Predictor-brightgreen)

## 🎯 Features

- **Smart Player Rankings**: Uses FPL's official expected points (`ep_next`) with custom fixture adjustments
- **Position Filtering**: Filter by GK, DEF, MID, or FWD to find the best options for each slot
- **Value Analysis**: Sort by "Best Value" to find budget gems (predicted points ÷ price)
- **Fixture Difficulty**: Visual indicators for easy/hard upcoming fixtures
- **Injury Tracking**: Automatically adjusts predictions based on player availability

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fpl-predictor.git
   cd fpl-predictor
   ```

2. **Backend Setup**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the App

**Terminal 1 - Start Backend:**
```bash
source venv/bin/activate
python3 backend/api.py
```
*Backend runs on http://localhost:5001*

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```
*Frontend runs on http://localhost:3000*

## 📊 How It Works

### Data Source
All data is fetched from the **official FPL API** (free, no authentication required):
- `https://fantasy.premierleague.com/api/bootstrap-static/` - Player stats
- `https://fantasy.premierleague.com/api/fixtures/` - Fixture difficulty ratings

### Prediction Algorithm

**Base Score:**
Uses FPL's own `ep_next` (Expected Points Next gameweek) as the foundation.

**Fixture Adjustment:**
- **Defenders/Goalkeepers**: ±15% based on fixture difficulty (clean sheets are fixture-dependent)
- **Midfielders/Forwards**: ±10% (attackers can score against anyone)

**Availability Penalty:**
Players with <100% chance of playing have their score multiplied by their injury likelihood.

**Example:**
```
Player: Gusto (Defender)
Base ep_next: 7.0 pts
Upcoming Fixture: Difficulty 2 (Easy)
Adjustment: 7.0 × 1.15 = 8.05 pts
```

## 🛠️ Tech Stack

### Backend
- **Python 3** + Flask
- **Pandas** for data processing
- **Requests** for API calls

### Frontend
- **Next.js 16** (React + TypeScript)
- **Tailwind CSS** for styling
- **Server-Side Rendering** for fast initial load

## 📁 Project Structure

```
fpl-predictor/
├── backend/
│   ├── api.py              # Flask server
│   ├── fpl_engine.py       # Prediction logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx    # Main dashboard
│   │   └── components/
│   │       └── PlayerCard.tsx
│   ├── package.json
│   └── tailwind.config.ts
└── venv/                   # Python virtual environment
```

## 🎮 Usage Guide

1. **Open** http://localhost:3000
2. **Filter** by position using the GK/DEF/MID/FWD buttons
3. **Sort** by "Predicted Points" (default) or "Best Value"
4. **Look for**:
   - 🟢 Green circles = Easy fixtures
   - 🔴 Red circles = Hard fixtures
   - ⚠️ Red text = Injury concerns

## 🔧 Customization

### Adjust Fixture Weights
Edit `/backend/fpl_engine.py` lines 80-91:

```python
# Make defenders MORE fixture-dependent
if difficulty <= 2: multiplier = 1.20  # Increase from 1.15
```

### Change Minimum Minutes Filter
Edit `/backend/fpl_engine.py` line 60:

```python
if p['minutes'] < 450:  # Increase from 270 (3 games → 5 games)
```

## 📈 Future Enhancements

- [ ] Historical performance tracking
- [ ] Compare against previous gameweeks
- [ ] Export top picks to CSV
- [ ] Team builder (15-man squad optimizer)
- [ ] Captain recommendations

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📄 License

MIT License - feel free to use this for your FPL domination!

## 🙏 Acknowledgments

- Data provided by the official FPL API
- Built with ❤️ for the FPL community

---

**Good luck with your FPL season!** 🏆
