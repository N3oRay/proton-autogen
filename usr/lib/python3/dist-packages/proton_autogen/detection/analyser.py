from shutil import which

def has_proton_call():
    return which("proton-call") is not None

def has_wine():
    return which("wine") is not None

def has_mangohud():
    return which("mangohud") is not None

def has_gamemode():
    return which("gamemoderun") is not None
