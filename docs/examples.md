```text

# installer via PPA (recommandé sur Debian/Ubuntu dérivés)
sudo add-apt-repository ppa:n3oray/proton-autogen
sudo apt update
sudo apt install proton-autogen

# ou installer depuis le dépôt (manuel)
git clone https://github.com/N3oRay/proton-autogen.git
cd proton-autogen
chmod +x install.sh
./install.sh

# lancer un exe
proton-autogen /chemin/vers/jeu.exe

# lancer l'interface GTK4
proton-autogen --ux

# diagnostic
proton-autogen --diag

# lister les protons détectés
proton-autogen --list-protons


$ proton-autogen 'Battle.net Launcher.exe'

[proton-autogen] System information:
  gpu: amd
  wayland: False
  steam_deck: False
  desktop: x-cinnamon
[info] proton-autogen: mangohud: True | gamemode: True | xalia: None | gpu: balanced
[proton-autogen] Runtime information
  Executable : /home/neoray/Documents/Proton/env/main/pfx/drive_c/Program Files (x86)/Battle.net/Battle.net Launcher.exe
  Proton     : Proton-CachyOS Latest
  Path       : /home/neoray/.local/share/Steam/compatibilitytools.d/Proton-CachyOS Latest
  proton-call: detected
  GameMode  : available
  MangoHud  : available

[info] proton-autogen: LOAD CONFIG PREFIX : main
[info] INFO: EXE architecture: 32bit
[proton-autogen] INIT PROFILE - type: dx11Bnet
[proton-autogen] PROFILE: DX11 Battle.net
[proton-autogen] SYNC: MANGOHUD=1 MANGOHUD_DLSYM=1
[proton-autogen] Apply PROFILE=DX11BNET | SYNC=OFF | WINED3D=OFF | XALIA=OFF | DXVK_HUD=OFF
[info] Prefix mode: Prefix mode : main
[info] Prefix path: Prefix path : /home/neoray/Documents/Proton/env/main
[proton-autogen] 32-bit legacy game detected
[proton-autogen] MangoHud 32-bit shim missing
[proton-autogen] Launch mode: Proton
```
