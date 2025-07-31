# 🎯 Sequence Game

## 📜 Description
### Sequence Game is a strategic, turn-based card and chip board game implemented in Python using the PySide6 GUI framework. Combining the essence of cards, board tactics, and light AI, Sequence challenges players to form chip sequences on a dynamic 10x10 card grid.Play against a friend or challenge an AI opponent across three difficulty levels — Easy, Medium, and Hard (with prediction-based moves). The game features visually rich gameplay, animated win effects, an interactive help guide, and intuitive user settings. Whether you're a casual player or a strategist, Sequence brings classic board gaming to your desktop.

---

## 🚀 Features
### 🎮 Game Modes:
- ✅ Single Player (vs AI)
- ✅ Two Players (local multiplayer)

### 🧠 AI Difficulty Levels:
- ✅ Easy — Random and defensive moves  
- ✅ Medium — Tries to block or complete sequences  
- ✅ Hard — Strategic AI with advanced decision-making  

### 📊 Game Mechanics:
- 10×10 Board with 4 corner wildcards (free chips)
- 🃏 Special Jack Cards:
  - One-Eyed Jack → Remove an opponent's chip
  - Two-Eyed Jack → Place a chip anywhere
- 🔴 Completed sequences are highlighted with red chips
- Tracks scores, turns, and win status

### 🧩 Game Logic:
- Validates player card and board clicks
- Smart handling of Jack cards
- Auto-skips invalid moves
- Chip color animations and win effects

### 🌈 User Interface:
- Emoji-based chips: 🔵 (Player 1), 🟢 (Player 2), 🔴 (Sequence)
- Win/loss/draw messages with animation
- Restart, Exit, and Help options
- Responsive layout with scroll support

---

## 💻 Installation
## 1️⃣ Clone the repository:
✅ 1. Requirements:
- Python 3.8+
- PySide6 GUI library  
Install via pip:
```
pip install PySide6
```
---
✅ 2. Download the Project:
Clone this repository using Git:
```
git clone https://github.com/anujadevelops/Sequence-Game.git
```
## 2️⃣ Navigate to the project directory:
```
cd Sequence-Game
```
## 3️⃣  Run the application:
Run using the command line:
```
python SequenceGame.py
```
## 4️⃣ Build .exe (Optional)
Use PyInstaller to build a Windows .exe file and run:
```
pip install pyinstaller
```
```
pyinstaller --onefile --noconsole SequenceGame.py
```

---

## 🛠️ Features in Detail
The Sequence Game offers the following core features:

---
### ✅ Game Mechanics:
- Card matching system
- Chip placement & locking
- AI plays hidden cards with animations
- Chip removal & wild card logic
- Sequence detection with direction scanning

### ✅ AI Engine:
- Makes contextual decisions based on difficulty:
  - Easy: Purely random
  - Medium: Plays optimally without prediction
  - Hard: Tries to form or block sequences

### ✅ Win Logic:
- Detects 5-in-a-row with flexible directions (↕️, ↔️, ↖️↘️, ↙️↗️)
- Allows chip overlaps if part of different sequences
- Victory ends game & disables board

### ✅ User Interface:
- Turn indicators with player name
- Status messages for each action
- Card-based hand display (Player vs AI: shows 🎴)
- Visual score display at top

### ✅ Accessibility:
- Tooltips, text guides, and color-coded feedback
- Large clickable buttons (mobile-friendly UI, but for desktop only)
- Menu layout with logical grouping

## 🤝 Contributing
### 1️⃣ Fork the repository.
### 2️⃣ Create a new branch (e.g., `git checkout -b feature-branch`).
### 3️⃣ Make your changes and thoroughly test them.
### 4️⃣ Commit your changes (e.g., `git commit -am "Add: Description of new feature or fix"`).
### 5️⃣ Push to your fork (e.g., `git push origin feature-branch`).
### 6️⃣ Submit a pull request describing your changes and the purpose of the contribution.

## 💡 Feedback
### If you have suggestions or encounter any issues, feel free to open an issue  or pull request for bugs, improvements, or suggestions! on the repository or reach out directly.

## ⚠️ Limitations
### ❌ Local multiplayer only (no online mode)
### ❌ Not optimized for mobile/touch devices
### ❌ Basic AI (no adaptive learning)
### ❌ No login or user accounts


---
## Thank you for checking out the Sequence Game , Let the sequences begin! 🧠🎲🟢🔵
