#!/bin/bash
set -e

echo "==> Installing dependencies..."
sudo pacman -S --needed --noconfirm \
    python \
    python-gobject \
    gtk4 \
    glib2

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
echo "You can test it with:"
echo "  proton-autogen --help"
echo "  proton-autogen --ux"
