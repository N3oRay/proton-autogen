#!/usr/bin/env bash
# tools/update-checksum.sh — met à jour les sommes du PKGBUILD ET régénère .SRCINFO.
#
# Nécessite les outils Arch : updpkgsums (paquet pacman-contrib) et makepkg.
# À lancer après avoir créé le tag de la version (le PKGBUILD télécharge le
# tarball GitHub de ce tag), AVANT de publier sur l'AUR.
#
# Pour seulement vérifier, sans modifier : tools/check_sum.sh
set -euo pipefail

cd "$(dirname "$0")/.."

for tool in updpkgsums makepkg; do
    command -v "$tool" >/dev/null || {
        echo "ERREUR : '$tool' introuvable (Arch : sudo pacman -S pacman-contrib)" >&2
        exit 1
    }
done

updpkgsums

# L'AUR lit .SRCINFO, pas le PKGBUILD : il doit toujours être synchronisé.
makepkg --printsrcinfo > .SRCINFO

git diff -- PKGBUILD .SRCINFO
