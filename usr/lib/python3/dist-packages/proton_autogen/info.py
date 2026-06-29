#info.py proton-autogen ux
# info.py
# Proton-Autogen Help System
# English (default) / Français

import locale


def get_language():
    lang = locale.setlocale(locale.LC_ALL, "")
    return "fr" if lang.lower().startswith("fr") else "en"


HELP_TEXT = {

###############################################################################
# ENGLISH
###############################################################################

"en": """PROTON-AUTOGEN - HELP

━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen <file.exe>
proton-autogen run <file.exe>
proton-autogen add <file.exe>
proton-autogen edit <file.exe>

━━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━
--ux        GTK4 interface
--v         version
--about     about information
--help      display this help
--help-env  environment help

━━━━━━━━━━━━━━━━━━━━━━━━━━
PREFIX SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
STEAM_COMPAT_DATA_PATH

--pc        custom prefix
--pa        automatic prefix
--ps        shared prefix
default     main prefix

━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFILES
━━━━━━━━━━━━━━━━━━━━━━━━━━
--json-profile
--profile dx11

━━━━━━━━━━━━━━━━━━━━━━━━━━
DISCOVERY
━━━━━━━━━━━━━━━━━━━━━━━━━━
--list-protons
--list-programs
--proton-paths
--diag

━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen game.exe
proton-autogen run game.exe

━━━━━━━━━━━━━━━━━━━━━━━━━━
OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━
--debug
--verbose
--mangohud
--gamemode
--wine
--proton

━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen game.exe
proton-autogen game.exe --gamemode --mangohud
gamescope -f -- proton-autogen game.exe

━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━
- Automatic Proton selection
- Wine fallback
- Steam / Flatpak support

""",

###############################################################################
# FRANÇAIS
###############################################################################

"fr": """PROTON-AUTOGEN - AIDE

━━━━━━━━━━━━━━━━━━━━━━━━━━
UTILISATION
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen <fichier.exe>
proton-autogen run <fichier.exe>
proton-autogen add <fichier.exe>
proton-autogen edit <fichier.exe>

━━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━
--ux        Interface GTK4
--v         version
--about     informations
--help      afficher cette aide
--help-env  aide sur l'environnement

━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTÈME DE PRÉFIXES
━━━━━━━━━━━━━━━━━━━━━━━━━━
STEAM_COMPAT_DATA_PATH

--pc        préfixe personnalisé
--pa        préfixe automatique
--ps        préfixe partagé
par défaut  préfixe principal

━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFILS
━━━━━━━━━━━━━━━━━━━━━━━━━━
--json-profile
--profile dx11

━━━━━━━━━━━━━━━━━━━━━━━━━━
DÉCOUVERTE
━━━━━━━━━━━━━━━━━━━━━━━━━━
--list-protons
--list-programs
--proton-paths
--diag

━━━━━━━━━━━━━━━━━━━━━━━━━━
EXÉCUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen game.exe
proton-autogen run game.exe

━━━━━━━━━━━━━━━━━━━━━━━━━━
OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━
--debug
--verbose
--mangohud
--gamemode
--wine
--proton

━━━━━━━━━━━━━━━━━━━━━━━━━━
EXEMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen game.exe
proton-autogen game.exe --gamemode --mangohud
gamescope -f -- proton-autogen game.exe

━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━
- Sélection automatique de Proton
- Repli sur Wine
- Compatible Steam / Flatpak

""",

###############################################################################
# CHINESE (Simplified)
###############################################################################

"zh": """PROTON-AUTOGEN - 帮助

━━━━━━━━━━━━━━━━━━━━━━━━━━
用法
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen <file.exe>
proton-autogen run <file.exe>
proton-autogen add <file.exe>
proton-autogen edit <file.exe>

━━━━━━━━━━━━━━━━━━━━━━━━━━
信息
━━━━━━━━━━━━━━━━━━━━━━━━━━
--ux        GTK4 图形界面
--v         版本
--about     关于信息
--help      显示此帮助
--help-env  环境帮助

━━━━━━━━━━━━━━━━━━━━━━━━━━
前缀系统
━━━━━━━━━━━━━━━━━━━━━━━━━━
STEAM_COMPAT_DATA_PATH

--pc        自定义前缀
--pa        自动前缀
--ps        共享前缀
default     主前缀

━━━━━━━━━━━━━━━━━━━━━━━━━━
配置文件
━━━━━━━━━━━━━━━━━━━━━━━━━━
--json-profile
--profile dx11

━━━━━━━━━━━━━━━━━━━━━━━━━━
发现
━━━━━━━━━━━━━━━━━━━━━━━━━━
--list-protons
--list-programs
--proton-paths
--diag

━━━━━━━━━━━━━━━━━━━━━━━━━━
执行
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen game.exe
proton-autogen run game.exe

━━━━━━━━━━━━━━━━━━━━━━━━━━
选项
━━━━━━━━━━━━━━━━━━━━━━━━━━
--debug
--verbose
--mangohud
--gamemode
--wine
--proton

━━━━━━━━━━━━━━━━━━━━━━━━━━
示例
━━━━━━━━━━━━━━━━━━━━━━━━━━
proton-autogen game.exe
proton-autogen game.exe --gamemode --mangohud
gamescope -f -- proton-autogen game.exe

━━━━━━━━━━━━━━━━━━━━━━━━━━
备注
━━━━━━━━━━━━━━━━━━━━━━━━━━
- 自动选择 Proton
- Wine 备用方案
- 支持 Steam / Flatpak

"""
}


CLI_HELP = {

###############################################################################
# ENGLISH
###############################################################################

"en": """proton-autogen

Usage:
  proton-autogen <file.exe>
  proton-autogen run <file.exe>
  proton-autogen add <file.exe>
  proton-autogen edit <file.exe>

Information:
  proton-autogen --ux
      GTK4 graphical interface

  proton-autogen --v
      Display version

  proton-autogen --about
      About Proton-Autogen

  proton-autogen --help
      Display this help

  proton-autogen --help-env
      Environment help (New in v2.5.3)

Prefix system (STEAM_COMPAT_DATA_PATH):

  proton-autogen --pc
      Custom prefix:
      ~/Documents/Proton/env/Proton Custom/

  proton-autogen --pa
      Automatic prefix:
      ~/Documents/Proton/env/UnrealTournament-a12bc34d

  proton-autogen --ps
      Shared prefix:
      ~/Documents/Proton/env/shared

  proton-autogen
      Default prefix:
      ~/Documents/Proton/env/main

Profiles:

  proton-autogen --json-profile
      Export all environment profiles as JSON

  proton-autogen --profile dx11
      Use the selected profile

Discovery:

  proton-autogen --list-protons
      List detected Proton installations

  proton-autogen --list-programs
      List registered programs

  proton-autogen --proton-paths
      Display detected Proton paths

  proton-autogen --diag
      Run diagnostics
""",

###############################################################################
# FRANÇAIS
###############################################################################

"fr": """proton-autogen

Utilisation :
  proton-autogen <fichier.exe>
  proton-autogen run <fichier.exe>
  proton-autogen add <fichier.exe>
  proton-autogen edit <fichier.exe>

Informations :
  proton-autogen --ux
      Interface graphique GTK4

  proton-autogen --v
      Afficher la version

  proton-autogen --about
      À propos de Proton-Autogen

  proton-autogen --help
      Afficher cette aide

  proton-autogen --help-env
      Aide sur l'environnement (Nouveau depuis v2.5.3)

Système de préfixes (STEAM_COMPAT_DATA_PATH) :

  proton-autogen --pc
      Préfixe personnalisé :
      ~/Documents/Proton/env/Proton Custom/

  proton-autogen --pa
      Préfixe automatique :
      ~/Documents/Proton/env/UnrealTournament-a12bc34d

  proton-autogen --ps
      Préfixe partagé :
      ~/Documents/Proton/env/shared

  proton-autogen
      Préfixe principal :
      ~/Documents/Proton/env/main

Profils :

  proton-autogen --json-profile
      Exporter tous les profils d'environnement au format JSON

  proton-autogen --profile dx11
      Utiliser le profil sélectionné

Découverte :

  proton-autogen --list-protons
      Lister les installations Proton détectées

  proton-autogen --list-programs
      Lister les programmes enregistrés

  proton-autogen --proton-paths
      Afficher les chemins Proton détectés

  proton-autogen --diag
      Lancer le diagnostic
""",

###############################################################################
# CHINESE (Simplified)
###############################################################################

"zh": """proton-autogen

用法：
  proton-autogen <file.exe>
  proton-autogen run <file.exe>
  proton-autogen add <file.exe>
  proton-autogen edit <file.exe>

信息：
  proton-autogen --ux
      GTK4 图形界面

  proton-autogen --v
      显示版本

  proton-autogen --about
      关于 Proton-Autogen

  proton-autogen --help
      显示此帮助

  proton-autogen --help-env
      环境帮助（v2.5.3 新增）

前缀系统（STEAM_COMPAT_DATA_PATH）：

  proton-autogen --pc
      自定义前缀：
      ~/Documents/Proton/env/Proton Custom/

  proton-autogen --pa
      自动前缀：
      ~/Documents/Proton/env/UnrealTournament-a12bc34d

  proton-autogen --ps
      共享前缀：
      ~/Documents/Proton/env/shared

  proton-autogen
      默认前缀：
      ~/Documents/Proton/env/main

配置文件：

  proton-autogen --json-profile
      将所有环境配置导出为 JSON

  proton-autogen --profile dx11
      使用指定配置

发现：

  proton-autogen --list-protons
      列出检测到的 Proton 安装

  proton-autogen --list-programs
      列出已注册程序

  proton-autogen --proton-paths
      显示检测到的 Proton 路径

  proton-autogen --diag
      运行诊断
"""
}

CLI_HELP_2 = {

###############################################################################
# ENGLISH
###############################################################################

"en": """
Game management:

  proton-autogen add <file.exe>
      Create a game profile in ~/.config/proton-autogen/

Execution:

  proton-autogen <file.exe>
      Run game using automatic Proton selection or saved config

  proton-autogen run <file.exe>
      Force execution without profile override

Options:

  --debug        Debug output
  --verbose      Verbose output
  --mangohud     Enable MangoHud overlay
  --gamemode     Enable GameMode
  --call         Use Proton-Call
  --wine         Use Wine
  --proton       Use Proton only (default)

Examples:

  proton-autogen add game.exe
  proton-autogen game.exe
  proton-autogen run game.exe
  proton-autogen game.exe --mangohud

  # Basic run
  proton-autogen game.exe

  # DX9 old game (recommended)
  proton-autogen SWEP1RCR.EXE --profile dx9dg

  # With GameMode + MangoHud
  proton-autogen game.exe --gamemode --mangohud

  # Gamescope (recommended for scaling)
  gamescope -f -W 1280 -H 1024 -- proton-autogen game.exe

  # Gamescope + FSR (may blur UI in old DX9 games)
  gamescope -f -W 1280 -H 1024 --fsr-sharpness 0 -- proton-autogen game.exe

Notes:

  - Uses saved JSON config when available
  - Automatically selects best Proton version
  - Falls back to Wine if Proton is unavailable
  - Supports Steam, Flatpak, and compatibilitytools installs
  - Configure custom Proton locations with
    ~/.config/proton-autogen.conf
""",

###############################################################################
# FRANÇAIS
###############################################################################

"fr": """
Gestion des jeux :

  proton-autogen add <fichier.exe>
      Crée un profil de jeu dans ~/.config/proton-autogen/

Exécution :

  proton-autogen <fichier.exe>
      Lance le jeu avec la sélection automatique
      de Proton ou la configuration enregistrée.

  proton-autogen run <fichier.exe>
      Force l'exécution sans utiliser le profil enregistré.

Options :

  --debug        Mode débogage
  --verbose      Mode verbeux
  --mangohud     Activer MangoHud
  --gamemode     Activer GameMode
  --call         Utiliser Proton-Call
  --wine         Utiliser Wine
  --proton       Utiliser uniquement Proton (par défaut)

Exemples :

  proton-autogen add game.exe
  proton-autogen game.exe
  proton-autogen run game.exe
  proton-autogen game.exe --mangohud

  # Exécution simple
  proton-autogen game.exe

  # Ancien jeu DX9 (recommandé)
  proton-autogen SWEP1RCR.EXE --profile dx9dg

  # Avec GameMode + MangoHud
  proton-autogen game.exe --gamemode --mangohud

  # Gamescope (recommandé pour la mise à l'échelle)
  gamescope -f -W 1280 -H 1024 -- proton-autogen game.exe

  # Gamescope + FSR (peut rendre l'interface floue avec les jeux DX9)
  gamescope -f -W 1280 -H 1024 --fsr-sharpness 0 -- proton-autogen game.exe

Notes :

  - Utilise la configuration JSON enregistrée lorsqu'elle existe
  - Sélectionne automatiquement la meilleure version de Proton
  - Utilise Wine si Proton n'est pas disponible
  - Compatible avec Steam, Flatpak et compatibilitytools
  - Configurer des emplacements Proton personnalisés avec
    ~/.config/proton-autogen.conf
""",

###############################################################################
# CHINESE (Simplified)
###############################################################################

"zh": """
游戏管理：

  proton-autogen add <file.exe>
      在 ~/.config/proton-autogen/ 中创建游戏配置文件

执行：

  proton-autogen <file.exe>
      使用自动 Proton 选择或已保存配置运行游戏

  proton-autogen run <file.exe>
      强制运行，不使用配置文件覆盖

选项：

  --debug        调试输出
  --verbose      详细输出
  --mangohud     启用 MangoHud 叠加层
  --gamemode     启用 GameMode
  --call         使用 Proton-Call
  --wine         使用 Wine
  --proton       仅使用 Proton（默认）

示例：

  proton-autogen add game.exe
  proton-autogen game.exe
  proton-autogen run game.exe
  proton-autogen game.exe --mangohud

  # 基本运行
  proton-autogen game.exe

  # 旧 DX9 游戏（推荐）
  proton-autogen SWEP1RCR.EXE --profile dx9dg

  # 启用 GameMode + MangoHud
  proton-autogen game.exe --gamemode --mangohud

  # Gamescope（推荐用于缩放）
  gamescope -f -W 1280 -H 1024 -- proton-autogen game.exe

  # Gamescope + FSR（可能使旧 DX9 游戏界面模糊）
  gamescope -f -W 1280 -H 1024 --fsr-sharpness 0 -- proton-autogen game.exe

说明：

  - 使用已保存的 JSON 配置（如果存在）
  - 自动选择最佳 Proton 版本
  - 如果 Proton 不可用则回退到 Wine
  - 支持 Steam、Flatpak 和 compatibilitytools 安装
  - 可在 ~/.config/proton-autogen.conf 配置自定义 Proton 路径
"""
}

def get_help_text(lang=None):
    lang = lang or get_language()
    return HELP_TEXT.get(lang, HELP_TEXT["en"])


def print_help(lang=None):
    lang = lang or get_language()

    print(CLI_HELP.get(lang, CLI_HELP["en"]))
    print(CLI_HELP_2.get(lang, CLI_HELP_2["en"]))


TR = {
    "en": {
        "usage": "Usage",
        "options": "Options",
        "examples": "Examples",
        "notes": "Notes",
        "about": "About",
    },
    "fr": {
        "usage": "Utilisation",
        "options": "Options",
        "examples": "Exemples",
        "notes": "Notes",
        "about": "À propos",
    },
}

def get_tr(key, lang=None):
    lang = lang or get_language()
    return TR.get(lang, TR["en"]).get(key, key)

#---------------------------------------------------------------------------------------------------------------------------
