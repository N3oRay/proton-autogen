# 🧩 Proton-Autogen

![Linux](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/python-3.x-yellow)
![Status](https://img.shields.io/badge/status-v1.0-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

**Smart Proton launcher for Windows `.exe` files on Linux**

Run Windows .exe files on Linux using Proton or Wine with zero manual setup.
---

## 🚀 Overview

Proton-Autogen is a lightweight Linux utility.
Automatic Windows `.exe`  execution system for Linux using Proton + Wine fallback

Instead of manually creating Steam shortcuts, configuring compatibility options, or managing Wine prefixes, simply:

* Right-click a `.exe`
* Select **Open with Proton-Autogen**
* Launch the application

The tool automatically detects available Proton installations (GE-Proton preferred), configures the runtime environment, and falls back to Wine when necessary.

---

## ✨ Features

* ▶ Run Windows `.exe` files directly via Proton
* 🧠 Automatic Proton detection
* 🚀 GE-Proton priority support
* 🍷 Automatic Wine fallback
* 🖱️ File manager integration

  * Nemo
  * Nautilus
  * Dolphin
* ⚙️ Optional GameMode support
* 📦 Debian package (.deb)
* 💻 Command-line interface
* 🔧 Lightweight and dependency-minimal

---

## 📸 Screenshots

### Nemo Integration

![Nemo Integration](docs/screenshots/nemo-right-click.png)

Right-click any Windows executable and select:

```text
Open with Proton-Autogen
```

---

## 🧪 Usage

### Terminal

```bash
proton-autogen game.exe
```

or

```bash
proton-autogen /path/to/application.exe
```

### Example Output

```text
Running Proton for:
~/Games/MyGame/game.exe

Using:
GE-Proton10-34

Launch initialized
```

---

## 📦 Installation


### Arch Linux (manual)

```bash
git clone https://github.com/N3oRay/proton-autogen.git
cd proton-autogen
sudo install -Dm755 usr/bin/proton-autogen /usr/bin/proton-autogen
sudo cp -r usr/share/* /usr/share/
```

### Debian / Ubuntu

```bash

dpkg-buildpackage -b -us -uc
sudo dpkg -i ../proton-autogen_*.deb
```

### Debian Package

```bash
sudo add-apt-repository ppa:n3oray/proton-autogen
sudo apt update
sudo apt install proton-autogen
```

This installs:

* `/usr/bin/proton-autogen`
* Nemo (Cinnamon) integration
* Nautilus (GNOME)  integration
* Dolphin (KDE Plasma) integration

---






## ⚠️ Requirements

### Required

* Python 3.x
* A working Proton installation

Supported locations:

```text
~/.steam/root/compatibilitytools.d
~/.steam/debian-installation/compatibilitytools.d
~/.local/share/Steam/compatibilitytools.d
```

### Optional
```
sudo apt install gamemode mangohud 
```
* GameMode
* MangoHud
* GE-Proton
* ProntonUp-qt

---

## 🧠 How It Works

1. Detect available Proton installations
2. Prefer GE-Proton when available
3. Launch executable through Proton
4. Fall back to Wine if Proton runtime tools are unavailable
5. Optionally enable GameMode

No Steam shortcut creation is required.

---

## 🗑️ Uninstallation

### Remove Package

```bash
sudo apt remove proton-autogen
```

### Full Cleanup

```bash
sudo apt purge proton-autogen
```

### Manual Cleanup

```bash
rm -rf ~/.config/proton-autogen
rm -f ~/.local/share/nemo/actions/proton-autogen.nemo_action
```

Restart Nemo:

```bash
nemo -q
```

Restart Nautilus:

```bash
nautilus -q
```

---

## 🚧 Known Limitations

* Not every Windows application works under Proton
* Some launchers require additional configuration
* Proton compatibility depends on the selected Proton version
* Certain applications may still require Wine tweaks

---

## 🛣️ Roadmap

* [ ] Game / Installer auto-detection
* [ ] Per-application profiles
* [ ] Configuration file support
* [ ] GUI frontend
* [ ] Lutris integration
* [ ] Bottles integration
* [ ] Automatic prefix management
* [ ] Silent mode

---

## 💡 Philosophy

Linux gaming is powerful but often fragmented.

Proton-Autogen aims to reduce friction by turning Proton into a transparent execution layer rather than a manually configured tool.

The goal is simple:

> Right-click → Run Windows application → It just works.

---

## 👤 Author

**neoray**

GitHub: https://github.com/N3oRay

---

## 📜 License

This project is licensed under the MIT License.

See the `LICENSE` file for details.
