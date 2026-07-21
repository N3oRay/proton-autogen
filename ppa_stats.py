
from launchpadlib.launchpad import Launchpad


lp = Launchpad.login_anonymously(
    "ppa-stats",
    "production"
)

ppa = lp.people["n3oray"].getPPAByName(
    name="proton-autogen"
)


total = 0
count = 0

for binary in ppa.getPublishedBinaries():

    downloads = binary.getDownloadCount()

    total += downloads
    count += 1


print(f"Publications analysées : {count}")
print(f"Téléchargements totaux : {total}")
