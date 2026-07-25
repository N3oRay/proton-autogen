from launchpadlib.launchpad import Launchpad
from packaging.version import Version

MIN_VERSION = Version("2.9.7")

lp = Launchpad.login_anonymously("ppa-stats", "production")

ppa = lp.people["n3oray"].getPPAByName(name="proton-autogen")

versions = {}

for binary in ppa.getPublishedBinaries():
    version = binary.binary_package_version

    if Version(version) < MIN_VERSION:
        break

    key = (binary.binary_package_name, version)
    versions[key] = versions.get(key, 0) + binary.getDownloadCount()

total = sum(versions.values())

for (name, version), downloads in versions.items():
    print(f"{name} {version}: {downloads}")

print(f"\nVersions analysées : {len(versions)}")
print(f"Téléchargements totaux : {total}")
