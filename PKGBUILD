pkgname=proton-autogen
pkgver=1.0.0
pkgrel=1
pkgdesc="GUI tool for Proton automation"
arch=('any')
url="https://github.com/N3oRay/proton-autogen"
license=('MIT')
depends=(
  'python'
  'python-gobject'
  'python-yaml'
  'gtk4'
  'glib2'
)
source=(
  "git+https://github.com/N3oRay/proton-autogen.git"
)
sha256sums=('SKIP')

package() {
  cd "$srcdir/proton-autogen"

  # Binary
  install -Dm755 usr/bin/proton-autogen \
    "$pkgdir/usr/bin/proton-autogen"

  # Python module
  install -d "$pkgdir/usr/lib/python3.*/site-packages/"
  cp -r usr/lib/python3/dist-packages/proton_autogen \
    "$pkgdir/usr/lib/python3.*/site-packages/"

  # Shared data
  cp -r usr/share "$pkgdir/usr/"

  # Desktop file + icon are already inside usr/share
}
