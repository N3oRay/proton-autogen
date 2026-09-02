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

Please use GitHub Issues to report bugs:
https://github.com/N3oRay/proton-autogen/issues

## 🎮 Compatibility reports

Testing games and applications is also a valuable contribution.

Please provide:

- Application/game name
- Executable name
- Linux distribution
- GPU
- Proton/Wine version
- Result (working, partial, not working)
- Additional configuration required

## 📦 Pull Requests

Before submitting a pull request:

- Explain the purpose of the change.
- Keep commits focused.
- Test your changes.
- Update documentation if needed.

Large changes should be discussed before implementation.

🌍 Translations

Translations are welcome and are an important part of making proton-autogen accessible to more users.

When adding or updating translations:

Keep the meaning consistent with the English source text.
Use natural terminology for the target language.
Avoid literal translations when they sound unnatural.
Preserve placeholders such as {game}.
Preserve formatting and escape sequences such as \n.
Make sure every translation key is present in all supported languages.
Checking Translation Completeness

Before submitting changes to translations, you can use the built-in translation checker:
```
proton-autogen --check-translations
```

This checks whether all supported translation files contain the required translation keys.

A successful check looks like:
```
[i18n] Checking translation completeness...
[i18n] OK: toutes les traductions sont complètes.
```

If a translation is missing, the checker will report the missing key(s), allowing you to update the affected language files before submitting your contribution.

It is recommended to run this command after adding or modifying translation keys.
