## ✨ Features

* ▶ Run Windows `.exe` files directly via Proton
* 🧠 Automatic Proton detection
* 🚀 Support for Proton-CachyOS, GE-Proton and custom Proton builds
* 🍷 Wine fallback support
* 📦 Prefix management
* 🖱️ File manager integration : Nemo, Nautilus, Dolphin
* 🎮 Game/application profiles
* 🖥️ GTK4 graphical interface
* 🛠️ Diagnostic tools
* ⚙️ CLI and advanced options
* 🔧 Lightweight and dependency-minimal



# ✨ Proton-Autogen Features

Proton-Autogen is a lightweight Linux utility designed to simplify launching Windows applications and games through Proton or Wine.

It automates runtime detection, reduces manual configuration, integrates with Linux file managers, and provides both graphical and command-line interfaces.

The goal is simple: **launch Windows applications on Linux without manually configuring every application.**

## 📋 Table of Contents

- Windows Executable Launching
- Automatic Proton Detection
- Multiple Proton Builds
- Wine Fallback
- Prefix Management
- File Manager Integration
- Application Profiles
- GTK4 Graphical Interface
- Diagnostic Tools
- Command-Line Interface
- Lightweight Design
- Getting Started

---

## ▶ Windows Executable Launching

Launch Windows `.exe` files directly from your Linux desktop or terminal.

Proton-Autogen helps remove the need to manually create Steam shortcuts just to start an executable.

**Example:**

```
proton-autogen /path/to/application.exe
```

Typical workflow:

1. Select a Windows executable.
2. Launch it through Proton-Autogen.
3. Let the application handle the available runtime configuration.
4. Troubleshoot launch problems with the diagnostic tools if necessary.

Compatibility depends on the application, runtime, and system configuration. Not every Windows program will work correctly.

## 🧠 Automatic Proton Detection

Proton-Autogen detects available Proton installations so you do not have to manually specify a runtime path for every launch.

This is particularly useful for users who maintain multiple Proton versions.

Benefits include:

- Less manual runtime configuration.
- Easier use of custom Proton installations.
- A simpler launch workflow.
- Reduced friction when switching between supported runtime environments.

## 🚀 Multiple Proton Builds

Proton-Autogen supports working with different Proton builds, including:

- **GE-Proton** — a community-maintained Proton build.
- **Proton-CachyOS** — a Proton variant associated with CachyOS.
- **Custom Proton builds** — compatible installations available on your system.

Different applications may behave differently depending on the Proton version used.

For best results, keep your preferred runtime updated and consult the relevant application's documentation when troubleshooting compatibility problems.

## 🍷 Wine Fallback

Proton-Autogen also supports Wine as a fallback when the required Proton runtime tools are unavailable.

This provides an alternative execution path for compatible Windows applications.

Wine and Proton have different configurations and compatibility characteristics. A fallback does not guarantee that an application will launch successfully.

## 📦 Prefix Management

Wine prefixes and Proton compatibility environments isolate application-specific configuration and Windows-related files.

Proton-Autogen includes prefix management capabilities intended to simplify this aspect of running Windows software on Linux.

Depending on the application's requirements, separate environments can help prevent configuration conflicts between applications.

**Important:** back up application data and existing prefixes before performing operations that modify or remove them.

For implementation details and available options, consult the installation guide and profile documentation.

## 🖱️ File Manager Integration

Launch Windows executables directly from supported Linux file managers.

Supported integrations include:

- **Nemo** — commonly used with Cinnamon.
- **Nautilus** — commonly used with GNOME.
- **Dolphin** — commonly used with KDE Plasma.

The intended workflow is straightforward:

1. Open the folder containing a Windows `.exe` file.
2. Right-click the executable.
3. Select **Open with Proton-Autogen**, when the integration is installed.
4. Follow the application's launch workflow.

This integration brings Windows application launching closer to the normal Linux desktop experience.

## 🎮 Application Profiles

Proton-Autogen supports application and game profiles to organize application-specific settings.

Profiles can help keep launch configuration associated with individual applications rather than repeatedly configuring the same options.

This is useful when working with several applications that have different runtime or configuration requirements.

See the profile documentation for examples of generated profile data.

## 🖥️ GTK4 Graphical Interface

Proton-Autogen includes a graphical interface built with GTK4.

The graphical interface provides an alternative to launching and managing the utility entirely through a terminal.

Start the interface with:

```
proton-autogen --ux
```

The command-line interface remains available for users who prefer terminal-based workflows.

## 🛠️ Diagnostic Tools

When an application fails to launch, diagnostic information can help identify configuration or runtime problems.

Generate a diagnostic report with:

```
proton-autogen --diag
```

Diagnostic reports can be useful when investigating:

- Missing or unavailable runtime components.
- Proton or Wine launch failures.
- Environment configuration problems.
- Issues that need further investigation before opening a bug report.

When reporting an issue, include the relevant diagnostic output and the steps needed to reproduce the problem. Review reports before sharing them publicly, especially if they contain local paths or other personal information.

See the examples documentation for sample output.

## ⚙️ Command-Line Interface

Proton-Autogen provides command-line entry points for common tasks.

| Command | Purpose |
| --- | --- |
| `proton-autogen /path/to/application.exe` | Launch a Windows executable |
| `proton-autogen --ux` | Open the graphical interface |
| `proton-autogen --diag` | Generate diagnostic information |

These commands provide a convenient starting point for desktop use, troubleshooting, and terminal-based workflows.

Consult the project's help output and documentation for additional options supported by your installed version.

## 🔧 Lightweight Design

Proton-Autogen is designed to automate common tasks without requiring users to configure every launch manually.

It builds on the Proton and Wine environments already available on Linux systems rather than replacing them with a separate Windows installation.

Python dependencies and system requirements still apply. See the main README for installation instructions and prerequisites.

---

## 🚀 Getting Started

Ready to try Proton-Autogen?

1. Follow the installation instructions.
2. Make sure a compatible Proton installation or Wine environment is available.
3. Launch a Windows executable from your file manager or terminal.
4. Open the graphical interface with `proton-autogen --ux` if needed.
5. Use `proton-autogen --diag` if you encounter problems.

### Related Documentation

- Main README — project overview and installation options.
- Installation Guide — installation and setup.
- Profiles — profile examples and configuration.
- Examples — diagnostic output examples.

---

## 💡 Project Philosophy

Linux offers powerful tools for running Windows applications, but configuring and managing them can be unnecessarily complicated.

Proton-Autogen aims to make this process more accessible through runtime detection, desktop integration, application profiles, and diagnostic tools.

**Less manual configuration. A simpler workflow. More control over how Windows applications run on Linux.**


