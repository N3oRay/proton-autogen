#!/usr/bin/env bash
set -e

SRC=$(grep -oP '(?<=source=\(").*(?=")' PKGBUILD)

wget -q "$SRC" -O /tmp/source.tar.gz

HASH=$(sha256sum /tmp/source.tar.gz | awk '{print $1}')

sed -i "s/sha256sums=('SKIP')/sha256sums=('$HASH')/" PKGBUILD

echo "Checksum updated: $HASH"
