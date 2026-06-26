def print_help():
    print("""proton-autogen

Usage:
  proton-autogen <file.exe>
  proton-autogen run <file.exe>
  proton-autogen add <file.exe>
  proton-autogen edit <file.exe>

Information:
  proton-autogen --v
  proton-autogen --about
  proton-autogen --help
  proton-autogen --help-env ( New V 2.5.3)

Prefix: (STEAM_COMPAT_DATA_PATH)
  proton_autogen --pc
    (Prefix Custom       : ~/Documents/Proton/env/Proton Custom/)
  proton-autogen --pa
    (Prefix auto         : ~/Documents/Proton/env/UnrealTournament-a12bc34d)
  proton-autogen --ps
    (Prefix shared       : ~/Documents/Proton/env/shared)
  proton-autogen
    (Prefix by default   : ~/Documents/Proton/env/main)

Profil:
  proton_autogen --json-profile  : Make all profile env Type in Json
  proton_autogen --profile dx11 : Use profile Type

Discovery:
  proton-autogen --list-protons
  proton-autogen --list-programs
  proton-autogen --proton-paths
  proton-autogen --diag

Game management:
  proton-autogen add <file.exe>
      Create a game profile in ~/.config/proton-autogen/

Execution:
  proton-autogen <file.exe>
      Run game using automatic Proton selection or saved config

  proton-autogen run <file.exe>
      Force execution without profile override

Options:
  --debug        Debug output
  --verbose      Verbose output
  --mangohud     Enable MangoHud overlay
  --gamemode     Enable GameMode
  --call         use Proton-Call
  --wine         use Wine
  --proton       use Proton only (run by default)

Examples:
  proton-autogen add game.exe
  proton-autogen game.exe
  proton-autogen run game.exe
  proton-autogen game.exe --mangohud


  # Basic run
  proton-autogen game.exe

  # DX9 old game (recommended)
  proton-autogen SWEP1RCR.EXE --profile dx9dg

  # With GameMode + MangoHud
  proton-autogen game.exe --gamemode --mangohud

  # Gamescope (recommended for scaling)
  gamescope -f -W 1280 -H 1024 -- proton-autogen game.exe

  # Gamescope + FSR (may blur UI in old DX9 games)
  gamescope -f -W 1280 -H 1024 --fsr-sharpness 0 -- proton-autogen game.exe

Notes:
  - Uses saved JSON config when available
  - Automatically selects best Proton version
  - Falls back to Wine if Proton is unavailable
  - Supports Steam, Flatpak, and compatibilitytools installs
  - Config custom Proton locations with ~/.config/proton-autogen.conf

""")
