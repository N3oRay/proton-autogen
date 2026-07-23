# Nom du paquet AUR/Pacman.
# Il doit correspondre au nom du paquet affiché dans les dépôts.
pkgname=proton-autogen

# Version du logiciel.
# Généralement synchronisée avec les tags Git (v3.0.2 ici).
pkgver=3.1.3

# Révision du paquet.
# Augmente uniquement quand le PKGBUILD change sans changement du logiciel.
# Exemple : correction du packaging -> pkgrel=2.
pkgrel=1

# Description courte affichée par pacman -Si.
pkgdesc="Automatic Proton/Wine launcher for Windows executables"

# Architecture supportée.
# x86_64 signifie PC 64 bits Intel/AMD.
# Si ton logiciel est 100% Python, "any" pourrait être possible.
arch=('x86_64')

# Page officielle du projet.
# Bonne pratique : GitHub, GitLab ou site officiel.
url="https://github.com/N3oRay/proton-autogen"

# Licence du projet.
# MIT nécessite normalement un fichier LICENSE inclus dans le paquet.
license=('MIT')


# Dépendances nécessaires à l'exécution.
# Pacman installera automatiquement ces paquets avant l'installation.
depends=(
  python            # Interpréteur Python
  python-gobject    # Bindings Python pour GTK/GObject
  python-pyyaml     # Lecture des fichiers YAML
  python-rich       # Affichage terminal amélioré
  gtk4              # Interface graphique GTK4
  glib2             # Bibliothèque système utilisée par GTK
  cairo             # Rendu graphique
  pango             # Gestion des polices
)


# Source téléchargée par makepkg.
# Ici le paquet récupère automatiquement le tag Git v3.0.2.
source=("https://github.com/N3oRay/proton-autogen/archive/refs/tags/v${pkgver}.tar.gz")

# Empêche la vérification d'intégrité.
# Acceptable pour un test, mais déconseillé pour AUR.
# Il faudrait idéalement mettre le vrai SHA256.
sha256sums=('SKIP')


# Fonction appelée par makepkg.
# Elle copie les fichiers dans $pkgdir, qui devient ensuite le paquet final.
package() {

    # Entre dans le dossier source extrait par makepkg.
    cd "$srcdir/$pkgname-$pkgver"


    # Installation du lanceur principal.
    #
    # -D : crée automatiquement les dossiers nécessaires
    # -m755 : permissions exécutables
    #
    # Résultat :
    # /usr/bin/proton-autogen
    install -Dm755 \
        usr/bin/proton-autogen \
        "$pkgdir/usr/bin/proton-autogen"


    # Création du dossier Python.
    #
    # ATTENTION :
    # /usr/lib/python/site-packages n'est PAS un chemin Arch standard.
    #
    # Sur Arch, Python utilise généralement :
    # /usr/lib/python3.x/site-packages/
    #
    # Cette partie risque d'être refusée par un mainteneur.
    install -dm755 \
        "$pkgdir/usr/lib/python/site-packages"


    # Copie du module Python.
    #
    # Problème potentiel :
    # Il faudrait idéalement installer via setuptools/pyproject
    # ou cibler le vrai site-packages Arch.
    cp -a proton_autogen \
        "$pkgdir/usr/lib/python/site-packages/"


    # Données propres au programme.
    #
    # Exemple :
    # configurations, templates, fichiers internes...
    #
    # /usr/share/proton-autogen est un emplacement correct.
    install -dm755 \
        "$pkgdir/usr/share/proton-autogen"


    # Copie des ressources.
    cp -a usr/share/proton-autogen/* \
        "$pkgdir/usr/share/proton-autogen/"


    # Entrée du menu applications.
    #
    # Crée :
    # /usr/share/applications/proton-autogen.desktop
    #
    # Correct pour un logiciel graphique.
    install -Dm644 \
        usr/share/applications/proton-autogen.desktop \
        "$pkgdir/usr/share/applications/proton-autogen.desktop"


    # Icône système.
    #
    # Chemin standard Freedesktop.
    install -Dm644 \
        usr/share/icons/hicolor/256x256/apps/proton-autogen.png \
        "$pkgdir/usr/share/icons/hicolor/256x256/apps/proton-autogen.png"


    # Page de manuel.
    #
    # Correct, mais Arch préfère généralement :
    # proton-autogen.1
    #
    # makepkg compressera ensuite automatiquement.
    #
    # Une source .gz peut fonctionner mais n'est pas idéale.
    install -Dm644 \
        debian/proton-autogen.1 \
        "$pkgdir/usr/share/man/man1/proton-autogen.1"
}
