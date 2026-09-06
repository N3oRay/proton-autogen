# Architecture Overview
```text
README.md                       # guide d'utilisation et installation
pyproject.toml                  # packaging (setuptools)
requirements*.txt               # dépendances
usr/
  bin/proton-autogen            # script d'entrée CLI
  lib/python3/dist-packages/
    proton_autogen/
      core.py                   # moteur principal (env, lancement, profils)
      backend.py                # orchestration CLI / actions
      ux/                       # GTK4 dashboard, assets CSS/images
      detection/                # detection de Proton/MangoHud/gamemode
      profiles/                 # définitions d'environnements (dx11, dx12, etc.)
      protondb/                 # intégration ProtonDB, cache/recommendations
      utils/                    # utilitaires (gamescope, steam_appid, etc.)
docs/                            # captures, guides d'installation et profils
debian/                          # fichiers pour package Debian
.github/                         # CI/workflows (build, tests, packaging)
tests/                           # tests (quelques tests présents)
install.sh / update.sh / uninstall.sh  # scripts d'installation/mise à jour
PKGBUILD / .SRCINFO               # packaging AUR/Arch metadata
```
# lancer un exe via Proton
proton-autogen /chemin/vers/jeu.exe

# options utiles (CLI)
```text
proton-autogen --list-protons
proton-autogen --diag
proton-autogen --ux            # lance le dashboard GTK
```

# Installation manuelle (exemple)
git clone https://github.com/N3oRay/proton-autogen.git
cd proton-autogen
chmod +x install.sh
./install.sh

# Ou construire un .deb (Debian/Ubuntu)
git clone https://github.com/N3oRay/proton-autogen.git
cd proton-autogen
dpkg-buildpackage -b -us -uc
sudo dpkg -i ../proton-autogen_*.deb

### proton_autogen.profiles
Contains all 18 game profiles (DX11, DX12, GoldSrc, etc).

# 🏗️ Architecture Overview - Proton-Autogen
```text
.SRCINFO                 (meta pour Arch)
.github/                 (actions / templates — ne semble pas critique)
.gitignore
About.md
CONTRIBUTE.md
LICENSE
Note.txt
PKGBUILD                 (paquet Arch/AUR)
README.md                (guide d'utilisation, installation, captures)
debian/                  (débian packaging)
docs/                    (screenshots, démonstrations)
install.sh               (script d'installation manuelle)
update.sh                (script de mise à jour)
pyproject.toml           (packaging Python minimal)
requirements*.txt        (dépendances)
tests/                   (répertoire de tests — vide dans l'arbre)
usr/
  bin/
    proton-autogen       (point d'entrée CLI — script Python)
  lib/python3/dist-packages/proton_autogen/
    ux/                  (UI GTK4 : dashboard, game_editor, etc.)
    backend.py           (logique de lancement, profils, etc.)
    ...                  (autres modules: info, diag, sensor, stats, etc.)
docs/screenshots/        (images démonstratives)
```

## 📦 Module Map

# Game Execution
```text
├─ run()                 # Main entry: detect Proton, setup env, launch
│  └─ Handles: proton-call mode, Wine fallback, session tracking
├─ print_runtime_info()  # Display detected runtime (GPU, Proton, etc)
```
# Game Management (CRUD)
```
├─ add_game()            # Register new game + config
├─ edit_game_ui()        # Interactive game config editor
├─ load_registered_games()          # Load all registered games from disk
├─ load_registered_games_ux()       # Format for UI display
```
# Game Discovery
```text
├─ find_windows_programs()          # Scan home for .exe files (naive)
├─ find_windows_programs_ux()       # Scan + dedup with registered games
├─ find_windows_programs_ux_search()  # @lru_cache search in common dirs
│  └─ Scans: ~/Bureau, ~/Downloads, ~/Jeux, ~/Téléchargements
│  └─ MAX_DEPTH = 6, excludes 100+ cache/temp dirs
```
# Proton Management
```text
├─ list_protons()       # Display all detected Proton versions
├─ choose_proton()      # Interactive Proton selector
├─ find_proton()        # Auto-select best Proton (GE > CachyOS > default)
├─ find_proton_by_name()  # Search by name pattern
├─ find_all_protons()   # Scan and return all Proton paths
```
# Prefix Management
```text
├─ list_prefixes()      # List available Wine prefixes
├─ choose_prefix()      # Interactive prefix selector
├─ create_new_prefix()  # Create new prefix interactively
├─ find_existing_prefix_for_game()  # Reuse existing prefix
```
# Utilities
```text
├─ normalize_flag()     # Parse boolean flags (1, true, yes, on)
├─ list_programs()      # CLI: list all discovered programs
├─ list_programs_ux()   # UI: list with badges and metadata
└─ _normalize()         # Clean names for search
```
### **Core Execution Modules**

#### `core.py` (2100 lines) - **Engine Principal**
**Responsibility:** Game environment setup and execution orchestration

# Base Initializer
```text
├─ init_env()            # Create clean environment dict
```
# Game Profile Factories (referenced in core.py)
```text
├─ env_legacy_app()      # Photoshop 6, legacy apps
├─ env_launcher()        # Battle.net, EA App, Ubisoft
├─ env_dx11()            # Default DX11 games
├─ env_dx12()            # VKD3D DirectX 12
├─ env_oldgame()         # WineD3D for DX8/DX9
├─ env_ut99()            # Unreal Tournament 99
├─ env_quake()           # Quake II
├─ env_win95()           # DirectDraw, Windows 95
├─ env_ut3()             # Unreal Tournament 3
├─ env_goldsrc()         # Half-Life, GoldSrc engine
└─ env_gtav_*()          # GTA V variants

# Typical Profile Structure
{
  "PROTON_NO_ESYNC": "0",     # Synchronization flags
  "PROTON_NO_FSYNC": "0",
  "WINEESYNC": "1",
  "WINEFSYNC": "1",
  "PROTON_USE_WINED3D": "0",  # Rendering backend
  "DXVK_CONFIG": "...",       # DXVK tuning
  "VKD3D_CONFIG": "...",      # VKD3D tuning
  "WINEDLLOVERRIDES": "...",  # DLL override rules
  "MANGOHUD": "0",            # Performance overlay
  "GAMEMODE": "0"             # Game mode flag
}
```
# Profile Definitions (18 total)
```text
├─ env_legacy_app()       # Legacy apps (Photoshop 6)
├─ env_launcher()         # Launchers (Battle.net, EA App, Ubisoft)
├─ env_dx11()            # DirectX 11 (most modern games)
├─ env_dx11BNet()        # DX11 specialized (Battle.net/HOTS)
├─ env_dx12()            # DirectX 12 (VKD3D)
├─ env_oldgame()         # DX8/DX9 with WineD3D
├─ env_dx8dg()           # DX8 + dgVoodoo compatibility
├─ env_dx9dg()           # DX9 + dgVoodoo compatibility
├─ env_dx9()             # DirectX 9 with FPS caps
├─ env_dx9opengl()       # DX9 + OpenGL fallback
├─ env_goldsrc()         # GoldSrc engine (Half-Life, Quake)
├─ env_ut99()            # Unreal Tournament 99
├─ env_quake()           # Quake II cleanup
├─ env_ut3()             # Unreal Tournament 3
├─ env_win95()           # Windows 95 DirectDraw
├─ env_desktop()         # Desktop apps (Photoshop, etc)
└─ env_gtav_*()          # GTA V (3 variants: compat, x11, safe)
```
# Core Functions
```text
├─ base_env()            # Build runtime environment dict
├─ run_game_proton()     # Execute via Proton subprocess
├─ run_standard()        # Wine fallback execution
├─ get_prefix_path()     # Resolve Wine prefix (main/shared/auto/custom)
└─ apply_user_profile()  # Override with user custom config
```
# Helpers
```text
├─ has_proton_call()     # Check proton-call availability
├─ has_wine()            # Check Wine installation
├─ has_mangohud()        # Check MangoHud availability
├─ has_gamemode()        # Check GameMode availability
├─ get_exe_arch()        # Detect PE32/PE32+ (32 vs 64-bit)
└─ load_proton_paths()   # Scan standard Proton locations
```
# Important Data Structures:

# Game Config (JSON, per game)
```text
{
  "id": "hash",
  "name": "Game Name",
  "path": "/path/to/game.exe",
  "favorite": False,
  "playtime": {
    "seconds": 12345,
    "launch_count": 42,
    "last_session": 1234567890,
    "last_launch": "2026-07-05T22:00:00Z"
  },
  "exe_type": "dx11",
  "proton": "/path/to/Proton",
  "prefix": {
    "name": "main",
    "path": "/path/to/prefix"
  },
  "features": {
    "mangohud": False,
    "gamemode": False,
    "xalia": None,
    "gpu": "auto"
  },
  "sync": {"esync": "auto", "fsync": "auto"},
  "env": {"DXVK_ASYNC": "1"}
}
```
# Proton Detection Result
```text
{
  "path": "/home/user/.steam/root/compatibilitytools.d/GE-Proton10-34",
  "name": "GE-Proton10-34",
  "version": "10.34",
  "priority": 30  # GE-Proton priority
}
```

# Feature Resolution
```text
├─ resolve_game_features()   # Replace "auto" with actual values
│  └─ gpu: "auto" → "safe"/"balanced"/"performance"/"extreme"
```
# GPU Profile Detection
```text
├─ detect_gpu_profile()      # Auto-select GPU profile based on system
│  ├─ Steam Deck    → "balanced"
│  ├─ Wayland       → "safe"
│  ├─ GPU Hybrid    → "balanced"
│  ├─ High-end GPU  → "extreme" (8GB VRAM, 16GB RAM, 8+ cores)
│  ├─ Mid-range GPU → "performance" (4GB VRAM, 8GB RAM)
│  ├─ Dedicated GPU → "balanced"
│  └─ Integrated GPU → "safe"
```
# GPU Environment Setup
```text
├─ gpu_env()                # Return GPU-specific env vars
│  └─ NVIDIA: PROTON_ENABLE_NVAPI=1, __GL_SHADER_DISK_CACHE=1
│  └─ AMD: RADV_PERFTEST=aco (or sam on high-end)
```

# CPU Optimization
├─ detect_use_all_available_cores()
└─ cpu_args()               # Return -USEALLAVAILABLECORES if applicable
