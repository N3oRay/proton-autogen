#!/usr/bin/env python3

# capabilities.py
"""
Détection « par capacités » d'un exécutable Windows, en complément (pas
en remplacement) de la détection par nom (profiles.csv + mots-clés dans
init.py). Suite à la discussion sur l'évolution du système de profils :
plutôt que de créer un profil VALID_PROFILES par catégorie détectée
(x86, unreal, vulkan, eac...), ce module expose des PROPRIÉTÉS d'un
exécutable sous forme d'un simple dict — à detect_exe_type_legacy() (ou
à tout autre appelant) de décider quoi en faire.

Deux familles de détection, séparées volontairement :

  1. Analyse du PE lui-même (read_pe_info) : architecture (machine type)
     et DLL réellement IMPORTÉES par l'exécutable (table d'imports).
     C'est la seule méthode fiable pour l'API graphique — d3d11.dll,
     vulkan-1.dll etc. sont des DLL SYSTÈME résolues par Wine/Proton à
     l'exécution ; leur simple présence dans le dossier du jeu ne
     prouve rien (la plupart du temps elles n'y sont même pas), alors
     que la table d'imports du PE indique précisément ce que
     l'exécutable a été compilé pour utiliser.

  2. Signatures de dossier (detect_engine, detect_electron, ...) : pour
     les éléments qui SONT réellement livrés à côté de l'exécutable
     (UnityPlayer.dll, Engine/Binaries/, resources/app.asar...), une
     simple lecture de dossier suffit et évite une analyse PE inutile.

Aucune dépendance externe : le parseur PE est un sous-ensemble minimal
et tolérant du format (struct uniquement), qui ne lève jamais — un
exécutable packé/protégé/tronqué renvoie simplement des résultats
vides plutôt qu'une exception.
"""

import os
import struct

from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.profiles.capabilities")


# ------------------------------------------------------------------------------------
# ANALYSE PE (architecture + table d'imports) — pure, sans GTK, sans dépendance
# ------------------------------------------------------------------------------------

# Machine type -> architecture, cf. IMAGE_FILE_HEADER.Machine (spec PE/COFF)
_ARCH_BY_MACHINE = {
    0x014C: "x86",
    0x8664: "x64",
    0xAA64: "arm64",
    0x01C0: "arm",
    0x01C4: "arm",   # ARMNT
}

# Taille max lue par exécutable : largement suffisant pour DOS header +
# COFF header + Optional header + table des sections + table d'imports
# (tout ça tient presque toujours dans les tout premiers Ko d'un PE),
# tout en bornant la lecture pour ne jamais charger un exécutable de
# plusieurs centaines de Mo en mémoire pour une simple inspection
# d'en-tête.
_PE_READ_LIMIT = 8 * 1024 * 1024


def _read_head(exe_path):
    try:
        with open(exe_path, "rb") as f:
            return f.read(_PE_READ_LIMIT)
    except OSError as e:
        logger.debug(f"[capabilities] {exe_path} illisible: {e}")
        return None


def read_pe_info(exe_path):
    """
    Parseur PE minimal : renvoie (machine, imports).

      machine : entier IMAGE_FILE_HEADER.Machine, ou None si le
                fichier n'est pas un PE valide / illisible.
      imports : set[str] des noms de DLL importées (en minuscules),
                vide si la table d'imports n'a pas pu être lue (fichier
                packé/protégé avec une structure non standard, PE sans
                imports statiques, erreur de parsing...).

    Ne lève jamais : toute anomalie de structure retombe sur un
    résultat partiel (machine connu mais imports vides) ou (None, set()).
    """

    data = _read_head(exe_path)

    if not data or len(data) < 64 or data[:2] != b"MZ":
        return None, set()

    try:
        pe_offset = struct.unpack_from("<I", data, 0x3C)[0]

        if pe_offset <= 0 or pe_offset + 24 > len(data):
            return None, set()

        if data[pe_offset:pe_offset + 4] != b"PE\x00\x00":
            return None, set()

        coff_offset = pe_offset + 4
        machine, num_sections = struct.unpack_from("<HH", data, coff_offset)
        size_opt_header = struct.unpack_from("<H", data, coff_offset + 16)[0]

        opt_header_offset = coff_offset + 20

        if size_opt_header < 2 or opt_header_offset + 2 > len(data):
            # En-tête COFF exploitable (donc architecture connue), mais
            # pas d'en-tête optionnel exploitable -> pas d'imports.
            return machine, set()

        magic = struct.unpack_from("<H", data, opt_header_offset)[0]

        if magic == 0x10B:       # PE32   (32-bit)
            data_dir_offset = opt_header_offset + 96
        elif magic == 0x20B:     # PE32+  (64-bit)
            data_dir_offset = opt_header_offset + 112
        else:
            return machine, set()

        # DataDirectory[1] = Import Table (RVA, Size)
        if data_dir_offset + 16 > len(data):
            return machine, set()

        import_rva, import_size = struct.unpack_from("<II", data, data_dir_offset + 8)

        if not import_rva or not import_size:
            return machine, set()

        # Table des sections (juste après l'en-tête optionnel), pour
        # convertir les RVA du PE en offsets réels dans le fichier.
        section_table_offset = opt_header_offset + size_opt_header
        sections = []

        for i in range(num_sections):
            off = section_table_offset + i * 40
            if off + 40 > len(data):
                break
            virt_size, virt_addr, raw_size, raw_ptr = struct.unpack_from(
                "<IIII", data, off + 8
            )
            sections.append((virt_addr, max(virt_size, raw_size), raw_ptr))

        def rva_to_offset(rva):
            for virt_addr, size, raw_ptr in sections:
                if virt_addr <= rva < virt_addr + size:
                    return raw_ptr + (rva - virt_addr)
            return None

        def read_cstring(offset, limit=256):
            if offset is None or offset >= len(data):
                return None
            end = data.find(b"\x00", offset, min(offset + limit, len(data)))
            if end == -1:
                return None
            return data[offset:end].decode("ascii", errors="ignore")

        import_table_offset = rva_to_offset(import_rva)

        if import_table_offset is None:
            return machine, set()

        imports = set()
        descriptor_size = 20  # sizeof(IMAGE_IMPORT_DESCRIPTOR)
        offset = import_table_offset

        # Le tableau de descripteurs se termine par une entrée entièrement
        # nulle. Borne de sécurité (256 DLL importées, très généreux même
        # pour un jeu moderne) pour ne jamais boucler indéfiniment sur un
        # fichier corrompu dont le tableau ne se termine jamais.
        for _ in range(256):
            if offset + descriptor_size > len(data):
                break

            first_thunk = struct.unpack_from("<I", data, offset)[0]
            name_rva = struct.unpack_from("<I", data, offset + 12)[0]

            if name_rva == 0 and first_thunk == 0:
                break  # entrée nulle = fin du tableau

            if name_rva:
                name = read_cstring(rva_to_offset(name_rva))
                if name:
                    imports.add(name.lower())

            offset += descriptor_size

        return machine, imports

    except (struct.error, IndexError, ValueError) as e:
        logger.debug(f"[capabilities] Erreur de parsing PE pour {exe_path}: {e}")
        return None, set()


def detect_architecture(machine):
    """machine : valeur renvoyée par read_pe_info(). None -> 'unknown'.
    N'est volontairement PAS exposé comme un profil VALID_PROFILES à
    part entière (cf. discussion) — c'est une propriété, à combiner par
    l'appelant avec d'autres critères (ex. DirectDraw + x86 -> oldgame)."""
    if machine is None:
        return "unknown"
    return _ARCH_BY_MACHINE.get(machine, "unknown")


# ------------------------------------------------------------------------------------
# API GRAPHIQUE / DIRECTDRAW / AUDIO / PHYSX — à partir de la table d'imports
# ------------------------------------------------------------------------------------

# dxgi.dll est volontairement absente : partagée par dx10/11/12, sa seule
# présence ne permet pas de distinguer laquelle des trois est utilisée.
_GRAPHICS_DLLS = {
    "dx8": ("d3d8.dll",),
    "dx9": ("d3d9.dll",),
    "dx10": ("d3d10.dll", "d3d10_1.dll"),
    "dx11": ("d3d11.dll",),
    "dx12": ("d3d12.dll",),
    "opengl": ("opengl32.dll",),
    "vulkan": ("vulkan-1.dll",),
}


def detect_graphics_api(imports):
    """dict {api: bool} à partir des DLL importées (cf. read_pe_info)."""
    return {
        api: any(dll in imports for dll in dlls)
        for api, dlls in _GRAPHICS_DLLS.items()
    }


_DIRECTDRAW_DLLS = ("ddraw.dll", "d3dim.dll", "dsound.dll")


def detect_directdraw(imports):
    return any(dll in imports for dll in _DIRECTDRAW_DLLS)


# Ordre volontaire : Wwise et FMOD avant XAudio/OpenAL, qu'ils utilisent
# fréquemment eux-mêmes en interne comme backend bas niveau — sans quoi
# un jeu Wwise serait aussi (à tort) détecté comme "xaudio".
_AUDIO_ENGINE_DLLS = (
    ("wwise", ("aksoundengine.dll",)),
    ("fmod", ("fmod.dll", "fmodstudio.dll", "fmodex.dll")),
    ("xaudio", tuple(f"xaudio2_{n}.dll" for n in range(0, 8))),
    ("openal", ("openal32.dll",)),
)


def detect_audio_engine(imports):
    for name, dlls in _AUDIO_ENGINE_DLLS:
        if any(dll in imports for dll in dlls):
            return name
    return None


def detect_physx(imports):
    return any(dll.startswith("physx") for dll in imports)


# ------------------------------------------------------------------------------------
# SIGNATURES DE DOSSIER — moteur, Electron, CEF, Java, XNA, anti-cheat
# ------------------------------------------------------------------------------------

def _list_dir(exe_dir):
    try:
        return set(os.listdir(exe_dir))
    except OSError:
        return set()


def detect_engine(exe_dir):
    """Unity / Unreal / Godot : signatures fiables car réellement
    livrées à côté de l'exécutable — contrairement aux DLL graphiques
    (résolues dynamiquement par Wine/Proton), on peut ici se contenter
    d'une lecture de dossier."""
    files = _list_dir(exe_dir)

    if "UnityPlayer.dll" in files or any(f.endswith("_Data") for f in files):
        return "unity"

    if "Engine" in files and os.path.isdir(os.path.join(exe_dir, "Engine")):
        return "unreal"

    if any(f.lower().startswith(("ue4game", "ue5game")) for f in files):
        return "unreal"

    if any("godot" in f.lower() for f in files):
        return "godot"

    return None


def detect_electron(exe_dir):
    resources_dir = os.path.join(exe_dir, "resources")
    contents = _list_dir(resources_dir)
    return "app.asar" in contents or "electron.asar" in contents


def detect_cef(exe_dir):
    files = _list_dir(exe_dir)
    return bool({"libcef.dll", "chrome.dll", "icudtl.dat"} & files)


def detect_java(exe_dir):
    files = _list_dir(exe_dir)
    if {"java.exe", "javaw.exe", "jvm.dll"} & files:
        return True
    return any(f.lower().endswith(".jar") for f in files)


def detect_xna(exe_dir):
    files = _list_dir(exe_dir)
    return bool(
        {"Microsoft.Xna.Framework.dll", "Microsoft.Xna.Framework.Game.dll"} & files
    )


# Signatures cherchées dans les noms de fichiers/dossiers (sous-chaîne,
# insensible à la casse) — les deux systèmes d'anti-cheat les plus
# courants sur les jeux distribués via Steam/launchers Windows.
_ANTICHEAT_MARKERS = (
    ("eac", ("easyanticheat",)),
    ("battleye", ("battleye", "beclient")),
)


def detect_anticheat(exe_dir):
    files = {f.lower() for f in _list_dir(exe_dir)}
    for name, markers in _ANTICHEAT_MARKERS:
        if any(marker in f for marker in markers for f in files):
            return name
    return None


# ------------------------------------------------------------------------------------
# POINT D'ENTRÉE UNIQUE
# ------------------------------------------------------------------------------------

def detect_capabilities(exe_path):
    """
    Analyse complète d'un exécutable : une seule lecture du PE + une
    seule lecture de dossier, pour alimenter toutes les détections
    ci-dessus sans réanalyser le fichier à chaque appel individuel.

    Retourne un dict de « capabilities », pensé pour être étendu sans
    jamais devoir ajouter un profil VALID_PROFILES dédié par catégorie :

        {
            "architecture": "x64",
            "graphics": {"dx8": False, "dx9": False, "dx10": False,
                         "dx11": True, "dx12": False, "opengl": False,
                         "vulkan": False},
            "directdraw": False,
            "audio": "fmod" | None,
            "physx": False,
            "engine": "unity" | "unreal" | "godot" | None,
            "electron": False,
            "cef": False,
            "java": False,
            "xna": False,
            "anti_cheat": "eac" | "battleye" | None,
        }
    """
    exe_dir = os.path.dirname(exe_path) or "."

    machine, imports = read_pe_info(exe_path)

    capabilities = {
        "architecture": detect_architecture(machine),
        "graphics": detect_graphics_api(imports),
        "directdraw": detect_directdraw(imports),
        "audio": detect_audio_engine(imports),
        "physx": detect_physx(imports),
        "engine": detect_engine(exe_dir),
        "electron": detect_electron(exe_dir),
        "cef": detect_cef(exe_dir),
        "java": detect_java(exe_dir),
        "xna": detect_xna(exe_dir),
        "anti_cheat": detect_anticheat(exe_dir),
    }

    logger.debug(f"[detect_capabilities] {os.path.basename(exe_path)}: {capabilities}")

    return capabilities
