#!/usr/bin/env bash
set -euo pipefail

echo "==> Detecting OS..."

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

echo "==> Installing dependencies..."

install_deps() {
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
}

install_deps

echo "==> Installing binary..."
sudo install -Dm755 \
    usr/bin/proton-autogen \
    /usr/bin/proton-autogen

echo "==> Installing resources..."
sudo mkdir -p /usr/share/proton-autogen
sudo cp -r usr/share/* /usr/share/proton-autogen/ 2>/dev/null || true

echo "==> Installing Python module..."

PYTHON_SITE=$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

sudo mkdir -p "$PYTHON_SITE/proton_autogen"

sudo cp -r \
    usr/lib/python3/dist-packages/proton_autogen \
    "$PYTHON_SITE/"

echo "==> Updating library cache..."
sudo ldconfig || true

echo ""
echo "=============================="
echo " Installation complete!"
echo "=============================="
echo ""
echo "Test it with:"
echo "  proton-autogen --help"
echo "  proton-autogen --ux"
echo ""
