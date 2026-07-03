pkgname=proton-autogen
pkgver=2.6.1
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

package() {
  cd "$srcdir/proton-autogen"

  # CLI
  install -Dm755 usr/bin/proton-autogen \
    "$pkgdir/usr/bin/proton-autogen"

  # Desktop file
  install -Dm644 usr/share/applications/proton-autogen.desktop \
    "$pkgdir/usr/share/applications/proton-autogen.desktop"

  # Icons
  cp -r usr/share/icons "$pkgdir/usr/share/"

  # Python module (PROPRE Arch way)
  install -d "$pkgdir/usr/lib/python3.*/site-packages/proton_autogen"
  cp -r proton_autogen/* \
    "$pkgdir/usr/lib/python3.*/site-packages/proton_autogen/"
}
