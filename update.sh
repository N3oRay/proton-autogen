#!/bin/bash
set -e

echo "==> Updating proton-autogen..."

# 1. Vérifier qu'on est dans un repo git
if [ ! -d ".git" ]; then
    echo "Error: not a git repository"
    exit 1
fi


# 3. Récupérer la dernière version
echo "==> Pulling latest version..."
git pull origin main

# 4. Restaurer stash si nécessaire
git stash pop || true

# 5. Réinstaller uniquement les fichiers système

echo "==> Updating binary..."
sudo install -Dm755 \
    usr/bin/proton-autogen \
    /usr/bin/proton-autogen

echo "==> Updating resources..."
sudo cp -r usr/share/* /usr/share/

echo "==> Updating Python module..."
PYTHON_SITE=$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

sudo cp -r \
    usr/lib/python3/dist-packages/proton_autogen \
    "$PYTHON_SITE/"

# 6. Cache refresh
echo "==> Updating library cache..."
sudo ldconfig

echo
echo "Update complete!"
echo "Run: proton-autogen --ux"
