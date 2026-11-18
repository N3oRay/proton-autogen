# proton_autogen/profiles/visualstudio.py
"""
Profil « VisualStudio » — applications et jeux qui dépendent du runtime
Microsoft Visual C++ 2015-2022 (vcruntime140 / msvcp140 / vcruntime140_1).

Typiquement : jeux Unreal Engine 4/5 et Unity IL2CPP (GameAssembly.dll),
launchers et applications C++ compilés avec MSVC, qui échouent avec
« VCRUNTIME140_1.dll / MSVCP140.dll introuvable » dans un préfixe vierge.

Fonctionnement (même schéma que le profil dotnet) :
  1. base graphique = profil dx11 (DXVK), pour ne rien perdre côté rendu ;
  2. vérification des runtimes VC++ dans le préfixe (registre + DLL réelles) ;
  3. installation automatique via utils.vcredist si absents ;
  4. si les DLL Microsoft sont présentes, WINEDLLOVERRIDES=n,b pour que Wine
     les charge au lieu de ses DLL internes.

Désactivation : PROTON_AUTOGEN_NO_VCREDIST=1
"""

import os

from proton_autogen.profiles.dx11 import env_dx11
from proton_autogen.utils.logger import StructuredLogger
from proton_autogen.utils.vcredist import (
    check_vcredist,
    ensure_vcredist,
    vcredist_dll_overrides,
)

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.profiles.visualstudio")

# Installeurs de prérequis : on ne pré-installe rien (ce sont eux qui le font)
_INSTALLER_KEYWORDS = (
    "vc_redist",
    "vcredist",
    "ueprereqsetup",
    "ue4prereqsetup",
)


def is_vc_installer(exe_path=None):
    """True si l'exécutable est lui-même un installeur de runtime VC++/UE."""
    if not exe_path:
        return False
    name = os.path.basename(exe_path).lower()
    return any(k in name for k in _INSTALLER_KEYWORDS)


def _merge_dll_overrides(existing, addition):
    """
    Fusionne deux chaînes WINEDLLOVERRIDES. En cas de conflit sur une même
    DLL, la valeur de `addition` l'emporte. Format Wine : "a,b=n,b;c=d".
    """
    modes = {}

    for chunk in (existing or "", addition or ""):
        for item in chunk.split(";"):
            item = item.strip()
            if "=" not in item:
                continue
            dlls, mode = item.rsplit("=", 1)
            for dll in dlls.split(","):
                dll = dll.strip()
                if dll:
                    modes[dll] = mode.strip()

    grouped = {}
    for dll, mode in modes.items():
        grouped.setdefault(mode, []).append(dll)

    return ";".join(f"{','.join(dlls)}={mode}" for mode, dlls in grouped.items())


def env_visualstudio(prefix=None, proton_path=None, exe_path=None):
    """
    Profil Visual C++ Redistributable 2015-2022.

    Réutilise le profil dx11 puis garantit la présence des runtimes VC++
    dans le préfixe. N'échoue jamais : si l'installation est impossible,
    le jeu est tout de même lancé avec les DLL internes de Wine.
    """

    env = env_dx11(prefix=prefix, proton_path=proton_path, exe_path=exe_path)

    logger.info("[proton-autogen] PROFILE: VisualStudio (VC++ 2015-2022)")

    # Pas de préfixe (ex. export_default_profiles) : profil de base uniquement
    if not prefix:
        return env

    if os.environ.get("PROTON_AUTOGEN_NO_VCREDIST") == "1":
        logger.info("[proton-autogen] VC++ auto-install disabled (PROTON_AUTOGEN_NO_VCREDIST=1)")
        return env

    if is_vc_installer(exe_path):
        logger.info("[proton-autogen] VC++ installer detected -> no pre-install")
        return env

    available = check_vcredist(prefix, arch="both")

    if not available and proton_path:
        logger.info("[proton-autogen] VC++ runtimes missing -> installing")
        available = ensure_vcredist(prefix=prefix, proton_path=proton_path)

        if not available:
            logger.info("[proton-autogen] Warning: VC++ installation failed")

    if available:
        env["WINEDLLOVERRIDES"] = _merge_dll_overrides(
            env.get("WINEDLLOVERRIDES"),
            vcredist_dll_overrides(),
        )
        logger.info("[proton-autogen] VC++ runtimes available -> native,builtin overrides")
    else:
        logger.info("[proton-autogen] VC++ runtimes unavailable -> Wine builtin DLLs")

    return env
