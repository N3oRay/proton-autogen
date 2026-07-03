# desc.py : info-bulles / UX descriptions

from gi.repository import Gtk


# -----------------------------
# CORE DESCRIPTIONS
# -----------------------------
_DESCRIPTIONS = {
    "zh": {

        "profile":
            "定义游戏的运行模式和优化设置（DX11、DX12、兼容模式、旧游戏或特定配置）。",

        "proton":
            "用于在 Linux 上运行游戏的 Proton 版本。不同版本可以提高兼容性、性能或修复错误。",

        "show_performance":
            "在游戏中显示 FPS、CPU 使用率、GPU 使用率、内存等性能信息的叠加层。",

        "optimize_performance":
            "在游戏运行时自动优化系统性能，调整优先级和系统参数。",

        "mangohud":
            "MangoHud 是一个实时显示 FPS、CPU/GPU 使用率、温度、内存等信息的叠加层。",

        "gamemode":
            "GameMode 是一个系统服务，在游戏运行期间临时优化系统性能以减少卡顿并提升性能。",

        "gpu":
            "定义游戏的 GPU 优化模式："
            "auto（自动检测）、safe（最大兼容性）、"
            "balanced（平衡模式）或 performance（最高性能/FPS）。",

        "prefix":
            "一个独立的环境，包含 Windows 配置、库和应用程序。每个环境彼此隔离以避免游戏之间的冲突。",

        "prefix_short":
            "为此应用创建一个独立环境。",

        "performance_overlay":
            "显示性能信息（FPS、CPU、GPU）",

        "system_optimization":
            "优化系统性能",
    },

    "es": {

        "profile":
            "Define el modo de ejecución y las optimizaciones aplicadas al juego (DX11, DX12, "
            "compatibilidad, juegos antiguos o configuraciones específicas).",

        "proton":
            "Versión de Proton utilizada para ejecutar el juego en Linux. "
            "Diferentes versiones pueden mejorar la compatibilidad, el rendimiento o corregir errores.",

        "show_performance":
            "Muestra una superposición en el juego con FPS, uso de CPU, uso de GPU, "
            "memoria y otras estadísticas de rendimiento.",

        "optimize_performance":
            "Optimiza automáticamente el rendimiento del sistema durante el juego ajustando "
            "prioridades y parámetros del sistema.",

        "mangohud":
            "MangoHud es una superposición que muestra en tiempo real FPS, uso de CPU/GPU, "
            "temperaturas, uso de memoria y otra información útil.",

        "gamemode":
            "GameMode es un servicio del sistema que optimiza temporalmente el rendimiento durante el juego "
            "para mejorar el rendimiento y reducir los tirones.",

        "gpu":
            "Define el modo de optimización de la GPU del juego: "
            "auto (detección automática), safe (máxima compatibilidad), "
            "balanced (equilibrado) o performance (máximo rendimiento/FPS).",

        "prefix":
            "Un entorno aislado que contiene la configuración de Windows, bibliotecas y software "
            "instalado para esta aplicación. Cada entorno es independiente para evitar conflictos entre juegos.",

        "prefix_short":
            "Crear un entorno separado para esta aplicación.",

        "performance_overlay":
            "Mostrar rendimiento (FPS, CPU, GPU)",

        "system_optimization":
            "Optimizar el rendimiento del sistema",
    },

    "fr": {

        "profile":
            "Définit le type d’exécution et les optimisations appliquées au jeu (DX11, DX12, "
            "compatibilité, anciens jeux ou configurations spécifiques).",

        "proton":
            "Version de Proton utilisée pour exécuter le jeu sous Linux. "
            "Différentes versions peuvent améliorer la compatibilité, les performances ou corriger des bugs.",

        "show_performance":
            "Affiche en jeu un panneau indiquant les FPS, l'utilisation du processeur (CPU), "
            "de la carte graphique (GPU), la mémoire et d'autres statistiques.",

        "optimize_performance":
            "Optimise automatiquement les performances du système pendant l'exécution du jeu "
            "en ajustant certaines priorités et paramètres.",

        "mangohud":
            "MangoHud est une surcouche graphique affichant en temps réel les FPS, la charge CPU/GPU, "
            "la température, la consommation mémoire et d'autres informations utiles.",

        "gamemode":
            "GameMode est un service qui optimise temporairement le système pendant l'exécution du jeu "
            "afin d'améliorer les performances et de réduire les ralentissements.",

        "gpu":
            "Définit le mode d’optimisation GPU utilisé par le jeu : "
            "auto (détection automatique), safe (compatibilité maximale), "
            "balanced (équilibré) ou performance (priorité FPS).",

        "prefix":
            "Un environnement séparé contenant la configuration Windows, les bibliothèques et les logiciels "
            "installés pour cette application. Chaque environnement est indépendant afin d'éviter les conflits entre les jeux.",

        "prefix_short":
            "Créer un environnement séparé pour cette application.",

        "performance_overlay":
            "Afficher les performances (FPS, CPU, GPU)",

        "system_optimization":
            "Optimiser les performances système",
    },

    "de": {

        "profile":
            "Definiert den Ausführungsmodus und die auf das Spiel angewendeten Optimierungen (DX11, DX12, "
            "Kompatibilität, ältere Spiele oder spezielle Konfigurationen).",

        "proton":
            "Proton-Version, die zum Ausführen des Spiels unter Linux verwendet wird. "
            "Unterschiedliche Versionen können die Kompatibilität verbessern, die Leistung steigern oder Fehler beheben.",

        "show_performance":
            "Zeigt im Spiel ein Overlay mit FPS, CPU-Auslastung, GPU-Auslastung, "
            "Speichernutzung und weiteren Leistungsstatistiken an.",

        "optimize_performance":
            "Optimiert automatisch die Systemleistung während des Spielens, indem Prioritäten "
            "und Systemeinstellungen angepasst werden.",

        "mangohud":
            "MangoHud ist ein Overlay, das in Echtzeit FPS, CPU-/GPU-Auslastung, Temperaturen, "
            "Speichernutzung und weitere nützliche Informationen anzeigt.",

        "gamemode":
            "GameMode ist ein Systemdienst, der das System während des Spielens temporär optimiert, "
            "um die Leistung zu verbessern und Ruckler zu reduzieren.",

        "gpu":
            "Legt den GPU-Optimierungsmodus des Spiels fest: "
            "auto (automatische Erkennung), safe (maximale Kompatibilität), "
            "balanced (ausgewogen) oder performance (maximale FPS).",

        "prefix":
            "Eine isolierte Umgebung, die die Windows-Konfiguration, Bibliotheken und installierte "
            "Software für diese Anwendung enthält. Jede Umgebung ist unabhängig, um Konflikte zwischen Spielen zu vermeiden.",

        "prefix_short":
            "Eine separate Umgebung für diese Anwendung erstellen.",

        "performance_overlay":
            "Leistungsanzeige (FPS, CPU, GPU)",

        "system_optimization":
            "Systemleistung optimieren",
    },

    "uk": {

        "profile":
            "Визначає режим запуску та оптимізації, що застосовуються до гри (DX11, DX12, "
            "сумісність, старі ігри або специфічні конфігурації).",

        "proton":
            "Версія Proton, що використовується для запуску гри в Linux. "
            "Різні версії можуть покращити сумісність, продуктивність або виправити помилки.",

        "show_performance":
            "Показує в грі панель з FPS, використанням CPU, GPU, пам’яті та іншими "
            "показниками продуктивності.",

        "optimize_performance":
            "Автоматично оптимізує продуктивність системи під час запуску гри, "
            "налаштовуючи пріоритети та параметри.",

        "mangohud":
            "MangoHud — це оверлей, який у реальному часі показує FPS, завантаження CPU/GPU, "
            "температуру, використання пам’яті та іншу корисну інформацію.",

        "gamemode":
            "GameMode — це системний сервіс, який тимчасово оптимізує систему під час гри "
            "для покращення продуктивності та зменшення затримок.",

        "gpu":
            "Визначає режим оптимізації GPU для гри: "
            "auto (автоматичне визначення), safe (максимальна сумісність), "
            "balanced (збалансований режим) або performance (максимальна продуктивність / FPS).",

        "prefix":
            "Ізольоване середовище, що містить конфігурацію Windows, бібліотеки та програмне "
            "забезпечення для цієї програми. Кожне середовище незалежне, щоб уникнути конфліктів між іграми.",

        "prefix_short":
            "Створити окреме середовище для цієї програми.",

        "performance_overlay":
            "Показати продуктивність (FPS, CPU, GPU)",

        "system_optimization":
            "Оптимізувати продуктивність системи",
    },

    "pt": {

        "profile":
            "Define o modo de execução e as otimizações aplicadas ao jogo (DX11, DX12, "
            "compatibilidade, jogos antigos ou configurações específicas).",

        "proton":
            "Versão do Proton usada para executar o jogo no Linux. "
            "Diferentes versões podem melhorar a compatibilidade, o desempenho ou corrigir erros.",

        "show_performance":
            "Exibe no jogo um painel com FPS, uso de CPU, GPU, memória e outras "
            "estatísticas de desempenho.",

        "optimize_performance":
            "Otimiza automaticamente o desempenho do sistema durante a execução do jogo, "
            "ajustando prioridades e configurações.",

        "mangohud":
            "O MangoHud é uma sobreposição que exibe em tempo real FPS, uso de CPU/GPU, "
            "temperatura, uso de memória e outras informações úteis.",

        "gamemode":
            "O GameMode é um serviço do sistema que otimiza temporariamente o desempenho durante o jogo "
            "para melhorar a performance e reduzir travamentos.",

        "gpu":
            "Define o modo de otimização da GPU no jogo: "
            "auto (detecção automática), safe (máxima compatibilidade), "
            "balanced (equilibrado) ou performance (máximo desempenho/FPS).",

        "prefix":
            "Um ambiente isolado contendo a configuração do Windows, bibliotecas e softwares "
            "instalados para esta aplicação. Cada ambiente é independente para evitar conflitos entre jogos.",

        "prefix_short":
            "Criar um ambiente separado para esta aplicação.",

        "performance_overlay":
            "Mostrar desempenho (FPS, CPU, GPU)",

        "system_optimization":
            "Otimizar o desempenho do sistema",
    },

    "en": {
        "profile":
            "Defines the execution profile and optimizations applied to the game (DX11, DX12, "
            "compatibility modes, legacy games or specific configurations).",

        "proton":
            "Proton version used to run the game on Linux. "
            "Different versions may improve compatibility, performance or fix specific issues.",

        "show_performance":
            "Displays an in-game overlay showing FPS, CPU usage, GPU usage, memory consumption "
            "and other useful performance statistics.",

        "optimize_performance":
            "Automatically optimizes system performance while the game is running by adjusting "
            "priorities and system settings.",

        "mangohud":
            "MangoHud is an in-game overlay that displays real-time FPS, CPU/GPU usage, "
            "temperatures, memory usage and other performance statistics.",

        "gamemode":
            "GameMode is a system service that temporarily optimizes your computer while a game "
            "is running to improve performance and reduce stuttering.",

        "gpu":
            "Defines the GPU optimization mode used by the game: "
            "auto (automatic detection), safe (maximum compatibility), "
            "balanced (balanced settings) or performance (maximum FPS).",

        "prefix":
            "A separate environment containing the Windows configuration, installed libraries and "
            "applications used by this program. Each environment is isolated to avoid conflicts between games.",

        "prefix_short":
            "Create a separate environment for this application.",

        "performance_overlay":
            "Show performance (FPS, CPU, GPU)",

        "system_optimization":
            "Optimize system performance",
    }
}


# -----------------------------
# CORE API
# -----------------------------
def get_description(key: str, lang: str = "en") -> str:
    """
    Return localized description for a given key.
    Falls back to English if language not found.
    """
    lang_table = _DESCRIPTIONS.get(lang) or _DESCRIPTIONS["en"]
    return lang_table.get(key, "")


# -----------------------------
# GTK TOOLTIP HELPERS
# -----------------------------
def set_tooltip(widget, key: str, lang: str = "en"):
    """
    Attach tooltip text to a GTK widget.
    """
    text = get_description(key, lang)
    if text:
        widget.set_tooltip_text(text)


def set_tooltip_from_text(widget, text: str):
    """
    Direct tooltip without key system.
    """
    if text:
        widget.set_tooltip_text(text)


def set_tooltip_if_available(widget, key: str, lang: str = "en"):
    """
    Safe version: never fails even if key is missing.
    """
    try:
        text = get_description(key, lang)
        if text:
            widget.set_tooltip_text(text)
    except Exception:
        pass


# -----------------------------
# BATCH TOOLTIP HELPERS
# -----------------------------
def apply_tooltips(widget_map: dict, lang: str = "en"):
    """
    Apply multiple tooltips at once.

    Example:
        apply_tooltips({
            self.mangohud: "mangohud",
            self.gamemode: "gamemode",
            self.prefix: "prefix"
        })
    """
    for widget, key in widget_map.items():
        set_tooltip_if_available(widget, key, lang)


# -----------------------------
# UTILITY: KEY HELPERS
# -----------------------------
def has_description(key: str, lang: str = "en") -> bool:
    """
    Check if a description exists for a key.
    """
    lang_table = _DESCRIPTIONS.get(lang) or _DESCRIPTIONS["en"]
    return key in lang_table


def list_keys(lang: str = "en") -> list:
    """
    Return all available description keys.
    """
    lang_table = _DESCRIPTIONS.get(lang) or _DESCRIPTIONS["en"]
    return list(lang_table.keys())


# -----------------------------
# OPTIONAL UX HELPERS
# -----------------------------
def attach_tooltip(widget, key: str, lang: str = "en"):
    """
    Alias cleaner pour set_tooltip (UX-friendly naming).
    """
    set_tooltip(widget, key, lang)


def attach_tooltips(widget_map: dict, lang: str = "en"):
    """
    Alias batch UX-friendly.
    """
    apply_tooltips(widget_map, lang)
