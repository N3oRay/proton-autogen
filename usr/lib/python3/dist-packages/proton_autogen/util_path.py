
import os
def proton_path(p):
    if isinstance(p, dict):
        return p.get("path")
    return p

def proton_name(p):
    if isinstance(p, dict):
        return p.get("name", "Unknown Proton")
    return os.path.basename(p) if p else "Unknown Proton"
