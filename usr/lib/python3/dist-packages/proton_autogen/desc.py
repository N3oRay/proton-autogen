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

        "gamescope":
            "Gamescope 是一个用于在受控图形环境中运行游戏的微型合成器。 "
            "它可以管理分辨率、全屏模式和刷新率，并提高某些游戏或图形配置的兼容性。",

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

    "hi": {
        "profile":
            "गेम पर लागू किए जाने वाले निष्पादन प्रोफ़ाइल और अनुकूलन को परिभाषित करता है (DX11, DX12, "
            "संगतता मोड, पुराने गेम या विशिष्ट कॉन्फ़िगरेशन)।",

        "proton":
            "Linux पर गेम चलाने के लिए उपयोग किया जाने वाला Proton संस्करण। "
            "अलग-अलग संस्करण संगतता और प्रदर्शन को बेहतर कर सकते हैं या विशिष्ट समस्याओं को ठीक कर सकते हैं।",

        "show_performance":
            "गेम के अंदर एक ओवरले दिखाता है जिसमें FPS, CPU उपयोग, GPU उपयोग, "
            "मेमोरी की खपत और प्रदर्शन से संबंधित अन्य उपयोगी आँकड़े दिखाई देते हैं।",

        "optimize_performance":
            "गेम चलने के दौरान प्राथमिकताओं और सिस्टम सेटिंग्स को समायोजित करके "
            "सिस्टम के प्रदर्शन को स्वचालित रूप से अनुकूलित करता है।",

        "mangohud":
            "MangoHud गेम के अंदर एक ओवरले है जो रीयल-टाइम में FPS, CPU/GPU उपयोग, "
            "तापमान, मेमोरी उपयोग और प्रदर्शन से संबंधित अन्य आँकड़े दिखाता है।",

        "gamemode":
            "GameMode एक सिस्टम सेवा है जो गेम चलने के दौरान कंप्यूटर को अस्थायी रूप से अनुकूलित करती है "
            "ताकि प्रदर्शन बेहतर हो और रुकावटें कम हों।",

        "gamescope":
            "Gamescope एक माइक्रो-कंपोज़िटर है जिसका उपयोग गेम को नियंत्रित ग्राफ़िकल वातावरण में चलाने के लिए किया जाता है। "
            "यह रिज़ॉल्यूशन, फ़ुलस्क्रीन मोड और रिफ्रेश रेट को प्रबंधित करने की अनुमति देता है "
            "और कुछ गेम या ग्राफ़िक्स कॉन्फ़िगरेशन के साथ संगतता में सुधार कर सकता है।",

        "gpu":
            "गेम द्वारा उपयोग किए जाने वाले GPU अनुकूलन मोड को परिभाषित करता है: "
            "auto (स्वचालित पहचान), safe (अधिकतम संगतता), "
            "balanced (संतुलित सेटिंग्स) या performance (अधिकतम FPS)।",

        "prefix":
            "एक अलग वातावरण जिसमें Windows कॉन्फ़िगरेशन, इंस्टॉल की गई लाइब्रेरी और "
            "इस प्रोग्राम द्वारा उपयोग किए जाने वाले एप्लिकेशन शामिल होते हैं। गेम्स के बीच टकराव से बचने के लिए प्रत्येक वातावरण अलग रखा जाता है।",

        "prefix_short":
            "इस एप्लिकेशन के लिए एक अलग वातावरण बनाएँ।",

        "performance_overlay":
            "प्रदर्शन दिखाएँ (FPS, CPU, GPU)",

        "system_optimization":
            "सिस्टम के प्रदर्शन को अनुकूलित करें",
    },

    "es": {
        "profile":
            "Define el perfil de ejecución y las optimizaciones aplicadas al juego (DX11, DX12, "
            "modos de compatibilidad, juegos antiguos o configuraciones específicas).",

        "proton":
            "Versión de Proton utilizada para ejecutar el juego en Linux. "
            "Diferentes versiones pueden mejorar la compatibilidad, el rendimiento o solucionar problemas específicos.",

        "show_performance":
            "Muestra una superposición dentro del juego con los FPS, el uso de la CPU, el uso de la GPU, "
            "el consumo de memoria y otras estadísticas útiles de rendimiento.",

        "optimize_performance":
            "Optimiza automáticamente el rendimiento del sistema mientras se ejecuta el juego, ajustando "
            "las prioridades y la configuración del sistema.",

        "mangohud":
            "MangoHud es una superposición dentro del juego que muestra en tiempo real los FPS, el uso de la CPU/GPU, "
            "las temperaturas, el uso de la memoria y otras estadísticas de rendimiento.",

        "gamemode":
            "GameMode es un servicio del sistema que optimiza temporalmente el ordenador mientras se ejecuta un juego "
            "para mejorar el rendimiento y reducir los tirones.",

        "gamescope":
            "Gamescope es un microcompositor utilizado para ejecutar juegos en un entorno gráfico controlado. "
            "Permite gestionar la resolución, el modo de pantalla completa y la frecuencia de actualización, "
            "y puede mejorar la compatibilidad con algunos juegos o configuraciones gráficas.",

        "gpu":
            "Define el modo de optimización de la GPU utilizado por el juego: "
            "auto (detección automática), safe (máxima compatibilidad), "
            "balanced (configuración equilibrada) o performance (máximos FPS).",

        "prefix":
            "Un entorno independiente que contiene la configuración de Windows, las bibliotecas instaladas y "
            "las aplicaciones utilizadas por este programa. Cada entorno está aislado para evitar conflictos entre juegos.",

        "prefix_short":
            "Crear un entorno independiente para esta aplicación.",

        "performance_overlay":
            "Mostrar el rendimiento (FPS, CPU, GPU)",

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

        "gamescope":
            "Gamescope est un compositeur graphique utilisé pour exécuter les jeux dans un environnement contrôlé. "
            "Il permet de gérer la résolution, le plein écran, la fréquence d'affichage et d'améliorer la compatibilité "
            "avec certains jeux ou configurations graphiques.",

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

        "gamescope":
            "Gamescope ist ein Micro-Compositor, der Spiele in einer kontrollierten grafischen Umgebung ausführt. "
            "Er ermöglicht die Verwaltung von Auflösung, Vollbildmodus und Bildwiederholrate und kann die Kompatibilität "
            "mit bestimmten Spielen oder Grafikkonfigurationen verbessern.",

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

        "gamescope":
            "Gamescope — це мікрокомпозитор, який запускає ігри в контрольованому графічному середовищі. "
            "Він дозволяє керувати роздільною здатністю, повноекранним режимом, частотою оновлення "
            "та може покращити сумісність із деякими іграми або графічними конфігураціями.",

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

        "gamescope":
            "Gamescope é um microcompositor usado para executar jogos em um ambiente gráfico controlado. "
            "Ele permite gerenciar resolução, modo de tela cheia, taxa de atualização e pode melhorar "
            "a compatibilidade com alguns jogos ou configurações gráficas.",

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

    "fi": {
        "profile":
            "Määrittää pelin suoritusprofiilin ja siihen sovellettavat optimoinnit (DX11, DX12, "
            "yhteensopivuustilat, vanhat pelit tai tietyt kokoonpanot).",

        "proton":
            "Pelien Linuxissa suorittamiseen käytettävä Proton-versio. "
            "Eri versiot voivat parantaa yhteensopivuutta ja suorituskykyä tai korjata tiettyjä ongelmia.",

        "show_performance":
            "Näyttää pelin sisäisen peittokuvan, jossa näkyvät FPS, suorittimen käyttö, näytönohjaimen käyttö, "
            "muistin kulutus ja muita hyödyllisiä suorituskykytietoja.",

        "optimize_performance":
            "Optimoi järjestelmän suorituskyvyn automaattisesti pelin ollessa käynnissä säätämällä "
            "prosessien prioriteetteja ja järjestelmäasetuksia.",

        "mangohud":
            "MangoHud on pelin sisäinen peittokuva, joka näyttää reaaliaikaisesti FPS:n, suorittimen ja näytönohjaimen käytön, "
            "lämpötilat, muistin käytön ja muita suorituskykytietoja.",

        "gamemode":
            "GameMode on järjestelmäpalvelu, joka optimoi tietokonetta tilapäisesti pelin ollessa käynnissä "
            "suorituskyvyn parantamiseksi ja nykimisen vähentämiseksi.",

        "gamescope":
            "Gamescope on mikrosommitin, jolla pelejä voidaan suorittaa hallitussa graafisessa ympäristössä. "
            "Sen avulla voidaan hallita resoluutiota, koko näytön tilaa ja virkistystaajuutta, "
            "ja se voi parantaa yhteensopivuutta joidenkin pelien tai grafiikka-asetusten kanssa.",

        "gpu":
            "Määrittää pelissä käytettävän näytönohjaimen optimointitilan: "
            "auto (automaattinen tunnistus), safe (paras yhteensopivuus), "
            "balanced (tasapainotetut asetukset) tai performance (maksimaalinen FPS).",

        "prefix":
            "Erillinen ympäristö, joka sisältää Windows-asetukset, asennetut kirjastot ja "
            "tämän ohjelman käyttämät sovellukset. Jokainen ympäristö on eristetty pelien välisten ristiriitojen välttämiseksi.",

        "prefix_short":
            "Luo tälle sovellukselle erillinen ympäristö.",

        "performance_overlay":
            "Näytä suorituskyky (FPS, CPU, GPU)",

        "system_optimization":
            "Optimoi järjestelmän suorituskyky",
    },


    "el": {
        "profile":
            "Καθορίζει το προφίλ εκτέλεσης και τις βελτιστοποιήσεις που εφαρμόζονται στο παιχνίδι (DX11, DX12, "
            "λειτουργίες συμβατότητας, παλαιότερα παιχνίδια ή συγκεκριμένες ρυθμίσεις).",

        "proton":
            "Η έκδοση του Proton που χρησιμοποιείται για την εκτέλεση του παιχνιδιού σε Linux. "
            "Διαφορετικές εκδόσεις μπορούν να βελτιώσουν τη συμβατότητα και την απόδοση ή να διορθώσουν συγκεκριμένα προβλήματα.",

        "show_performance":
            "Εμφανίζει μια επικάλυψη μέσα στο παιχνίδι με τα FPS, τη χρήση της CPU, τη χρήση της GPU, "
            "την κατανάλωση μνήμης και άλλα χρήσιμα στατιστικά απόδοσης.",

        "optimize_performance":
            "Βελτιστοποιεί αυτόματα την απόδοση του συστήματος κατά την εκτέλεση του παιχνιδιού, προσαρμόζοντας "
            "τις προτεραιότητες και τις ρυθμίσεις του συστήματος.",

        "mangohud":
            "Το MangoHud είναι μια επικάλυψη μέσα στο παιχνίδι που εμφανίζει σε πραγματικό χρόνο τα FPS, τη χρήση της CPU/GPU, "
            "τις θερμοκρασίες, τη χρήση μνήμης και άλλα στατιστικά απόδοσης.",

        "gamemode":
            "Το GameMode είναι μια υπηρεσία συστήματος που βελτιστοποιεί προσωρινά τον υπολογιστή κατά την εκτέλεση ενός παιχνιδιού "
            "για τη βελτίωση της απόδοσης και τη μείωση των κολλημάτων.",

        "gamescope":
            "Το Gamescope είναι ένας μικροσυνθέτης που χρησιμοποιείται για την εκτέλεση παιχνιδιών σε ένα ελεγχόμενο γραφικό περιβάλλον. "
            "Επιτρέπει τη διαχείριση της ανάλυσης, της λειτουργίας πλήρους οθόνης και του ρυθμού ανανέωσης, "
            "και μπορεί να βελτιώσει τη συμβατότητα με ορισμένα παιχνίδια ή ρυθμίσεις γραφικών.",

        "gpu":
            "Καθορίζει τη λειτουργία βελτιστοποίησης της GPU που χρησιμοποιείται από το παιχνίδι: "
            "auto (αυτόματη ανίχνευση), safe (μέγιστη συμβατότητα), "
            "balanced (ισορροπημένες ρυθμίσεις) ή performance (μέγιστα FPS).",

        "prefix":
            "Ένα ξεχωριστό περιβάλλον που περιέχει τη διαμόρφωση των Windows, τις εγκατεστημένες βιβλιοθήκες και "
            "τις εφαρμογές που χρησιμοποιούνται από αυτό το πρόγραμμα. Κάθε περιβάλλον είναι απομονωμένο για την αποφυγή συγκρούσεων μεταξύ παιχνιδιών.",

        "prefix_short":
            "Δημιουργία ξεχωριστού περιβάλλοντος για αυτή την εφαρμογή.",

        "performance_overlay":
            "Εμφάνιση απόδοσης (FPS, CPU, GPU)",

        "system_optimization":
            "Βελτιστοποίηση της απόδοσης του συστήματος",
    },

    "it": {
        "profile":
            "Definisce il profilo di esecuzione e le ottimizzazioni applicate al gioco (DX11, DX12, "
            "modalità di compatibilità, giochi legacy o configurazioni specifiche).",

        "proton":
            "Versione di Proton utilizzata per eseguire il gioco su Linux. "
            "Versioni diverse possono migliorare la compatibilità, le prestazioni o risolvere problemi specifici.",

        "show_performance":
            "Mostra una sovrapposizione (overlay) all'interno del gioco con FPS, utilizzo della CPU, utilizzo della GPU, "
            "consumo di memoria e altre utili statistiche sulle prestazioni.",

        "optimize_performance":
            "Ottimizza automaticamente le prestazioni del sistema durante l'esecuzione del gioco, modificando "
            "le priorità e le impostazioni di sistema.",

        "mangohud":
            "MangoHud è un overlay all'interno del gioco che mostra in tempo reale FPS, utilizzo di CPU/GPU, "
            "temperature, utilizzo della memoria e altre statistiche sulle prestazioni.",

        "gamemode":
            "GameMode è un servizio di sistema che ottimizza temporaneamente il computer durante l'esecuzione di un gioco "
            "per migliorare le prestazioni e ridurre gli scatti.",

        "gamescope":
            "Gamescope è un micro-compositore utilizzato per eseguire i giochi in un ambiente grafico controllato. "
            "Consente di gestire la risoluzione, la modalità a schermo intero e la frequenza di aggiornamento, "
            "e può migliorare la compatibilità con alcuni giochi o configurazioni grafiche.",

        "gpu":
            "Definisce la modalità di ottimizzazione della GPU utilizzata dal gioco: "
            "auto (rilevamento automatico), safe (massima compatibilità), "
            "balanced (impostazioni bilanciate) o performance (FPS massimi).",

        "prefix":
            "Un ambiente separato contenente la configurazione di Windows, le librerie installate e "
            "le applicazioni utilizzate da questo programma. Ogni ambiente è isolato per evitare conflitti tra i giochi.",

        "prefix_short":
            "Crea un ambiente separato per questa applicazione.",

        "performance_overlay":
            "Mostra le prestazioni (FPS, CPU, GPU)",

        "system_optimization":
            "Ottimizza le prestazioni del sistema",
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

        "gamescope":
            "Gamescope is a micro-compositor used to run games in a controlled graphical environment. "
            "It allows managing resolution, fullscreen mode, refresh rate and can improve compatibility "
            "with some games or graphics configurations.",

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
