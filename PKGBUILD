pkgname=proton-autogen
pkgver=2.6.1
pkgrel=1
pkgdesc="Automatic Proton/Wine launcher for Windows executables"
arch=('any')
url="https://github.com/N3oRay/proton-autogen"
license=('MIT')

depends=(
  python
  python-gobject
  python-yaml
  gtk4
  glib2
)

source=("git+https://github.com/N3oRay/proton-autogen.git")
sha256sums=('SKIP')

package() {
  cd "$srcdir/proton-autogen"

  install -Dm755 usr/bin/proton-autogen \
    "$pkgdir/usr/bin/proton-autogen"

  install -Dm644 usr/share/applications/proton-autogen.desktop \
    "$pkgdir/usr/share/applications/proton-autogen.desktop"

  cp -r usr/share/icons \
    "$pkgdir/usr/share/"

  install -d "$pkgdir/usr/lib/python3/site-packages/"
  cp -r usr/lib/python3/dist-packages/proton_autogen \
    "$pkgdir/usr/lib/python3/site-packages/"
}
