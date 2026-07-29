# i18n.py
import os
import locale
from typing import Optional
import sys
#------------------------------------------------------------------------------------
def detect_help_env_lang():
    """
    Détecte la langue pour --help-env :
    priorité = CLI > env LANGUAGE > défaut en
    """

    # 1. Override CLI
    if "--en" in sys.argv:
        return "en"
    if "--fr" in sys.argv:
        return "fr"
    if "--uk" in sys.argv:
        return "uk"
    if "--de" in sys.argv:
        return "de"
    if "--zh" in sys.argv:
        return "zh"
    if "--hi" in sys.argv:
        return "hi"
    if "--es" in sys.argv:
        return "es"
    if "--pt" in sys.argv:
        return "pt"

    # 2. Variable d'environnement système
    lang_env = os.environ.get("LANGUAGE") or os.environ.get("LANG")

    if lang_env:
        lang_env = lang_env.lower()

        if lang_env.startswith("fr"):
            return "fr"
        if lang_env.startswith("en"):
            return "en"
        if lang_env.startswith("de"):
            return "de"
        if lang_env.startswith("uk"):
            return "uk"
        if lang_env.startswith("zh"):
            return "zh"
        if lang_env.startswith("hi"):
            return "hi"
        if lang_env.startswith("es"):
            return "es"
        if lang_env.startswith("pt"):
            return "pt"

    # 3. défaut
    return "en"

LANG = {
    "en": {
        "no_proton_installation": "No Proton installation found",
        "detected_proton_installations": "Detected Proton installations",
        "selected": "selected",
        "prefix_name": "Prefix name (empty = auto)",
        "diagnostic": "proton-autogen diagnostic",
        "version": "Version",
        "python": "Python",
        "runtime": "Runtime",
        "wine": "Wine",
        "yes": "yes",
        "no": "no",
        "none": "none",
        "platform": "Platform",
        "detected_programs": "Detected Windows programs",
        "no_windows_programs": "No Windows programs found",

        "search_finished": "The program search finished in {time:.3f}s",

        "load_config_prefix": "LOAD CONFIG PREFIX : {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "mangohud": "MangoHud",
        "runtime_information": "Runtime information",
        "executable": "Executable",
        "proton": "Proton",
        "path": "Path",
        "detected": "Detected",
        "missing": "Missing",
        "available": "Available",
        "unavailable": "Unavailable",
        "favorite": "Favorite",
        "favorites": "Favorites",
        "playtime": "Play time",
        "remove_from_library": "Remove game from library",
        "export_lutris": "Export Lutris (.yml)",
        "edit": "Edit",
        "checking_executable": "Checking executable",
        "loading_game_configuration": "Loading game configuration",
        "detecting_system": "Detecting system",
        "starting_proton": "Starting Proton",
        "starting_wine": "Starting Wine",
        "runtime_selected": "Proton runtime selected",
        "missing_executable_title": "Missing executable",
        "missing_executable_message": "Executable not found",
        "starting_proton_call": "Starting Proton Call",
        "run_started": "Run started",
        "config_read_error": "Configuration read error {file}: {error}",
        "proton_not_found": """
        No Proton installation found.

        Install a Proton version (e.g. via ProtonUp-Qt)
        or specify PROTON_PATH.

        Command line:
          protonup -d ~/.steam/root/compatibilitytools.d

        Restart Steam and try again.
        """,
    },

    "fr": {
        "no_proton_installation": "Aucune installation Proton trouvée",
        "detected_proton_installations": "Installations Proton détectées",
        "selected": "sélectionné",
        "prefix_name": "Nom du prefix (vide = automatique)",
        "diagnostic": "Diagnostic proton-autogen",
        "version": "Version",
        "python": "Python",
        "runtime": "Environnement",
        "wine": "Wine",
        "yes": "oui",
        "no": "non",
        "none": "aucune",
        "platform": "Plateforme",
        "detected_programs": "Programmes Windows détectés",
        "no_windows_programs": "Aucun programme Windows trouvé",

        "search_finished": "Recherche terminée en {time:.3f}s",

        "load_config_prefix": "CHARGEMENT CONFIG PREFIX : {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "mangohud": "MangoHud",
        "runtime_information": "Informations d'exécution",
        "executable": "Exécutable",
        "proton": "Proton",
        "path": "Chemin",
        "detected": "Détecté",
        "missing": "Manquant",
        "available": "Disponible",
        "unavailable": "Indisponible",
        "favorite": "Favori",
        "favorites": "Favoris",
        "playtime": "Temps de jeu",
        "remove_from_library": "Retirer le jeu de la bibliothèque",
        "export_lutris": "Exporter vers Lutris (.yml)",
        "edit": "Modifier",
        "checking_executable": "Vérification de l'exécutable",
        "loading_game_configuration": "Chargement de la configuration du jeu",
        "detecting_system": "Détection du système",
        "starting_proton": "Lancement de Proton",
        "starting_wine": "Lancement de Wine",
        "runtime_selected": "Environnement Proton sélectionné",
        "missing_executable_title": "Exécutable manquant",
        "missing_executable_message": "L'exécutable est introuvable",
        "starting_proton_call": "Lancement de Proton Call",
        "run_started": "Lancement terminé",
        "config_read_error": "Erreur de lecture de configuration {file}: {error}",
        "proton_not_found": """
        Aucune installation Proton trouvée.

        Installez une version de Proton (par exemple avec ProtonUp-Qt)
        ou définissez PROTON_PATH.

        Commande :
          protonup -d ~/.steam/root/compatibilitytools.d

        Redémarrez Steam puis réessayez.
        """,
    },

    "zh": {
        "no_proton_installation": "未找到 Proton 安装",
        "detected_proton_installations": "检测到的 Proton 安装",
        "selected": "已选择",
        "prefix_name": "Prefix 名称（留空 = 自动）",
        "diagnostic": "proton-autogen 诊断",
        "version": "版本",
        "python": "Python",
        "runtime": "运行环境",
        "wine": "Wine",
        "yes": "是",
        "no": "否",
        "none": "无",
        "platform": "平台",
        "detected_programs": "检测到的 Windows 程序",
        "no_windows_programs": "未找到 Windows 程序",

        "search_finished": "搜索完成，用时 {time:.3f} 秒",

        "load_config_prefix": "加载配置前缀：{prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "mangohud": "MangoHud",
        "runtime_information": "运行环境信息",
        "executable": "可执行文件",
        "proton": "Proton",
        "path": "路径",
        "detected": "已检测",
        "missing": "缺失",
        "available": "可用",
        "unavailable": "不可用",
        "favorite": "收藏",
        "favorites": "收藏夹",
        "playtime": "游戏时间",
        "remove_from_library": "从库中移除游戏",
        "export_lutris": "导出到 Lutris (.yml)",
        "edit": "编辑",
        "checking_executable": "正在检查可执行文件",
        "loading_game_configuration": "正在加载游戏配置",
        "detecting_system": "正在检测系统",
        "starting_proton": "正在启动 Proton",
        "starting_wine": "正在启动 Wine",
        "runtime_selected": "已选择 Proton 运行环境",
        "missing_executable_title": "缺少可执行文件",
        "missing_executable_message": "未找到可执行文件",
        "starting_proton_call": "正在启动 Proton Call",
        "run_started": "启动完成",
        "config_read_error": "读取配置错误 {file}: {error}",
        "proton_not_found": """
                        未找到 Proton 安装。

                        请安装 Proton 版本（例如使用 ProtonUp-Qt）
                        或设置 PROTON_PATH。

                        命令：
                          protonup -d ~/.steam/root/compatibilitytools.d

                        请重启 Steam 后重试。
                        """,
    },
}



CURRENT_LANG = "en"

def _get_system_locale() -> Optional[str]:
    """Récupère la locale système via les variables d'environnement,
    puis via le module locale en dernier recours."""

    # LANGUAGE peut être une liste "fr_FR:en_US:en" -> on prend le 1er élément
    raw = (
        os.environ.get("LANGUAGE")
        or os.environ.get("LC_ALL")
        or os.environ.get("LC_MESSAGES")
        or os.environ.get("LANG")
    )

    if raw:
        return raw.split(":")[0]

    # Fallback : API moderne, remplace getdefaultlocale() (supprimée en 3.13)
    try:
        loc = locale.getlocale()
        if loc and loc[0]:
            return loc[0]
    except Exception:
        pass

    return None


def detect_language() -> str:
    """
    Détecte la langue du système.
    Retourne une langue supportée par LANG (fallback "en").
    """
    system_lang = _get_system_locale()

    if not system_lang:
        return "en"

    # Exemple:
    # fr_FR.UTF-8 -> fr
    # zh_CN.UTF-8 -> zh
    # en_US.UTF-8 -> en
    normalized = (
        system_lang
        .lower()
        .replace("-", "_")
        .split(".")[0]
    )

    lang = normalized.split("_")[0]

    return lang if lang in LANG else "en"


def set_language(lang: Optional[str]) -> None:
    global CURRENT_LANG

    if not lang or not isinstance(lang, str):
        CURRENT_LANG = detect_language()
        return

    lang = lang.lower().replace("-", "_").split("_")[0]
    CURRENT_LANG = lang if lang in LANG else "en"


def init_language() -> None:
    """Initialise automatiquement la langue depuis le système."""
    set_language(detect_language())


def get_language() -> str:
    return CURRENT_LANG


def tr(key: str, **kwargs) -> str:
    """Traduit une clé, avec repli sur l'anglais si absente."""
    lang_table = LANG.get(CURRENT_LANG, LANG["en"])
    text = lang_table.get(key, LANG["en"].get(key, key))

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            # Évite un crash si un placeholder attendu manque dans kwargs
            return text

    return text
