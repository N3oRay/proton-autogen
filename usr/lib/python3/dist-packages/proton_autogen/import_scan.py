# import_scan.py
"""
Import global des installations Wine/Proton existantes.

Sources couvertes : Lutris, Bottles, Heroic, préfixes Wine "nus".
Steam est volontairement exclu (déjà géré par Steam + son propre Proton).
Installations natives uniquement — pas de support Flatpak pour le moment.

Philosophie : chaque scanner est indépendant et silencieux à l'échec
(un lanceur absent ne doit jamais faire planter le scan global), et
retourne une liste plate de dicts normalisés. La création du profil de
jeu proton-autogen reste déléguée à editor.add_game_ux() : ce module
NE duplique PAS la logique d'écriture de config, et NE modifie PAS le
comportement existant de l'application (add_game_ux / find_proton
restent inchangés pour tous les appels hors import).
"""

import os
import json
import sqlite3

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def _expand(p: str) -> str:
    return os.path.expanduser(os.path.expandvars(p))


# Exécutables présents par défaut dans (quasi) tout préfixe Wine, jamais
# installés volontairement par l'utilisateur : utilitaires Windows/Wine
# fournis d'office (Internet Explorer, Bloc-notes, Wordpad, etc.) ainsi
# que les binaires de Wine lui-même. À exclure systématiquement du scan
# des préfixes "nus", faute de quoi ils remontent une fois par préfixe.
_WINE_BUILTIN_EXES = {
    "iexplore.exe",
    "notepad.exe",
    "wordpad.exe",
    "mspaint.exe",
    "regedit.exe",
    "taskmgr.exe",
    "control.exe",
    "explorer.exe",
    "winecfg.exe",
    "wineboot.exe",
    "winefile.exe",
    "wineconsole.exe",
    "msiexec.exe",
    "rundll32.exe",
    "cmd.exe",
    "write.exe",
    "wmplayer.exe",
    "hh.exe",
    "regsvr32.exe",
    "eject.exe",
    "start.exe",
    "reg.exe",
    "regedt32.exe",
    "progman.exe",
}


def _is_real_exe(name: str) -> bool:
    """Filtre les faux positifs évidents : désinstalleurs, redistribuables,
    et exécutables Windows/Wine fournis par défaut dans tout préfixe."""
    n = name.lower()

    if n in _WINE_BUILTIN_EXES:
        return False

    junk = ("unins", "setup", "vcredist", "dxsetup", "directx", "_installer")
    return not any(j in n for j in junk)


# ----------------------------------------------------------------------
# LUTRIS (natif : ~/.config/lutris + ~/.local/share/lutris)
# ----------------------------------------------------------------------
def scan_lutris() -> dict:
    """
    Les métadonnées (nom, slug, configpath, runner) vivent en sqlite
    (pga.db), la config technique par jeu (exe, prefix) en YAML dans
    games/*.yml. Le nom de fichier YAML n'est PAS "{slug}.yml" : Lutris
    lui ajoute un suffixe numérique unique ("{slug}-{id}.yml"), stocké
    dans la colonne configpath de la table games. On retombe sur
    "{slug}.yml" seulement si configpath est absent (anciennes bases).
    Seuls les jeux runner='wine' et installed=1 sont retenus.
    """
    if not HAS_YAML:
        return {"available": False, "count": 0, "items": [], "reason": "PyYAML absent"}

    db_path = os.path.expanduser("~/.local/share/lutris/pga.db")
    yml_dir = os.path.expanduser("~/.config/lutris/games")

    if not os.path.isfile(db_path) or not os.path.isdir(yml_dir):
        return {"available": False, "count": 0, "items": []}

    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(
            "SELECT slug, name, configpath FROM games "
            "WHERE installed = 1 AND runner = 'wine'"
        )
        rows = cur.fetchall()
        con.close()
    except Exception:
        return {"available": False, "count": 0, "items": []}

    items = []
    for slug, name, configpath in rows:
        yml_filename = f"{configpath}.yml" if configpath else f"{slug}.yml"
        yml_path = os.path.join(yml_dir, yml_filename)
        exe_path, prefix_path = None, None

        if os.path.isfile(yml_path):
            try:
                with open(yml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                game = data.get("game", {}) or {}
                if game.get("exe"):
                    exe_path = _expand(game["exe"])
                if game.get("prefix"):
                    prefix_path = _expand(game["prefix"])
            except Exception:
                pass

        items.append({
            "source": "lutris",
            "name": name,
            "exe_path": exe_path,
            "prefix_path": prefix_path,
            "needs_manual_exe": exe_path is None,
            "raw_id": slug,
        })

    return {"available": True, "count": len(items), "items": items}


# ----------------------------------------------------------------------
# BOTTLES (natif : ~/.local/share/bottles/bottles)
# ----------------------------------------------------------------------
def scan_bottles() -> dict:
    """
    Chaque "bottle" = un préfixe. On lit bottle.yml pour la liste des
    programmes déclarés (External_Programs / Programs selon version).
    À défaut, repli sur un scan borné des .exe dans drive_c.
    """
    base = os.path.expanduser("~/.local/share/bottles/bottles")
    if not os.path.isdir(base) or not HAS_YAML:
        return {"available": False, "count": 0, "items": []}

    items = []
    try:
        bottle_names = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
    except OSError:
        return {"available": False, "count": 0, "items": []}

    for bottle_name in bottle_names:
        bottle_dir = os.path.join(base, bottle_name)
        yml_path = os.path.join(bottle_dir, "bottle.yml")

        programs = {}
        if os.path.isfile(yml_path):
            try:
                with open(yml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                programs = data.get("External_Programs") or data.get("Programs") or {}
            except Exception:
                programs = {}

        if programs:
            for prog_key, prog_data in programs.items():
                exe = prog_data.get("path") if isinstance(prog_data, dict) else None
                items.append({
                    "source": "bottles",
                    "name": prog_data.get("name", prog_key) if isinstance(prog_data, dict) else prog_key,
                    "exe_path": _expand(exe) if exe else None,
                    "prefix_path": bottle_dir,
                    "needs_manual_exe": exe is None,
                    "raw_id": f"{bottle_name}:{prog_key}",
                })
        else:
            drive_c = os.path.join(bottle_dir, "drive_c")
            if os.path.isdir(drive_c):
                for root, dirs, files in os.walk(drive_c):
                    depth = root[len(drive_c):].count(os.sep)
                    if depth >= 4:
                        dirs[:] = []
                        continue
                    if "windows" in root.lower():
                        continue
                    for f in files:
                        if f.lower().endswith(".exe") and _is_real_exe(f):
                            items.append({
                                "source": "bottles",
                                "name": os.path.splitext(f)[0],
                                "exe_path": os.path.join(root, f),
                                "prefix_path": bottle_dir,
                                "needs_manual_exe": False,
                                "raw_id": f"{bottle_name}:{f}",
                            })

    return {"available": True, "count": len(items), "items": items}


# ----------------------------------------------------------------------
# HEROIC (natif : ~/.config/heroic — Epic via legendary + GOG)
# ----------------------------------------------------------------------
def scan_heroic() -> dict:
    base = os.path.expanduser("~/.config/heroic")
    if not os.path.isdir(base):
        return {"available": False, "count": 0, "items": []}

    items = []
    sources = [
        os.path.join(base, "legendaryConfig", "legendary", "installed.json"),
        os.path.join(base, "gog_store", "installed.json"),
    ]

    for src in sources:
        if not os.path.isfile(src):
            continue
        try:
            with open(src, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        entries = data.values() if isinstance(data, dict) else data
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if entry.get("platform", "Windows") != "Windows":
                continue  # jeux nativement Linux : rien à importer côté Proton

            install_path = entry.get("install_path", "")
            executable = entry.get("executable", "")
            exe_path = os.path.join(install_path, executable) if install_path and executable else None

            app_name = entry.get("app_name", "")
            prefix_path = None
            cfg_path = os.path.join(base, "GamesConfig", f"{app_name}.json")
            if os.path.isfile(cfg_path):
                try:
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    prefix_path = cfg.get(app_name, {}).get("winePrefix")
                except Exception:
                    pass

            items.append({
                "source": "heroic",
                "name": entry.get("title", app_name),
                "exe_path": _expand(exe_path) if exe_path else None,
                "prefix_path": _expand(prefix_path) if prefix_path else None,
                "needs_manual_exe": exe_path is None,
                "raw_id": app_name,
            })

    return {"available": bool(items), "count": len(items), "items": items}


# ----------------------------------------------------------------------
# PRÉFIXES WINE "NUS"
# ----------------------------------------------------------------------
_DEFAULT_WINE_LOCATIONS = (
    "~/.wine",
    "~/Games",
    "~/.local/share/wineprefixes",
    "~/.PlayOnLinux/wineprefix",
)


def _looks_like_prefix(path: str) -> bool:
    return os.path.isdir(os.path.join(path, "drive_c")) and (
        os.path.isfile(os.path.join(path, "system.reg"))
        or os.path.isfile(os.path.join(path, "user.reg"))
    )


def scan_wine_prefixes(extra_paths: list = None) -> dict:
    """
    Scanne les emplacements connus + les chemins fournis en cas d'échec
    du scan par défaut (cf. --import en CLI / dialog GTK). Exclut le
    PREFIX_DIR déjà géré par proton-autogen pour ne pas se réimporter
    lui-même.
    """
    from proton_autogen.config import load_prefix_dir

    locations = list(_DEFAULT_WINE_LOCATIONS) + (extra_paths or [])
    known_root = os.path.realpath(load_prefix_dir())
    items = []

    for loc in locations:
        loc = _expand(loc)
        if not os.path.isdir(loc):
            continue

        candidates = [loc] if _looks_like_prefix(loc) else [
            os.path.join(loc, d) for d in os.listdir(loc)
            if os.path.isdir(os.path.join(loc, d))
        ]

        for prefix_dir in candidates:
            if not _looks_like_prefix(prefix_dir):
                continue
            if os.path.realpath(prefix_dir).startswith(known_root):
                continue  # déjà géré par proton-autogen

            drive_c = os.path.join(prefix_dir, "drive_c")
            for root, dirs, files in os.walk(drive_c):
                depth = root[len(drive_c):].count(os.sep)
                if depth >= 3:
                    dirs[:] = []
                    continue
                if "windows" in root.lower() or "programdata" in root.lower():
                    continue
                for f in files:
                    if f.lower().endswith(".exe") and _is_real_exe(f):
                        items.append({
                            "source": "wine",
                            "name": os.path.splitext(f)[0],
                            "exe_path": os.path.join(root, f),
                            "prefix_path": prefix_dir,
                            "needs_manual_exe": False,
                            "raw_id": os.path.join(root, f),
                        })

    return {"available": True, "count": len(items), "items": items}


# ----------------------------------------------------------------------
# AGRÉGATEUR
# ----------------------------------------------------------------------
def scan_all(extra_wine_paths: list = None) -> dict:
    return {
        "lutris": scan_lutris(),
        "bottles": scan_bottles(),
        "heroic": scan_heroic(),
        "wine": scan_wine_prefixes(extra_wine_paths),
    }


def any_source_available(results: dict) -> bool:
    return any(r.get("available") and r.get("count", 0) > 0 for r in results.values())


def total_count(results: dict) -> int:
    return sum(r.get("count", 0) for r in results.values())


# ----------------------------------------------------------------------
# IMPORT EFFECTIF — find_proton() résolu UNE SEULE FOIS pour tout le batch
# ----------------------------------------------------------------------
def import_selected(results: dict, enabled_sources: set) -> dict:
    """
    Importe les items des sources cochées via add_game_ux (comportement
    existant inchangé). find_proton() n'est appelé qu'une fois ici, et
    réutilisé pour chaque jeu du batch via le paramètre proton=... de
    add_game_ux — ce paramètre est optionnel et ne change rien aux
    appels existants ailleurs dans l'application.

    Retourne {imported, skipped, errors}.
    """
    from proton_autogen.editor import add_game_ux
    from proton_autogen.loader import get_game_config_path
    from proton_autogen.diag import find_proton

    cached_proton = find_proton()  # un seul appel pour tout le batch

    imported, skipped, errors = 0, 0, []

    for source, data in results.items():
        if source not in enabled_sources:
            continue

        for item in data.get("items", []):
            exe_path = item.get("exe_path")

            if not exe_path or not os.path.isfile(exe_path):
                skipped += 1
                continue

            config_path, _ = get_game_config_path(exe_path)
            if os.path.isfile(config_path):
                skipped += 1  # déjà présent : ne pas écraser un profil existant
                continue

            prefix = None
            if item.get("prefix_path") and os.path.isdir(item["prefix_path"]):
                prefix = {
                    "name": f"{item['source']}-{os.path.basename(item['prefix_path'])}",
                    "path": item["prefix_path"],
                }

            try:
                add_game_ux(exe_path, prefix=prefix, proton=cached_proton)
                imported += 1
            except Exception as e:
                errors.append({"exe": exe_path, "error": str(e)})

    return {"imported": imported, "skipped": skipped, "errors": errors}
