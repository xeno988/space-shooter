# Space Shooter - Advanced

Advanced 2D space shooter game built with Python and Pygame!

## 🎮 Features

- **Multiple Levels**: Difficulty increases with each level
- **Power-ups System**:
  - 🛡️ **Shield**: Protect yourself from damage
  - ⚡ **Rapid Fire**: Shoot faster
  - 🔱 **Triple Shot**: Shoot 3 bullets at once
  - ❤️ **Healing**: Restore health

- **Enemy System**: Dynamic enemy spawning with increasing difficulty
- **Score System**: Points for defeating enemies and collecting power-ups
- **Health & Shield**: Manage your defenses
- **High Score Tracking**: Save and display your best score
- **Pause Feature**: Press ESC to pause during gameplay
- **Multiple Game States**: Menu, Playing, Paused, Level Complete, Game Over

## 🚀 Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/xeno988/space-shooter.git
cd space-shooter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 How to Play

```bash
python main.py
```

### Controls

- **Arrow Keys**: Move your ship (Up, Down, Left, Right)
- **SPACE**: Shoot
- **ESC**: Pause/Resume
- **SPACE** (in menus): Select/Confirm

### Gameplay

1. **Main Menu**: Press SPACE to start the game
2. **During Game**: 
   - Avoid enemy bullets
   - Destroy enemies to earn points
   - Collect power-ups for advantages
   - Survive until all enemies are defeated to complete the level
3. **Level Complete**: Press SPACE to advance to the next level
4. **Game Over**: Press SPACE to return to main menu

## 🎨 Game Elements

### Player Ship (Blue)
- Controlled with arrow keys
- Shoots green bullets
- Has health and shield bar
- Can collect power-ups

### Enemies (Red)
- Spawn from top of screen
- Shoot back at you (red bullets)
- Drop power-ups when destroyed
- Increase in health at higher levels

### Power-ups
- 🛡️ **Cyan Square**: Shield (50 HP)
- ⚡ **Yellow Square**: Rapid Fire (5 seconds)
- 🔱 **Green Square**: Triple Shot (5 seconds)
- ❤️ **Red Square**: Heal (30 HP)

## 📊 Scoring

- Normal Enemy Hit: +10 points
- Enemy Destroyed: +90 points
- Power-up Collected: +50 points

## 💾 Save System

- High score is automatically saved to `highscore.json`
- Your best score will be displayed on the main menu

## 🎓 Game Mechanics

- **Collision Detection**: Bullets vs enemies, enemies vs player
- **Health System**: Shield absorbs damage first, then health
- **Power-up Duration**: 5 seconds (300 frames)
- **Progressive Difficulty**: 
  - Enemies spawn faster at higher levels
  - Enemies move faster
  - Enemies have more health

## 🛠️ Technical Details

- **Language**: Python 3
- **Game Engine**: Pygame 2.5.2
- **Resolution**: 800x600 pixels
- **FPS**: 60
- **Architecture**: Object-oriented design with dataclasses

## 📁 File Structure

```
space-shooter/
├── main.py           # Main game file
├── requirements.txt  # Python dependencies
├── README.md        # This file
└── highscore.json   # Saved high score (auto-generated)
```

## 🚀 Future Enhancements

- [ ] Sound effects and background music
- [ ] Particle effects
- [ ] More enemy types
- [ ] Boss battles
- [ ] Leaderboard system
- [ ] Configuration file for difficulty settings
- [ ] Mobile support
- [ ] Fullscreen mode

## 📝 License

MIT License - Feel free to use this project for learning and personal use!

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements!

## 👨‍💻 Author

Created with ❤️ using Python and Pygame

---

**Enjoy the game! 🎮🚀**
