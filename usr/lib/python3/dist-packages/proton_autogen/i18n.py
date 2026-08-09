# i18n.py
import os
import locale
from typing import Optional
import sys
#------------------------------------------------------------------------------------
def detect_help_env_lang():
    """
    Détecte la langue pour --help-env :
    priorité = CLI > env LANGUAGE/LANG > défaut en
    """
    for arg in sys.argv:
        if arg.startswith("--") and arg[2:] in LANG:
            return arg[2:]

    lang_env = (os.environ.get("LANGUAGE") or os.environ.get("LANG") or "").lower()
    for code in LANG:
        if lang_env.startswith(code):
            return code

    return "en"

def _check_translation_completeness():
    """Vérifie que toutes les langues définissent les mêmes clés que 'en'."""
    reference_keys = set(LANG["en"].keys())
    for lang_code, table in LANG.items():
        if lang_code == "en":
            continue
        missing = reference_keys - set(table.keys())
        if missing:
            print(f"[i18n] WARNING: langue '{lang_code}' — clés manquantes: {sorted(missing)}")

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
        "xrandr": "Xrandr",
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

    "uk": {
        "no_proton_installation": "Встановлення Proton не знайдено",
        "detected_proton_installations": "Виявлені встановлення Proton",
        "selected": "вибрано",
        "prefix_name": "Назва префікса (порожньо = автоматично)",
        "diagnostic": "діагностика proton-autogen",
        "version": "Версія",
        "python": "Python",
        "runtime": "Середовище виконання",
        "wine": "Wine",
        "yes": "так",
        "no": "ні",
        "none": "немає",
        "platform": "Платформа",
        "detected_programs": "Виявлені програми Windows",
        "no_windows_programs": "Програми Windows не знайдено",

        "search_finished": "Пошук програм завершено за {time:.3f} с",

        "load_config_prefix": "ЗАВАНТАЖЕННЯ ПРЕФІКСА КОНФІГУРАЦІЇ : {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "xrandr": "Xrandr",
        "mangohud": "MangoHud",
        "runtime_information": "Інформація про середовище виконання",
        "executable": "Виконуваний файл",
        "proton": "Proton",
        "path": "Шлях",
        "detected": "Виявлено",
        "missing": "Відсутнє",
        "available": "Доступно",
        "unavailable": "Недоступно",
        "favorite": "Улюблене",
        "favorites": "Улюблені",
        "playtime": "Час гри",
        "remove_from_library": "Видалити гру з бібліотеки",
        "export_lutris": "Експортувати до Lutris (.yml)",
        "edit": "Редагувати",
        "checking_executable": "Перевірка виконуваного файлу",
        "loading_game_configuration": "Завантаження конфігурації гри",
        "detecting_system": "Визначення системи",
        "starting_proton": "Запуск Proton",
        "starting_wine": "Запуск Wine",
        "runtime_selected": "Середовище виконання Proton вибрано",
        "missing_executable_title": "Виконуваний файл відсутній",
        "missing_executable_message": "Виконуваний файл не знайдено",
        "starting_proton_call": "Запуск Proton Call",
        "run_started": "Запуск розпочато",
        "config_read_error": "Помилка читання конфігурації {file}: {error}",
        "proton_not_found": """
        Встановлення Proton не знайдено.

        Встановіть версію Proton (наприклад, через ProtonUp-Qt)
        або вкажіть PROTON_PATH.

        Командний рядок:
          protonup -d ~/.steam/root/compatibilitytools.d

        Перезапустіть Steam і спробуйте ще раз.
        """,
    },



    "pt": {
        "no_proton_installation": "Nenhuma instalação do Proton encontrada",
        "detected_proton_installations": "Instalações do Proton detectadas",
        "selected": "selecionado",
        "prefix_name": "Nome do prefixo (vazio = automático)",
        "diagnostic": "diagnóstico do proton-autogen",
        "version": "Versão",
        "python": "Python",
        "runtime": "Ambiente de execução",
        "wine": "Wine",
        "yes": "sim",
        "no": "não",
        "none": "nenhum",
        "platform": "Plataforma",
        "detected_programs": "Programas do Windows detectados",
        "no_windows_programs": "Nenhum programa do Windows encontrado",

        "search_finished": "A pesquisa de programas terminou em {time:.3f}s",

        "load_config_prefix": "CARREGANDO PREFIXO DE CONFIGURAÇÃO : {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "xrandr": "Xrandr",
        "mangohud": "MangoHud",
        "runtime_information": "Informações do ambiente de execução",
        "executable": "Executável",
        "proton": "Proton",
        "path": "Caminho",
        "detected": "Detectado",
        "missing": "Ausente",
        "available": "Disponível",
        "unavailable": "Indisponível",
        "favorite": "Favorito",
        "favorites": "Favoritos",
        "playtime": "Tempo de jogo",
        "remove_from_library": "Remover jogo da biblioteca",
        "export_lutris": "Exportar para Lutris (.yml)",
        "edit": "Editar",
        "checking_executable": "Verificando o executável",
        "loading_game_configuration": "Carregando a configuração do jogo",
        "detecting_system": "Detectando o sistema",
        "starting_proton": "Iniciando o Proton",
        "starting_wine": "Iniciando o Wine",
        "runtime_selected": "Ambiente de execução do Proton selecionado",
        "missing_executable_title": "Executável ausente",
        "missing_executable_message": "Executável não encontrado",
        "starting_proton_call": "Iniciando o Proton Call",
        "run_started": "Execução iniciada",
        "config_read_error": "Erro ao ler a configuração {file}: {error}",
        "proton_not_found": """
        Nenhuma instalação do Proton encontrada.

        Instale uma versão do Proton (por exemplo, através do ProtonUp-Qt)
        ou especifique PROTON_PATH.

        Linha de comando:
          protonup -d ~/.steam/root/compatibilitytools.d

        Reinicie o Steam e tente novamente.
        """,
    },



    "es": {
        "no_proton_installation": "No se encontró ninguna instalación de Proton",
        "detected_proton_installations": "Instalaciones de Proton detectadas",
        "selected": "seleccionado",
        "prefix_name": "Nombre del prefijo (vacío = automático)",
        "diagnostic": "diagnóstico de proton-autogen",
        "version": "Versión",
        "python": "Python",
        "runtime": "Entorno de ejecución",
        "wine": "Wine",
        "yes": "sí",
        "no": "no",
        "none": "ninguno",
        "platform": "Plataforma",
        "detected_programs": "Programas de Windows detectados",
        "no_windows_programs": "No se encontraron programas de Windows",

        "search_finished": "La búsqueda de programas terminó en {time:.3f}s",

        "load_config_prefix": "CARGANDO PREFIJO DE CONFIGURACIÓN : {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "xrandr": "Xrandr",
        "mangohud": "MangoHud",
        "runtime_information": "Información del entorno de ejecución",
        "executable": "Ejecutable",
        "proton": "Proton",
        "path": "Ruta",
        "detected": "Detectado",
        "missing": "Faltante",
        "available": "Disponible",
        "unavailable": "No disponible",
        "favorite": "Favorito",
        "favorites": "Favoritos",
        "playtime": "Tiempo de juego",
        "remove_from_library": "Eliminar juego de la biblioteca",
        "export_lutris": "Exportar a Lutris (.yml)",
        "edit": "Editar",
        "checking_executable": "Comprobando el ejecutable",
        "loading_game_configuration": "Cargando la configuración del juego",
        "detecting_system": "Detectando el sistema",
        "starting_proton": "Iniciando Proton",
        "starting_wine": "Iniciando Wine",
        "runtime_selected": "Entorno de ejecución de Proton seleccionado",
        "missing_executable_title": "Falta el ejecutable",
        "missing_executable_message": "No se encontró el ejecutable",
        "starting_proton_call": "Iniciando Proton Call",
        "run_started": "Ejecución iniciada",
        "config_read_error": "Error al leer la configuración {file}: {error}",
        "proton_not_found": """
        No se encontró ninguna instalación de Proton.

        Instala una versión de Proton (por ejemplo, mediante ProtonUp-Qt)
        o especifica PROTON_PATH.

        Línea de comandos:
          protonup -d ~/.steam/root/compatibilitytools.d

        Reinicia Steam e inténtalo de nuevo.
        """,
    },

    "hi": {
        "no_proton_installation": "कोई Proton इंस्टॉलेशन नहीं मिला",
        "detected_proton_installations": "पता लगाए गए Proton इंस्टॉलेशन",
        "selected": "चयनित",
        "prefix_name": "प्रिफिक्स का नाम (खाली = स्वचालित)",
        "diagnostic": "proton-autogen निदान",
        "version": "संस्करण",
        "python": "Python",
        "runtime": "रनटाइम",
        "wine": "Wine",
        "yes": "हाँ",
        "no": "नहीं",
        "none": "कोई नहीं",
        "platform": "प्लेटफ़ॉर्म",
        "detected_programs": "पता लगाए गए Windows प्रोग्राम",
        "no_windows_programs": "कोई Windows प्रोग्राम नहीं मिला",

        "search_finished": "प्रोग्राम खोज {time:.3f}s में पूरी हुई",

        "load_config_prefix": "कॉन्फ़िगरेशन प्रिफिक्स लोड हो रहा है : {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "xrandr": "Xrandr",
        "mangohud": "MangoHud",
        "runtime_information": "रनटाइम जानकारी",
        "executable": "एक्ज़ीक्यूटेबल",
        "proton": "Proton",
        "path": "पथ",
        "detected": "पता लगाया गया",
        "missing": "अनुपलब्ध",
        "available": "उपलब्ध",
        "unavailable": "उपलब्ध नहीं",
        "favorite": "पसंदीदा",
        "favorites": "पसंदीदा",
        "playtime": "खेलने का समय",
        "remove_from_library": "गेम को लाइब्रेरी से हटाएँ",
        "export_lutris": "Lutris में निर्यात करें (.yml)",
        "edit": "संपादित करें",
        "checking_executable": "एक्ज़ीक्यूटेबल की जाँच हो रही है",
        "loading_game_configuration": "गेम कॉन्फ़िगरेशन लोड हो रहा है",
        "detecting_system": "सिस्टम का पता लगाया जा रहा है",
        "starting_proton": "Proton शुरू हो रहा है",
        "starting_wine": "Wine शुरू हो रहा है",
        "runtime_selected": "Proton रनटाइम चयनित",
        "missing_executable_title": "एक्ज़ीक्यूटेबल अनुपलब्ध",
        "missing_executable_message": "एक्ज़ीक्यूटेबल नहीं मिला",
        "starting_proton_call": "Proton Call शुरू हो रहा है",
        "run_started": "रन शुरू हो गया",
        "config_read_error": "कॉन्फ़िगरेशन पढ़ने में त्रुटि {file}: {error}",
        "proton_not_found": """
        कोई Proton इंस्टॉलेशन नहीं मिला।

        Proton का कोई संस्करण इंस्टॉल करें (उदाहरण के लिए ProtonUp-Qt के माध्यम से)
        या PROTON_PATH निर्दिष्ट करें।

        कमांड लाइन:
          protonup -d ~/.steam/root/compatibilitytools.d

        Steam को पुनः प्रारंभ करें और फिर से प्रयास करें।
        """,
    },


    "de": {
        "no_proton_installation": "Keine Proton-Installation gefunden",
        "detected_proton_installations": "Erkannte Proton-Installationen",
        "selected": "ausgewählt",
        "prefix_name": "Prefix-Name (leer = automatisch)",
        "diagnostic": "proton-autogen-Diagnose",
        "version": "Version",
        "python": "Python",
        "runtime": "Laufzeitumgebung",
        "wine": "Wine",
        "yes": "ja",
        "no": "nein",
        "none": "keine",
        "platform": "Plattform",
        "detected_programs": "Erkannte Windows-Programme",
        "no_windows_programs": "Keine Windows-Programme gefunden",

        "search_finished": "Die Programmsuche wurde in {time:.3f}s abgeschlossen",

        "load_config_prefix": "KONFIGURATIONSPRÄFIX LADEN : {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "xrandr": "Xrandr",
        "mangohud": "MangoHud",
        "runtime_information": "Informationen zur Laufzeitumgebung",
        "executable": "Ausführbare Datei",
        "proton": "Proton",
        "path": "Pfad",
        "detected": "Erkannt",
        "missing": "Fehlt",
        "available": "Verfügbar",
        "unavailable": "Nicht verfügbar",
        "favorite": "Favorit",
        "favorites": "Favoriten",
        "playtime": "Spielzeit",
        "remove_from_library": "Spiel aus der Bibliothek entfernen",
        "export_lutris": "Lutris exportieren (.yml)",
        "edit": "Bearbeiten",
        "checking_executable": "Ausführbare Datei wird überprüft",
        "loading_game_configuration": "Spielkonfiguration wird geladen",
        "detecting_system": "System wird erkannt",
        "starting_proton": "Proton wird gestartet",
        "starting_wine": "Wine wird gestartet",
        "runtime_selected": "Proton-Laufzeitumgebung ausgewählt",
        "missing_executable_title": "Ausführbare Datei fehlt",
        "missing_executable_message": "Ausführbare Datei nicht gefunden",
        "starting_proton_call": "Proton Call wird gestartet",
        "run_started": "Ausführung gestartet",
        "config_read_error": "Fehler beim Lesen der Konfiguration {file}: {error}",
        "proton_not_found": """
        Keine Proton-Installation gefunden.

        Installiere eine Proton-Version (z. B. über ProtonUp-Qt)
        oder gib PROTON_PATH an.

        Befehlszeile:
          protonup -d ~/.steam/root/compatibilitytools.d

        Starte Steam neu und versuche es erneut.
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
        "xrandr": "Xrandr",
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
        "xrandr": "Xrandr",
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
