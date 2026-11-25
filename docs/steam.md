# Using Proton-Autogen from Steam

Proton-Autogen can be selected in Steam as a **compatibility tool**. Steam then
launches the game through `proton-autogen run`, so the game keeps exactly the
same behaviour as a launch from the file manager or the UX (per-game config,
Proton selection, prefix, MangoHud / GameMode / Gamescope, env variables...).

## Install

```bash
proton-autogen install-steam            # ~/.steam/root/compatibilitytools.d/Proton-Autogen/
proton-autogen install-steam --check    # verify permissions and integrity only
```

Options: `--dest DIR` (another `compatibilitytools.d`), `--launcher PATH`,
`-y/--yes` (do not ask before replacing a modified installation).

Restart Steam, then: game **Properties > Compatibility > Force the use of a
specific Steam Play compatibility tool > Proton-Autogen**.

An existing, different installation is never overwritten without confirmation;
each replaced file is saved as `<name>.bak-<date>`. Other files in the folder
are left untouched.

Exit codes: `0` ok, `1` error, `4` cancelled / confirmation impossible,
`5` verification failed.

## Uninstall

```bash
proton-autogen uninstall-steam            # asks for confirmation
proton-autogen uninstall-steam --yes      # no question
proton-autogen uninstall-steam --purge    # delete the whole folder (backups included)
```

Only a folder installed by Proton-Autogen is touched: a symlink, or a folder
without the wrapper's marker, is refused. Only the files listed below are
deleted. A file you modified since the install is kept as `<name>.bak-<date>`,
and any other file stays in place, so the folder is removed only when it ends up
empty. Nothing installed is not an error (exit code `0`). The Steam folder
`compatibilitytools.d` itself is never removed.

Games set to *Proton-Autogen* in Steam go back to Steam's default tool; restart
Steam to refresh its list.

## From the UX: "Steam configuration"

The main menu has a **Steam configuration** entry. Its window shows whether
Steam is found and whether Proton-Autogen is installed (and healthy), and offers
**Install in Steam** (**Reinstall / repair** when already installed) and
**Uninstall from Steam**. Replacing a modified installation and uninstalling
always ask for confirmation. It uses exactly the same code as the two commands.

## Installed files

| File | Role |
|------|------|
| `compatibilitytool.vdf` | declares the tool to Steam |
| `toolmanifest.vdf` | makes Steam call `/proton %verb%` |
| `proton` | entry point called by Steam |
| `autogen_wrapper.py` | turns `proton <verb> <exe> [args]` into `proton-autogen run --steam -- <exe> [args]` |
| `launcher.path` | absolute path of the `proton-autogen` launcher |
| `INSTALL_MANIFEST.json` | SHA-256 of the installed files (used by `--check`) |

## Notes

* The tool runs on the host (no `require_tool_appid`), so `proton-autogen` must
  be installed on the host. Steam installed as a Flatpak cannot see it.
* Steam's own prefix (`STEAM_COMPAT_DATA_PATH`) is not used: Proton-Autogen
  keeps managing its prefixes. `SteamAppId` and the Steam client path given by
  Steam are reused.
* The installed wrapper is ignored by Proton detection (`--list-protons`,
  automatic selection), and refuses to run if it is ever called recursively.
* Only Proton launch mode forwards the program arguments.
