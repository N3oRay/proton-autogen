# Proton Paths

Proton-autogen automatically searches for Proton installations in several standard locations.

This allows it to work with different Steam installations, including native Steam, Steam Flatpak, Arch Linux, CachyOS, Proton-GE, Proton-CachyOS, and custom Proton builds.

## Automatic detection

By default, Proton-autogen searches the following locations:

### Steam

```text
~/.steam/root/compatibilitytools.d
~/.steam/steam/compatibilitytools.d
~/.local/share/Steam/compatibilitytools.d
```

These directories are commonly used for Proton-GE and other custom Proton versions.

### Steam runtimes

Proton-autogen also checks the Steam `common` directory:

```text
~/.steam/steam/steamapps/common
~/.local/share/Steam/steamapps/common
```

This allows Proton versions installed directly by Steam to be detected.

### System-wide installations

Proton-autogen also checks:

```text
/usr/share/steam/compatibilitytools.d
```

This is useful for system-wide Proton installations, including installations commonly used by Arch Linux and CachyOS.

## Steam Flatpak

If Steam is installed through Flatpak, Proton-autogen also supports the following locations:

```text
~/.var/app/com.valvesoftware.Steam/.local/share/Steam/compatibilitytools.d
~/.var/app/com.valvesoftware.Steam/.steam/root/compatibilitytools.d
```

These paths are not required in the main configuration file because they are included automatically when Proton-autogen creates its default configuration.

## Custom Proton paths

If your Proton installation is located somewhere else, you can add a custom path.

The configuration file is:

```text
~/.config//proton-autogen/proton-autogen.conf
```

Example:

```ini
[proton]
paths=~/Proton
```

You can also specify multiple paths.

Using `;`:

```ini
[proton]
paths=~/Proton;~/Games/Proton;/opt/proton
```

Using `:`:

```ini
[proton]
paths=~/Proton:~/Games/Proton:/opt/proton
```

Or using separate lines:

```ini
[proton]
paths=
    ~/Proton
    ~/Games/Proton
    /opt/proton
```

All three formats are supported.

## Using `~`

You can use `~` as a shortcut for your home directory.

For example:

```text
~/Proton
```

is equivalent to:

```text
/home/your-user/Proton
```

This makes the configuration portable between users.

## Checking detected paths

You can display the Proton paths detected by Proton-autogen with:

```bash
proton-autogen --proton-paths
```

You can also list the Proton versions that were detected:

```bash
proton-autogen --list-protons
```

For more information about your system and Proton environment, run:

```bash
proton-autogen --diag
```

## Troubleshooting

If Proton-autogen does not detect your Proton installation:

1. Check where Proton is installed.
2. Verify that the directory contains the Proton installation.
3. Run:

```bash
proton-autogen --proton-paths
```

4. If the path is not listed, add it to:

```text
~/.config/proton-autogen/proton-autogen.conf
```

For example:

```ini
[proton]
paths=/path/to/your/proton
```

Then run:

```bash
proton-autogen --list-protons
```

again.

## Summary

Proton-autogen uses a combination of:

* Standard Steam paths
* Steam runtime paths
* System-wide paths
* Steam Flatpak paths
* User-defined custom paths

You normally do not need to configure anything manually.

If Proton is installed in a non-standard location, simply add its directory to:

```text
~/.config/proton-autogen/proton-autogen.conf
```
