#!/bin/bash
set -e

echo "==> Detecting package manager..."

if command -v pacman &> /dev/null; then
    PM="pacman"
elif command -v apt &> /dev/null; then
    PM="apt"
else
    echo "Unsupported system (no pacman or apt found)."
    exit 1
fi

echo "==> Using package manager: $PM"

echo "==> Installing dependencies..."

if [ "$PM" = "pacman" ]; then
    sudo pacman -S --needed --noconfirm \
        python \
        python-gobject \
        python-pyyaml \
        gtk4 \
        glib2

elif [ "$PM" = "apt" ]; then
    sudo apt update
    sudo apt install -y \
        python3 \
        python3-gi \
        python3-yaml \
        gir1.2-gtk-4.0 \
        libglib2.0-0 \
        python3-pip
fi

echo "==> Installing binary..."
sudo install -Dm755 \
    usr/bin/proton-autogen \
    /usr/bin/proton-autogen

echo "==> Installing resources..."
sudo cp -r usr/share/* /usr/share/

echo "==> Installing Python module..."

PYTHON_SITE=$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

sudo cp -r \
    usr/lib/python3/dist-packages/proton_autogen \
    "$PYTHON_SITE/"

echo "==> Updating library cache..."
sudo ldconfig

echo
echo "Installation complete!"
echo
echo "Test commands:"
echo "  proton-autogen --help"
echo "  proton-autogen --ux"
