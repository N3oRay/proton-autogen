from collections import defaultdict
from packaging.version import Version
from launchpadlib.launchpad import Launchpad

MIN_VERSION = Version("2.9.7")

lp = Launchpad.login_anonymously("ppa-stats", "production")

ppa = lp.people["n3oray"].getPPAByName(name="proton-autogen")

versions = defaultdict(int)

for binary in ppa.getPublishedBinaries():
    version = Version(binary.binary_package_version)

    if version >= MIN_VERSION:
        versions[(binary.binary_package_name, str(version))] += (
            binary.getDownloadCount()
        )

total = sum(versions.values())

for (name, version), downloads in versions.items():
    print(f"{name} {version}: {downloads}")

print(f"\nVersions analysées : {len(versions)}")
print(f"Téléchargements totaux : {total}")
