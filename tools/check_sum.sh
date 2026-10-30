#!/usr/bin/env bash
# shellcheck disable=SC2154  # `source` et `sha256sums` sont définis par le PKGBUILD chargé plus bas
# tools/check_sum.sh — VÉRIFIE (sans rien modifier) que sha256sums du PKGBUILD
# correspond aux sources actuellement servies.
#
# Fonctionne partout (bash + curl + sha256sum), sans outil Arch. Code retour :
#   0  toutes les sommes correspondent (ou sont « SKIP »)
#   1  au moins une somme diffère, ou le téléchargement a échoué
#
# Pour METTRE À JOUR les sommes, utiliser tools/update-checksum.sh.
set -euo pipefail

cd "$(dirname "$0")/.."

# Charge pkgver, source et sha256sums depuis le PKGBUILD : ${pkgver} est ainsi
# développé comme le fait makepkg. (Les fonctions build()/package() sont définies
# mais jamais exécutées.)
# shellcheck disable=SC1091
source ./PKGBUILD

if [[ ${#source[@]} -ne ${#sha256sums[@]} ]]; then
    echo "ERREUR : ${#source[@]} source(s) mais ${#sha256sums[@]} somme(s) sha256 dans le PKGBUILD" >&2
    exit 1
fi

workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT

status=0

for index in "${!source[@]}"; do
    entry=${source[$index]}
    expected=${sha256sums[$index]}

    if [[ $entry == *::* ]]; then
        name=${entry%%::*}
        url=${entry#*::}
    else
        url=$entry
        name=${url##*/}
    fi

    if [[ $expected == SKIP ]]; then
        echo "IGNORÉ  $name (SKIP)"
        continue
    fi

    if ! curl -fsSL --retry 3 --max-time 120 -o "$workdir/$name" "$url"; then
        echo "ÉCHEC   $name : téléchargement impossible ($url)" >&2
        status=1
        continue
    fi

    actual=$(sha256sum "$workdir/$name" | cut -d' ' -f1)

    if [[ $actual == "$expected" ]]; then
        echo "OK      $name  $actual"
    else
        echo "ÉCHEC   $name" >&2
        echo "        attendu  $expected" >&2
        echo "        obtenu   $actual" >&2
        status=1
    fi
done

exit $status
