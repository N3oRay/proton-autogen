# Proton Prefix Guide

If you use Proton or Wine outside a managed Steam workflow, you will eventually encounter the concept of a **prefix**.

Prefixes are fundamental to running Windows applications on Linux, but they are often misunderstood.

## What is a prefix?

A prefix is a directory containing a Windows-compatible environment managed by Wine or Proton.

A simplified prefix might look like:

```text
prefix/
├── drive_c/
│   ├── Program Files/
│   ├── Program Files (x86)/
│   └── users/
├── dosdevices/
└── configuration
```

The exact layout depends on the Wine/Proton implementation and configuration.

## A prefix is not a virtual machine

A Proton prefix does not contain a complete Windows operating system.

It contains the files and configuration needed to provide a Windows-like environment to applications.

The application still runs through the Linux compatibility stack.

```text
Windows application
       ↓
    Proton/Wine
       ↓
     Prefix
       ↓
      Linux
```

## Why use prefixes?

Prefixes provide isolation.

Imagine two applications:

```text
Game A → DXVK configuration
Game B → different configuration
```

Putting both into one environment can lead to conflicts.

Separate prefixes provide:

```text
Game A → Prefix A
Game B → Prefix B
```

Each application can then have its own:

- installed components;
- registry settings;
- DLLs;
- Windows version configuration;
- environment;
- application data.

## Steam prefixes

Steam normally manages Proton prefixes automatically.

They are associated with individual Steam applications.

This is convenient because the user usually does not have to think about them.

The situation changes when running Proton outside Steam.

You may need to create and maintain prefixes yourself.

## Manual prefix management

A common Wine workflow is:

```bash
WINEPREFIX="$HOME/.wine-myapp" wine application.exe
```

The `WINEPREFIX` variable tells Wine which prefix to use.

Proton has its own invocation conventions and environment requirements, so commands should be based on the particular Proton distribution being used.

## Prefix lifecycle

A useful way to think about prefixes is:

```text
Create
  ↓
Configure
  ↓
Install application
  ↓
Run
  ↓
Update
  ↓
Backup / remove
```

A prefix is stateful.

Changing it can affect future application launches.

## Why prefixes sometimes become problematic

A prefix can accumulate configuration over time.

For example:

```text
Application
   ↓
Installer
   ↓
DLL override
   ↓
Runtime update
   ↓
Additional component
   ↓
Configuration change
```

Eventually it may become difficult to understand why an application works or fails.

This is one reason isolated prefixes are useful.

## Prefixes and application profiles

An application profile can describe how an application should be launched.

Conceptually:

```text
Application profile
       │
       ├── Runtime
       ├── Environment
       ├── Prefix
       └── Launch options
```

This separates the application's desired configuration from the underlying execution mechanism.

## Proton-Autogen and prefixes

One of Proton-Autogen's goals is to make prefix management less visible to the user.

Instead of requiring the user to manually decide:

```text
Where should the prefix live?
Should I create one?
Which runtime should use it?
Which environment should it have?
```

the launcher can manage the prefix as part of the application configuration.

The intended workflow is:

```text
EXE
 ↓
Application configuration
 ↓
Prefix resolution
 ↓
Create or reuse
 ↓
Launch
```

## Should every application have its own prefix?

There is no universal rule.

Dedicated prefixes are generally useful when:

- applications require conflicting configurations;
- you want isolation;
- you are troubleshooting;
- you want reproducible environments;
- you want to remove an application cleanly.

Shared environments can sometimes be useful, but they increase the possibility of configuration conflicts.

## Backing up a prefix

A prefix contains application state, so it can be valuable to back it up.

Before modifying a working prefix, consider making a copy or snapshot.

For large prefixes, filesystem snapshots or archive tools may be more appropriate.

## Do not blindly delete prefixes

Deleting a prefix can remove:

- installed Windows applications;
- application settings;
- save data stored inside the prefix;
- registry configuration;
- downloaded components.

Before deleting one, check where the application's data is stored.

Some games also store saves outside the prefix.

## Troubleshooting a broken prefix

When an application suddenly stops working, the prefix is one of the first things worth investigating.

Useful questions include:

1. Did the runtime change?
2. Did a DLL override change?
3. Did an installer modify the environment?
4. Was a Windows component installed?
5. Did the GPU driver change?
6. Does the application work in a clean prefix?

Testing a clean prefix can be an effective diagnostic technique.

## A clean-prefix test

A useful debugging strategy is:

```text
Existing prefix
      ↓
   fails
      ↓
Create clean prefix
      ↓
   test app
```

If the application works in the clean prefix, the problem may be caused by accumulated configuration rather than the application itself.

## Conclusion

Prefixes are one of the most important concepts in Wine and Proton.

They provide isolated Windows-compatible environments without requiring virtual machines.

The challenge is that manually managing them can become complicated.

Proton-Autogen aims to make this complexity mostly invisible:

```text
Application
    ↓
Proton-Autogen
    ↓
Prefix management
    ↓
Proton / Wine
    ↓
Linux
```

Understanding prefixes is still useful for troubleshooting, but users should not necessarily have to manage them manually for every application.
