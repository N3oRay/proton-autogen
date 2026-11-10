# ✨ Proton-Autogen Features

Proton-Autogen launches Windows applications and games on Linux through Proton or Wine, with as little manual configuration as possible. It detects the runtime, prepares the prefix and the environment, and gives you a command line, a graphical interface and file-manager integration to manage your programs.

> The goal: **launch Windows applications on Linux without manually configuring every application.**

## At a glance

- ▶ Run any Windows `.exe` with Proton, with Wine as a fallback
- 🧠 Automatic detection of Proton, Proton-GE, Proton-CachyOS and custom builds
- 📦 Prefix management (main, shared, or one per game)
- 🎮 18 built-in profiles plus a community profile database
- 🖥️ GTK4 interface: list, grid and cover-library views, drag and drop, 19 themes, 20 languages
- ⚙️ Per-game editor: GPU mode, MangoHud, GameMode, Gamescope, custom environment variables
- 📥 Import from Lutris, Bottles, Heroic and existing Wine prefixes
- 💾 Save detection and ZIP backups at the end of a session
- 🛠️ Diagnostics, logs and a catalog of 121 documented environment variables

## 📋 Table of Contents

- [Launching Windows programs](#-launching-windows-programs)
- [Proton detection and selection](#-proton-detection-and-selection)
- [Prefix management](#-prefix-management)
- [Profiles](#-profiles)
- [Graphical interface](#-graphical-interface)
- [Per-game editor](#-per-game-editor)
- [Performance tools](#-performance-tools)
- [Running games and sessions](#-running-games-and-sessions)
- [Save management](#-save-management)
- [Importing and discovering programs](#-importing-and-discovering-programs)
- [Steam AppID and ProtonDB](#-steam-appid-and-protondb)
- [Environment variables](#-environment-variables)
- [Desktop integration](#-desktop-integration)
- [Diagnostics and logs](#-diagnostics-and-logs)
- [Command-line reference](#-command-line-reference)
- [Installation and packaging](#-installation-and-packaging)

---

## ▶ Launching Windows programs

```bash
proton-autogen /path/to/application.exe
```

Proton-Autogen picks a Proton build, prepares the prefix and the environment variables, then starts the program. No Steam shortcut is needed.

| Command | Purpose |
|---|---|
| `proton-autogen game.exe` | Run, using the saved settings of the game when it is registered |
| `proton-autogen run game.exe` | Run without applying the saved profile |
| `proton-autogen add game.exe` | Register a game and create its settings |
| `proton-autogen edit game.exe` | Edit the settings of a registered game |

If no Proton build is available, Proton-Autogen falls back to Wine. If Wine is missing too, it prints installation commands for your distribution. Force a runtime with `--proton` or `--wine`.

Compatibility depends on the program, the runtime and your system. Not every Windows program works with Wine or Proton.

See also: [Run EXE on Linux](run-exe-on-linux.md).

## 🧠 Proton detection and selection

Proton-Autogen searches for Proton builds in the usual places:

- Steam `compatibilitytools.d` folders (native and Flatpak Steam)
- Steam `steamapps/common`
- `/usr/share/steam/compatibilitytools.d`
- any folder you add in `~/.config/proton-autogen/proton-autogen.conf`

Supported builds include **GE-Proton**, **Proton-CachyOS**, Proton Experimental, Valve's Proton and custom builds.

When you do not choose a build yourself, the selection is automatic: Proton-CachyOS first, then GE-Proton, then Proton Experimental, then other Proton builds, and the highest version within each group. You can pick a specific build per game in the editor.

```bash
proton-autogen --list-protons     # builds that were found
proton-autogen --proton-paths     # folders that are searched
```

See [Proton Paths](PROTON_PATHS.md).

## 📦 Prefix management

A prefix is the isolated Windows-like folder where a program stores its settings and data. Separate prefixes keep applications from interfering with each other.

| Mode | Option | Location |
|---|---|---|
| Main (default) | *(none)* | `~/Documents/Proton/env/main` |
| Shared | `--ps` | `~/Documents/Proton/env/shared` |
| Automatic, one per game | `--pa` | `~/Documents/Proton/env/<GameName>-<hash>` |
| Custom | `--pc` | `~/Documents/Proton/env/Proton Custom/` |

The root folder can be changed with `prefix_dir` in `proton-autogen.conf` or in the settings panel of the graphical interface. Back up your data before deleting or recreating a prefix.

See [Proton Prefix Guide](proton-prefix-guide.md).

## 🎮 Profiles

A profile is a tested set of environment variables and options for a type of application. Proton-Autogen chooses one automatically, in this order:

1. The community profile database (`profiles.csv`), matched on the executable name.
2. An analysis of the program itself: its architecture and the DLLs it imports.
3. Name-based heuristics.

Built-in profiles: `legacy`, `launcher`, `desktop`, `dx8dg`, `dx9`, `dx9opengl`, `dx11`, `dx11Bnet`, `dx12`, `dotnet`, `dotnet_csharp`, `gtav_compat`, `gtav_x11`, `gtav_safe`, `oldgame`, `ut3`, `ut99` and `valve`.

Some profiles do more than set variables:

- **Older DirectX games**: the needed DLL wrappers (`ddraw`, `d3d8`, `d3d9`, `dsound`) are installed, taken from the Proton in use first and from a wrapper bundled with Proton-Autogen otherwise.
- **.NET applications**: dedicated profiles, including detection of RAGE:MP and FiveM.

Force a profile for one launch with `--profile`:

```bash
proton-autogen game.exe --profile dx11
```

Your own entries go in `~/.config/proton-autogen/profiles.csv` and override the system database. See [Profiles](profiles.md).

## 🖥️ Graphical interface

```bash
proton-autogen --ux
```

- **Three views of your games**: list, grid, and a cover library with one portrait (2:3) cover per game. The grid and the library can be zoomed.
- **Recent games carousel**, **favorites** (★ filter) and a **search box** that looks through names, paths and profiles.
- **Drag and drop**: drop one or several `.exe` files on the window to register them. Other file types are ignored, and games that already have a configuration are left untouched.
- **Context menu** on each game (right click, the Menu key or Shift+F10), plus a window listing the **keyboard shortcuts**.
- **Status history** and desktop-style toasts for the result of each action.
- **Settings panel**: theme, language (applied at the next launch), remembered window size, custom Proton folders, prefix root folder, automatic scan of new applications, and reduced visual effects.
- **19 themes** and **20 languages** (translations are checked with `proton-autogen --check-translations`).
- **Reduced visual effects** lowers CPU usage by softening the shadows of repeated elements.
- **Switch-style toggles** in the game editor when libadwaita 1.4 or newer is installed; otherwise regular check boxes are used.

The command line stays fully available for terminal workflows.

## ⚙️ Per-game editor

Each registered game has its own settings, stored as JSON in `~/.config/proton-autogen/games/`:

- profile, Proton build and prefix mode
- GPU mode: `auto`, `safe`, `balanced`, `performance` or `extreme`
- Steam AppID, with a ProtonDB shortcut
- cover image for the library view
- favorite flag
- MangoHud (with an FPS limit), GameMode and Gamescope
- sleep inhibition and the end-of-session save prompt
- **custom environment variables** (one `KEY=VALUE` per line); known variables are highlighted so typos stand out. They are applied last, so they can deliberately override computed values.

## 🚀 Performance tools

Optional tools are used only when they are installed:

| Tool | Option | Effect |
|---|---|---|
| MangoHud | `--mangohud` | FPS, frame time and performance overlay |
| GameMode | `--gamemode` | Host performance optimizations while the game runs |
| Gamescope | `--gamescope` | Micro-compositor: internal resolution, refresh rate, display options |

The dashboard can also **apply a recommended MangoHud configuration**. Your existing `~/.config/MangoHud` is saved first and can be restored with one click.

## ⏱️ Running games and sessions

- **Running games are tracked across processes**: a game started from the terminal also shows up in the graphical window, which can follow it.
- **Launch detection**: the launch dialog closes when the application has actually opened a window, instead of after a fixed delay. Without X11 support it falls back to a CPU-activity heuristic.
- **Compact mode while playing**: the main window is minimized and a persistent notification takes over. Clicking it restores the window, and the window is restored automatically when the game exits.
- **Sleep inhibition**: the screen stays on and the machine does not suspend during a game. Choose *never*, *always* (default) or *per game* in the settings.
- **Statistics**: playtime, last launch and "recent" badges per game, plus a ProtonDB rating badge when available.

## 💾 Save management

Proton-Autogen finds save games with three complementary strategies, without a per-game path database:

1. Save files next to the game executable (for example `SAVEGAME.000`).
2. Save folders a few levels under the install folder, recognized by name (for example `SAVE`, `SAVEGAME`).
3. Standard Windows locations inside the prefix: *Saved Games*, *Documents/My Games*, *AppData/Local* and *AppData/Roaming*.

At the end of a session it can offer a **ZIP backup** of the detected saves, which you can turn off per game. A **Memory** button in the game editor opens the backup manager for that game, to back up on demand or to find earlier backups.

## 📥 Importing and discovering programs

- **Import existing installations** from **Lutris**, **Bottles**, **Heroic** (native and Flatpak versions) and plain Wine prefixes. Steam is intentionally excluded because Steam manages its own games.

  ```bash
  proton-autogen --import
  ```

  The command lists what it found and asks for confirmation. The same import is available in the graphical interface.
- **Automatic scan** for new Windows applications, with folders that are always skipped. The scan can be turned off in the settings. See `scan-excludes.example.txt` in this folder.
- **Shortcuts**: create a `.desktop` entry for a game, either in the application menu or on the desktop.

```bash
proton-autogen --list-programs    # registered programs
proton-autogen --json-profile     # export environment profiles as JSON
```

## 🆔 Steam AppID and ProtonDB

- The Steam AppID of a game is detected automatically, and from a table of known executables as a last resort. It sets `STEAM_COMPAT_APP_ID`, `SteamAppId` and `SteamGameId`, which some launchers, overlays and shader caches need. You can also enter it by hand.
- With an AppID, the **ProtonDB** rating is fetched, cached and shown as a badge in the game list; a button opens the game's ProtonDB page. ProtonDB is optional: without a network connection everything else keeps working.

## 🔧 Environment variables

Proton-Autogen documents **121 Proton, Wine, DXVK, VKD3D and Wayland variables**, with a description in each supported language:

```bash
proton-autogen --help-env
```

Per-game custom variables are set in the editor (see above).

## 🖱️ Desktop integration

Right-click a Windows executable and choose **Open with Proton-Autogen** in:

- **Nautilus** (GNOME), through the `python-nautilus` extension
- **Nemo** (Cinnamon)
- **Dolphin** (KDE Plasma)

Proton-Autogen also ships a desktop entry and icon, and works under Flatpak, where host commands are run outside the sandbox.

## 🛠️ Diagnostics and logs

```bash
proton-autogen --diag
```

The report covers detected runtimes and tools and is meant to be attached to bug reports. Review it before sharing, since it can contain local paths. See [Examples](examples.md).

Add `--debug` or `--verbose` to any launch for more output. Logs are written to `~/.local/share/proton-autogen/logs/`.

## ⌨️ Command-line reference

| Option | Purpose |
|---|---|
| `<file.exe>`, `run`, `add`, `edit` | Launch and manage programs |
| `--ux` | Graphical interface |
| `--import` | Import existing Lutris, Bottles, Heroic and Wine installations |
| `--list-programs` | List registered programs |
| `--list-protons` | List detected Proton builds |
| `--proton-paths` | Show the searched Proton folders |
| `--profile <name>` | Use a profile for this launch |
| `--json-profile` | Export all environment profiles as JSON |
| `--proton`, `--wine`, `--call` | Choose the runtime (`--call` uses Proton-Call) |
| `--ps`, `--pa`, `--pc` | Shared, automatic or custom prefix |
| `--mangohud`, `--gamemode`, `--gamescope` | Enable optional tools |
| `--debug`, `--verbose` | More output |
| `--diag` | Diagnostic report |
| `--help`, `--help-env` | Help and environment-variable catalog |
| `--about`, `--v` / `--version` | About and version |
| `--check-translations` | Check that all translations are complete |

## 📦 Installation and packaging

- **Arch Linux / CachyOS**: AUR (`paru -S proton-autogen`)
- **Ubuntu / Linux Mint / Pop!_OS**: official PPA (`ppa:n3oray/proton-autogen`)
- **Debian and derivatives**: `.deb` package
- **Fedora**: see the [Fedora installation guide](fedora-install.md)
- **Flatpak**: see the [Flatpak guide](INSTALL_FLATPAK.md)
- **From source**: `install.sh`

See the [Installation Guide](install.md) for details.

---

## 💡 Project philosophy

Linux offers powerful tools for running Windows applications, but configuring them can be needlessly complicated. Proton-Autogen builds on the Proton and Wine you already have, adding runtime detection, profiles, desktop integration and diagnostics.

**Less manual configuration. A simpler workflow. More control over how Windows applications run on Linux.**

## Related documentation

- [Installation](install.md)
- [Examples](examples.md)
- [Profiles](profiles.md)
- [Proton Paths](PROTON_PATHS.md)
- [Run EXE on Linux](run-exe-on-linux.md)
- [Architecture](ARCHITECTURE.md)
