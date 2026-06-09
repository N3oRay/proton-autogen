proton-autogen.

# 🧩 proton-autogen

![Linux](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/python-3.x-yellow)
![Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-TBD-lightgrey)

**Smart Proton launcher for Windows `.exe` files on Linux**

---

## 🚀 Overview

`proton-autogen` is a lightweight Linux utility that allows you to run Windows `.exe` files using Proton in a simple and seamless way.

It integrates directly into your file manager (tested with :contentReference[oaicite:0]{index=0}), enabling you to right-click any `.exe` file and launch it instantly via Proton.

The goal is to remove all manual Proton/Wine configuration and make Windows executables feel like native Linux applications.

---

## ✨ Features

- ▶ Run `.exe` files directly via Proton
- 🖱️ Native file manager integration (right-click in Nemo)
- ⚙️ Automatic Proton environment setup
- 🧠 Support for custom Proton builds (e.g. GE-Proton)
- 📦 Easy CLI usage + `.deb` packaging
- 🔧 Lightweight and dependency-minimal

---

## 📸 Screenshots

### 📁 Right-click integration in Nemo

![Right click integration](docs/screenshots/nemo-right-click.png)

> Right-click any `.exe` file → “Open with Proton-Autogen”

---

### 🖥️ Terminal usage

```bash
proton-autogen /path/to/game.exe

Example output:

Running Proton Custom for /path/to/game.exe
gamemodeauto:
Proton launch initialized
⚙️ Installation
📦 Option 1 — Debian package (.deb)
sudo dpkg -i proton-autogen.deb
sudo apt -f install

This will:

install the CLI tool
register file manager integration
add system-wide command proton-autogen
🧪 Option 2 — Install from source
git clone https://github.com/yourname/proton-autogen
cd proton-autogen
pip install -e .
🧠 Usage
▶ Terminal
proton-autogen /path/to/file.exe
🖱️ File manager (Nemo)

Right click any .exe file:

Open with Proton-Autogen
⚠️ Requirements
Core dependency
Python 3.x
System requirements
Steam Proton or custom Proton (GE-Proton recommended)
Bash shell environment
Optional (recommended)
GameMode for performance optimization
MangoHud for performance overlay
🧠 Important note

Python alone is NOT sufficient.

proton-autogen acts as a runtime orchestrator for Proton and requires a working Proton installation to function.

📦 Files installed
/usr/bin/proton-autogen
Nemo integration:
~/.local/share/nemo/actions/proton-autogen.nemo_action
🗑️ Uninstallation
Remove package
sudo apt remove proton-autogen
Full cleanup (recommended)
sudo apt purge proton-autogen
Manual cleanup (if needed)
rm -rf ~/.config/proton-autogen
rm -f ~/.local/share/nemo/actions/proton-autogen.nemo_action
nemo -q
🚧 Known limitations
Not all .exe files are guaranteed to work under Proton
Some applications require manual Wine/Proton tuning
ProtonFixes may not fully activate outside Steam environment
Debug logs may appear depending on Proton configuration
🧩 Roadmap
 Auto-detection (game / installer / launcher)
 Proton profile system per executable
 GUI configuration tool
 Integration with Lutris and Bottles
 Automatic prefix management
 Silent mode (no logs)
💡 Philosophy

Linux gaming is powerful but fragmented.

proton-autogen aims to reduce friction by turning Proton into a transparent execution layer, instead of a manually configured tool.

The goal is simple:

Right-click → Run Windows app → It just works.

👤 Author

neoray

📜 License

TBD

⭐ Why this exists

Existing tools like Proton, Wine, Lutris, or Bottles are powerful but often require manual setup or separate environments.

proton-autogen focuses on:

simplicity
file manager integration
automatic runtime selection
minimal user friction


## License

This project is licensed under the MIT License.
