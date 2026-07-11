#!/usr/bin/env bash
set -euo pipefail

echo "==> Updating proton-autogen..."

# -----------------------------
# 1. Check git repository
# -----------------------------
if [ ! -d ".git" ]; then
    echo "Error: not a git repository"
    exit 1
fi

# -----------------------------
# 2. Detect OS / package manager
# -----------------------------
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
else
    echo "Cannot detect OS."
    exit 1
fi

PM=""

case "${ID:-}" in
    arch|cachyos)
        PM="pacman"
        ;;
    debian|ubuntu|linuxmint|pop)
        PM="apt"
        ;;
    fedora)
        PM="dnf"
        ;;
    *)
        echo "Unsupported distro: ${ID:-unknown}"
        exit 1
        ;;
esac

echo "==> Detected OS: $ID"
echo "==> Package manager: $PM"

# -----------------------------
# 3. Update repo safely
# -----------------------------
echo "==> Fetching latest changes..."

git fetch origin main

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "==> Already up to date."
else
    echo "==> Pulling updates..."
    git restore update.sh
    git pull origin main
fi

# -----------------------------
# 4. Restore stash (safe)
# -----------------------------
git stash pop || true

# -----------------------------
# 5. Install dependencies only if needed
# -----------------------------
echo "==> Ensuring dependencies..."

case "$PM" in
    pacman)
        sudo pacman -S --needed --noconfirm \
            python \
            python-gobject \
            python-pyyaml \
            gtk4 \
            glib2
        ;;
    apt)
        sudo apt update
        sudo apt install -y \
            python3 \
            python3-gi \
            python3-yaml \
            gir1.2-gtk-4.0 \
            libglib2.0-0 \
            python3-pip
        ;;
    dnf)
        sudo dnf install -y \
            python3 \
            python3-gobject \
            python3-pyyaml \
            gtk4 \
            glib2
        ;;
esac

# -----------------------------
# 6. Install/update binary
# -----------------------------
echo "==> Updating binary..."
sudo install -Dm755 \
    usr/bin/proton-autogen \
    /usr/bin/proton-autogen

# -----------------------------
# 7. Install/update resources (safe copy)
# -----------------------------
echo "==> Updating resources..."

sudo install -d /usr/share/proton-autogen
sudo cp -r usr/share/proton-autogen/* /usr/share/proton-autogen/
sudo cp debian/proton-autogen.1.gz /usr/share/man/man1/

sudo install -d /usr/share/applications
sudo install -m644 \
    usr/share/applications/proton-autogen.desktop \
    /usr/share/applications/

sudo install -d /usr/share/icons/hicolor/256x256/apps
sudo install -m644 \
    usr/share/icons/hicolor/256x256/apps/proton-autogen.png \
    /usr/share/icons/hicolor/256x256/apps/

# -----------------------------
# 8. Update Python module
# -----------------------------
echo "==> Updating Python module..."

PYTHON_SITE=$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

sudo mkdir -p "$PYTHON_SITE/proton_autogen"

sudo cp -r \
    usr/lib/python3/dist-packages/proton_autogen \
    "$PYTHON_SITE/"

# -----------------------------
# 9. Refresh cache (safe)
# -----------------------------
echo "==> Updating library cache..."
sudo ldconfig || true

# -----------------------------
# Done
# -----------------------------
echo ""
echo "=============================="
echo " Update complete!"
echo "=============================="
echo ""
echo "Run:"
echo "  proton-autogen --help"
echo "  proton-autogen --ux"
echo ""
