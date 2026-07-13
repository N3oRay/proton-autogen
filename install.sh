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
                pango \
                cairo \
                glib2
            ;;
        apt)
            sudo apt update
            sudo apt install -y \
                python3 \
                python3-gi \
                python3-yaml \
                python3-cairo \
                gir1.2-gtk-4.0 \
                gir1.2-pango-1.0 \
                libglib2.0-0 \
                python3-pip
            ;;
        dnf)
            sudo dnf install -y \
                python3 \
                python3-gobject \
                python3-pyyaml \
                gtk4 \
                pango \
                cairo \
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
echo "  proton-autogen --diag"
echo "  proton-autogen --ux"
echo ""
