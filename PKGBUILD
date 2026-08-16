pkgname=proton-autogen
pkgver=3.2.6
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
    gtk4
    gdk-pixbuf2
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

sha256sums=('d54ed60f3db0e972ce3b841a69c9a6f9d667368eafe53d2f7b87bfbaf56d7a33')

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
