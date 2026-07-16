pkgname=proton-autogen
pkgver=3.0.2
pkgrel=1
pkgdesc="Automatic Proton/Wine launcher for Windows executables"
arch=('x86_64')
url="https://github.com/N3oRay/proton-autogen"
license=('MIT')

depends=(
  python
  python-gobject
  python-pyyaml
  python-rich
  gtk4
  glib2
  cairo
  pango
)

source=(
  "https://github.com/N3oRay/proton-autogen/archive/refs/tags/v${pkgver}.tar.gz"
)

sha256sums=('SKIP')


package() {
    cd "$srcdir/$pkgname-$pkgver"


    # Binary
    install -Dm755 \
        usr/bin/proton-autogen \
        "$pkgdir/usr/bin/proton-autogen"


    # Python module
    python_site=$(python -c "import site; print(site.getsitepackages()[0])")

    install -dm755 \
        "$pkgdir/$python_site"

    cp -r usr/lib/python3/dist-packages/proton_autogen \
        "$pkgdir/$python_site/"


    # Application data
    install -dm755 \
        "$pkgdir/usr/share/proton-autogen"

    cp -r usr/share/proton-autogen/* \
        "$pkgdir/usr/share/proton-autogen/"


    # Desktop entry
    install -Dm644 \
        usr/share/applications/proton-autogen.desktop \
        "$pkgdir/usr/share/applications/proton-autogen.desktop"


    # Icon
    install -Dm644 \
        usr/share/icons/hicolor/256x256/apps/proton-autogen.png \
        "$pkgdir/usr/share/icons/hicolor/256x256/apps/proton-autogen.png"


    # Man page
    install -Dm644 \
        debian/proton-autogen.1.gz \
        "$pkgdir/usr/share/man/man1/proton-autogen.1.gz"
}
