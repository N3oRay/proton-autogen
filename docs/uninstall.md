## 🗑️ Uninstallation

### Remove Package

```bash
sudo apt remove proton-autogen
```

### Full Cleanup

```bash
sudo apt purge proton-autogen
```

### Manual Cleanup

```bash
chmod +x ./uninstall.sh
./uninstall.sh
```
The uninstall script only removes Proton-Autogen files and configuration.
It does not remove Steam, Proton versions, or existing Wine prefixes.

Restart Nemo:

```bash
nemo -q
```

Restart Nautilus:

```bash
nautilus -q
```

---
