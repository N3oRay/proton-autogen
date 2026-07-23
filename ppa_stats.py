from launchpadlib.launchpad import Launchpad


lp = Launchpad.login_anonymously(
    "ppa-stats",
    "production"
)

ppa = lp.people["n3oray"].getPPAByName(
    name="proton-autogen"
)

versions = {}

for binary in ppa.getPublishedBinaries():

    key = (
        binary.binary_package_name,
        binary.binary_package_version
    )

    downloads = binary.getDownloadCount()

    versions[key] = versions.get(key, 0) + downloads


total = sum(versions.values())

for (name, version), downloads in versions.items():
    print(f"{name} {version}: {downloads}")

print()
print(f"Versions analysées : {len(versions)}")
print(f"Téléchargements totaux : {total}")
