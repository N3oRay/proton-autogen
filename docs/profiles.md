# Community Game Profiles

Proton-Autogen includes a community-maintained game profile database (`profiles.csv`) used to automatically select the best runtime profile for known Windows games and applications.

Everyone is welcome to contribute. No Python knowledge is required.

# Profiles

Profiles allow you to customize the execution environment for specific applications or games without modifying Proton-Autogen itself.

They are intended to make it easy to reuse environment variables, compatibility settings, and launch options across multiple applications. Whether you want to improve compatibility, optimize performance, or maintain separate configurations for different games, profiles provide a simple and reusable solution.

If you plan to contribute new built-in profiles or improve existing ones, please read the project's contribution guidelines first:
👉  📖 [CONTRIBUTING documentation](/CONTRIBUTING.md)

## Location

System database:

```text
/usr/share/proton-autogen/profiles.csv
```

User overrides:

```text
~/.config/proton-autogen/profiles.csv
```

Entries in the user database automatically override entries from the system database.

## CSV Format

```csv
exe,game,exe_type,notes
```

### Fields

| Field      | Description                    |
| ---------- | ------------------------------ |
| `exe`      | Executable filename (required) |
| `game`     | Game or application name       |
| `exe_type` | Proton-Autogen profile         |
| `notes`    | Optional compatibility notes   |

Example:

```csv
exe,game,exe_type,notes
SWEP1RCR.EXE,Star Wars Racer,dx9opengl,DirectX 8/9 OpenGL wrapper
hl2.exe,Half-Life 2,valve,Source Engine
Cyberpunk2077.exe,Cyberpunk 2077,dx12,DirectX 12
Battle.net.exe,Battle.net,dx11Bnet,Blizzard Launcher
```

## Available Profiles

| Profile       | Typical use                                       |
| ------------- | ------------------------------------------------- |
| `launcher`    | Game launchers                                    |
| `dx11`        | DirectX 10/11 games                               |
| `dx11Bnet`    | Battle.net launcher                               |
| `dx12`        | DirectX 12 games                                  |
| `dx9`         | DirectX 9 games                                   |
| `dx9opengl`   | Legacy DirectX 8/9 games using the OpenGL wrapper |
| `gtav_compat` | GTA V compatibility profile                       |
| `gtav_x11`    | GTA IV / GTA V optimized profile                  |
| `gtav_safe`   | GTA V safe profile                                |
| `oldgame`     | Very old Windows games                            |
| `valve`       | GoldSrc / Source Engine games                     |
| `ut3`         | Unreal Engine 3 games                             |
| `ut99`        | Unreal Tournament 99                              |
| `legacy`      | Legacy Windows applications                       |
| `desktop`     | Desktop utilities and applications                |

## Adding a New Game

Simply add a new line:

```csv
Game.exe,My Awesome Game,dx11,Works with DXVK
```

Submit a Pull Request and it can become part of the official database.

## Tips

* Use only the executable filename (not the full path).
* Profile names are case-sensitive.
* One executable per line.
* Keep notes short and informative.
* If a game has multiple executables, add one entry for each executable.

Community contributions help Proton-Autogen recognize more games and provide better default settings for everyone.
