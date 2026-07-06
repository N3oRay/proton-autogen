ENV_VARS = [

    # =========================================================
    # DXVK
    # =========================================================
    {
        "name": "DXVK_FULLSCREEN",
        "type": "dxvk",
        "category": "compatibility",
        "description_fr": "Force DXVK à utiliser un mode plein écran exclusif ou contrôlé pour les applications Vulkan via DXVK.",
        "description_en": "Forces DXVK to use exclusive or controlled fullscreen mode for Vulkan-based applications."
    },
    {
        "name": "DXVK_ASYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Active la compilation asynchrone des shaders avec DXVK afin de réduire les saccades liées à leur compilation pendant le jeu.",
        "description_en": "Enables asynchronous shader compilation in DXVK to reduce shader compilation stuttering during gameplay."
    },
    {
        "name": "DXVK_CONFIG",
        "type": "dxvk",
        "category": "configuration",
        "description_fr": "Configuration personnalisée DXVK.",
        "description_en": "Custom DXVK configuration."
    },
    {
        "name": "DXVK_HUD",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Affiche l'overlay DXVK (FPS, mémoire, shaders).",
        "description_en": "Displays DXVK HUD overlay."
    },
    {
        "name": "DXVK_LOG_LEVEL",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Niveau de logs DXVK.",
        "description_en": "DXVK logging level."
    },
    {
        "name": "DXVK_LOG_PATH",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Chemin des logs DXVK.",
        "description_en": "DXVK log output path."
    },
    {
        "name": "DXVK_STATE_CACHE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Active le cache DXVK.",
        "description_en": "Enables DXVK state cache."
    },
    {
        "name": "DXVK_STATE_CACHE_PATH",
        "type": "dxvk",
        "category": "configuration",
        "description_fr": "Chemin du cache DXVK.",
        "description_en": "DXVK cache path."
    },
    {
        "name": "DXVK_STATE_CACHE_SIZE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Taille du cache DXVK.",
        "description_en": "DXVK cache size limit."
    },
    {
        "name": "DXVK_ENABLE_NVAPI",
        "type": "dxvk",
        "category": "compatibility",
        "description_fr": "Active NVAPI via DXVK.",
        "description_en": "Enables NVAPI support."
    },
    {
        "name": "DXVK_FILTER_DEVICE_NAME",
        "type": "dxvk",
        "category": "graphics",
        "description_fr": "Force un GPU Vulkan.",
        "description_en": "Forces a specific Vulkan GPU."
    },
    {
        "name": "DXVK_FRAME_RATE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Limite les FPS.",
        "description_en": "FPS limiter."
    },

    # =========================================================
    # VKD3D (DirectX 12)
    # =========================================================
    {
        "name": "VKD3D_CONFIG",
        "type": "vkd3d",
        "category": "configuration",
        "description_fr": "Configuration VKD3D-Proton (DX12).",
        "description_en": "VKD3D-Proton configuration."
    },
    {
        "name": "VKD3D_DEBUG",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Logs VKD3D.",
        "description_en": "VKD3D debug output."
    },
    {
        "name": "VKD3D_SHADER_DEBUG",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Debug shaders DX12.",
        "description_en": "DX12 shader debugging."
    },
    {
        "name": "VKD3D_FEATURE_LEVEL",
        "type": "vkd3d",
        "category": "compatibility",
        "description_fr": "Force un feature level DX12.",
        "description_en": "Forces DX12 feature level."
    },
    {
        "name": "VKD3D_DEBUGFLAGS",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Flags debug VKD3D.",
        "description_en": "VKD3D debug flags."
    },

    # =========================================================
    # PROTON
    # =========================================================
    {
        "name": "PROTON_LOG",
        "type": "proton",
        "category": "debug",
        "description_fr": "Active les logs Proton.",
        "description_en": "Enables Proton logs."
    },
    {
        "name": "PROTON_LOG_DIR",
        "type": "proton",
        "category": "debug",
        "description_fr": "Dossier des logs Proton.",
        "description_en": "Proton log directory."
    },
    {
        "name": "PROTON_NO_ESYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Désactive Esync.",
        "description_en": "Disables Esync."
    },
    {
        "name": "PROTON_NO_FSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Désactive Fsync.",
        "description_en": "Disables Fsync."
    },
    {
        "name": "PROTON_USE_WINED3D",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Utilise WineD3D au lieu de DXVK.",
        "description_en": "Uses WineD3D instead of DXVK."
    },
    {
        "name": "PROTON_ENABLE_NVAPI",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active le support de NVIDIA NVAPI dans Proton pour permettre l'utilisation de certaines fonctionnalités spécifiques aux cartes NVIDIA.",
        "description_en": "Enables NVIDIA NVAPI support in Proton, allowing access to certain NVIDIA-specific features."
    },
    {
        "name": "PROTON_ENABLE_WAYLAND",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active le support Wayland dans Proton lorsque disponible.",
        "description_en": "Enables Wayland support in Proton when available."
    },
    {
        "name": "PROTON_ENABLE_HDR",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active la prise en charge HDR pour les jeux compatibles via Proton. Dépréciée dans Proton-CachyOS où le HDR est géré automatiquement.",
        "description_en": "Enables HDR support for compatible games through Proton. Deprecated in Proton-CachyOS where HDR is handled automatically."
    },
    {
        "name": "PROTON_FORCE_LARGE_ADDRESS_AWARE",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Force LAA pour 32-bit.",
        "description_en": "Forces Large Address Awareness."
    },
    {
        "name": "PROTON_ENABLE_FSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Force Fsync Proton.",
        "description_en": "Enables Fsync."
    },

    {
        "name": "PROTON_USE_NTSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Active NTSync, une méthode de synchronisation plus efficace visant à améliorer les performances CPU et la compatibilité des jeux Windows.",
        "description_en": "Enables NTSync, a more efficient synchronization method designed to improve CPU performance and Windows game compatibility."
    },

    # =========================================================
    # WINE
    # =========================================================
    {
        "name": "WINEPREFIX",
        "type": "wine",
        "category": "configuration",
        "description_fr": "Préfixe Wine.",
        "description_en": "Wine prefix path."
    },
    {
        "name": "WINEARCH",
        "type": "wine",
        "category": "configuration",
        "description_fr": "Architecture Wine.",
        "description_en": "Wine architecture."
    },
    {
        "name": "WINEDEBUG",
        "type": "wine",
        "category": "debug",
        "description_fr": "Debug Wine.",
        "description_en": "Wine debug output."
    },
    {
        "name": "WINEDLLOVERRIDES",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Overrides DLL.",
        "description_en": "DLL override rules."
    },
    {
        "name": "WINEESYNC",
        "type": "wine",
        "category": "performance",
        "description_fr": "Esync Wine.",
        "description_en": "Wine Esync."
    },
    {
        "name": "WINEFSYNC",
        "type": "wine",
        "category": "performance",
        "description_fr": "Fsync Wine.",
        "description_en": "Wine Fsync."
    },
    {
        "name": "WINE_LARGE_ADDRESS_AWARE",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "LAA Wine.",
        "description_en": "Large address aware mode."
    },

    {
        "name": "WINE_FULLSCREEN_FSR",
        "type": "wine",
        "category": "graphics",
        "description_fr": "Active ou désactive l'utilisation de FSR (FidelityFX Super Resolution) pour l'upscaling en plein écran dans Wine/Proton.",
        "description_en": "Enables or disables FidelityFX Super Resolution (FSR) upscaling in fullscreen mode in Wine/Proton."
    },
    {
        "name": "WINE_VK_FULLSCREEN_METHOD",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Définit la méthode utilisée par Wine pour gérer le plein écran Vulkan (ex: desktop, exclusive, auto).",
        "description_en": "Defines how Wine handles Vulkan fullscreen mode (e.g., desktop, exclusive, auto)."
    },
    # =========================================================
    # SDL
    # =========================================================

    {
        "name": "SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR",
        "type": "sdl",
        "category": "graphics",
        "description_fr": "Contrôle si SDL demande au compositeur X11 de contourner la composition (bypass). Peut réduire la latence ou les problèmes d'affichage, mais peut causer des soucis de focus ou de capture de souris sur certains gestionnaires de fenêtres.",
        "description_en": "Controls whether SDL requests the X11 compositor bypass. Can reduce latency and rendering issues, but may cause focus or mouse capture problems on some window managers."
    },

    {
        "name": "SDL_MOUSE_AUTO_CAPTURE",
        "type": "sdl",
        "category": "input",
        "description_fr": "Active la capture automatique de la souris lorsque la fenêtre devient active. Améliore le comportement des jeux en plein écran ou en mode FPS, en évitant la perte de contrôle de la souris.",
        "description_en": "Enables automatic mouse capture when the window becomes active. Improves mouse behavior in fullscreen or FPS-style games by preventing loss of mouse control."
    },
    {
        "name": "SDL_MOUSE_RELATIVE_MODE_WARP",
        "type": "sdl",
        "category": "input",
        "description_fr": "Active le mode de souris relative avec recentering (warp). Utilisé par certains jeux anciens pour simuler un mouvement continu de la souris. Peut améliorer la compatibilité avec les jeux DirectDraw ou moteurs anciens.",
        "description_en": "Enables relative mouse mode using pointer warping. Used by some older games to simulate continuous mouse movement. Can improve compatibility with DirectDraw or legacy engines."
    },
    {
        "name": "SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR",
        "type": "sdl",
        "category": "graphics",
        "description_fr": "Demande au gestionnaire de fenêtres X11 de contourner le compositeur pour la fenêtre SDL. Peut réduire la latence et améliorer la réactivité, mais peut aussi causer des problèmes de focus ou de capture de souris selon le gestionnaire de fenêtres.",
        "description_en": "Requests the X11 window manager to bypass the compositor for the SDL window. Can reduce latency and improve responsiveness, but may cause focus or mouse capture issues depending on the window manager."
    },
    {
        "name": "SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS",
        "type": "sdl",
        "category": "window",
        "description_fr": "Détermine si la fenêtre doit être minimisée lors d'une perte de focus. Utile pour éviter certains comportements de plein écran instable dans les anciens jeux.",
        "description_en": "Determines whether the window should be minimized when it loses focus. Useful to avoid unstable fullscreen behavior in older games."
    },
    {
        "name": "SDL_HINT_GRAB_KEYBOARD",
        "type": "sdl",
        "category": "input",
        "description_fr": "Force SDL à capturer le clavier lorsque la fenêtre est active. Empêche les touches de sortir du contexte du jeu, améliorant l'immersion et la compatibilité des anciens moteurs.",
        "description_en": "Forces SDL to grab the keyboard when the window is active. Prevents key input from leaving the game context, improving immersion and compatibility with legacy engines."
    },

    # =========================================================
    # VULKAN
    # =========================================================
    {
        "name": "VK_ICD_FILENAMES",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "ICD Vulkan forcé.",
        "description_en": "Forces Vulkan ICD."
    },
    {
        "name": "VK_LAYER_PATH",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "Chemin layers Vulkan.",
        "description_en": "Vulkan layers path."
    },
    {
        "name": "VK_INSTANCE_LAYERS",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "Layers Vulkan.",
        "description_en": "Vulkan instance layers."
    },
    {
        "name": "VK_LOADER_DEBUG",
        "type": "vulkan",
        "category": "debug",
        "description_fr": "Debug loader Vulkan.",
        "description_en": "Vulkan loader debug."
    },

    # =========================================================
    # MESA / AMD
    # =========================================================
    {
        "name": "MESA_VK_DEVICE_SELECT",
        "type": "mesa",
        "category": "graphics",
        "description_fr": "Sélection GPU Mesa.",
        "description_en": "Select Vulkan GPU."
    },
    {
        "name": "RADV_PERFTEST",
        "type": "mesa",
        "category": "performance",
        "description_fr": "Optimisations RADV.",
        "description_en": "RADV experimental features."
    },
    {
        "name": "RADV_DEBUG",
        "type": "mesa",
        "category": "debug",
        "description_fr": "Debug RADV.",
        "description_en": "RADV debug mode."
    },
    {
        "name": "mesa_glthread",
        "type": "mesa",
        "category": "performance",
        "description_fr": "Multithread OpenGL.",
        "description_en": "OpenGL threading."
    },

    {
        "name": "MESA_GL_VERSION_OVERRIDE",
        "type": "opengl",
        "category": "graphics",
        "description_fr": "Force la version d'OpenGL exposée par le pilote Mesa aux applications.",
        "description_en": "Forces the OpenGL version reported by the Mesa driver to applications."
    },
    {
        "name": "MESA_GLSL_VERSION_OVERRIDE",
        "type": "opengl",
        "category": "graphics",
        "description_fr": "Force la version du langage de shaders GLSL utilisée par Mesa pour la compilation des shaders.",
        "description_en": "Forces the GLSL shader language version used by Mesa for shader compilation."
    },

    # =========================================================
    # NVIDIA
    # =========================================================
    {
        "name": "__GL_SHADER_DISK_CACHE",
        "type": "nvidia",
        "category": "performance",
        "description_fr": "Cache shaders NVIDIA.",
        "description_en": "NVIDIA shader cache."
    },
    {
        "name": "__GL_SHADER_DISK_CACHE_PATH",
        "type": "nvidia",
        "category": "configuration",
        "description_fr": "Chemin cache NVIDIA.",
        "description_en": "NVIDIA cache path."
    },
    {
        "name": "__GL_SYNC_TO_VBLANK",
        "type": "nvidia",
        "category": "graphics",
        "description_fr": "VSync NVIDIA.",
        "description_en": "Vertical sync."
    },
    {
        "name": "__GL_THREADED_OPTIMIZATIONS",
        "type": "nvidia",
        "category": "performance",
        "description_fr": "Threading NVIDIA.",
        "description_en": "Threaded optimizations."
    },

    # =========================================================
    # SYSTEM LINUX
    # =========================================================
    {
        "name": "LD_LIBRARY_PATH",
        "type": "system",
        "category": "linux",
        "description_fr": "Librairies Linux.",
        "description_en": "Linux library path."
    },
    {
        "name": "LD_PRELOAD",
        "type": "system",
        "category": "linux",
        "description_fr": "Préchargement libs.",
        "description_en": "Preload libraries."
    },
    {
        "name": "MALLOC_ARENA_MAX",
        "type": "system",
        "category": "performance",
        "description_fr": "Optimisation mémoire.",
        "description_en": "Memory allocator tuning."
    },

    {
        "name": "GAMEMODERUN",
        "type": "system",
        "category": "performance",
        "description_fr": "Lance le jeu via GameMode afin d'appliquer automatiquement des optimisations système dédiées au jeu.",
        "description_en": "Launches the game through GameMode to automatically apply gaming-oriented system optimizations."
    },

    # =========================================================
    # STEAM
    # =========================================================
    {
        "name": "STEAM_COMPAT_APP_ID",
        "type": "steam",
        "category": "internal",
        "description_fr": "App Steam ID.",
        "description_en": "Steam app ID."
    },
    {
        "name": "STEAM_COMPAT_DATA_PATH",
        "type": "steam",
        "category": "internal",
        "description_fr": "Prefix Proton.",
        "description_en": "Proton prefix path."
    },
    {
        "name": "STEAM_COMPAT_TOOL_PATHS",
        "type": "steam",
        "category": "internal",
        "description_fr": "Tools Proton.",
        "description_en": "Proton tools path."
    },
    {
        "name": "STEAM_COMPAT_SHADER_PATH",
        "type": "steam",
        "category": "performance",
        "description_fr": "Cache shaders Steam.",
        "description_en": "Steam shader cache."
    },

    # =========================================================
    # HUD / OVERLAY
    # =========================================================
    {
        "name": "MANGOHUD",
        "type": "hud",
        "category": "overlay",
        "description_fr": "Overlay MangoHud.",
        "description_en": "MangoHud overlay."
    },
    {
        "name": "MANGOHUD_DLSYM",
        "type": "hud",
        "category": "compatibility",
        "description_fr": "Active le mode d'injection dynamique MangoHud via dlsym pour améliorer la détection des applications utilisant des bibliothèques graphiques chargées dynamiquement.",
        "description_en": "Enables MangoHud dynamic dlsym injection mode to improve detection of applications using dynamically loaded graphics libraries."
    },
    {
        "name": "MANGOHUD_CONFIG",
        "type": "hud",
        "category": "configuration",
        "description_fr": "Définit les paramètres de configuration MangoHud (affichage, métriques, limite FPS, position et options de l'overlay).",
        "description_en": "Defines MangoHud configuration parameters (display, metrics, FPS limit, position and overlay options)."
    },
    {
        "name": "MANGOHUD_OPENGL",
        "type": "hud",
        "category": "compatibility",
        "description_fr": "Active le support du rendu OpenGL dans MangoHud pour afficher l'overlay avec les applications utilisant OpenGL.",
        "description_en": "Enables MangoHud OpenGL rendering support to display the overlay with applications using OpenGL."
    },
    {
        "name": "vblank_mode",
        "type": "hud",
        "category": "graphics",
        "description_fr": "VSync Mesa.",
        "description_en": "Mesa vsync mode."
    },

    # =========================================================
    # WINE / GSTREAMER (MULTIMEDIA STACK CONTROL)
    # =========================================================
    {
        "name": "GST_PLUGIN_PATH",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Chemin des plugins GStreamer. Vide pour éviter les conflits avec les plugins système ou Proton.",
        "description_en": "GStreamer plugin path. Empty to avoid conflicts with system or Proton plugins."
    },
    {
        "name": "GST_DEBUG",
        "type": "wine",
        "category": "debug",
        "description_fr": "Niveau de logs GStreamer. 0 désactive totalement les logs.",
        "description_en": "GStreamer debug level. 0 disables all logging."
    },
    {
        "name": "WINE_DISABLE_GSTREAMER",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Désactive l’utilisation de GStreamer dans Wine pour éviter les erreurs multimédia et dépendances cassées.",
        "description_en": "Disables Wine GStreamer integration to prevent multimedia errors and broken dependencies."
    },
    # =========================================================
    # GAME
    # =========================================================
    {
        "name": "USE_D3D11",
        "type": "game",
        "category": "graphics",
        "description_fr": "Force l'utilisation du moteur de rendu Direct3D 11 au lieu de versions plus récentes de DirectX.",
        "description_en": "Forces the use of the Direct3D 11 renderer instead of newer DirectX versions."
    },
    {
        "name": "USEALLAVAILABLECORES",
        "type": "game",
        "category": "performance",
        "description_fr": "Demande au moteur Unreal Engine d'utiliser tous les cœurs CPU disponibles pour le traitement du jeu.",
        "description_en": "Instructs Unreal Engine to use all available CPU cores for game processing."
    }
]
