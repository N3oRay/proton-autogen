# How to Use Proton Without Steam

Proton is best known as the compatibility layer used by Steam to run Windows games on Linux.

However, Proton itself can also be used outside the Steam client.

This distinction is useful because not every Windows application or game belongs in a Steam library.

## Proton and Steam are different things

A common misconception is:

```text
Proton = Steam
```

A more accurate model is:

```text
Steam
  ↓
manages
  ↓
Proton
```

Steam provides the user interface, library management, downloads, game configuration, and many other services.

Proton is the compatibility runtime used to execute Windows software.

This means that the runtime can be useful independently of the Steam client.

## Why run Proton without Steam?

There are several legitimate use cases.

For example:

- a Windows application downloaded directly from a vendor;
- a DRM-free game;
- an installer obtained outside Steam;
- a game from another store;
- a local `.exe`;
- testing a Windows application;
- development and compatibility testing.

In these cases, creating a Steam shortcut may not be the most natural workflow.

## The manual approach

Using Proton outside Steam generally requires identifying:

1. A Proton installation.
2. A Windows executable.
3. A `WINEPREFIX`.
4. The correct environment variables.
5. The correct Proton invocation.
6. Any application-specific arguments.

Conceptually:

```text
PROTON
WINEPREFIX
    +
EXE
    +
environment
    ↓
Proton
```

The details can vary between Proton distributions and versions.

This is one of the reasons why manual Proton usage is powerful but not particularly beginner-friendly.

## Prefixes

A prefix is the environment in which Proton/Wine stores Windows application state.

You can think of it as a lightweight, isolated Windows installation:

```text
Prefix
├── drive_c/
├── users/
├── Program Files/
└── configuration
```

The prefix is not a virtual machine.

It is a directory containing the Windows-compatible environment created by Wine/Proton.

## Why prefixes matter

Suppose two applications need different configurations.

Using a single prefix:

```text
Application A ─┐
               ├── Shared prefix
Application B ─┘
```

can create conflicts.

Using separate prefixes:

```text
Application A → Prefix A
Application B → Prefix B
```

provides much better isolation.

## Proton-Autogen

The purpose of Proton-Autogen is to remove much of this manual setup.

Instead of asking the user to understand every part of the Proton invocation, Proton-Autogen can manage the workflow:

```text
EXE
 ↓
detect application
 ↓
resolve runtime
 ↓
resolve profile
 ↓
create/reuse prefix
 ↓
construct environment
 ↓
launch
```

The user-facing action can therefore remain simple.

## Proton-Autogen is not a Steam replacement

It is important to understand the scope.

Proton-Autogen does not attempt to reproduce the Steam client.

It does not replace:

- Steam's store;
- Steam downloads;
- Steam Cloud;
- Steam achievements;
- Steam multiplayer services;
- Steam library management.

Instead, it focuses on the execution side of Windows applications.

## When Steam remains the better choice

Steam is usually the easiest option when:

- the game is available on Steam;
- you want Steam Cloud;
- you want Steam achievements;
- you need Steam's controller configuration;
- the game has Steam-specific integration.

There is no reason to avoid Steam simply because Proton can also operate outside it.

## When Proton-Autogen can make sense

Proton-Autogen is particularly interesting when your starting point is:

```text
I have a Windows executable.
I want to run it on Linux.
```

rather than:

```text
I have a Steam game.
```

That distinction defines the project's main use case.

## Conclusion

Using Proton without Steam is useful when you want the compatibility technology without the Steam client workflow.

Manual execution is possible, but managing runtimes, prefixes, and environment variables can become tedious.

Proton-Autogen aims to provide a simpler abstraction:

```text
Windows EXE
    ↓
Proton-Autogen
    ↓
Proton
    ↓
Linux
```

The goal is not to replace Steam.

It is to make Proton easier to use when Steam is not the application manager you want.
