# Contributing to proton-autogen

Thank you for your interest in contributing to proton-autogen!

This project aims to simplify game management on Linux using Proton, per-game profiles, and system-aware optimizations.

## 🌍 Community

Proton-Autogen is being tested and discussed by the Linux community:

- 🐧 Linux Mint community
- 🚀 CachyOS community
- 💬 Linux gaming users

The project is actively evolving based on user feedback.

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

## Profiles

Proton-Autogen includes a profile system that allows users to customize runtime behavior for specific applications and games.

Before creating or modifying built-in profiles, please read the dedicated documentation:

- 📖 [Profiles documentation](docs/profiles.md)

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
```    
## 🤝 Ways to contribute

Thank you for your interest in contributing to Proton-Autogen!

All contributions are welcome:
- bug reports
- compatibility improvements
- new game/application profiles
- documentation improvements
- translations
- code improvements

## 🐛 Reporting bugs

Before opening an issue:

- Check that you are using the latest version.
- Include your Linux distribution.
- Include your Proton/Wine version.
- Provide the executable name.
- Include logs if possible.

