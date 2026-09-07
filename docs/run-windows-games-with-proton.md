# Run Windows Games on Linux with Proton

Proton makes it possible to run many Windows games on Linux without installing Windows.

For Steam users, Proton is largely invisible: Steam manages the runtime, prefix, launch configuration, and game integration.

The situation becomes more complicated when you want to run a Windows game that is not installed through Steam.

This guide explains the basic architecture and how Proton-Autogen can simplify that workflow.

## What is Proton?

Proton is a compatibility layer built around Wine and additional technologies designed primarily for Windows games.

A simplified stack looks like this:

```text
Windows game
     ↓
   Proton
     ↓
 Wine compatibility layer
     ↓
DXVK / VKD3D-Proton
     ↓
    Linux
```

Depending on the game, Proton can translate:

- Direct3D 9 through DXVK;
- Direct3D 10/11 through DXVK;
- Direct3D 12 through VKD3D-Proton;
- Windows API calls through Wine.

## Why games need more than just Wine

Games frequently depend on technologies that are not present in a basic Wine installation.

Examples include:

- DirectX;
- Vulkan;
- Windows libraries;
- launchers;
- anti-cheat systems;
- game-specific environment variables;
- controller support;
- performance overlays.

Proton bundles and integrates many of the components required by modern games.

## Running a non-Steam game with Proton

Steam can be used to launch some non-Steam Windows games by adding them as a non-Steam game.

This works, but it has an important consequence:

```text
Windows game
      ↓
Steam shortcut
      ↓
Steam Proton
```

For users who simply want to run an `.exe`, this can introduce an unnecessary layer.

You may have to:

1. Add the executable to Steam.
2. Open the game's properties.
3. Force a Proton version.
4. Configure launch options.
5. Determine where Steam created the prefix.
6. Troubleshoot the game from there.

This is useful for many users, but it is not the only possible workflow.

## Proton-Autogen

Proton-Autogen is intended to make Proton usable as a more transparent execution layer.

The conceptual workflow is:

```text
game.exe
   ↓
Proton-Autogen
   ↓
Application detection
   ↓
Runtime selection
   ↓
Prefix management
   ↓
Environment configuration
   ↓
Game launch
```

This is particularly useful when the desired interaction is simply:

> "I have a Windows game. Run it."

rather than:

> "I want to create and maintain a Steam shortcut for this executable."

## Proton versions

Different games can behave differently depending on the Proton version.

Possible runtimes include:

- Valve Proton;
- Proton Experimental;
- GE-Proton;
- Wine-based fallbacks where appropriate.

There is no single Proton version that is optimal for every game.

For this reason, runtime selection should be treated as part of compatibility management rather than a permanent universal setting.

## Prefixes

A Proton prefix contains the Windows environment used by a game.

Conceptually:

```text
Game A
  ↓
Prefix A

Game B
  ↓
Prefix B
```

Keeping applications isolated can prevent changes made for one game from affecting another.

## Performance tools

Linux gaming often involves additional tools such as:

- GameMode;
- MangoHud;
- Gamescope.

These are optional layers around the application rather than requirements of Proton itself.

A typical stack might look like:

```text
Gamescope
    ↓
GameMode
    ↓
MangoHud
    ↓
Proton
    ↓
Windows game
```

Proton-Autogen can help manage these options when they are part of the application's configuration.

## Compatibility limitations

Proton does not guarantee that every Windows game will work.

Common obstacles include:

### Anti-cheat

Some anti-cheat systems require explicit support from the game developer.

### DRM

Certain DRM implementations may not function correctly under Wine/Proton.

### Launchers

A game may depend on a separate Windows launcher.

### Hardware-specific behavior

GPU drivers and Vulkan support can have a significant impact on compatibility.

## A useful mental model

Think of Proton as the compatibility layer and Proton-Autogen as the automation layer around it.

```text
                  Proton-Autogen
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
       Runtime        Prefix       Environment
          │             │             │
          └─────────────┼─────────────┘
                        ↓
                      Proton
                        ↓
                    Windows game
```

This separation is important.

Proton-Autogen does not replace Proton. It attempts to make using Proton outside traditional Steam workflows easier.

## Conclusion

Proton has dramatically improved Windows gaming on Linux.

The next usability problem is configuration.

If you want to launch Windows games without manually managing every Proton command, prefix, and environment setting, Proton-Autogen provides an automated workflow around the existing Proton ecosystem.
````
