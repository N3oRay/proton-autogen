# Contributing to proton-autogen

Thank you for your interest in contributing to proton-autogen!

This project aims to simplify game management on Linux using Proton, per-game profiles, and system-aware optimizations.

---

## 📬 Contact

Maintainer: N3oray
Email: <n3oray77@gmail.com>

---

## 🧭 Project Goals

- Provide a simple and powerful GUI for managing games on Linux
- Automatically optimize Proton settings per game
- Offer system-aware performance profiles (GPU, GameMode, MangoHud, etc.)
- Keep configuration files human-readable and portable

---

## 🛠️ Code Style

Please follow these guidelines:

- Python 3.10+
- Clear and readable code (prefer readability over clever code)
- Use type hints when possible
- Keep functions small and focused
- Avoid unnecessary side effects

Example:

```python
def resolve_game_features(game: dict, system: dict) -> dict:
    ...
