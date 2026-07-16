#!/bin/bash
set -e

dpkg-buildpackage -b -us -uc
sudo dpkg -i ../proton-autogen_*.deb
