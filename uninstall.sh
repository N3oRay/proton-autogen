#!/usr/bin/env bash
set -euo pipefail

echo "==> Detecting OS..."

if [[ -f /etc/os-release ]]; then
    . /etc/os-release
else
    echo "Cannot detect OS."
    exit 1
fi

echo "==> Detected OS: ${ID:-unknown}"

echo "==> Removing user configuration..."

# User configuration is intentionally preserved.
# rm -rf \
#    "${HOME}/.config/proton-autogen"

rm -f \
    "${HOME}/.local/share/nemo/actions/proton-autogen.nemo_action"


echo "==> Removing executable..."

sudo rm -f \
    /usr/bin/proton-autogen


echo "==> Removing application resources..."

sudo rm -rf \
    /usr/share/proton-autogen


echo "==> Removing desktop entry..."

sudo rm -f \
    /usr/share/applications/proton-autogen.desktop


echo "==> Removing icons..."

sudo rm -f \
    /usr/share/icons/hicolor/256x256/apps/proton-autogen.png

sudo rm -f \
    /usr/share/icons/hicolor/256x256/apps/io.github.N3oRay.ProtonAutogen.png

echo "==> Removing KDE service menu..."

sudo rm -f \
    /usr/share/kio/servicemenus/proton-autogen.desktop

echo "==> Removing Nautilus extension..."

sudo rm -f \
    /usr/share/nautilus-python/extensions/proton_autogen_nautilus.py

echo "==> Removing Nemo action..."

sudo rm -f \
    /usr/share/nemo/actions/proton-autogen.nemo_action


echo "==> Removing man page..."

sudo rm -f \
    /usr/share/man/man1/proton-autogen.1.gz


echo "==> Removing Python module..."

PYTHON_PATHS=(
    "/usr/lib/python3/dist-packages/proton_autogen"
    "/usr/local/lib/python3/dist-packages/proton_autogen"
)

# Ajout des chemins Python détectés dynamiquement
if command -v python3 >/dev/null 2>&1; then
    PYTHON_SITE=$(python3 - <<EOF
import sysconfig
print(sysconfig.get_paths()["purelib"])
EOF
)

    PYTHON_PATHS+=(
        "${PYTHON_SITE}/proton_autogen"
    )
fi


for path in "${PYTHON_PATHS[@]}"; do
    if [[ -d "$path" ]]; then
        echo "Removing: $path"
        sudo rm -rf "$path"
    fi
done


echo "==> Updating caches..."

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database \
        /usr/share/applications \
        2>/dev/null || true
fi


if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache \
        -f /usr/share/icons/hicolor \
        2>/dev/null || true
fi


echo "==> Cleaning Python cache..."

sudo find /usr \
    -type d \
    -name "__pycache__" \
    -path "*proton_autogen*" \
    -exec rm -rf {} + \
    2>/dev/null || true


echo ""
echo "=============================="
echo " proton-autogen removed!"
echo "=============================="
echo ""

echo "Note:"
echo "- Dependencies (GTK4, Python, Proton, MangoHud...) were not removed."
echo "- They may be used by other applications."
