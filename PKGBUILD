pkgname=proton-autogen
pkgver=3.3.7
pkgrel=1
pkgdesc="Automatic Proton/Wine launcher for Windows executables"
arch=('any')
url="https://github.com/N3oRay/proton-autogen"
license=('MIT')

depends=(
    python
    python-gobject
    python-pyyaml
    python-rich
    python-requests
    python-psutil
    gtk4
    gdk-pixbuf2
    graphene
)

makedepends=(
    python-build
    python-installer
    python-wheel
    python-setuptools
)

source=(
    "https://github.com/N3oRay/proton-autogen/archive/refs/tags/v${pkgver}.tar.gz"
)

sha256sums=('273c8c3665b29526eff820ee05c99e8ac1b3e6b088f4d678329b52fa6f6f2eff')

build() {
    cd "$srcdir/$pkgname-$pkgver"

    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$pkgname-$pkgver"

    # Installation du module Python
    python -m installer \
        --destdir="$pkgdir" \
        dist/*.whl

    # Lanceur
    install -Dm755 \
        usr/bin/proton-autogen \
        "$pkgdir/usr/bin/proton-autogen"

    # Ressources
    install -dm755 \
        "$pkgdir/usr/share/proton-autogen"

    # Ressources
    cp -a \
        usr/share/proton-autogen/. \
        "$pkgdir/usr/share/proton-autogen/"

    # Desktop
    install -Dm644 \
        usr/share/applications/proton-autogen.desktop \
        "$pkgdir/usr/share/applications/proton-autogen.desktop"

    # Icône
    install -Dm644 \
        usr/share/icons/hicolor/256x256/apps/proton-autogen.png \
        "$pkgdir/usr/share/icons/hicolor/256x256/apps/proton-autogen.png"

    install -Dm644 \
        usr/share/icons/hicolor/256x256/apps/proton-autogen.png \
        "$pkgdir/usr/share/icons/hicolor/256x256/apps/io.github.N3oRay.ProtonAutogen.png"

    # Page de manuel
    install -Dm644 \
        debian/proton-autogen.1.gz \
        "$pkgdir/usr/share/man/man1/proton-autogen.1.gz"

    # Licence
    install -Dm644 \
        LICENSE \
        "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
