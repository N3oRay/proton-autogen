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
    arch|endeavouros|cachyos|garuda|manjaro|arcolinux|rebornos)
        PM="pacman"
        ;;
    debian|ubuntu|linuxmint|pop|elementary|zorin)
        PM="apt"
        ;;
    fedora|nobara)
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
                python-rich \
                python-requests \
                gtk4 \
                gdk-pixbuf2 \
                graphene
            ;;
        apt)
            sudo apt update
            sudo apt install -y \
                python3 \
                python3-gi \
                python3-yaml \
                python3-cairo \
                python3-rich \
                python3-requests \
                gir1.2-gtk-4.0 \
                gir1.2-graphene-1.0 \
                gir1.2-gdkpixbuf-2.0 \
                gir1.2-pango-1.0 \
                libglib2.0-0 \
                python3-pip
            ;;
        dnf)
            sudo dnf install -y \
                python3 \
                python3-gobject \
                python3-pyyaml \
                python3-rich \
                python3-requests \
                gtk4 \
                graphene \
                gdk-pixbuf2
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
sudo install -Dm644 \
    debian/proton-autogen.1.gz \
    /usr/share/man/man1/proton-autogen.1.gz


sudo install -d /usr/share/applications
sudo install -m644 \
    usr/share/applications/proton-autogen.desktop \
    /usr/share/applications/

sudo install -d /usr/share/icons/hicolor/256x256/apps
sudo install -m644 \
    usr/share/icons/hicolor/256x256/apps/proton-autogen.png \
    /usr/share/icons/hicolor/256x256/apps/

sudo install -m644 \
    usr/share/icons/hicolor/256x256/apps/proton-autogen.png \
    /usr/share/icons/hicolor/256x256/apps/io.github.N3oRay.ProtonAutogen.png

echo "==> Detecting file managers..."
install_file_manager_integrations() {

    # KDE / Dolphin / KIO
    if command -v dolphin >/dev/null 2>&1 || \
       command -v kioexec >/dev/null 2>&1; then

        echo "==> KDE/KIO detected."
        echo "==> Installing KDE service menu..."

        sudo install -Dm644 \
            usr/share/kio/servicemenus/proton-autogen.desktop \
            /usr/share/kio/servicemenus/proton-autogen.desktop
    else
        echo "==> KDE/KIO not detected. Skipping KDE service menu."
    fi


    # Nautilus
    if command -v nautilus >/dev/null 2>&1; then

        echo "==> Nautilus detected."
        echo "==> Installing Nautilus extension..."

        sudo install -Dm644 \
            usr/share/nautilus-python/extensions/proton_autogen_nautilus.py \
            /usr/share/nautilus-python/extensions/proton_autogen_nautilus.py
    else
        echo "==> Nautilus not detected. Skipping Nautilus extension."
    fi


    # Nemo
    if command -v nemo >/dev/null 2>&1; then

        echo "==> Nemo detected."
        echo "==> Installing Nemo action..."

        sudo install -Dm644 \
            usr/share/nemo/actions/proton-autogen.nemo_action \
            /usr/share/nemo/actions/proton-autogen.nemo_action
    else
        echo "==> Nemo not detected. Skipping Nemo action."
    fi
}

install_file_manager_integrations

echo "==> Installing Python module..."

PYTHON_SITE=$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

sudo mkdir -p "$PYTHON_SITE/proton_autogen"

sudo cp -r \
    usr/lib/python3/dist-packages/proton_autogen \
    "$PYTHON_SITE/"

#echo "==> Updating library cache..."
#sudo ldconfig || true

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
