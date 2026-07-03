pkgname=proton-autogen
pkgver=2.8.7
pkgrel=1
pkgdesc="Automatic Proton/Wine launcher for Windows executables"
arch=('x86_64')
url="https://github.com/N3oRay/proton-autogen"
license=('MIT')

depends=(
  python
  python-gobject
  python-yaml
  gtk4
  glib2
  gobject-introspection-runtime
)

source=("git+https://github.com/N3oRay/proton-autogen.git")
sha256sums=('SKIP')

pkgver() {
  cd "$srcdir/proton-autogen"
  git describe --tags --long | sed 's/^v//; s/-/./g'
}

package() {
    cd "$srcdir/proton-autogen"

    install -Dm755 usr/bin/proton-autogen \
        "$pkgdir/usr/bin/proton-autogen"

    install -Dm644 usr/share/applications/proton-autogen.desktop \
        "$pkgdir/usr/share/applications/proton-autogen.desktop"

    cp -r usr/share/icons "$pkgdir/usr/share/"

    PYTHON_SITE=$(python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

    install -d "$pkgdir/$PYTHON_SITE"

    cp -r usr/lib/python3/dist-packages/proton_autogen \
        "$pkgdir/$PYTHON_SITE/"
}
