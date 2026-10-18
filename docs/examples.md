## 📸 Screenshots

![Screenshot](https://github.com/N3oRay/proton-autogen/blob/main/docs/screenshots/pics0.jpg)

```text

# install via PPA (recommended for Debian/Ubuntu-based distributions)
sudo add-apt-repository ppa:n3oray/proton-autogen
sudo apt update
sudo apt install proton-autogen

# or install from the repository (manual)
git clone https://github.com/N3oRay/proton-autogen.git
cd proton-autogen
chmod +x install.sh
./install.sh

# launch an .exe file
proton-autogen /path/to/game.exe

# launch the GTK4 interface
proton-autogen --ux

# diagnostics
proton-autogen --diag

# list detected Proton versions
proton-autogen --list-protons


$ proton-autogen 'Battle.net Launcher.exe'

[proton-autogen] System information:
gpu: amd
wayland: False
steam_deck: False
desktop: x-cinnamon
[info] proton-autogen: mangohud: True | gamemode: True | xalia: None | gpu: balanced
[proton-autogen] Runtime information 
Executable: /home/neoray/Documents/Proton/env/main/pfx/drive_c/Program Files (x86)/Battle.net/Battle.net Launcher.exe 
Proton: Proton-CachyOS Latest 
Path: /home/neoray/.local/share/Steam/compatibilitytools.d/Proton-CachyOS Latest 
proton-call: detected 
GameMode: available 
MangoHud: available

[info] proton-autogen: LOAD CONFIG PREFIX: main
[info] INFO: EXE architecture: 32bit
[proton-autogen] INIT PROFILE - type: dx11Bnet
[proton-autogen] PROFILE: DX11 Battle.net
[proton-autogen] SYNC: MANGOHUD=1 MANGOHUD_DLSYM=1
[proton-autogen] Apply PROFILE=DX11BNET | SYNC=OFF | WINED3D=OFF | XALIA=OFF | DXVK_HUD=OFF
[info] Mode prefix: Mode prefix: main
[info] Prefix path: Prefix path: /home/neoray/Documents/Proton/env/main
[proton-autogen] 32-bit legacy game detected
[proton-autogen] MangoHud 32-bit shim missing
[proton-autogen] Launch mode: Proton
```
