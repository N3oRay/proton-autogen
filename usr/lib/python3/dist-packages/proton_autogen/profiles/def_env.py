DXVK_ENV_VARS = [

    # =========================================================
    # DXVK
    # =========================================================
    {
        "name": "DXVK_FULLSCREEN",
        "type": "dxvk",
        "category": "compatibility",
        "description_fr": "Force DXVK à utiliser un mode plein écran exclusif ou contrôlé pour les applications Vulkan via DXVK.",
        "description_en": "Forces DXVK to use exclusive or controlled fullscreen mode for Vulkan-based applications.",
        "description_de": "Erzwingt, dass DXVK für Vulkan-basierte Anwendungen einen exklusiven oder kontrollierten Vollbildmodus verwendet.",
        "description_uk": "Примусово змушує DXVK використовувати ексклюзивний або керований повноекранний режим для програм на основі Vulkan.",
        "description_zh": "强制 DXVK 为基于 Vulkan 的应用程序使用独占或受控全屏模式。",
        "description_hi": "DXVK को Vulkan आधारित अनुप्रयोगों के लिए विशेष या नियंत्रित पूर्णस्क्रीन मोड का उपयोग करने के लिए बाध्य करता है।",
        "description_es": "Fuerza a DXVK a utilizar un modo de pantalla completa exclusivo o controlado para aplicaciones basadas en Vulkan.",
        "description_pt": "Força o DXVK a usar um modo de tela cheia exclusivo ou controlado para aplicações baseadas em Vulkan."
    },
    {
        "name": "DXVK_ASYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Active la compilation asynchrone des shaders avec DXVK afin de réduire les saccades liées à leur compilation pendant le jeu.",
        "description_en": "Enables asynchronous shader compilation in DXVK to reduce shader compilation stuttering during gameplay.",
        "description_de": "Aktiviert die asynchrone Shader-Kompilierung in DXVK, um Ruckler während der Shader-Kompilierung im Spiel zu reduzieren.",
        "description_uk": "Вмикає асинхронну компіляцію шейдерів у DXVK для зменшення підлагувань під час гри.",
        "description_zh": "启用 DXVK 异步着色器编译，以减少游戏过程中因着色器编译导致的卡顿。",
        "description_hi": "DXVK में एसिंक्रोनस शेडर संकलन सक्षम करता है ताकि गेम के दौरान शेडर संकलन से होने वाली रुकावट कम हो।",
        "description_es": "Activa la compilación asíncrona de shaders en DXVK para reducir los tirones causados por la compilación durante el juego.",
        "description_pt": "Ativa a compilação assíncrona de shaders no DXVK para reduzir travamentos causados pela compilação durante o jogo."
    },
    {
        "name": "DXVK_CONFIG",
        "type": "dxvk",
        "category": "configuration",
        "description_fr": "Configuration personnalisée DXVK.",
        "description_en": "Custom DXVK configuration.",
        "description_de": "Benutzerdefinierte DXVK-Konfiguration.",
        "description_uk": "Користувацька конфігурація DXVK.",
        "description_zh": "自定义 DXVK 配置。",
        "description_hi": "कस्टम DXVK कॉन्फ़िगरेशन।",
        "description_es": "Configuración personalizada de DXVK.",
        "description_pt": "Configuração personalizada do DXVK."
    },
    {
        "name": "DXVK_HUD",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Affiche l'overlay DXVK (FPS, mémoire, shaders).",
        "description_en": "Displays DXVK HUD overlay.",
        "description_de": "Zeigt das DXVK-HUD (FPS, Speicher, Shader) an.",
        "description_uk": "Відображає накладку DXVK HUD (FPS, пам'ять, шейдери).",
        "description_zh": "显示 DXVK HUD 覆盖层（FPS、内存、着色器）。",
        "description_hi": "DXVK HUD ओवरले (FPS, मेमोरी, शेडर) प्रदर्शित करता है।",
        "description_es": "Muestra la superposición DXVK HUD (FPS, memoria, shaders).",
        "description_pt": "Exibe o overlay DXVK HUD (FPS, memória, shaders)."
    },
    {
        "name": "DXVK_LOG_LEVEL",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Niveau de logs DXVK.",
        "description_en": "DXVK logging level.",
        "description_de": "DXVK-Protokollierungsstufe.",
        "description_uk": "Рівень журналювання DXVK.",
        "description_zh": "DXVK 日志级别。",
        "description_hi": "DXVK लॉग स्तर।",
        "description_es": "Nivel de registro de DXVK.",
        "description_pt": "Nível de log do DXVK."
    },
    {
        "name": "DXVK_LOG_PATH",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Chemin des logs DXVK.",
        "description_en": "DXVK log output path.",
        "description_de": "Ausgabepfad für DXVK-Protokolle.",
        "description_uk": "Шлях збереження журналів DXVK.",
        "description_zh": "DXVK 日志输出路径。",
        "description_hi": "DXVK लॉग आउटपुट पथ।",
        "description_es": "Ruta de salida de los registros DXVK.",
        "description_pt": "Caminho de saída dos logs do DXVK."
    },
    {
        "name": "DXVK_STATE_CACHE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Active le cache DXVK.",
        "description_en": "Enables DXVK state cache.",
        "description_de": "Aktiviert den DXVK-State-Cache.",
        "description_uk": "Вмикає кеш стану DXVK.",
        "description_zh": "启用 DXVK 状态缓存。",
        "description_hi": "DXVK स्टेट कैश सक्षम करता है।",
        "description_es": "Activa la caché de estado de DXVK.",
        "description_pt": "Ativa o cache de estado do DXVK."
    },
    {
        "name": "DXVK_STATE_CACHE_PATH",
        "type": "dxvk",
        "category": "configuration",
        "description_fr": "Chemin du cache DXVK.",
        "description_en": "DXVK cache path.",
        "description_de": "Pfad zum DXVK-State-Cache.",
        "description_uk": "Шлях до кешу DXVK.",
        "description_zh": "DXVK 缓存路径。",
        "description_hi": "DXVK कैश पथ।",
        "description_es": "Ruta de la caché de DXVK.",
        "description_pt": "Caminho do cache do DXVK."
    },
    {
        "name": "DXVK_STATE_CACHE_SIZE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Taille du cache DXVK.",
        "description_en": "DXVK cache size limit.",
        "description_de": "Größenbegrenzung des DXVK-State-Caches.",
        "description_uk": "Розмір кешу DXVK.",
        "description_zh": "DXVK 缓存大小限制。",
        "description_hi": "DXVK कैश आकार सीमा।",
        "description_es": "Límite de tamaño de la caché DXVK.",
        "description_pt": "Limite de tamanho do cache do DXVK."
    },
    {
        "name": "DXVK_ENABLE_NVAPI",
        "type": "dxvk",
        "category": "compatibility",
        "description_fr": "Active NVAPI via DXVK.",
        "description_en": "Enables NVAPI support.",
        "description_de": "Aktiviert die NVAPI-Unterstützung in DXVK.",
        "description_uk": "Вмикає підтримку NVAPI через DXVK.",
        "description_zh": "启用 DXVK 的 NVAPI 支持。",
        "description_hi": "DXVK के माध्यम से NVAPI समर्थन सक्षम करता है।",
        "description_es": "Activa la compatibilidad con NVAPI mediante DXVK.",
        "description_pt": "Ativa o suporte a NVAPI através do DXVK."
    },
    {
        "name": "DXVK_FILTER_DEVICE_NAME",
        "type": "dxvk",
        "category": "graphics",
        "description_fr": "Force un GPU Vulkan.",
        "description_en": "Forces a specific Vulkan GPU.",
        "description_de": "Erzwingt die Verwendung einer bestimmten Vulkan-GPU.",
        "description_uk": "Примусово вибирає певний Vulkan GPU.",
        "description_zh": "强制使用指定的 Vulkan GPU。",
        "description_hi": "एक विशिष्ट Vulkan GPU को बाध्य करता है।",
        "description_es": "Fuerza una GPU Vulkan específica.",
        "description_pt": "Força uma GPU Vulkan específica."
    },
    {
        "name": "DXVK_FRAME_RATE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Limite les FPS.",
        "description_en": "FPS limiter.",
        "description_de": "Begrenzt die Bildrate (FPS).",
        "description_uk": "Обмежує частоту кадрів (FPS).",
        "description_zh": "限制帧率（FPS）。",
        "description_hi": "FPS सीमा निर्धारित करता है।",
        "description_es": "Limita los FPS.",
        "description_pt": "Limita os FPS."
    },
    {
        "name": "DXVK_DEBUG",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Active les options de débogage de DXVK.",
        "description_en": "Enables DXVK debugging options.",
        "description_de": "Aktiviert die Debugging-Optionen von DXVK.",
        "description_uk": "Вмикає параметри налагодження DXVK.",
        "description_zh": "启用 DXVK 调试选项。",
        "description_hi": "DXVK डीबग विकल्पों को सक्षम करता है।",
        "description_es": "Activa las opciones de depuración de DXVK.",
        "description_pt": "Ativa as opções de depuração do DXVK."
    },
    {
        "name": "DXVK_CONFIG_FILE",
        "type": "dxvk",
        "category": "configuration",
        "description_fr": "Définit le chemin du fichier de configuration DXVK.",
        "description_en": "Sets the path to the DXVK configuration file.",
        "description_de": "Legt den Pfad zur DXVK-Konfigurationsdatei fest.",
        "description_uk": "Визначає шлях до файлу конфігурації DXVK.",
        "description_zh": "设置 DXVK 配置文件的路径。",
        "description_hi": "DXVK कॉन्फ़िगरेशन फ़ाइल का पथ निर्धारित करता है।",
        "description_es": "Establece la ruta del archivo de configuración de DXVK.",
        "description_pt": "Define o caminho para o ficheiro de configuração do DXVK."
    },
    {
        "name": "DXVK_SHADER_CACHE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Active ou désactive le cache des shaders de DXVK.",
        "description_en": "Enables or disables the DXVK shader cache.",
        "description_de": "Aktiviert oder deaktiviert den Shader-Cache von DXVK.",
        "description_uk": "Вмикає або вимикає кеш шейдерів DXVK.",
        "description_zh": "启用或禁用 DXVK 着色器缓存。",
        "description_hi": "DXVK शेडर कैश को सक्षम या अक्षम करता है।",
        "description_es": "Activa o desactiva la caché de sombreadores de DXVK.",
        "description_pt": "Ativa ou desativa o cache de shaders do DXVK."
    },
    {
        "name": "DXVK_SHADER_CACHE_PATH",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Définit le chemin du cache des shaders de DXVK.",
        "description_en": "Sets the path to the DXVK shader cache.",
        "description_de": "Legt den Pfad zum Shader-Cache von DXVK fest.",
        "description_uk": "Визначає шлях до кешу шейдерів DXVK.",
        "description_zh": "设置 DXVK 着色器缓存的路径。",
        "description_hi": "DXVK शेडर कैश का पथ निर्धारित करता है।",
        "description_es": "Establece la ruta de la caché de sombreadores de DXVK.",
        "description_pt": "Define o caminho para o cache de shaders do DXVK."
    }
]
VKD3D_ENV_VARS = [
    # =========================================================
    # VKD3D (DirectX 12)
    # =========================================================
    {
        "name": "VKD3D_CONFIG",
        "type": "vkd3d",
        "category": "configuration",
        "description_fr": "Configuration VKD3D-Proton (DX12).",
        "description_en": "VKD3D-Proton configuration.",
        "description_de": "VKD3D-Proton-Konfiguration.",
        "description_uk": "Конфігурація VKD3D-Proton (DX12).",
        "description_zh": "VKD3D-Proton 配置（DX12）。",
        "description_hi": "VKD3D-Proton कॉन्फ़िगरेशन (DX12)।",
        "description_es": "Configuración de VKD3D-Proton (DX12).",
        "description_pt": "Configuração do VKD3D-Proton (DX12)."
    },
    {
        "name": "VKD3D_DEBUG",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Logs VKD3D.",
        "description_en": "VKD3D debug output.",
        "description_de": "VKD3D-Debugausgabe.",
        "description_uk": "Вивід налагоджувальних журналів VKD3D.",
        "description_zh": "VKD3D 调试输出。",
        "description_hi": "VKD3D डिबग आउटपुट।",
        "description_es": "Salida de depuración de VKD3D.",
        "description_pt": "Saída de depuração do VKD3D."
    },
    {
        "name": "VKD3D_SHADER_DEBUG",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Debug shaders DX12.",
        "description_en": "DX12 shader debugging.",
        "description_de": "Debugging für DirectX-12-Shader.",
        "description_uk": "Налагодження шейдерів DX12.",
        "description_zh": "DX12 着色器调试。",
        "description_hi": "DX12 शेडर डिबगिंग।",
        "description_es": "Depuración de shaders DX12.",
        "description_pt": "Depuração de shaders DX12."
    },
    {
        "name": "VKD3D_FEATURE_LEVEL",
        "type": "vkd3d",
        "category": "compatibility",
        "description_fr": "Force un feature level DX12.",
        "description_en": "Forces DX12 feature level.",
        "description_de": "Erzwingt ein bestimmtes DirectX-12-Feature-Level.",
        "description_uk": "Примусово встановлює рівень функцій DX12.",
        "description_zh": "强制设置 DX12 功能级别。",
        "description_hi": "DX12 फ़ीचर लेवल को बाध्य करता है।",
        "description_es": "Fuerza un nivel de características de DX12.",
        "description_pt": "Força um nível de recursos do DX12."
    },
    {
        "name": "VKD3D_DEBUGFLAGS",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Flags debug VKD3D.",
        "description_en": "VKD3D debug flags.",
        "description_de": "VKD3D-Debug-Flags.",
        "description_uk": "Прапорці налагодження VKD3D.",
        "description_zh": "VKD3D 调试标志。",
        "description_hi": "VKD3D डिबग फ़्लैग।",
        "description_es": "Indicadores de depuración de VKD3D.",
        "description_pt": "Flags de depuração do VKD3D."
    },
    {
        "name": "VKD3D_LOG_FILE",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Définit le fichier dans lequel VKD3D-Proton écrit ses logs.",
        "description_en": "Sets the file where VKD3D-Proton writes its logs.",
        "description_de": "Legt die Datei fest, in die VKD3D-Proton seine Logs schreibt.",
        "description_uk": "Визначає файл, у який VKD3D-Proton записує журнали.",
        "description_zh": "设置 VKD3D-Proton 写入日志的文件。",
        "description_hi": "वह फ़ाइल निर्धारित करता है जिसमें VKD3D-Proton लॉग लिखता है।",
        "description_es": "Define el archivo donde VKD3D-Proton escribe sus registros.",
        "description_pt": "Define o ficheiro onde o VKD3D-Proton grava os seus registos."
    },
    {
        "name": "VKD3D_VULKAN_DEVICE",
        "type": "vkd3d",
        "category": "graphics",
        "description_fr": "Force VKD3D-Proton à utiliser un périphérique Vulkan spécifique.",
        "description_en": "Forces VKD3D-Proton to use a specific Vulkan device.",
        "description_de": "Zwingt VKD3D-Proton, ein bestimmtes Vulkan-Gerät zu verwenden.",
        "description_uk": "Примусово використовує певний пристрій Vulkan у VKD3D-Proton.",
        "description_zh": "强制 VKD3D-Proton 使用指定的 Vulkan 设备。",
        "description_hi": "VKD3D-Proton को किसी विशिष्ट Vulkan डिवाइस का उपयोग करने के लिए बाध्य करता है।",
        "description_es": "Fuerza a VKD3D-Proton a utilizar un dispositivo Vulkan específico.",
        "description_pt": "Força o VKD3D-Proton a utilizar um dispositivo Vulkan específico."
    },
    {
        "name": "VKD3D_FILTER_DEVICE_NAME",
        "type": "vkd3d",
        "category": "graphics",
        "description_fr": "Sélectionne le périphérique Vulkan selon son nom.",
        "description_en": "Selects the Vulkan device by name.",
        "description_de": "Wählt das Vulkan-Gerät anhand seines Namens aus.",
        "description_uk": "Вибирає пристрій Vulkan за його назвою.",
        "description_zh": "根据名称选择 Vulkan 设备。",
        "description_hi": "नाम के आधार पर Vulkan डिवाइस चुनता है।",
        "description_es": "Selecciona el dispositivo Vulkan por su nombre.",
        "description_pt": "Seleciona o dispositivo Vulkan pelo nome."
    },
    {
        "name": "VKD3D_DISABLE_EXTENSIONS",
        "type": "vkd3d",
        "category": "compatibility",
        "description_fr": "Désactive certaines extensions Vulkan utilisées par VKD3D-Proton.",
        "description_en": "Disables specific Vulkan extensions used by VKD3D-Proton.",
        "description_de": "Deaktiviert bestimmte von VKD3D-Proton verwendete Vulkan-Erweiterungen.",
        "description_uk": "Вимикає певні розширення Vulkan, які використовує VKD3D-Proton.",
        "description_zh": "禁用 VKD3D-Proton 使用的指定 Vulkan 扩展。",
        "description_hi": "VKD3D-Proton द्वारा उपयोग किए जाने वाले कुछ Vulkan एक्सटेंशन को अक्षम करता है।",
        "description_es": "Desactiva determinadas extensiones de Vulkan utilizadas por VKD3D-Proton.",
        "description_pt": "Desativa determinadas extensões Vulkan utilizadas pelo VKD3D-Proton."
    },
    {
        "name": "VKD3D_SWAPCHAIN_PRESENT_MODE",
        "type": "vkd3d",
        "category": "graphics",
        "description_fr": "Force le mode de présentation Vulkan de la swapchain.",
        "description_en": "Forces the Vulkan swapchain presentation mode.",
        "description_de": "Erzwingt den Vulkan-Präsentationsmodus der Swapchain.",
        "description_uk": "Примусово встановлює режим подання Vulkan для swapchain.",
        "description_zh": "强制设置 Vulkan 交换链的呈现模式。",
        "description_hi": "Vulkan स्वैपचेन के प्रेज़ेंटेशन मोड को बाध्य करता है।",
        "description_es": "Fuerza el modo de presentación de la swapchain de Vulkan.",
        "description_pt": "Força o modo de apresentação da swapchain Vulkan."
    },
    {
        "name": "VKD3D_FRAME_RATE",
        "type": "vkd3d",
        "category": "performance",
        "description_fr": "Limite le nombre d'images par seconde de VKD3D-Proton.",
        "description_en": "Limits the frame rate in VKD3D-Proton.",
        "description_de": "Begrenzt die Bildrate in VKD3D-Proton.",
        "description_uk": "Обмежує частоту кадрів у VKD3D-Proton.",
        "description_zh": "限制 VKD3D-Proton 的帧率。",
        "description_hi": "VKD3D-Proton में फ़्रेम रेट को सीमित करता है।",
        "description_es": "Limita la tasa de fotogramas en VKD3D-Proton.",
        "description_pt": "Limita a taxa de fotogramas no VKD3D-Proton."
    },
    {
        "name": "VKD3D_SHADER_CACHE_PATH",
        "type": "vkd3d",
        "category": "performance",
        "description_fr": "Définit le chemin du cache des shaders VKD3D-Proton.",
        "description_en": "Sets the path to the VKD3D-Proton shader cache.",
        "description_de": "Legt den Pfad zum Shader-Cache von VKD3D-Proton fest.",
        "description_uk": "Визначає шлях до кешу шейдерів VKD3D-Proton.",
        "description_zh": "设置 VKD3D-Proton 着色器缓存的路径。",
        "description_hi": "VKD3D-Proton शेडर कैश का पथ निर्धारित करता है।",
        "description_es": "Establece la ruta de la caché de sombreadores de VKD3D-Proton.",
        "description_pt": "Define o caminho para o cache de shaders do VKD3D-Proton."
    },
    {
        "name": "VKD3D_SHADER_DUMP_PATH",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Définit le dossier d'export des shaders VKD3D-Proton.",
        "description_en": "Sets the directory where VKD3D-Proton dumps shaders.",
        "description_de": "Legt das Verzeichnis fest, in das VKD3D-Proton Shader exportiert.",
        "description_uk": "Визначає каталог для збереження шейдерів VKD3D-Proton.",
        "description_zh": "设置 VKD3D-Proton 导出着色器的目录。",
        "description_hi": "वह फ़ोल्डर निर्धारित करता है जिसमें VKD3D-Proton शेडर निर्यात करता है।",
        "description_es": "Establece el directorio donde VKD3D-Proton exporta los sombreadores.",
        "description_pt": "Define o diretório onde o VKD3D-Proton exporta os shaders."
    },
    {
        "name": "VKD3D_SHADER_OVERRIDE",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Permet de remplacer certains shaders de VKD3D-Proton.",
        "description_en": "Allows specific VKD3D-Proton shaders to be overridden.",
        "description_de": "Ermöglicht das Ersetzen bestimmter VKD3D-Proton-Shader.",
        "description_uk": "Дозволяє замінювати певні шейдери VKD3D-Proton.",
        "description_zh": "允许替换指定的 VKD3D-Proton 着色器。",
        "description_hi": "कुछ VKD3D-Proton शेडर को बदलने की अनुमति देता है।",
        "description_es": "Permite reemplazar determinados sombreadores de VKD3D-Proton.",
        "description_pt": "Permite substituir determinados shaders do VKD3D-Proton."
    }
]
PROTON_ENV_VARS = [
    # =========================================================
    # PROTON
    # =========================================================

    {
        "name": "PROTON_LOG",
        "type": "proton",
        "category": "debug",
        "description_fr": "Active les logs Proton.",
        "description_en": "Enables Proton logs.",
        "description_de": "Aktiviert die Proton-Protokollierung.",
        "description_uk": "Вмикає журнали Proton.",
        "description_zh": "启用 Proton 日志。",
        "description_hi": "Proton लॉग सक्षम करता है।",
        "description_es": "Activa los registros de Proton.",
        "description_pt": "Ativa os logs do Proton."
    },
    {
        "name": "PROTON_LOG_DIR",
        "type": "proton",
        "category": "debug",
        "description_fr": "Dossier des logs Proton.",
        "description_en": "Proton log directory.",
        "description_de": "Verzeichnis für Proton-Protokolle.",
        "description_uk": "Каталог журналів Proton.",
        "description_zh": "Proton 日志目录。",
        "description_hi": "Proton लॉग निर्देशिका।",
        "description_es": "Directorio de registros de Proton.",
        "description_pt": "Diretório de logs do Proton."
    },
    {
        "name": "PROTON_NO_ESYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Désactive Esync.",
        "description_en": "Disables Esync.",
        "description_de": "Deaktiviert Esync.",
        "description_uk": "Вимикає Esync.",
        "description_zh": "禁用 Esync。",
        "description_hi": "Esync अक्षम करता है।",
        "description_es": "Desactiva Esync.",
        "description_pt": "Desativa o Esync."
    },
    {
        "name": "PROTON_NO_FSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Désactive Fsync.",
        "description_en": "Disables Fsync.",
        "description_de": "Deaktiviert Fsync.",
        "description_uk": "Вимикає Fsync.",
        "description_zh": "禁用 Fsync。",
        "description_hi": "Fsync अक्षम करता है।",
        "description_es": "Desactiva Fsync.",
        "description_pt": "Desativa o Fsync."
    },
    {
        "name": "PROTON_USE_WINED3D",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Utilise WineD3D au lieu de DXVK.",
        "description_en": "Uses WineD3D instead of DXVK.",
        "description_de": "Verwendet WineD3D anstelle von DXVK.",
        "description_uk": "Використовує WineD3D замість DXVK.",
        "description_zh": "使用 WineD3D 替代 DXVK。",
        "description_hi": "DXVK के बजाय WineD3D का उपयोग करता है।",
        "description_es": "Utiliza WineD3D en lugar de DXVK.",
        "description_pt": "Usa WineD3D em vez do DXVK."
    },
    {
        "name": "PROTON_USE_D7VK",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Direct3D 7 - Utilise D7VK à la place de DXVK/D3D9.",
        "description_en": "Direct3D 7 - Uses D7VK instead of DXVK/D3D9.",
        "description_de": "Direct3D 7 - Verwendet D7VK anstelle von DXVK/D3D9.",
        "description_uk": "Direct3D 7 - Використовує D7VK замість DXVK/D3D9.",
        "description_zh": "Direct3D 7 - 使用 D7VK 替代 DXVK/D3D9。",
        "description_hi": "Direct3D 7 - DXVK/D3D9 के बजाय D7VK का उपयोग करता है।",
        "description_es": "Direct3D 7 - Utiliza D7VK en lugar de DXVK/D3D9.",
        "description_pt": "Direct3D 7 - Usa D7VK em vez de DXVK/D3D9."
    },
    {
        "name": "PROTON_ENABLE_NVAPI",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active le support de NVIDIA NVAPI dans Proton pour permettre l'utilisation de certaines fonctionnalités spécifiques aux cartes NVIDIA.",
        "description_en": "Enables NVIDIA NVAPI support in Proton, allowing access to certain NVIDIA-specific features.",
        "description_de": "Aktiviert die NVIDIA-NVAPI-Unterstützung in Proton und ermöglicht den Zugriff auf NVIDIA-spezifische Funktionen.",
        "description_uk": "Вмикає підтримку NVIDIA NVAPI у Proton для доступу до певних функцій відеокарт NVIDIA.",
        "description_zh": "在 Proton 中启用 NVIDIA NVAPI 支持，以访问某些 NVIDIA 专属功能。",
        "description_hi": "Proton में NVIDIA NVAPI समर्थन सक्षम करता है, जिससे कुछ NVIDIA विशेष सुविधाओं का उपयोग किया जा सकता है।",
        "description_es": "Activa el soporte NVIDIA NVAPI en Proton, permitiendo acceder a ciertas funciones específicas de NVIDIA.",
        "description_pt": "Ativa o suporte NVIDIA NVAPI no Proton, permitindo acesso a determinados recursos específicos da NVIDIA."
    },
    {
        "name": "PROTON_ENABLE_WAYLAND",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active le support Wayland dans Proton lorsque disponible.",
        "description_en": "Enables Wayland support in Proton when available.",
        "description_de": "Aktiviert die Wayland-Unterstützung in Proton, sofern verfügbar.",
        "description_uk": "Вмикає підтримку Wayland у Proton, якщо вона доступна.",
        "description_zh": "在可用时启用 Proton 的 Wayland 支持。",
        "description_hi": "उपलब्ध होने पर Proton में Wayland समर्थन सक्षम करता है।",
        "description_es": "Activa el soporte de Wayland en Proton cuando está disponible.",
        "description_pt": "Ativa o suporte Wayland no Proton quando disponível."
    },
    {
        "name": "PROTON_ENABLE_HDR",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active la prise en charge HDR pour les jeux compatibles via Proton. Dépréciée dans Proton-CachyOS où le HDR est géré automatiquement.",
        "description_en": "Enables HDR support for compatible games through Proton. Deprecated in Proton-CachyOS where HDR is handled automatically.",
        "description_de": "Aktiviert HDR-Unterstützung für kompatible Spiele über Proton. In Proton-CachyOS veraltet, da HDR dort automatisch verwaltet wird.",
        "description_uk": "Вмикає підтримку HDR для сумісних ігор через Proton. Застаріло в Proton-CachyOS, де HDR керується автоматично.",
        "description_zh": "通过 Proton 为兼容游戏启用 HDR 支持。在 Proton-CachyOS 中已弃用，因为 HDR 会自动管理。",
        "description_hi": "Proton के माध्यम से संगत गेम के लिए HDR समर्थन सक्षम करता है। Proton-CachyOS में अप्रचलित है क्योंकि HDR स्वचालित रूप से प्रबंधित होता है।",
        "description_es": "Activa el soporte HDR para juegos compatibles mediante Proton. Está obsoleto en Proton-CachyOS, donde HDR se gestiona automáticamente.",
        "description_pt": "Ativa o suporte HDR para jogos compatíveis através do Proton. Está descontinuado no Proton-CachyOS, onde o HDR é gerenciado automaticamente."
    },
    {
        "name": "PROTON_FORCE_LARGE_ADDRESS_AWARE",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Force LAA pour 32-bit.",
        "description_en": "Forces Large Address Awareness.",
        "description_de": "Erzwingt Large Address Awareness für 32-Bit-Anwendungen.",
        "description_uk": "Примусово вмикає Large Address Awareness для 32-бітних програм.",
        "description_zh": "强制启用 32 位程序的大地址感知。",
        "description_hi": "32-बिट अनुप्रयोगों के लिए Large Address Awareness को मजबूर करता है।",
        "description_es": "Fuerza Large Address Awareness para aplicaciones de 32 bits.",
        "description_pt": "Força Large Address Awareness para aplicações de 32 bits."
    },
    {
        "name": "PROTON_DISCORD_BRIDGE",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Active le pont Discord Rich Presence intégré à Proton. Permet à certains jeux de communiquer leur présence à Discord.",
        "description_en": "Enables Proton's built-in Discord Rich Presence bridge. Allows supported games to report their presence to Discord.",
        "description_de": "Aktiviert die integrierte Discord-Rich-Presence-Brücke von Proton. Ermöglicht unterstützten Spielen, ihren Status an Discord zu übermitteln.",
        "description_uk": "Вмикає вбудований у Proton міст Discord Rich Presence. Дозволяє підтримуваним іграм передавати свій статус у Discord.",
        "description_zh": "启用 Proton 内置的 Discord Rich Presence 桥接功能。允许支持的游戏向 Discord 提供游戏状态。",
        "description_hi": "Proton के अंतर्निहित Discord Rich Presence ब्रिज को सक्षम करता है। समर्थित गेम को अपनी स्थिति Discord पर भेजने देता है।",
        "description_es": "Activa el puente Discord Rich Presence integrado en Proton. Permite que los juegos compatibles comuniquen su estado a Discord.",
        "description_pt": "Ativa a ponte Discord Rich Presence integrada no Proton. Permite que jogos compatíveis comuniquem o seu estado ao Discord."
    },
    {
        "name": "PROTON_USE_OPTISCALER",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Active l'intégration d'OptiScaler dans GE-Proton. Permet selon le jeu d'utiliser des techniques d'upscaling modernes.",
        "description_en": "Enables OptiScaler integration in GE-Proton. Allows modern upscaling techniques to be used depending on the game.",
        "description_de": "Aktiviert die OptiScaler-Integration in GE-Proton. Ermöglicht je nach Spiel die Nutzung moderner Upscaling-Techniken.",
        "description_uk": "Вмикає інтеграцію OptiScaler у GE-Proton. Залежно від гри дозволяє використовувати сучасні методи масштабування.",
        "description_zh": "启用 GE-Proton 的 OptiScaler 集成。根据游戏情况，可使用现代升频技术。",
        "description_hi": "GE-Proton में OptiScaler एकीकरण सक्षम करता है। गेम के आधार पर आधुनिक अपस्केलिंग तकनीकों का उपयोग किया जा सकता है।",
        "description_es": "Activa la integración de OptiScaler en GE-Proton. Permite utilizar técnicas modernas de reescalado según el juego.",
        "description_pt": "Ativa a integração do OptiScaler no GE-Proton. Permite utilizar técnicas modernas de upscaling, dependendo do jogo."
    },
    {
        "name": "PROTON_SONY_DUALSENSE_AS_DUALSHOCK4",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Fait passer une DualSense/DualSense Edge pour une DualShock 4 auprès du jeu. Utile pour les jeux compatibles avec la DS4 mais pas avec la DualSense.",
        "description_en": "Makes a DualSense/DualSense Edge appear as a DualShock 4 to the game. Useful for games that support the DS4 but not the DualSense.",
        "description_de": "Gibt eine DualSense/DualSense Edge gegenüber dem Spiel als DualShock 4 aus. Nützlich für Spiele, die die DS4, aber nicht die DualSense unterstützen.",
        "description_uk": "Представляє DualSense/DualSense Edge для гри як DualShock 4. Корисно для ігор, які підтримують DS4, але не DualSense.",
        "description_zh": "让游戏将 DualSense/DualSense Edge 识别为 DualShock 4。适用于支持 DS4 但不支持 DualSense 的游戏。",
        "description_hi": "गेम के सामने DualSense/DualSense Edge को DualShock 4 के रूप में प्रस्तुत करता है। उन गेम्स के लिए उपयोगी है जो DS4 का समर्थन करते हैं लेकिन DualSense का नहीं।",
        "description_es": "Hace que el juego detecte un DualSense/DualSense Edge como un DualShock 4. Útil para juegos compatibles con DS4 pero no con DualSense.",
        "description_pt": "Faz com que o jogo reconheça um DualSense/DualSense Edge como um DualShock 4. Útil para jogos compatíveis com DS4, mas não com DualSense."
    },
    {
        "name": "PROTON_SONY_HIDRAW_XINPUT",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Convertit les contrôleurs Sony DS4/DualSense/DualSense Edge en XInput. Utile si les jeux détectent mal les contrôleurs PlayStation ou leurs mappages.",
        "description_en": "Converts Sony DS4/DualSense/DualSense Edge controllers to XInput. Useful when games misdetect PlayStation controllers or their mappings.",
        "description_de": "Konvertiert Sony DS4/DualSense/DualSense Edge-Controller in XInput. Nützlich bei Erkennungs- oder Zuordnungsproblemen.",
        "description_uk": "Перетворює контролери Sony DS4/DualSense/DualSense Edge на XInput. Корисно при проблемах із розпізнаванням або прив’язкою кнопок.",
        "description_zh": "将 Sony DS4/DualSense/DualSense Edge 控制器转换为 XInput。适用于控制器识别或按键映射异常的情况。",
        "description_hi": "Sony DS4/DualSense/DualSense Edge कंट्रोलरों को XInput में बदलता है। कंट्रोलर पहचान या मैपिंग की समस्याओं में उपयोगी।",
        "description_es": "Convierte los mandos Sony DS4/DualSense/DualSense Edge a XInput. Útil si hay problemas de detección o asignación.",
        "description_pt": "Converte os comandos Sony DS4/DualSense/DualSense Edge para XInput. Útil em caso de problemas de deteção ou mapeamento."
    },
    {
        "name": "PROTON_STEAMINPUT_XINPUT_FALLBACK",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Crée un périphérique Steam Input et lui transmet les contrôleurs XInput. Utile pour les jeux nécessitant Steam Input, notamment avec Wine-Wayland.",
        "description_en": "Creates a Steam Input device and forwards XInput controllers to it. Useful for games requiring Steam Input, especially with Wine-Wayland.",
        "description_de": "Erstellt ein Steam-Input-Gerät und leitet XInput-Controller an dieses weiter. Nützlich für Spiele mit Steam-Input-Anforderung, insbesondere mit Wine-Wayland.",
        "description_uk": "Створює пристрій Steam Input і передає йому контролери XInput. Корисно для ігор, що потребують Steam Input, зокрема з Wine-Wayland.",
        "description_zh": "创建 Steam Input 设备并传递 XInput 控制器。适用于需要 Steam Input 的游戏，尤其是 Wine-Wayland。",
        "description_hi": "Steam Input डिवाइस बनाता है और XInput कंट्रोलरों को इसमें भेजता है। Steam Input की आवश्यकता वाले गेम्स में, खासकर Wine-Wayland के साथ, उपयोगी।",
        "description_es": "Crea un dispositivo Steam Input y le transmite los mandos XInput. Útil para juegos que requieren Steam Input, especialmente con Wine-Wayland.",
        "description_pt": "Cria um dispositivo Steam Input e encaminha os comandos XInput. Útil para jogos que requerem Steam Input, especialmente com Wine-Wayland."
    },
    {
        "name": "PROTON_ENABLE_FSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Force Fsync Proton.",
        "description_en": "Enables Fsync.",
        "description_de": "Aktiviert Fsync.",
        "description_uk": "Вмикає Fsync у Proton.",
        "description_zh": "启用 Proton Fsync。",
        "description_hi": "Proton Fsync सक्षम करता है।",
        "description_es": "Activa Fsync en Proton.",
        "description_pt": "Ativa o Fsync no Proton."
    },
    {
        "name": "PROTON_WAYLAND_MONITOR",
        "type": "proton",
        "category": "performance",
        "description_fr": "Sélectionne le moniteur Wayland utilisé par Proton. Exemple : PROTON_WAYLAND_MONITOR=HDMI-A-1 %command%",
        "description_en": "Selects the Wayland monitor used by Proton. Example: PROTON_WAYLAND_MONITOR=HDMI-A-1 %command%",
        "description_de": "Wählt den von Proton verwendeten Wayland-Monitor aus. Beispiel: PROTON_WAYLAND_MONITOR=HDMI-A-1 %command%",
        "description_uk": "Вибирає монітор Wayland, який використовує Proton. Приклад: PROTON_WAYLAND_MONITOR=HDMI-A-1 %command%",
        "description_zh": "选择 Proton 使用的 Wayland 显示器。例如：PROTON_WAYLAND_MONITOR=HDMI-A-1 %command%",
        "description_hi": "Proton द्वारा उपयोग किए जाने वाले Wayland मॉनिटर का चयन करता है। उदाहरण: PROTON_WAYLAND_MONITOR=HDMI-A-1 %command%",
        "description_es": "Selecciona el monitor Wayland utilizado por Proton. Ejemplo: PROTON_WAYLAND_MONITOR=HDMI-A-1 %command%",
        "description_pt": "Seleciona o monitor Wayland utilizado pelo Proton. Exemplo: PROTON_WAYLAND_MONITOR=HDMI-A-1 %command%"
    },
    {
        "name": "PROTON_USE_NTSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Active NTSync, une méthode de synchronisation plus efficace visant à améliorer les performances CPU et la compatibilité des jeux Windows.",
        "description_en": "Enables NTSync, a more efficient synchronization method designed to improve CPU performance and Windows game compatibility.",
        "description_de": "Aktiviert NTSync, eine effizientere Synchronisationsmethode zur Verbesserung der CPU-Leistung und der Kompatibilität von Windows-Spielen.",
        "description_uk": "Вмикає NTSync — ефективніший метод синхронізації для покращення продуктивності CPU та сумісності ігор Windows.",
        "description_zh": "启用 NTSync，这是一种更高效的同步方法，旨在提升 CPU 性能并改善 Windows 游戏兼容性。",
        "description_hi": "NTSync सक्षम करता है, जो CPU प्रदर्शन और Windows गेम संगतता सुधारने के लिए एक अधिक कुशल सिंक्रोनाइज़ेशन विधि है।",
        "description_es": "Activa NTSync, un método de sincronización más eficiente diseñado para mejorar el rendimiento de la CPU y la compatibilidad con juegos de Windows.",
        "description_pt": "Ativa o NTSync, um método de sincronização mais eficiente criado para melhorar o desempenho da CPU e a compatibilidade com jogos Windows."
    }
]
WINE_ENV_VARS = [
    # =========================================================
    # WINE
    # =========================================================

    {
        "name": "WINEPREFIX",
        "type": "wine",
        "category": "configuration",
        "description_fr": "Préfixe Wine.",
        "description_en": "Wine prefix path.",
        "description_de": "Pfad zum Wine-Präfix.",
        "description_uk": "Шлях до префікса Wine.",
        "description_zh": "Wine 前缀路径。",
        "description_hi": "Wine प्रीफ़िक्स का पथ।",
        "description_es": "Ruta del prefijo de Wine.",
        "description_pt": "Caminho do prefixo Wine."
    },
    {
        "name": "WINEARCH",
        "type": "wine",
        "category": "configuration",
        "description_fr": "Architecture Wine.",
        "description_en": "Wine architecture.",
        "description_de": "Wine-Architektur.",
        "description_uk": "Архітектура Wine.",
        "description_zh": "Wine 架构。",
        "description_hi": "Wine आर्किटेक्चर।",
        "description_es": "Arquitectura de Wine.",
        "description_pt": "Arquitetura do Wine."
    },
    {
        "name": "WINEDEBUG",
        "type": "wine",
        "category": "debug",
        "description_fr": "Debug Wine.",
        "description_en": "Wine debug output.",
        "description_de": "Wine-Debugausgabe.",
        "description_uk": "Налагодження Wine.",
        "description_zh": "Wine 调试输出。",
        "description_hi": "Wine डिबग आउटपुट।",
        "description_es": "Salida de depuración de Wine.",
        "description_pt": "Saída de depuração do Wine."
    },
    {
        "name": "WINEDLLOVERRIDES",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Overrides DLL.",
        "description_en": "DLL override rules.",
        "description_de": "Regeln zum Überschreiben von DLLs.",
        "description_uk": "Правила перевизначення DLL.",
        "description_zh": "DLL 覆盖规则。",
        "description_hi": "DLL ओवरराइड नियम।",
        "description_es": "Reglas de reemplazo de DLL.",
        "description_pt": "Regras de substituição de DLL."
    },
    {
        "name": "WINEALSA_CHANNELS",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Force le nombre de canaux audio exposés par WineALSA : 2 = stéréo, 4 = 4 canaux, 6 = 5.1, 8 = 7.1. Utile pour résoudre les problèmes de son et de spatialisation audio.",
        "description_en": "Forces the number of audio channels exposed by WineALSA: 2 = stereo, 4 = 4 channels, 6 = 5.1, 8 = 7.1. Useful for troubleshooting audio and spatial audio issues.",
        "description_de": "Erzwingt die Anzahl der von WineALSA bereitgestellten Audiokanäle: 2 = Stereo, 4 = 4 Kanäle, 6 = 5.1, 8 = 7.1. Nützlich zur Behebung von Problemen mit Audio und Raumklang.",
        "description_uk": "Примусово встановлює кількість аудіоканалів, доступних через WineALSA: 2 = стерео, 4 = 4 канали, 6 = 5.1, 8 = 7.1. Корисно для усунення проблем зі звуком і просторовим аудіо.",
        "description_zh": "强制设置 WineALSA 提供的音频声道数量：2 = 立体声，4 = 4 声道，6 = 5.1，8 = 7.1。适用于排查音频和空间音频问题。",
        "description_hi": "WineALSA द्वारा उपलब्ध कराए जाने वाले ऑडियो चैनलों की संख्या निर्धारित करता है: 2 = स्टीरियो, 4 = 4 चैनल, 6 = 5.1, 8 = 7.1। ऑडियो और स्थानिक ऑडियो से जुड़ी समस्याओं को हल करने में उपयोगी।",
        "description_es": "Fuerza el número de canales de audio expuestos por WineALSA: 2 = estéreo, 4 = 4 canales, 6 = 5.1, 8 = 7.1. Útil para solucionar problemas de audio y audio espacial.",
        "description_pt": "Força o número de canais de áudio disponibilizados pelo WineALSA: 2 = estéreo, 4 = 4 canais, 6 = 5.1, 8 = 7.1. Útil para solucionar problemas de áudio e áudio espacial."
    },
    {
        "name": "WINEALSA_SPATIAL",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Active le downmix spatial de WineALSA.",
        "description_en": "Enables WineALSA spatial downmixing.",
        "description_de": "Aktiviert das räumliche Downmixing von WineALSA.",
        "description_uk": "Вмикає просторове мікшування WineALSA.",
        "description_zh": "启用 WineALSA 空间混音。",
        "description_hi": "WineALSA के स्थानिक डाउनमिक्सिंग को सक्षम करता है।",
        "description_es": "Activa el downmix espacial de WineALSA.",
        "description_pt": "Ativa o downmix espacial do WineALSA."
    },
    {
        "name": "WINEESYNC",
        "type": "wine",
        "category": "performance",
        "description_fr": "Esync Wine.",
        "description_en": "Wine Esync.",
        "description_de": "Wine Esync.",
        "description_uk": "Esync у Wine.",
        "description_zh": "Wine Esync。",
        "description_hi": "Wine Esync।",
        "description_es": "Esync de Wine.",
        "description_pt": "Esync do Wine."
    },
    {
        "name": "WINEFSYNC",
        "type": "wine",
        "category": "performance",
        "description_fr": "Fsync Wine.",
        "description_en": "Wine Fsync.",
        "description_de": "Wine Fsync.",
        "description_uk": "Fsync у Wine.",
        "description_zh": "Wine Fsync。",
        "description_hi": "Wine Fsync।",
        "description_es": "Fsync de Wine.",
        "description_pt": "Fsync do Wine."
    },
    {
        "name": "WINE_LARGE_ADDRESS_AWARE",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "LAA Wine.",
        "description_en": "Large address aware mode.",
        "description_de": "Large-Address-Aware-Modus.",
        "description_uk": "Режим Large Address Aware у Wine.",
        "description_zh": "大地址感知模式。",
        "description_hi": "Large Address Aware मोड।",
        "description_es": "Modo Large Address Aware.",
        "description_pt": "Modo Large Address Aware."
    },

    {
        "name": "WINE_FULLSCREEN_FSR",
        "type": "wine",
        "category": "graphics",
        "description_fr": "Active ou désactive l'utilisation de FSR (FidelityFX Super Resolution) pour l'upscaling en plein écran dans Wine/Proton.",
        "description_en": "Enables or disables FidelityFX Super Resolution (FSR) upscaling in fullscreen mode in Wine/Proton.",
        "description_de": "Aktiviert oder deaktiviert FidelityFX Super Resolution (FSR) für das Upscaling im Vollbildmodus unter Wine/Proton.",
        "description_uk": "Вмикає або вимикає масштабування FSR (FidelityFX Super Resolution) у повноекранному режимі Wine/Proton.",
        "description_zh": "启用或禁用 Wine/Proton 全屏模式下的 FSR（FidelityFX Super Resolution）升频。",
        "description_hi": "Wine/Proton में फुलस्क्रीन मोड के लिए FSR (FidelityFX Super Resolution) अपस्केलिंग को सक्षम या अक्षम करता है।",
        "description_es": "Activa o desactiva el escalado FSR (FidelityFX Super Resolution) en modo pantalla completa en Wine/Proton.",
        "description_pt": "Ativa ou desativa o upscaling FSR (FidelityFX Super Resolution) no modo tela cheia no Wine/Proton."
    },

    {
        "name": "WINE_VK_FULLSCREEN_METHOD",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Définit la méthode utilisée par Wine pour gérer le plein écran Vulkan (ex: desktop, exclusive, auto).",
        "description_en": "Defines how Wine handles Vulkan fullscreen mode (e.g., desktop, exclusive, auto).",
        "description_de": "Legt fest, wie Wine den Vulkan-Vollbildmodus behandelt (z. B. Desktop, exklusiv oder automatisch).",
        "description_uk": "Визначає метод, який Wine використовує для керування повноекранним режимом Vulkan (наприклад: desktop, exclusive, auto).",
        "description_zh": "定义 Wine 处理 Vulkan 全屏模式的方法（例如：desktop、exclusive、auto）。",
        "description_hi": "निर्धारित करता है कि Wine Vulkan फुलस्क्रीन मोड को कैसे संभालता है (जैसे: desktop, exclusive, auto)।",
        "description_es": "Define cómo Wine gestiona el modo de pantalla completa Vulkan (por ejemplo: desktop, exclusive, auto).",
        "description_pt": "Define como o Wine gerencia o modo tela cheia Vulkan (ex.: desktop, exclusive, auto)."
    }
]
SDL_ENV_VARS = [
    # =========================================================
    # SDL
    # =========================================================

    {
        "name": "SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR",
        "type": "sdl",
        "category": "graphics",
        "description_fr": "Contrôle si SDL demande au compositeur X11 de contourner la composition (bypass). Peut réduire la latence ou les problèmes d'affichage, mais peut causer des soucis de focus ou de capture de souris sur certains gestionnaires de fenêtres.",
        "description_en": "Controls whether SDL requests the X11 compositor bypass. Can reduce latency and rendering issues, but may cause focus or mouse capture problems on some window managers.",
        "description_de": "Legt fest, ob SDL den X11-Compositor umgehen soll. Kann die Latenz verringern und Darstellungsprobleme reduzieren, kann jedoch auf einigen Fenstermanagern Fokus- oder Mausaufnahmeprobleme verursachen.",
        "description_uk": "Керує тим, чи SDL запитує обхід композитора X11. Може зменшити затримку та проблеми відображення, але на деяких віконних менеджерах може спричинити проблеми з фокусом або захопленням миші.",
        "description_zh": "控制 SDL 是否请求绕过 X11 合成器。可以降低延迟并减少显示问题，但在某些窗口管理器上可能导致焦点或鼠标捕获问题。",
        "description_hi": "यह नियंत्रित करता है कि SDL X11 कंपोज़िटर को बायपास करने का अनुरोध करता है या नहीं। यह विलंबता और रेंडरिंग समस्याओं को कम कर सकता है, लेकिन कुछ विंडो मैनेजर में फोकस या माउस कैप्चर समस्याएँ पैदा कर सकता है।",
        "description_es": "Controla si SDL solicita evitar el compositor X11. Puede reducir la latencia y problemas de renderizado, pero puede causar problemas de enfoque o captura del ratón en algunos gestores de ventanas.",
        "description_pt": "Controla se o SDL solicita ignorar o compositor X11. Pode reduzir a latência e problemas de renderização, mas pode causar problemas de foco ou captura do mouse em alguns gerenciadores de janelas."
    },

    {
        "name": "SDL_MOUSE_AUTO_CAPTURE",
        "type": "sdl",
        "category": "input",
        "description_fr": "Active la capture automatique de la souris lorsque la fenêtre devient active. Améliore le comportement des jeux en plein écran ou en mode FPS, en évitant la perte de contrôle de la souris.",
        "description_en": "Enables automatic mouse capture when the window becomes active. Improves mouse behavior in fullscreen or FPS-style games by preventing loss of mouse control.",
        "description_de": "Aktiviert die automatische Mausaufnahme, sobald das Fenster aktiv wird. Verbessert das Mausverhalten in Vollbild- oder Ego-Shooter-Spielen und verhindert den Verlust der Maussteuerung.",
        "description_uk": "Вмикає автоматичне захоплення миші, коли вікно стає активним. Покращує керування мишею у повноекранних іграх або FPS, запобігаючи втраті контролю.",
        "description_zh": "启用窗口激活时自动捕获鼠标。在全屏或 FPS 类游戏中改善鼠标行为，避免鼠标控制丢失。",
        "description_hi": "विंडो सक्रिय होने पर स्वचालित माउस कैप्चर सक्षम करता है। फुलस्क्रीन या FPS गेम में माउस नियंत्रण खोने से बचाकर व्यवहार सुधारता है।",
        "description_es": "Activa la captura automática del ratón cuando la ventana se activa. Mejora el comportamiento del ratón en juegos a pantalla completa o tipo FPS evitando perder el control.",
        "description_pt": "Ativa a captura automática do mouse quando a janela fica ativa. Melhora o comportamento do mouse em jogos de tela cheia ou estilo FPS, evitando perda de controle."
    },

    {
        "name": "SDL_MOUSE_RELATIVE_MODE_WARP",
        "type": "sdl",
        "category": "input",
        "description_fr": "Active le mode de souris relative avec recentering (warp). Utilisé par certains jeux anciens pour simuler un mouvement continu de la souris. Peut améliorer la compatibilité avec les jeux DirectDraw ou moteurs anciens.",
        "description_en": "Enables relative mouse mode using pointer warping. Used by some older games to simulate continuous mouse movement. Can improve compatibility with DirectDraw or legacy engines.",
        "description_de": "Aktiviert den relativen Mausmodus mit Pointer-Warping. Wird von einigen älteren Spielen verwendet, um kontinuierliche Mausbewegungen zu simulieren. Kann die Kompatibilität mit DirectDraw-Spielen oder älteren Spiel-Engines verbessern.",
        "description_uk": "Вмикає відносний режим миші з переміщенням курсора до центру. Використовується деякими старими іграми для імітації безперервного руху миші. Може покращити сумісність із DirectDraw та старими рушіями.",
        "description_zh": "启用带指针重定位的相对鼠标模式。一些旧游戏使用此功能模拟连续鼠标移动，可提高 DirectDraw 或旧版引擎的兼容性。",
        "description_hi": "कर्सर को पुनः केंद्रित करने वाले रिलेटिव माउस मोड को सक्षम करता है। कुछ पुराने गेम लगातार माउस मूवमेंट के लिए इसका उपयोग करते हैं। DirectDraw या पुराने इंजन की संगतता सुधार सकता है।",
        "description_es": "Activa el modo de ratón relativo mediante reposicionamiento del puntero. Algunos juegos antiguos lo usan para simular movimiento continuo del ratón. Puede mejorar la compatibilidad con DirectDraw o motores antiguos.",
        "description_pt": "Ativa o modo de mouse relativo usando reposicionamento do ponteiro. Alguns jogos antigos usam isso para simular movimento contínuo do mouse. Pode melhorar a compatibilidade com DirectDraw ou engines antigos."
    },

    {
        "name": "SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR",
        "type": "sdl",
        "category": "graphics",
        "description_fr": "Demande au gestionnaire de fenêtres X11 de contourner le compositeur pour la fenêtre SDL. Peut réduire la latence et améliorer la réactivité, mais peut aussi causer des problèmes de focus ou de capture de souris selon le gestionnaire de fenêtres.",
        "description_en": "Requests the X11 window manager to bypass the compositor for the SDL window. Can reduce latency and improve responsiveness, but may cause focus or mouse capture issues depending on the window manager.",
        "description_de": "Fordert den X11-Fenstermanager auf, den Compositor für das SDL-Fenster zu umgehen. Kann die Latenz verringern und die Reaktionsfähigkeit verbessern, je nach Fenstermanager jedoch Fokus- oder Mausaufnahmeprobleme verursachen.",
        "description_uk": "Просить менеджер вікон X11 обійти композитор для SDL-вікна. Може зменшити затримку та покращити швидкість реакції, але залежно від менеджера можуть виникати проблеми з фокусом або мишею.",
        "description_zh": "请求 X11 窗口管理器为 SDL 窗口绕过合成器。可以降低延迟并提高响应速度，但根据窗口管理器不同可能导致焦点或鼠标捕获问题。",
        "description_hi": "SDL विंडो के लिए X11 विंडो मैनेजर को कंपोज़िटर बायपास करने का अनुरोध करता है। यह विलंबता कम कर सकता है लेकिन कुछ मैनेजर में फोकस या माउस कैप्चर समस्याएँ उत्पन्न कर सकता है।",
        "description_es": "Solicita al gestor de ventanas X11 evitar el compositor para la ventana SDL. Puede reducir la latencia y mejorar la respuesta, pero puede causar problemas de enfoque o captura del ratón.",
        "description_pt": "Solicita ao gerenciador de janelas X11 ignorar o compositor para a janela SDL. Pode reduzir a latência e melhorar a resposta, mas pode causar problemas de foco ou captura do mouse."
    },

    {
        "name": "SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS",
        "type": "sdl",
        "category": "window",
        "description_fr": "Détermine si la fenêtre doit être minimisée lors d'une perte de focus. Utile pour éviter certains comportements de plein écran instable dans les anciens jeux.",
        "description_en": "Determines whether the window should be minimized when it loses focus. Useful to avoid unstable fullscreen behavior in older games.",
        "description_de": "Legt fest, ob das Fenster beim Verlust des Fokus minimiert werden soll. Nützlich, um instabiles Vollbildverhalten in älteren Spielen zu vermeiden.",
        "description_uk": "Визначає, чи потрібно згортати вікно при втраті фокуса. Корисно для уникнення нестабільної роботи повноекранного режиму у старих іграх.",
        "description_zh": "确定窗口失去焦点时是否应最小化。用于避免旧游戏中的不稳定全屏行为。",
        "description_hi": "निर्धारित करता है कि फोकस खोने पर विंडो को छोटा किया जाए या नहीं। पुराने गेम में अस्थिर फुलस्क्रीन व्यवहार को रोकने में उपयोगी है।",
        "description_es": "Determina si la ventana debe minimizarse al perder el enfoque. Útil para evitar comportamientos inestables de pantalla completa en juegos antiguos.",
        "description_pt": "Define se a janela deve ser minimizada quando perde o foco. Útil para evitar comportamentos instáveis de tela cheia em jogos antigos."
    },

    {
        "name": "SDL_HINT_GRAB_KEYBOARD",
        "type": "sdl",
        "category": "input",
        "description_fr": "Force SDL à capturer le clavier lorsque la fenêtre est active. Empêche les touches de sortir du contexte du jeu, améliorant l'immersion et la compatibilité des anciens moteurs.",
        "description_en": "Forces SDL to grab the keyboard when the window is active. Prevents key input from leaving the game context, improving immersion and compatibility with legacy engines.",
        "description_de": "Erzwingt, dass SDL die Tastatur erfasst, solange das Fenster aktiv ist. Verhindert, dass Tasteneingaben den Spielkontext verlassen, und verbessert die Immersion sowie die Kompatibilität mit älteren Spiel-Engines.",
        "description_uk": "Примусово захоплює клавіатуру SDL, коли вікно активне. Запобігає виходу натискань клавіш за межі гри та покращує сумісність зі старими рушіями.",
        "description_zh": "强制 SDL 在窗口活动时捕获键盘。防止按键输入离开游戏环境，提高沉浸感并改善旧引擎兼容性。",
        "description_hi": "जब विंडो सक्रिय हो तो SDL को कीबोर्ड कैप्चर करने के लिए मजबूर करता है। इनपुट को गेम संदर्भ से बाहर जाने से रोकता है और पुराने इंजन की संगतता सुधारता है।",
        "description_es": "Fuerza a SDL a capturar el teclado cuando la ventana está activa. Evita que las teclas salgan del contexto del juego, mejorando la inmersión y compatibilidad con motores antiguos.",
        "description_pt": "Força o SDL a capturar o teclado quando a janela está ativa. Impede que entradas de teclado saiam do contexto do jogo, melhorando a imersão e a compatibilidade com engines antigas."
    }
]
VULKAN_ENV_VARS = [
    # =========================================================
    # VULKAN
    # =========================================================
    {
        "name": "AMD_VULKAN_ICD",
        "type": "vulkan",
        "category": "driver",
        "description_fr": "Choisit l’ICD Vulkan AMD (RADV ou AMDVLK) utilisé par les applications.",
        "description_en": "Selects the AMD Vulkan ICD (RADV or AMDVLK) used by applications.",
        "description_de": "Wählt die von Anwendungen verwendete AMD-Vulkan-ICD (RADV oder AMDVLK) aus.",
        "description_uk": "Вибирає AMD Vulkan ICD (RADV або AMDVLK), який використовується програмами.",
        "description_zh": "选择应用程序使用的 AMD Vulkan ICD（RADV 或 AMDVLK）。",
        "description_hi": "एप्लिकेशन द्वारा उपयोग किए जाने वाले AMD Vulkan ICD (RADV या AMDVLK) का चयन करता है।",
        "description_es": "Selecciona el ICD Vulkan de AMD (RADV o AMDVLK) utilizado por las aplicaciones.",
        "description_pt": "Seleciona o ICD Vulkan AMD (RADV ou AMDVLK) usado pelos aplicativos."
    },
    {
        "name": "VK_ICD_FILENAMES",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "ICD Vulkan forcé.",
        "description_en": "Forces Vulkan ICD.",
        "description_de": "Erzwingt einen bestimmten Vulkan-ICD.",
        "description_uk": "Примусово вибирає Vulkan ICD.",
        "description_zh": "强制指定 Vulkan ICD。",
        "description_hi": "एक विशिष्ट Vulkan ICD को मजबूर करता है।",
        "description_es": "Fuerza un ICD de Vulkan específico.",
        "description_pt": "Força um ICD Vulkan específico."
    },
    {
        "name": "VK_LAYER_PATH",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "Chemin layers Vulkan.",
        "description_en": "Vulkan layers path.",
        "description_de": "Pfad zu den Vulkan-Layern.",
        "description_uk": "Шлях до шарів Vulkan.",
        "description_zh": "Vulkan 层路径。",
        "description_hi": "Vulkan लेयर्स का पथ।",
        "description_es": "Ruta de las capas de Vulkan.",
        "description_pt": "Caminho das camadas Vulkan."
    },
    {
        "name": "VK_INSTANCE_LAYERS",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "Layers Vulkan.",
        "description_en": "Vulkan instance layers.",
        "description_de": "Vulkan-Instanz-Layer.",
        "description_uk": "Шари екземпляра Vulkan.",
        "description_zh": "Vulkan 实例层。",
        "description_hi": "Vulkan इंस्टेंस लेयर्स।",
        "description_es": "Capas de instancia de Vulkan.",
        "description_pt": "Camadas de instância Vulkan."
    },
    {
        "name": "VK_LOADER_DEBUG",
        "type": "vulkan",
        "category": "debug",
        "description_fr": "Debug loader Vulkan.",
        "description_en": "Vulkan loader debug.",
        "description_de": "Debugausgabe des Vulkan-Loaders.",
        "description_uk": "Налагодження завантажувача Vulkan.",
        "description_zh": "Vulkan 加载器调试。",
        "description_hi": "Vulkan लोडर डिबग मोड।",
        "description_es": "Depuración del cargador de Vulkan.",
        "description_pt": "Depuração do carregador Vulkan."
    }
]
MESA_ENV_VARS = [
    # =========================================================
    # MESA / AMD
    # =========================================================
    {
        "name": "MESA_VK_DEVICE_SELECT",
        "type": "mesa",
        "category": "graphics",
        "description_fr": "Sélection GPU Mesa.",
        "description_en": "Select Vulkan GPU.",
        "description_de": "Wählt die Vulkan-GPU unter Mesa aus.",
        "description_uk": "Вибір Vulkan-GPU через Mesa.",
        "description_zh": "选择 Mesa 下的 Vulkan GPU。",
        "description_hi": "Mesa के अंतर्गत Vulkan GPU का चयन करता है।",
        "description_es": "Selecciona la GPU Vulkan en Mesa.",
        "description_pt": "Seleciona a GPU Vulkan no Mesa."
    },
    {
        "name": "MESA_SHADER_CACHE_MAX_SIZE",
        "type": "mesa",
        "category": "performance",
        "description_fr": "Définit la taille maximale du cache disque des shaders Mesa afin de conserver davantage de shaders compilés et réduire les recompilations lors du lancement des jeux.",
        "description_en": "Sets the maximum Mesa shader disk cache size to keep more compiled shaders and reduce shader recompilation when launching games.",
        "description_de": "Legt die maximale Größe des Mesa-Shader-Disk-Caches fest, um mehr kompilierte Shader zu speichern und Neukompilierungen beim Starten von Spielen zu reduzieren.",
        "description_uk": "Визначає максимальний розмір дискового кешу шейдерів Mesa, щоб зберігати більше скомпільованих шейдерів і зменшити повторну компіляцію під час запуску ігор.",
        "description_zh": "设置 Mesa 着色器磁盘缓存的最大大小，以保存更多已编译着色器，并减少游戏启动时的着色器重新编译。",
        "description_hi": "Mesa शेडर डिस्क कैश का अधिकतम आकार निर्धारित करता है, ताकि अधिक संकलित शेडर सुरक्षित रहें और गेम शुरू करते समय पुनः संकलन कम हो।",
        "description_es": "Establece el tamaño máximo de la caché de disco de sombreadores de Mesa para conservar más sombreadores compilados y reducir la recompilación al iniciar juegos.",
        "description_pt": "Define o tamanho máximo do cache em disco de shaders do Mesa para manter mais shaders compilados e reduzir a recompilação ao iniciar jogos."
    },
    {
        "name": "RADV_PERFTEST",
        "type": "mesa",
        "category": "performance",
        "description_fr": "Optimisations RADV.",
        "description_en": "RADV experimental features.",
        "description_de": "Aktiviert experimentelle RADV-Funktionen.",
        "description_uk": "Експериментальні функції та оптимізації RADV.",
        "description_zh": "启用 RADV 实验性功能。",
        "description_hi": "RADV की प्रयोगात्मक सुविधाएँ सक्षम करता है।",
        "description_es": "Activa funciones experimentales de RADV.",
        "description_pt": "Ativa recursos experimentais do RADV."
    },
    {
        "name": "RADV_DEBUG",
        "type": "mesa",
        "category": "debug",
        "description_fr": "Debug RADV.",
        "description_en": "RADV debug mode.",
        "description_de": "RADV-Debugmodus.",
        "description_uk": "Режим налагодження RADV.",
        "description_zh": "RADV 调试模式。",
        "description_hi": "RADV डिबग मोड।",
        "description_es": "Modo de depuración de RADV.",
        "description_pt": "Modo de depuração do RADV."
    },
    {
        "name": "mesa_glthread",
        "type": "mesa",
        "category": "performance",
        "description_fr": "Multithread OpenGL.",
        "description_en": "OpenGL threading.",
        "description_de": "Aktiviert OpenGL-Multithreading.",
        "description_uk": "Багатопотокова обробка OpenGL.",
        "description_zh": "OpenGL 多线程处理。",
        "description_hi": "OpenGL थ्रेडिंग।",
        "description_es": "Procesamiento multihilo de OpenGL.",
        "description_pt": "Processamento multithread do OpenGL."
    },
    {
        "name": "MESA_GL_VERSION_OVERRIDE",
        "type": "opengl",
        "category": "graphics",
        "description_fr": "Force la version d'OpenGL exposée par le pilote Mesa aux applications.",
        "description_en": "Forces the OpenGL version reported by the Mesa driver to applications.",
        "description_de": "Erzwingt die vom Mesa-Treiber gemeldete OpenGL-Version für Anwendungen.",
        "description_uk": "Примусово задає версію OpenGL, яку драйвер Mesa повідомляє програмам.",
        "description_zh": "强制 Mesa 驱动向应用程序报告指定的 OpenGL 版本。",
        "description_hi": "अनुप्रयोगों के लिए Mesa ड्राइवर द्वारा रिपोर्ट किए गए OpenGL संस्करण को बाध्य करता है।",
        "description_es": "Fuerza la versión de OpenGL que el controlador Mesa informa a las aplicaciones.",
        "description_pt": "Força a versão do OpenGL informada pelo driver Mesa aos aplicativos."
    },
    {
        "name": "MESA_GLSL_VERSION_OVERRIDE",
        "type": "opengl",
        "category": "graphics",
        "description_fr": "Force la version du langage de shaders GLSL utilisée par Mesa pour la compilation des shaders.",
        "description_en": "Forces the GLSL shader language version used by Mesa for shader compilation.",
        "description_de": "Erzwingt die von Mesa für die Shader-Kompilierung verwendete GLSL-Version.",
        "description_uk": "Примусово задає версію мови шейдерів GLSL, яку Mesa використовує для компіляції шейдерів.",
        "description_zh": "强制 Mesa 在着色器编译时使用指定的 GLSL 着色语言版本。",
        "description_hi": "Mesa द्वारा शेडर संकलन के लिए उपयोग किए जाने वाले GLSL संस्करण को बाध्य करता है।",
        "description_es": "Fuerza la versión del lenguaje de sombreadores GLSL utilizada por Mesa para compilar sombreadores.",
        "description_pt": "Força a versão da linguagem de shaders GLSL usada pelo Mesa para compilação de shaders."
    }
]
NVIDIA_ENV_VARS = [
    # =========================================================
    # NVIDIA
    # =========================================================
    {
        "name": "__GL_SHADER_DISK_CACHE",
        "type": "nvidia",
        "category": "performance",
        "description_fr": "Active le cache disque des shaders NVIDIA afin de conserver les shaders compilés et réduire les temps de compilation ainsi que les saccades en jeu.",
        "description_en": "Enables the NVIDIA shader disk cache to store compiled shaders and reduce compilation times and stuttering during gameplay.",
        "description_de": "Aktiviert den NVIDIA-Shader-Disk-Cache, um kompilierte Shader zu speichern und Kompilierungszeiten sowie Ruckler im Spiel zu reduzieren.",
        "description_uk": "Вмикає дисковий кеш шейдерів NVIDIA для збереження скомпільованих шейдерів і зменшення часу компіляції та підлагувань у грі.",
        "description_zh": "启用 NVIDIA 着色器磁盘缓存，以保存已编译着色器并减少编译时间和游戏卡顿。",
        "description_hi": "NVIDIA शेडर डिस्क कैश को सक्षम करता है ताकि संकलित शेडर सुरक्षित रहें और संकलन समय व गेम में रुकावट कम हो।",
        "description_es": "Activa la caché de disco de sombreadores de NVIDIA para conservar sombreadores compilados y reducir los tiempos de compilación y los tirones durante el juego.",
        "description_pt": "Ativa o cache em disco de shaders da NVIDIA para manter shaders compilados e reduzir o tempo de compilação e travamentos durante o jogo."
    },
    {
        "name": "__GL_SHADER_DISK_CACHE_PATH",
        "type": "nvidia",
        "category": "configuration",
        "description_fr": "Chemin cache NVIDIA.",
        "description_en": "NVIDIA cache path.",
        "description_de": "Pfad zum NVIDIA-Cache.",
        "description_uk": "Шлях до кешу NVIDIA.",
        "description_zh": "NVIDIA 缓存路径。",
        "description_hi": "NVIDIA कैश पथ।",
        "description_es": "Ruta de la caché de NVIDIA.",
        "description_pt": "Caminho do cache da NVIDIA."
    },
    {
        "name": "__GL_SHADER_DISK_CACHE_SKIP_CLEANUP",
        "type": "nvidia",
        "category": "performance",
        "description_fr": "Empêche le nettoyage automatique du cache disque des shaders NVIDIA afin de conserver les données compilées plus longtemps.",
        "description_en": "Prevents automatic cleanup of the NVIDIA shader disk cache, keeping compiled shader data available for longer.",
        "description_de": "Verhindert die automatische Bereinigung des NVIDIA-Shader-Disk-Caches, damit kompilierte Shader-Daten länger erhalten bleiben.",
        "description_uk": "Запобігає автоматичному очищенню дискового кешу шейдерів NVIDIA, зберігаючи скомпільовані дані шейдерів довше.",
        "description_zh": "阻止自动清理 NVIDIA 着色器磁盘缓存，使已编译的着色器数据保留更长时间。",
        "description_hi": "NVIDIA शेडर डिस्क कैश की स्वचालित सफाई को रोकता है, जिससे संकलित शेडर डेटा अधिक समय तक सुरक्षित रहता है।",
        "description_es": "Evita la limpieza automática de la caché de disco de sombreadores de NVIDIA, conservando los datos compilados durante más tiempo.",
        "description_pt": "Impede a limpeza automática do cache em disco de shaders da NVIDIA, mantendo os dados compilados por mais tempo."
    },
    {
        "name": "__GL_SYNC_TO_VBLANK",
        "type": "nvidia",
        "category": "graphics",
        "description_fr": "VSync NVIDIA.",
        "description_en": "Vertical sync.",
        "description_de": "Vertikale Synchronisation (VSync).",
        "description_uk": "Вертикальна синхронізація (VSync).",
        "description_zh": "垂直同步（VSync）。",
        "description_hi": "वर्टिकल सिंक (VSync)।",
        "description_es": "Sincronización vertical (VSync).",
        "description_pt": "Sincronização vertical (VSync)."
    },
    {
        "name": "__GL_THREADED_OPTIMIZATIONS",
        "type": "nvidia",
        "category": "performance",
        "description_fr": "Threading NVIDIA.",
        "description_en": "Threaded optimizations.",
        "description_de": "Aktiviert Thread-Optimierungen.",
        "description_uk": "Багатопотокові оптимізації NVIDIA.",
        "description_zh": "启用 NVIDIA 线程优化。",
        "description_hi": "NVIDIA थ्रेडेड ऑप्टिमाइज़ेशन सक्षम करता है।",
        "description_es": "Optimizaciones mediante subprocesos de NVIDIA.",
        "description_pt": "Otimizações de processamento em threads da NVIDIA."
    }
]
SYSTEM_ENV_VARS = [

    # =========================================================
    # SYSTEM LINUX
    # =========================================================
    {
        "name": "LD_LIBRARY_PATH",
        "type": "system",
        "category": "linux",
        "description_fr": "Librairies Linux.",
        "description_en": "Linux library path.",
        "description_de": "Pfad zu Linux-Bibliotheken.",
        "description_uk": "Шлях до бібліотек Linux.",
        "description_zh": "Linux 库路径。",
        "description_hi": "Linux लाइब्रेरी पथ।",
        "description_es": "Ruta de bibliotecas de Linux.",
        "description_pt": "Caminho das bibliotecas Linux."
    },
    {
        "name": "LD_PRELOAD",
        "type": "system",
        "category": "linux",
        "description_fr": "Charge des bibliothèques partagées avant celles utilisées normalement par l’application.",
        "description_en": "Loads shared libraries before those normally used by the application.",
        "description_de": "Lädt gemeinsam genutzte Bibliotheken vor den normalerweise von der Anwendung verwendeten Bibliotheken.",
        "description_uk": "Завантажує спільні бібліотеки перед тими, які зазвичай використовує програма.",
        "description_zh": "在应用程序通常使用的库之前加载共享库。",
        "description_hi": "ऐप्लिकेशन द्वारा सामान्य रूप से उपयोग की जाने वाली लाइब्रेरी से पहले साझा लाइब्रेरी लोड करता है।",
        "description_es": "Carga bibliotecas compartidas antes de las que normalmente utiliza la aplicación.",
        "description_pt": "Carrega bibliotecas partilhadas antes das normalmente utilizadas pela aplicação."
    },
    {
        "name": "MALLOC_ARENA_MAX",
        "type": "system",
        "category": "performance",
        "description_fr": "Optimisation mémoire.",
        "description_en": "Memory allocator tuning.",
        "description_de": "Optimiert den Speicher-Allocator.",
        "description_uk": "Налаштування розподілу пам’яті.",
        "description_zh": "内存分配器优化。",
        "description_hi": "मेमोरी एलोकेटर ट्यूनिंग।",
        "description_es": "Ajuste del asignador de memoria.",
        "description_pt": "Ajuste do alocador de memória."
    },
    {
        "name": "GAMEMODERUN",
        "type": "system",
        "category": "performance",
        "description_fr": "Lance le jeu via GameMode afin d'appliquer automatiquement des optimisations système dédiées au jeu.",
        "description_en": "Launches the game through GameMode to automatically apply gaming-oriented system optimizations.",
        "description_de": "Startet das Spiel über GameMode, um automatisch auf Spiele abgestimmte Systemoptimierungen anzuwenden.",
        "description_uk": "Запускає гру через GameMode для автоматичного застосування системних оптимізацій, призначених для ігор.",
        "description_zh": "通过 GameMode 启动游戏，以自动应用针对游戏优化的系统设置。",
        "description_hi": "गेम के लिए अनुकूलित सिस्टम सुधारों को स्वचालित रूप से लागू करने के लिए GameMode के माध्यम से गेम लॉन्च करता है।",
        "description_es": "Inicia el juego mediante GameMode para aplicar automáticamente optimizaciones del sistema orientadas a juegos.",
        "description_pt": "Inicia o jogo através do GameMode para aplicar automaticamente otimizações do sistema voltadas para jogos."
    }
]
STEAM_ENV_VARS = [
    # =========================================================
    # STEAM
    # =========================================================
    {
        "name": "STEAM_COMPAT_APP_ID",
        "type": "steam",
        "category": "internal",
        "description_fr": "Définit l’identifiant de l’application Steam utilisée pour la compatibilité.",
        "description_en": "Sets the Steam app ID used for compatibility.",
        "description_de": "Legt die Steam-App-ID für die Kompatibilität fest.",
        "description_uk": "Визначає ідентифікатор програми Steam, який використовується для сумісності.",
        "description_zh": "设置用于兼容性的 Steam 应用程序 ID。",
        "description_hi": "संगतता के लिए उपयोग की जाने वाली Steam ऐप ID निर्धारित करता है।",
        "description_es": "Establece el ID de la aplicación de Steam utilizado para la compatibilidad.",
        "description_pt": "Define o ID da aplicação Steam utilizado para a compatibilidade."
    },
    {
        "name": "STEAM_COMPAT_CLIENT_INSTALL_PATH",
        "type": "steam",
        "category": "internal",
        "description_fr": "Indique le chemin d'installation du client Steam utilisé par Proton afin de localiser les fichiers, bibliothèques et composants nécessaires à l'exécution des jeux Windows.",
        "description_en": "Specifies the installation path of the Steam client used by Proton to locate the files, libraries, and components required to run Windows games.",
        "description_de": "Gibt den Installationspfad des von Proton verwendeten Steam-Clients an.",
        "description_uk": "Визначає шлях встановлення клієнта Steam, який Proton використовує для пошуку файлів, бібліотек і компонентів, необхідних для запуску ігор Windows.",
        "description_zh": "指定 Proton 使用的 Steam 客户端安装路径，以定位运行 Windows 游戏所需的文件、库和组件。",
        "description_hi": "Proton द्वारा उपयोग किए जाने वाले Steam क्लाइंट के इंस्टॉलेशन पथ को निर्दिष्ट करता है, ताकि Windows गेम चलाने के लिए आवश्यक फ़ाइलें, लाइब्रेरी और घटक खोजे जा सकें।",
        "description_es": "Especifica la ruta de instalación del cliente de Steam utilizada por Proton para localizar los archivos, bibliotecas y componentes necesarios para ejecutar juegos de Windows.",
        "description_pt": "Especifica o caminho de instalação do cliente Steam usado pelo Proton para localizar os arquivos, bibliotecas e componentes necessários para executar jogos do Windows."
    },
    {
        "name": "STEAM_COMPAT_MOUNTS",
        "type": "steam",
        "category": "internal",
        "description_fr": "Définit des répertoires supplémentaires à monter dans l'environnement de compatibilité Steam/Proton afin de rendre des fichiers ou bibliothèques accessibles au jeu.",
        "description_en": "Specifies additional directories to mount inside the Steam/Proton compatibility environment, making files or libraries accessible to the game.",
        "description_de": "Legt zusätzliche Verzeichnisse fest, die in die Steam-/Proton-Kompatibilitätsumgebung eingebunden werden, damit Dateien oder Bibliotheken für das Spiel verfügbar sind.",
        "description_uk": "Визначає додаткові каталоги, які слід змонтувати в середовищі сумісності Steam/Proton, щоб зробити файли або бібліотеки доступними для гри.",
        "description_zh": "指定要挂载到 Steam/Proton 兼容环境中的其他目录，使游戏能够访问这些文件或库。",
        "description_hi": "Steam/Proton संगतता वातावरण में माउंट किए जाने वाले अतिरिक्त निर्देशिकाओं को निर्दिष्ट करता है, ताकि गेम उन फ़ाइलों या लाइब्रेरी तक पहुँच सके।",
        "description_es": "Especifica directorios adicionales que se montarán dentro del entorno de compatibilidad de Steam/Proton para que el juego pueda acceder a archivos o bibliotecas.",
        "description_pt": "Especifica diretórios adicionais a serem montados no ambiente de compatibilidade do Steam/Proton, tornando arquivos ou bibliotecas acessíveis ao jogo."
    },
    {
        "name": "STEAM_COMPAT_DATA_PATH",
        "type": "steam",
        "category": "internal",
        "description_fr": "Définit le chemin du préfixe de compatibilité Steam/Proton contenant l'environnement Wine utilisé par le jeu (configuration, registre, DLL et fichiers système virtuels).",
        "description_en": "Defines the Steam/Proton compatibility prefix path containing the Wine environment used by the game (configuration, registry, DLLs and virtual system files).",
        "description_de": "Legt den Pfad zum Steam/Proton-Kompatibilitätspräfix fest, das die vom Spiel verwendete Wine-Umgebung enthält (Konfiguration, Registry, DLLs und virtuelle Systemdateien).",
        "description_uk": "Визначає шлях до префікса сумісності Steam/Proton, який містить середовище Wine, що використовується грою (налаштування, реєстр, DLL та віртуальні системні файли).",
        "description_zh": "定义 Steam/Proton 兼容性前缀路径，其中包含游戏使用的 Wine 环境（配置、注册表、DLL 和虚拟系统文件）。",
        "description_hi": "Steam/Proton संगतता प्रीफ़िक्स पथ को परिभाषित करता है जिसमें गेम द्वारा उपयोग किया जाने वाला Wine वातावरण (कॉन्फ़िगरेशन, रजिस्ट्री, DLL और वर्चुअल सिस्टम फ़ाइलें) शामिल होता है।",
        "description_es": "Define la ruta del prefijo de compatibilidad de Steam/Proton que contiene el entorno Wine utilizado por el juego (configuración, registro, DLL ...).",
        "description_pt": "Define o caminho do prefixo de compatibilidade Steam/Proton que contém o ambiente Wine usado pelo jogo (configurações, registro, DLLs e arquivos de sistema virtuais)."
    },
    {
        "name": "STEAM_COMPAT_TOOL_PATHS",
        "type": "steam",
        "category": "internal",
        "description_fr": "Définit le chemin vers les outils de compatibilité Steam/Proton utilisés par le jeu (runtime Proton, composants Wine, DXVK, VKD3D et autres bibliothèques nécessaires).",
        "description_en": "Defines the path to the Steam/Proton compatibility tools used by the game (Proton runtime, Wine components, DXVK, VKD3D and other required libraries).",
        "description_de": "Legt den Pfad zu den von Steam/Proton verwendeten Kompatibilitätswerkzeugen fest (Proton-Runtime, Wine-Komponenten, DXVK, VKD3D und weitere benötigte Bibliotheken).",
        "description_uk": "Визначає шлях до інструментів сумісності Steam/Proton, які використовуються грою (середовище Proton, компоненти Wine, DXVK, VKD3D та інші необхідні бібліотеки).",
        "description_zh": "定义游戏使用的 Steam/Proton 兼容工具路径（Proton 运行环境、Wine 组件、DXVK、VKD3D 以及其他必要库）。",
        "description_hi": "गेम द्वारा उपयोग किए जाने वाले Steam/Proton संगतता टूल्स का पथ निर्धारित करता है (Proton रनटाइम, Wine घटक, DXVK, VKD3D और अन्य आवश्यक लाइब्रेरी)।",
        "description_es": "Define la ruta de las herramientas de compatibilidad Steam/Proton utilizadas por el juego (runtime de Proton, componentes de Wine, DXVK, VKD3D y otras bibliotecas necesarias).",
        "description_pt": "Define o caminho das ferramentas de compatibilidade Steam/Proton usadas pelo jogo (runtime do Proton, componentes Wine, DXVK, VKD3D e outras bibliotecas necessárias)."
    },
    {
        "name": "STEAM_COMPAT_SHADER_PATH",
        "type": "steam",
        "category": "performance",
        "description_fr": "Définit le chemin du cache des shaders Steam.",
        "description_en": "Sets the path to the Steam shader cache.",
        "description_de": "Legt den Pfad zum Steam-Shader-Cache fest.",
        "description_uk": "Визначає шлях до кешу шейдерів Steam.",
        "description_zh": "设置 Steam 着色器缓存的路径。",
        "description_hi": "Steam शेडर कैश का पथ निर्धारित करता है।",
        "description_es": "Establece la ruta de la caché de sombreadores de Steam.",
        "description_pt": "Define o caminho para o cache de shaders do Steam."
    }
]
HUD_ENV_VARS = [
    # =========================================================
    # HUD / OVERLAY
    # =========================================================
    {
        "name": "MANGOHUD",
        "type": "hud",
        "category": "overlay",
        "description_fr": "Overlay MangoHud.",
        "description_en": "MangoHud overlay.",
        "description_de": "MangoHud-Overlay.",
        "description_uk": "Оверлей MangoHud.",
        "description_zh": "MangoHud 覆盖层。",
        "description_hi": "MangoHud ओवरले।",
        "description_es": "Superposición de MangoHud.",
        "description_pt": "Sobreposição do MangoHud."
    },
    {
        "name": "MANGOHUD_DLSYM",
        "type": "hud",
        "category": "compatibility",
        "description_fr": "Active le mode d'injection dynamique MangoHud via dlsym pour améliorer la détection des applications utilisant des bibliothèques graphiques chargées dynamiquement.",
        "description_en": "Enables MangoHud dynamic dlsym injection mode to improve detection of applications using dynamically loaded graphics libraries.",
        "description_de": "Aktiviert den dynamischen dlsym-Injektionsmodus von MangoHud, um Anwendungen mit dynamisch geladenen Grafikbibliotheken besser zu erkennen.",
        "description_uk": "Увімкнює режим динамічної ін'єкції dlsym у MangoHud для кращого виявлення програм, які використовують динамічно завантажувані графічні бібліотеки.",
        "description_zh": "启用 MangoHud 的 dlsym 动态注入模式，以改进对使用动态加载图形库应用程序的检测。",
        "description_hi": "गतिशील रूप से लोड की गई ग्राफ़िक्स लाइब्रेरी का उपयोग करने वाले अनुप्रयोगों की बेहतर पहचान के लिए MangoHud का dlsym डायनामिक इंजेक्शन मोड सक्षम करता है।",
        "description_es": "Activa el modo de inyección dinámica mediante dlsym de MangoHud para mejorar la detección de aplicaciones que utilizan bibliotecas gráficas cargadas dinámicamente.",
        "description_pt": "Ativa o modo de injeção dinâmica via dlsym do MangoHud para melhorar a detecção de aplicativos que utilizam bibliotecas gráficas carregadas dinamicamente."
    },
    {
        "name": "MANGOHUD_CPU_SENSOR",
        "type": "hud",
        "category": "configuration",
        "description_fr": "Sélectionne le capteur CPU utilisé par MangoHud pour afficher la température, la fréquence ou d'autres informations matérielles lorsque plusieurs capteurs sont disponibles.",
        "description_en": "Selects the CPU sensor used by MangoHud to display temperature, clock speed, or other hardware information when multiple sensors are available.",
        "description_de": "Wählt den von MangoHud verwendeten CPU-Sensor aus, um Temperatur, Taktfrequenz oder andere Hardwareinformationen anzuzeigen, wenn mehrere Sensoren verfügbar sind.",
        "description_uk": "Визначає датчик процесора, який MangoHud використовує для відображення температури, тактової частоти та іншої інформації про обладнання, якщо доступно кілька датчиків.",
        "description_zh": "当系统存在多个 CPU 传感器时，选择 MangoHud 用于显示温度、频率或其他硬件信息的 CPU 传感器。",
        "description_hi": "यदि कई CPU सेंसर उपलब्ध हों, तो तापमान, क्लॉक गति और अन्य हार्डवेयर जानकारी प्रदर्शित करने के लिए MangoHud किस CPU सेंसर का उपयोग करेगा, यह निर्धारित करता है।",
        "description_es": "Selecciona el sensor de CPU que utilizará MangoHud para mostrar la temperatura, la frecuencia u otra información del hardware cuando haya varios sensores disponibles.",
        "description_pt": "Seleciona o sensor de CPU que o MangoHud utilizará para exibir a temperatura, a frequência ou outras informações de hardware quando houver vários sensores disponíveis."
    },
    {
        "name": "MANGOHUD_CONFIG",
        "type": "hud",
        "category": "configuration",
        "description_fr": "Définit les paramètres de configuration MangoHud (affichage, métriques, limite FPS, position et options de l'overlay).",
        "description_en": "Defines MangoHud configuration parameters (display, metrics, FPS limit, position and overlay options).",
        "description_de": "Legt die Konfigurationsparameter von MangoHud fest (Anzeige, Metriken, FPS-Limit, Position und Overlay-Optionen).",
        "description_uk": "Визначає параметри конфігурації MangoHud (відображення, метрики, обмеження FPS, розташування та параметри оверлею).",
        "description_zh": "定义 MangoHud 的配置参数（显示、指标、FPS 限制、位置和覆盖层选项）。",
        "description_hi": "MangoHud के कॉन्फ़िगरेशन पैरामीटर (डिस्प्ले, मेट्रिक्स, FPS सीमा, स्थिति और ओवरले विकल्प) निर्धारित करता है।",
        "description_es": "Define los parámetros de configuración de MangoHud (visualización, métricas, límite de FPS, posición y opciones de la superposición).",
        "description_pt": "Define os parâmetros de configuração do MangoHud (exibição, métricas, limite de FPS, posição e opções da sobreposição)."
    },
    {
        "name": "MANGOHUD_OPENGL",
        "type": "hud",
        "category": "compatibility",
        "description_fr": "Active le support du rendu OpenGL dans MangoHud pour afficher l'overlay avec les applications utilisant OpenGL.",
        "description_en": "Enables MangoHud OpenGL rendering support to display the overlay with applications using OpenGL.",
        "description_de": "Aktiviert die OpenGL-Unterstützung von MangoHud, damit das Overlay auch in OpenGL-Anwendungen angezeigt wird.",
        "description_uk": "Увімкнює підтримку рендерингу OpenGL у MangoHud для відображення оверлею в застосунках, що використовують OpenGL.",
        "description_zh": "启用 MangoHud 的 OpenGL 渲染支持，以便在使用 OpenGL 的应用程序中显示覆盖层。",
        "description_hi": "OpenGL का उपयोग करने वाले अनुप्रयोगों में ओवरले प्रदर्शित करने के लिए MangoHud का OpenGL रेंडरिंग समर्थन सक्षम करता है।",
        "description_es": "Activa la compatibilidad con OpenGL en MangoHud para mostrar la superposición en aplicaciones que utilizan OpenGL.",
        "description_pt": "Ativa o suporte de renderização OpenGL no MangoHud para exibir a sobreposição em aplicativos que utilizam OpenGL."
    },
    {
        "name": "MANGOHUD_VERBOSE",
        "type": "hud",
        "category": "debug",
        "description_fr": "Active ou désactive les messages d'initialisation détaillés de MangoHud.",
        "description_en": "Enables or disables verbose MangoHud initialization messages.",
        "description_de": "Aktiviert oder deaktiviert ausführliche Initialisierungsmeldungen von MangoHud.",
        "description_uk": "Вмикає або вимикає докладні повідомлення ініціалізації MangoHud.",
        "description_zh": "启用或禁用 MangoHud 的详细初始化日志。",
        "description_hi": "MangoHud के विस्तृत प्रारंभिक लॉग को सक्षम या अक्षम करता है।",
        "description_es": "Activa o desactiva los mensajes detallados de inicialización de MangoHud.",
        "description_pt": "Ativa ou desativa as mensagens detalhadas de inicialização do MangoHud."
    },
    {
        "name": "vblank_mode",
        "type": "hud",
        "category": "graphics",
        "description_fr": "Contrôle le VSync de Mesa : 0 = désactivé, 1 = activé, 2 = activé sauf pour les applications contrôlées par l'utilisateur, 3 = activé.",
        "description_en": "Controls Mesa VSync: 0 = off, 1 = on, 2 = on except for user-controlled apps, 3 = on.",
        "description_de": "Steuert Mesa VSync: 0 = aus, 1 = ein, 2 = ein außer bei benutzergesteuerten Anwendungen, 3 = ein.",
        "description_uk": "Керує VSync Mesa: 0 = вимкнено, 1 = увімкнено, 2 = увімкнено, крім програм під керуванням користувача, 3 = увімкнено.",
        "description_zh": "控制 Mesa VSync：0 = 关闭，1 = 开启，2 = 开启但允许应用程序控制，3 = 开启。",
        "description_hi": "Mesa VSync को नियंत्रित करता है: 0 = बंद, 1 = चालू, 2 = चालू लेकिन उपयोगकर्ता-नियंत्रित ऐप्स को छोड़कर, 3 = चालू।",
        "description_es": "Controla el VSync de Mesa: 0 = desactivado, 1 = activado, 2 = activado excepto en aplicaciones controladas por el usuario, 3 = activado.",
        "description_pt": "Controla o VSync do Mesa: 0 = desativado, 1 = ativado, 2 = ativado exceto em aplicações controladas pelo utilizador, 3 = ativado."
    }
]
GSTREAMER_ENV_VARS = [
    # =========================================================
    # WINE / GSTREAMER (MULTIMEDIA STACK CONTROL)
    # =========================================================
    {
        "name": "GST_PLUGIN_PATH",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Chemin des plugins GStreamer. Vide pour éviter les conflits avec les plugins système ou Proton.",
        "description_en": "GStreamer plugin path. Empty to avoid conflicts with system or Proton plugins.",
        "description_de": "Pfad zu den GStreamer-Plugins. Leer lassen, um Konflikte mit System- oder Proton-Plugins zu vermeiden.",
        "description_uk": "Шлях до плагінів GStreamer. Залиште порожнім, щоб уникнути конфліктів із системними плагінами або плагінами Proton.",
        "description_zh": "GStreamer 插件路径。留空可避免与系统或 Proton 插件发生冲突。",
        "description_hi": "GStreamer प्लगइन पथ। सिस्टम या Proton प्लगइनों के साथ टकराव से बचने के लिए इसे खाली छोड़ें।",
        "description_es": "Ruta de los complementos de GStreamer. Déjela vacía para evitar conflictos con los complementos del sistema o de Proton.",
        "description_pt": "Caminho dos plugins do GStreamer. Deixe vazio para evitar conflitos com plugins do sistema ou do Proton."
    },
    {
        "name": "GST_DEBUG",
        "type": "wine",
        "category": "debug",
        "description_fr": "Niveau de logs GStreamer. 0 désactive totalement les logs.",
        "description_en": "GStreamer debug level. 0 disables all logging.",
        "description_de": "Debugstufe von GStreamer. 0 deaktiviert sämtliche Protokollausgaben.",
        "description_uk": "Рівень журналювання GStreamer. Значення 0 повністю вимикає ведення журналів.",
        "description_zh": "GStreamer 调试级别。设置为 0 可完全禁用日志输出。",
        "description_hi": "GStreamer डिबग स्तर। 0 पर सेट करने से सभी लॉगिंग पूरी तरह अक्षम हो जाती है।",
        "description_es": "Nivel de depuración de GStreamer. El valor 0 desactiva completamente todos los registros.",
        "description_pt": "Nível de depuração do GStreamer. O valor 0 desativa completamente todos os logs."
    },
    {
        "name": "WINE_DISABLE_GSTREAMER",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Désactive l’utilisation de GStreamer dans Wine pour éviter les erreurs multimédia et dépendances cassées.",
        "description_en": "Disables Wine GStreamer integration to prevent multimedia errors and broken dependencies.",
        "description_de": "Deaktiviert die GStreamer-Integration in Wine, um Multimediafehler und fehlerhafte Abhängigkeiten zu vermeiden.",
        "description_uk": "Вимикає інтеграцію GStreamer у Wine, щоб запобігти мультимедійним помилкам і проблемам із залежностями.",
        "description_zh": "禁用 Wine 中的 GStreamer 集成，以避免多媒体错误和依赖项问题。",
        "description_hi": "मल्टीमीडिया त्रुटियों और टूटी हुई निर्भरताओं से बचने के लिए Wine में GStreamer एकीकरण को अक्षम करता है।",
        "description_es": "Desactiva la integración de GStreamer en Wine para evitar errores multimedia y dependencias dañadas.",
        "description_pt": "Desativa a integração do GStreamer no Wine para evitar erros multimídia e dependências quebradas."
    },
    {
        "name": "GST_REGISTRY_REUSE_PLUGIN_SCANNER",
        "type": "wine",
        "category": "performance",
        "description_fr": "Réutilise le processus d'analyse des plugins GStreamer afin de réduire le temps de découverte des plugins et d'améliorer les performances au démarrage.",
        "description_en": "Reuses the GStreamer plugin scanner process to reduce plugin discovery time and improve startup performance.",
        "description_de": "Verwendet den GStreamer-Plugin-Scanner erneut, um die Erkennungszeit von Plugins zu verkürzen und die Startleistung zu verbessern.",
        "description_uk": "Повторно використовує процес сканування плагінів GStreamer, щоб скоротити час їх виявлення та покращити швидкість запуску.",
        "description_zh": "重复使用 GStreamer 插件扫描进程，以减少插件发现时间并提升启动性能。",
        "description_hi": "प्लगइन खोजने में लगने वाला समय कम करने और स्टार्टअप प्रदर्शन बेहतर बनाने के लिए GStreamer प्लगइन स्कैनर प्रक्रिया का पुन: उपयोग करता है।",
        "description_es": "Reutiliza el proceso de exploración de complementos de GStreamer para reducir el tiempo de detección de los complementos y mejorar el rendimiento al iniciar.",
        "description_pt": "Reutiliza o processo de verificação de plugins do GStreamer para reduzir o tempo de descoberta dos plugins e melhorar o desempenho na inicialização."
    },
    {
        "name": "GST_PLUGIN_FEATURE_RANK",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Modifie la priorité des plugins, codecs et fonctionnalités GStreamer afin de privilégier ou désactiver certains composants.",
        "description_en": "Changes the priority of GStreamer plugins, codecs, and features to prefer or disable specific components.",
        "description_de": "Ändert die Priorität von GStreamer-Plugins, Codecs und Funktionen, um bestimmte Komponenten zu bevorzugen oder zu deaktivieren.",
        "description_uk": "Змінює пріоритет плагінів, кодеків і компонентів GStreamer, щоб надати перевагу або вимкнути певні елементи.",
        "description_zh": "修改 GStreamer 插件、编解码器和功能的优先级，以优先使用或禁用特定组件。",
        "description_hi": "विशिष्ट घटकों को प्राथमिकता देने या अक्षम करने के लिए GStreamer प्लगइनों, कोडेक्स और सुविधाओं की प्राथमिकता बदलता है।",
        "description_es": "Modifica la prioridad de los complementos, códecs y funciones de GStreamer para priorizar o deshabilitar componentes específicos.",
        "description_pt": "Altera a prioridade dos plugins, codecs e recursos do GStreamer para priorizar ou desativar componentes específicos."
    }
]
GAME_ENV_VARS = [
    # =========================================================
    # GAME
    # =========================================================
    {
        "name": "USE_D3D11",
        "type": "game",
        "category": "graphics",
        "description_fr": "Force l'utilisation du moteur de rendu Direct3D 11 au lieu de versions plus récentes de DirectX.",
        "description_en": "Forces the use of the Direct3D 11 renderer instead of newer DirectX versions.",
        "description_de": "Erzwingt die Verwendung des Direct3D-11-Renderers anstelle neuerer DirectX-Versionen.",
        "description_uk": "Примусово використовує рендерер Direct3D 11 замість новіших версій DirectX.",
        "description_zh": "强制使用 Direct3D 11 渲染器，而不是较新的 DirectX 版本。",
        "description_hi": "नए DirectX संस्करणों के बजाय Direct3D 11 रेंडरर का उपयोग करने के लिए बाध्य करता है।",
        "description_es": "Fuerza el uso del renderizador Direct3D 11 en lugar de versiones más recientes de DirectX.",
        "description_pt": "Força o uso do renderizador Direct3D 11 em vez de versões mais recentes do DirectX."
    },
    {
        "name": "USEALLAVAILABLECORES",
        "type": "game",
        "category": "performance",
        "description_fr": "Demande au moteur Unreal Engine d'utiliser tous les cœurs CPU disponibles pour le traitement du jeu.",
        "description_en": "Instructs Unreal Engine to use all available CPU cores for game processing.",
        "description_de": "Weist die Unreal Engine an, alle verfügbaren CPU-Kerne für die Spielverarbeitung zu verwenden.",
        "description_uk": "Вказує Unreal Engine використовувати всі доступні ядра процесора для обробки гри.",
        "description_zh": "指示 Unreal Engine 使用所有可用的 CPU 核心来处理游戏。",
        "description_hi": "Unreal Engine को गेम प्रोसेसिंग के लिए सभी उपलब्ध CPU कोर का उपयोग करने का निर्देश देता है।",
        "description_es": "Indica a Unreal Engine que utilice todos los núcleos de CPU disponibles para el procesamiento del juego.",
        "description_pt": "Instrui a Unreal Engine a utilizar todos os núcleos de CPU disponíveis para o processamento do jogo."
    }
]


ENV_VARS = (
    DXVK_ENV_VARS
    + VKD3D_ENV_VARS
    + PROTON_ENV_VARS
    + WINE_ENV_VARS
    + SDL_ENV_VARS
    + VULKAN_ENV_VARS
    + MESA_ENV_VARS
    + NVIDIA_ENV_VARS
    + SYSTEM_ENV_VARS
    + STEAM_ENV_VARS
    + HUD_ENV_VARS
    + GSTREAMER_ENV_VARS
    + GAME_ENV_VARS
)
