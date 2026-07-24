#legacy_function
import os
import uuid

#  Legacy function. Prefix creation is now handled through game configuration and prefix profiles.
def create_new_prefix():
    name = input(tr("prefix_name") + ": ").strip()

    if not name:
        name = f"auto-{uuid.uuid4().hex[:8]}"

    root = os.path.expanduser("~/Documents/Proton/env")
    path = os.path.join(root, name)

    os.makedirs(path, exist_ok=True)

    return name
