# Proton-Autogen — Flatpak Installation

This document explains how to build, install, and run Proton-Autogen as a Flatpak from source.

Note: Proton-Autogen is currently being prepared for Flathub. Until it is available there, the application can be built locally using flatpak-builder.

# Requirements

Make sure the following packages are installed:

Flatpak
flatpak-builder
GNOME SDK and runtime

Proton-Autogen currently uses:
```bash
org.gnome.Platform
org.gnome.Sdk
runtime-version: 49
```
# Install Flatpak and flatpak-builder
# Debian / Ubuntu
```bash
sudo apt install flatpak flatpak-builder
```
# Fedora
```bash
sudo dnf install flatpak flatpak-builder
```
# Arch Linux
```bash
sudo pacman -S flatpak flatpak-builder
```
# Install the GNOME Runtime and SDK

Install the GNOME 49 runtime:
```bash
flatpak install flathub org.gnome.Platform//49
```

Install the GNOME 49 SDK:
```bash
flatpak install flathub org.gnome.Sdk//49
```

If Flathub is not configured yet:
```bash
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```
# Build and Install

Clone the Proton-Autogen repository:
```bash
git clone https://github.com/N3oRay/proton-autogen.git
cd proton-autogen
```

Build and install the Flatpak:
```bash
flatpak-builder --user --install --force-clean \
    build-dir io.github.N3oRay.ProtonAutogen.yml

```
The application is now installed for the current user.

# Run Proton-Autogen
# Graphical Interface

Launch the GTK4 interface:

flatpak run io.github.N3oRay.ProtonAutogen --ux

# Command Line

Display the help:
```bash
flatpak run io.github.N3oRay.ProtonAutogen --help
```

Launch a Windows executable:
```bash
flatpak run io.github.N3oRay.ProtonAutogen game.exe
```

For example:
```bash
flatpak run io.github.N3oRay.ProtonAutogen ~/Games/MyGame/game.exe
```
# Terminal Alias

To avoid typing the full Flatpak command every time, you can create a proton-autogen alias.

After creating the alias, you can use:
```bash
proton-autogen game.exe
```

instead of:
```bash
flatpak run io.github.N3oRay.ProtonAutogen game.exe
```
# Fish

For the Fish shell:
```bash
alias proton-autogen 'flatpak run io.github.N3oRay.ProtonAutogen'
```

You can then use:
```bash
proton-autogen --help
proton-autogen --ux
proton-autogen game.exe
```
# Make the Fish Alias Permanent

Add the following line to:
```bash
~/.config/fish/config.fish
```
```bash
alias proton-autogen 'flatpak run io.github.N3oRay.ProtonAutogen'
```

Then reload the configuration:
```bash
source ~/.config/fish/config.fish
```
# Bash

For the Bash shell:
```bash
alias proton-autogen='flatpak run io.github.N3oRay.ProtonAutogen'
```

You can then use:
```bash
proton-autogen --help
proton-autogen --ux
proton-autogen game.exe
```
# Make the Bash Alias Permanent

Add the following line to:
```bash
~/.bashrc
```
```bash
alias proton-autogen='flatpak run io.github.N3oRay.ProtonAutogen'
```

Then reload the configuration:
```bash
source ~/.bashrc
```
# Zsh

For the Zsh shell:
```bash
alias proton-autogen='flatpak run io.github.N3oRay.ProtonAutogen'
```

You can then use:
```bash
proton-autogen --help
proton-autogen --ux
proton-autogen game.exe
```
# Make the Zsh Alias Permanent

Add the following line to:
```bash
~/.zshrc
```
```bash
alias proton-autogen='flatpak run io.github.N3oRay.ProtonAutogen'
```

Then reload the configuration:
```bash
source ~/.zshrc
```
# Common Commands

Once the alias has been configured, the following commands are available.

# Display Help
proton-autogen --help

# Launch the Graphical Interface
proton-autogen --ux

# Launch a Windows Program
proton-autogen game.exe

# Add a Game Profile
proton-autogen add game.exe

# Edit a Game Profile
proton-autogen edit game.exe

# Run Without the Saved Profile
proton-autogen run game.exe

# Flatpak Permissions

Proton-Autogen needs access to Windows executables, Proton installations, Steam libraries, Wine prefixes, and game data located on the host system.

The Flatpak manifest therefore provides the required filesystem access:
```bash
- --filesystem=host
```

Proton and Wine processes are executed on the host through:
```bash
flatpak-spawn --host
```

This allows Proton-Autogen to use the host's Proton/Wine environment while the main application remains a Flatpak application.

# Rebuild the Flatpak

After modifying the source code, rebuild the application with:
```bash
flatpak-builder --user --install --force-clean \
    build-dir io.github.N3oRay.ProtonAutogen.yml
```

The --force-clean option cleans the build directory before rebuilding.

# Remove the Local Installation

To uninstall the locally installed Flatpak:
```bash
flatpak uninstall --user io.github.N3oRay.ProtonAutogen
```

To remove the application and its stored data:
```bash
flatpak uninstall --user --delete-data io.github.N3oRay.ProtonAutogen
```
# Troubleshooting
# Check the Installed Application
```bash
flatpak list | grep Proton
```
# Check Application Information
```bash
flatpak info io.github.N3oRay.ProtonAutogen
```
# Test the Graphical Interface
```bash
flatpak run io.github.N3oRay.ProtonAutogen --ux
```
# Test the CLI
```bash
flatpak run io.github.N3oRay.ProtonAutogen --help
```

# Run with Flatpak Debug Output
```bash
flatpak run --verbose io.github.N3oRay.ProtonAutogen --help
```
# Flathub

Proton-Autogen is being prepared for publication on Flathub.

Once available on Flathub, the application will be installable directly from the Flathub repository without requiring a local build.

The Flatpak application ID is:

io.github.N3oRay.ProtonAutogen

# Summary
# Build
```bash
flatpak-builder --user --install --force-clean \
    build-dir io.github.N3oRay.ProtonAutogen.yml
```
# Run the UX
```bash
flatpak run io.github.N3oRay.ProtonAutogen --ux
```

# Run a Windows executable
```bash
flatpak run io.github.N3oRay.ProtonAutogen game.exe
```
# Bash / Zsh Alias
```bash
alias proton-autogen='flatpak run io.github.N3oRay.ProtonAutogen'
```

# Fish Alias
```bash
alias proton-autogen 'flatpak run io.github.N3oRay.ProtonAutogen'
```

After configuring the alias:
```bash
proton-autogen --ux
proton-autogen game.exe
proton-autogen add game.exe
proton-autogen edit game.exe
proton-autogen --help
```
