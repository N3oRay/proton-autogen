import os
from proton_autogen.utils.logger import StructuredLogger

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.profiles.base")
# ---------------------------------------------------
# BASE CLEANER (shared)
# ---------------------------------------------------
def init_env():
    logger.debug( "Initializing environment variables.")
    env = os.environ.copy()

    for k in [
        "LD_PRELOAD",
        "LD_LIBRARY_PATH",
        "VK_ICD_FILENAMES",
        "VK_DRIVER_FILES",
        "DXVK_HUD",
        "VKD3D_CONFIG",
        "WINEDEBUG",
        "RADV_PERFTEST",
    ]:
        env.pop(k, None)


    # =========================
    # FIX GStreamer Proton/Wine
    # =========================
    for k in [
        "GST_PLUGIN_PATH",
        "GST_PLUGIN_SYSTEM_PATH",
        "GST_REGISTRY",
        "GST_REGISTRY_UPDATE",
        "GST_DEBUG",
    ]:
        env.pop(k, None)


    env["STEAM_COMPAT_APP_ID"] = "0"


    return env
