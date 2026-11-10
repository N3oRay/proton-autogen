# Run Windows EXE Files on Linux

Many Windows `.exe` programs run on Linux without a virtual machine or a dual boot. Wine and Proton translate Windows API calls into Linux ones, and **Proton-Autogen** takes care of the setup around them: which Proton to use, which prefix, which environment variables, and which launch command.

## Quick start

1. **Install Proton-Autogen** (see the [installation guide](install.md) for all methods):

   ```bash
   # Arch Linux / CachyOS
   paru -S proton-autogen

   # Ubuntu / Linux Mint / Pop!_OS
   sudo add-apt-repository ppa:n3oray/proton-autogen
   sudo apt update
   sudo apt install proton-autogen
   ```

2. **Run your program** from a terminal:

   ```bash
   proton-autogen game.exe
   ```

   or right-click the `.exe` in Nautilus, Nemo or Dolphin and choose **Open with Proton-Autogen**.

3. **Prefer a window?** Start the graphical interface:

   ```bash
   proton-autogen --ux
   ```

You also need at least one Proton build (for example Proton-GE, Proton-CachyOS, or a Proton installed by Steam). If none is found, Proton-Autogen falls back to Wine when Wine is installed.

## Why Windows programs need a compatibility layer

A Windows program expects Windows APIs. Linux does not provide them natively, so Wine and Proton sit in between:

```text
Windows program  →  Wine / Proton  →  Linux
```

The `.exe` itself is rarely the problem. The work is in choosing the right runtime, giving the program a suitable prefix (its own "Windows" folder), and setting the right environment variables.

## Wine or Proton?

| | Wine | Proton |
|---|---|---|
| Typical use | Desktop applications, utilities, older software | Games, DirectX 9/11/12 programs |
| Graphics | Wine's own Direct3D, or DXVK if you add it | DXVK and VKD3D-Proton included |
| Manual command | `WINEPREFIX=~/.wine-app wine app.exe` | `proton run app.exe` with several `STEAM_COMPAT_*` variables |
| In Proton-Autogen | Used as a fallback, or forced with `--wine` | Default, or forced with `--proton` |

There is no universal winner: if a program misbehaves with one, try the other (`--wine` / `--proton`).

## What Proton-Autogen does when you run an EXE

```text
game.exe
   ↓
Find Proton installations
   ↓
Pick a Proton build
   ↓
Pick a profile (environment variables)
   ↓
Create or reuse a prefix
   ↓
Build the launch command
   ↓
Run
```

1. **Finds Proton builds** in the usual places: `compatibilitytools.d` folders of Steam (native and Flatpak), Steam's `steamapps/common`, and `/usr/share/steam/compatibilitytools.d`. Add your own folders in `~/.config/proton-autogen/proton-autogen.conf` (see [Proton Paths](PROTON_PATHS.md)).
2. **Picks a build automatically** by name: Proton-CachyOS first, then GE-Proton, then Proton Experimental, then other Proton builds. Within each group the highest version wins. You can override the choice per game.
3. **Picks a profile.** The executable name is looked up in the profile database (`profiles.csv`); if it is unknown, the program is analyzed to choose a suitable profile (DirectX 9, DirectX 11, DirectX 12, .NET, and so on). See [Profiles](profiles.md).
4. **Prepares the prefix** (see below).
5. **Builds the command.** Roughly, it is equivalent to:

   ```bash
   STEAM_COMPAT_DATA_PATH="$HOME/Documents/Proton/env/main" \
   STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.steam/steam" \
   /path/to/proton-build/proton run game.exe
   ```

   with the profile's environment variables added, and `gamemoderun` and/or `gamescope` in front when you enable them.
6. **Runs the program**, using the saved settings of the game when it has been registered with `add`.

## Prefixes

A prefix is the isolated Windows-like folder where a program stores its settings, installed components and data. Separate prefixes keep one program's changes from breaking another's.

| Mode | Option | Location |
|---|---|---|
| Main (default) | *(none)* | `~/Documents/Proton/env/main` |
| Shared | `--ps` | `~/Documents/Proton/env/shared` |
| Automatic, one per game | `--pa` | `~/Documents/Proton/env/<GameName>-<hash>` |
| Custom | `--pc` | `~/Documents/Proton/env/Proton Custom/` |

To store prefixes somewhere else, set `prefix_dir` in `~/.config/proton-autogen/proton-autogen.conf`:

```ini
[proton]
prefix_dir = ~/Games/prefixes
```

## Common commands

| Command | What it does |
|---|---|
| `proton-autogen game.exe` | Run a program with automatic Proton selection or its saved settings |
| `proton-autogen run game.exe` | Run without using the saved profile |
| `proton-autogen add game.exe` | Register a game and create its settings |
| `proton-autogen edit game.exe` | Edit a registered game's settings |
| `proton-autogen --ux` | Graphical interface (GTK4) |
| `proton-autogen --list-protons` | List the Proton builds that were found |
| `proton-autogen game.exe --profile dx11` | Force a profile |
| `proton-autogen --diag` | Print a diagnostic report |
| `proton-autogen --help-env` | Help about environment variables |

Optional performance tools are only used if they are installed:

```bash
proton-autogen game.exe --mangohud               # FPS and frame-time overlay
proton-autogen game.exe --gamemode               # GameMode optimizations
proton-autogen game.exe --gamescope              # Gamescope micro-compositor
proton-autogen game.exe --gamemode --mangohud    # combine them
```

## Troubleshooting

If a program does not start, go through these steps in order:

1. **Generate a diagnostic report**, then read it for missing tools and detected paths:

   ```bash
   proton-autogen --diag
   ```

2. **Check that a Proton build is found:**

   ```bash
   proton-autogen --list-protons
   ```

   `No Proton installation found` means there is no Proton in the searched folders. Install one (for example Proton-GE) or add its folder in `proton-autogen.conf` ([Proton Paths](PROTON_PATHS.md)).

3. **Run again with more output:**

   ```bash
   proton-autogen game.exe --debug --verbose
   ```

   Logs are written to `~/.local/share/proton-autogen/logs/`.

4. **Try the other runtime:** `--wine` or `--proton`.
5. **Try a fresh prefix** with `--pa`, in case the shared one is in a bad state.
6. **Try another profile** with `--profile` (for example `dx9`, `dx11` or `dx12` for the matching DirectX version).
7. **Check the basics:** an up-to-date GPU driver, Vulkan support (`vulkaninfo --summary`), and the program's architecture (`file game.exe` shows whether it is 32-bit or 64-bit).

Not every Windows program works with Wine or Proton. Software that depends on kernel-level anti-cheat or on Windows-only drivers is the most likely to fail. For games with a Steam page, [ProtonDB](https://www.protondb.com) reports what works for other players.

## FAQ

**Do I need Steam?**
Proton-Autogen does not need Steam shortcuts. It does need a Proton build, and those are usually installed in Steam-related folders. See [Proton Without Steam](proton-without-steam.md).

**Can I run an installer (`setup.exe`)?**
Yes, it is launched like any other `.exe`. Once the installation is done, launch the installed program the same way, and keep using the same prefix so it finds its files.

**Where are my settings stored?**
Under `~/.config/proton-autogen/`: registered games are in `games/`, the main configuration in `proton-autogen.conf`, and your profile overrides in `profiles.csv`.

**What if Proton and Wine are both missing?**
Install one of them. The Wine fallback prints distribution-specific installation commands when `wine` is not found.

## Related documentation

- [Installation](install.md)
- [Run Windows Games with Proton](run-windows-games-with-proton.md)
- [Proton Without Steam](proton-without-steam.md)
- [Proton Prefix Guide](proton-prefix-guide.md)
- [Proton Paths](PROTON_PATHS.md)
- [Profiles](profiles.md)
- [Examples](examples.md)
