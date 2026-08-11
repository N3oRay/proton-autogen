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
        "ready": "Ready",
        "menu_diagnostics": "Diagnostics",
        "menu_sensors": "Sensors",
        "menu_help_mangohud": "Help MangoHud",
        "menu_help": "Help",
        "menu_requirements": "Requirements",
        "menu_about_proton": "About Proton",
        "menu_about": "About",
        "already_stopping": "Already stopping {name}",
        "stop_already_in_progress": "All running games are already stopping",
        "select_game_to_stop": "Select a game to stop",
        "select_game_to_stop_detail": "Multiple games are currently running. Select the one you want to stop.",
        "confirm_stop_title": "Stop running game?",
        "confirm_stop_detail": "Unsaved progress may be lost. ({name})",
        "cancel": "Cancel",
        "stop_game": "Stop",
        "stopping_game": "Stopping {name}...",
        "no_active_game": "No active game",
        "running_game": "Running {name}...",
        "game_finished": "{name} finished",
        "lutris_export_completed": "Lutris export completed",
        "lutris_export_failed": "Lutris export failed",
        "missing_game_path": "Game path is missing",
        "unknown_game": "Unknown game",
        "launching_game": "Launching {name}...",
        "launch_failed": "Launch failed: {error}",
        "launch_failed_short": "Unable to launch game",
        "updating": "Updating...",
        "game_removed_from_library": "{name} removed from library",
        "unable_to_remove_game": "Unable to remove game",
        "game_added": "{name} added ✔",
        "game_added_to_library": "{name} added to library",
        "add_game_failed": "Add game failed",
        "unable_to_add_game": "Unable to add game",
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

    "it": {
        "ready": "Pronto",
        "menu_diagnostics": "Diagnostica",
        "menu_sensors": "Sensori",
        "menu_help_mangohud": "Guida MangoHud",
        "menu_help": "Guida",
        "menu_requirements": "Prerequisiti",
        "menu_about_proton": "Informazioni su Proton",
        "menu_about": "Informazioni",
        "already_stopping": "{name} è già in fase di arresto",
        "stop_already_in_progress": "Tutti i giochi in esecuzione sono già in fase di arresto",
        "select_game_to_stop": "Seleziona un gioco da arrestare",
        "select_game_to_stop_detail": "Sono attualmente in esecuzione più giochi. Seleziona quello che vuoi arrestare.",
        "confirm_stop_title": "Arrestare il gioco in esecuzione?",
        "confirm_stop_detail": "I progressi non salvati potrebbero andare persi. ({name})",
        "cancel": "Annulla",
        "stop_game": "Interrompi",
        "stopping_game": "Arresto di {name}...",
        "no_active_game": "Nessun gioco attivo",
        "running_game": "{name} in esecuzione...",
        "game_finished": "{name} terminato",
        "lutris_export_completed": "Esportazione Lutris completata",
        "lutris_export_failed": "Esportazione Lutris non riuscita",
        "missing_game_path": "Percorso del gioco mancante",
        "unknown_game": "Gioco sconosciuto",
        "launching_game": "Avvio di {name}...",
        "launch_failed": "Avvio non riuscito: {error}",
        "launch_failed_short": "Impossibile avviare il gioco",
        "updating": "Aggiornamento...",
        "game_removed_from_library": "{name} rimosso dalla libreria",
        "unable_to_remove_game": "Impossibile rimuovere il gioco",
        "game_added": "{name} aggiunto ✔",
        "game_added_to_library": "{name} aggiunto alla libreria",
        "add_game_failed": "Aggiunta del gioco non riuscita",
        "unable_to_add_game": "Impossibile aggiungere il gioco",
        "no_proton_installation": "Nessuna installazione di Proton trovata",
        "detected_proton_installations": "Installazioni di Proton rilevate",
        "selected": "selezionato",
        "prefix_name": "Nome del prefisso (vuoto = automatico)",
        "diagnostic": "diagnostica proton-autogen",
        "version": "Versione",
        "python": "Python",
        "runtime": "Runtime",
        "wine": "Wine",
        "yes": "sì",
        "no": "no",
        "none": "nessuno",
        "platform": "Piattaforma",
        "detected_programs": "Programmi Windows rilevati",
        "no_windows_programs": "Nessun programma Windows trovato",

        "search_finished": "La ricerca dei programmi è terminata in {time:.3f}s",

        "load_config_prefix": "CARICAMENTO CONFIGURAZIONE PREFISSO: {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "xrandr": "Xrandr",
        "mangohud": "MangoHud",
        "runtime_information": "Informazioni sul runtime",
        "executable": "Eseguibile",
        "proton": "Proton",
        "path": "Percorso",
        "detected": "Rilevato",
        "missing": "Mancante",
        "available": "Disponibile",
        "unavailable": "Non disponibile",
        "favorite": "Preferito",
        "favorites": "Preferiti",
        "playtime": "Tempo di gioco",
        "remove_from_library": "Rimuovi il gioco dalla libreria",
        "export_lutris": "Esporta Lutris (.yml)",
        "edit": "Modifica",
        "checking_executable": "Controllo dell'eseguibile",
        "loading_game_configuration": "Caricamento della configurazione del gioco",
        "detecting_system": "Rilevamento del sistema",
        "starting_proton": "Avvio di Proton",
        "starting_wine": "Avvio di Wine",
        "runtime_selected": "Runtime Proton selezionato",
        "missing_executable_title": "Eseguibile mancante",
        "missing_executable_message": "Eseguibile non trovato",
        "starting_proton_call": "Avvio di Proton Call",
        "run_started": "Esecuzione avviata",
        "config_read_error": "Errore durante la lettura della configurazione {file}: {error}",
        "proton_not_found": """
        Nessuna installazione di Proton trovata.

        Installa una versione di Proton (ad esempio tramite ProtonUp-Qt)
        oppure specifica PROTON_PATH.

        Riga di comando:
          protonup -d ~/.steam/root/compatibilitytools.d

        Riavvia Steam e riprova.
        """,
    },

    "fi": {
        "ready": "Valmis",
        "menu_diagnostics": "Diagnostiikka",
        "menu_sensors": "Anturit",
        "menu_help_mangohud": "MangoHud-ohje",
        "menu_help": "Ohje",
        "menu_requirements": "Vaatimukset",
        "menu_about_proton": "Tietoja Protonista",
        "menu_about": "Tietoja",
        "already_stopping": "{name} on jo pysähtymässä",
        "stop_already_in_progress": "Kaikkien käynnissä olevien pelien pysäyttäminen on jo käynnissä",
        "select_game_to_stop": "Valitse pysäytettävä peli",
        "select_game_to_stop_detail": "Useita pelejä on parhaillaan käynnissä. Valitse peli, jonka haluat pysäyttää.",
        "confirm_stop_title": "Pysäytetäänkö käynnissä oleva peli?",
        "confirm_stop_detail": "Tallentamattomat edistymiset saatetaan menettää. ({name})",
        "cancel": "Peruuta",
        "stop_game": "Pysäytä",
        "stopping_game": "Pysäytetään {name}...",
        "no_active_game": "Ei aktiivista peliä",
        "running_game": "{name} käynnissä...",
        "game_finished": "{name} päättyi",
        "lutris_export_completed": "Lutris-vienti valmis",
        "lutris_export_failed": "Lutris-vienti epäonnistui",
        "missing_game_path": "Pelin polku puuttuu",
        "unknown_game": "Tuntematon peli",
        "launching_game": "Käynnistetään {name}...",
        "launch_failed": "Käynnistys epäonnistui: {error}",
        "launch_failed_short": "Pelin käynnistäminen epäonnistui",
        "updating": "Päivitetään...",
        "game_removed_from_library": "{name} poistettu kirjastosta",
        "unable_to_remove_game": "Pelin poistaminen epäonnistui",
        "game_added": "{name} lisätty ✔",
        "game_added_to_library": "{name} lisätty kirjastoon",
        "add_game_failed": "Pelin lisääminen epäonnistui",
        "unable_to_add_game": "Pelin lisääminen ei onnistu",
        "no_proton_installation": "Proton-asennusta ei löytynyt",
        "detected_proton_installations": "Havaitut Proton-asennukset",
        "selected": "valittu",
        "prefix_name": "Prefiksin nimi (tyhjä = automaattinen)",
        "diagnostic": "proton-autogen-diagnostiikka",
        "version": "Versio",
        "python": "Python",
        "runtime": "Runtime",
        "wine": "Wine",
        "yes": "kyllä",
        "no": "ei",
        "none": "ei mitään",
        "platform": "Alusta",
        "detected_programs": "Havaitut Windows-ohjelmat",
        "no_windows_programs": "Windows-ohjelmia ei löytynyt",

        "search_finished": "Ohjelmien haku valmistui ajassa {time:.3f}s",

        "load_config_prefix": "LADATAAN ASETUKSIA, PREFIKSI: {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "xrandr": "Xrandr",
        "mangohud": "MangoHud",
        "runtime_information": "Runtime-tiedot",
        "executable": "Suoritettava tiedosto",
        "proton": "Proton",
        "path": "Polku",
        "detected": "Havaittu",
        "missing": "Puuttuu",
        "available": "Saatavilla",
        "unavailable": "Ei saatavilla",
        "favorite": "Suosikki",
        "favorites": "Suosikit",
        "playtime": "Pelien peliaika",
        "remove_from_library": "Poista peli kirjastosta",
        "export_lutris": "Vie Lutris (.yml)",
        "edit": "Muokkaa",
        "checking_executable": "Tarkistetaan suoritettavaa tiedostoa",
        "loading_game_configuration": "Ladataan pelin asetuksia",
        "detecting_system": "Tunnistetaan järjestelmää",
        "starting_proton": "Käynnistetään Proton",
        "starting_wine": "Käynnistetään Wine",
        "runtime_selected": "Proton-runtime valittu",
        "missing_executable_title": "Suoritettava tiedosto puuttuu",
        "missing_executable_message": "Suoritettavaa tiedostoa ei löytynyt",
        "starting_proton_call": "Käynnistetään Proton Call",
        "run_started": "Suoritus aloitettu",
        "config_read_error": "Virhe asetusten lukemisessa {file}: {error}",
        "proton_not_found": """
        Proton-asennusta ei löytynyt.

        Asenna Proton-versio (esimerkiksi ProtonUp-Qt:n avulla)
        tai määritä PROTON_PATH.

        Komentorivi:
          protonup -d ~/.steam/root/compatibilitytools.d

        Käynnistä Steam uudelleen ja yritä uudelleen.
        """,
    },

    "el": {
        "ready": "Έτοιμο",
        "menu_diagnostics": "Διαγνωστικά",
        "menu_sensors": "Αισθητήρες",
        "menu_help_mangohud": "Βοήθεια MangoHud",
        "menu_help": "Βοήθεια",
        "menu_requirements": "Προαπαιτούμενα",
        "menu_about_proton": "Σχετικά με το Proton",
        "menu_about": "Σχετικά",
        "already_stopping": "Το {name} βρίσκεται ήδη σε διαδικασία τερματισμού",
        "stop_already_in_progress": "Όλα τα παιχνίδια που εκτελούνται βρίσκονται ήδη σε διαδικασία τερματισμού",
        "select_game_to_stop": "Επιλέξτε ένα παιχνίδι για τερματισμό",
        "select_game_to_stop_detail": "Αυτή τη στιγμή εκτελούνται πολλά παιχνίδια. Επιλέξτε αυτό που θέλετε να τερματίσετε.",
        "confirm_stop_title": "Τερματισμός του παιχνιδιού που εκτελείται;",
        "confirm_stop_detail": "Η μη αποθηκευμένη πρόοδος ενδέχεται να χαθεί. ({name})",
        "cancel": "Ακύρωση",
        "stop_game": "Τερματισμός",
        "stopping_game": "Τερματισμός του {name}...",
        "no_active_game": "Δεν υπάρχει ενεργό παιχνίδι",
        "running_game": "Εκτέλεση του {name}...",
        "game_finished": "Το {name} ολοκληρώθηκε",
        "lutris_export_completed": "Η εξαγωγή Lutris ολοκληρώθηκε",
        "lutris_export_failed": "Η εξαγωγή Lutris απέτυχε",
        "missing_game_path": "Λείπει η διαδρομή του παιχνιδιού",
        "unknown_game": "Άγνωστο παιχνίδι",
        "launching_game": "Εκκίνηση του {name}...",
        "launch_failed": "Η εκκίνηση απέτυχε: {error}",
        "launch_failed_short": "Αδυναμία εκκίνησης του παιχνιδιού",
        "updating": "Ενημέρωση...",
        "game_removed_from_library": "Το {name} αφαιρέθηκε από τη βιβλιοθήκη",
        "unable_to_remove_game": "Αδυναμία αφαίρεσης του παιχνιδιού",
        "game_added": "Το {name} προστέθηκε ✔",
        "game_added_to_library": "Το {name} προστέθηκε στη βιβλιοθήκη",
        "add_game_failed": "Η προσθήκη του παιχνιδιού απέτυχε",
        "unable_to_add_game": "Αδυναμία προσθήκης του παιχνιδιού",
        "no_proton_installation": "Δεν βρέθηκε εγκατάσταση Proton",
        "detected_proton_installations": "Εντοπίστηκαν εγκαταστάσεις Proton",
        "selected": "επιλεγμένο",
        "prefix_name": "Όνομα prefix (κενό = αυτόματο)",
        "diagnostic": "διαγνωστικά proton-autogen",
        "version": "Έκδοση",
        "python": "Python",
        "runtime": "Runtime",
        "wine": "Wine",
        "yes": "ναι",
        "no": "όχι",
        "none": "κανένα",
        "platform": "Πλατφόρμα",
        "detected_programs": "Εντοπισμένα προγράμματα Windows",
        "no_windows_programs": "Δεν βρέθηκαν προγράμματα Windows",

        "search_finished": "Η αναζήτηση προγραμμάτων ολοκληρώθηκε σε {time:.3f}s",

        "load_config_prefix": "ΦΟΡΤΩΣΗ ΡΥΘΜΙΣΕΩΝ PREFIX: {prefix}",

        "feature_status": "{key}: {value}",
        "proton_call": "proton-call",
        "gamemode": "GameMode",
        "gamescope": "GameScope",
        "xrandr": "Xrandr",
        "mangohud": "MangoHud",
        "runtime_information": "Πληροφορίες runtime",
        "executable": "Εκτελέσιμο",
        "proton": "Proton",
        "path": "Διαδρομή",
        "detected": "Εντοπίστηκε",
        "missing": "Λείπει",
        "available": "Διαθέσιμο",
        "unavailable": "Μη διαθέσιμο",
        "favorite": "Αγαπημένο",
        "favorites": "Αγαπημένα",
        "playtime": "Χρόνος παιχνιδιού",
        "remove_from_library": "Αφαίρεση παιχνιδιού από τη βιβλιοθήκη",
        "export_lutris": "Εξαγωγή Lutris (.yml)",
        "edit": "Επεξεργασία",
        "checking_executable": "Έλεγχος εκτελέσιμου",
        "loading_game_configuration": "Φόρτωση ρυθμίσεων παιχνιδιού",
        "detecting_system": "Εντοπισμός συστήματος",
        "starting_proton": "Εκκίνηση Proton",
        "starting_wine": "Εκκίνηση Wine",
        "runtime_selected": "Επιλέχθηκε το Proton runtime",
        "missing_executable_title": "Λείπει το εκτελέσιμο",
        "missing_executable_message": "Δεν βρέθηκε το εκτελέσιμο",
        "starting_proton_call": "Εκκίνηση Proton Call",
        "run_started": "Η εκτέλεση ξεκίνησε",
        "config_read_error": "Σφάλμα ανάγνωσης ρυθμίσεων {file}: {error}",
        "proton_not_found": """
        Δεν βρέθηκε εγκατάσταση Proton.

        Εγκαταστήστε μια έκδοση του Proton (π.χ. μέσω του ProtonUp-Qt)
        ή καθορίστε το PROTON_PATH.

        Γραμμή εντολών:
          protonup -d ~/.steam/root/compatibilitytools.d

        Επανεκκινήστε το Steam και δοκιμάστε ξανά.
        """,
    },

    "uk": {
        "ready": "Готово",
        "menu_diagnostics": "Діагностика",
        "menu_sensors": "Датчики",
        "menu_help_mangohud": "Довідка MangoHud",
        "menu_help": "Довідка",
        "menu_requirements": "Вимоги",
        "menu_about_proton": "Про Proton",
        "menu_about": "Про програму",
        "already_stopping": "{name} вже зупиняється",
        "stop_already_in_progress": "Усі запущені ігри вже зупиняються",
        "select_game_to_stop": "Виберіть гру, яку потрібно зупинити",
        "select_game_to_stop_detail": "Зараз запущено кілька ігор. Виберіть гру, яку ви хочете зупинити.",
        "confirm_stop_title": "Зупинити гру, що виконується?",
        "confirm_stop_detail": "Незбережений прогрес може бути втрачено. ({name})",
        "cancel": "Скасувати",
        "stop_game": "Зупинити",
        "stopping_game": "Зупинення {name}...",
        "no_active_game": "Немає активної гри",
        "running_game": "{name} запущено...",
        "game_finished": "{name} завершено",
        "lutris_export_completed": "Експорт до Lutris завершено",
        "lutris_export_failed": "Помилка експорту до Lutris",
        "missing_game_path": "Шлях до гри відсутній",
        "unknown_game": "Невідома гра",
        "launching_game": "Запуск {name}...",
        "launch_failed": "Помилка запуску: {error}",
        "launch_failed_short": "Не вдалося запустити гру",
        "updating": "Оновлення...",
        "game_removed_from_library": "{name} видалено з бібліотеки",
        "unable_to_remove_game": "Не вдалося видалити гру",
        "game_added": "{name} додано ✔",
        "game_added_to_library": "{name} додано до бібліотеки",
        "add_game_failed": "Помилка додавання гри",
        "unable_to_add_game": "Не вдалося додати гру",
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
        "ready": "Pronto",
        "menu_diagnostics": "Diagnóstico",
        "menu_sensors": "Sensores",
        "menu_help_mangohud": "Ajuda do MangoHud",
        "menu_help": "Ajuda",
        "menu_requirements": "Requisitos",
        "menu_about_proton": "Sobre o Proton",
        "menu_about": "Sobre",
        "already_stopping": "{name} já está sendo interrompido",
        "stop_already_in_progress": "Todos os jogos em execução já estão sendo interrompidos",
        "select_game_to_stop": "Selecionar um jogo para parar",
        "select_game_to_stop_detail": "Estão vários jogos em execução. Selecione o jogo que pretende parar.",
        "confirm_stop_title": "Parar o jogo em execução?",
        "confirm_stop_detail": "O progresso não salvo pode ser perdido. ({name})",
        "cancel": "Cancelar",
        "stop_game": "Parar",
        "stopping_game": "Parando {name}...",
        "no_active_game": "Nenhum jogo ativo",
        "running_game": "{name} está em execução...",
        "game_finished": "{name} terminou",
        "lutris_export_completed": "Exportação do Lutris concluída",
        "lutris_export_failed": "Falha na exportação do Lutris",
        "missing_game_path": "Caminho do jogo ausente",
        "unknown_game": "Jogo desconhecido",
        "launching_game": "Iniciando {name}...",
        "launch_failed": "Falha ao iniciar: {error}",
        "launch_failed_short": "Não foi possível iniciar o jogo",
        "updating": "Atualizando...",
        "game_removed_from_library": "{name} removido da biblioteca",
        "unable_to_remove_game": "Não foi possível remover o jogo",
        "game_added": "{name} adicionado ✔",
        "game_added_to_library": "{name} adicionado à biblioteca",
        "add_game_failed": "Falha ao adicionar o jogo",
        "unable_to_add_game": "Não foi possível adicionar o jogo",
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
        "ready": "Listo",
        "menu_diagnostics": "Diagnóstico",
        "menu_sensors": "Sensores",
        "menu_help_mangohud": "Ayuda de MangoHud",
        "menu_help": "Ayuda",
        "menu_requirements": "Requisitos",
        "menu_about_proton": "Acerca de Proton",
        "menu_about": "Acerca de",
        "already_stopping": "{name} ya se está deteniendo",
        "stop_already_in_progress": "Todos los juegos en ejecución ya se están deteniendo",
        "select_game_to_stop": "Seleccionar un juego para detener",
        "select_game_to_stop_detail": "Hay varios juegos en ejecución. Selecciona el juego que quieres detener.",
        "confirm_stop_title": "¿Detener el juego en ejecución?",
        "confirm_stop_detail": "Se podría perder el progreso no guardado. ({name})",
        "cancel": "Cancelar",
        "stop_game": "Detener",
        "stopping_game": "Deteniendo {name}...",
        "no_active_game": "Ningún juego activo",
        "running_game": "{name} está en ejecución...",
        "game_finished": "{name} ha terminado",
        "lutris_export_completed": "Exportación de Lutris completada",
        "lutris_export_failed": "Error en la exportación de Lutris",
        "missing_game_path": "Falta la ruta del juego",
        "unknown_game": "Juego desconocido",
        "launching_game": "Iniciando {name}...",
        "launch_failed": "Error al iniciar: {error}",
        "launch_failed_short": "No se pudo iniciar el juego",
        "updating": "Actualizando...",
        "game_removed_from_library": "{name} eliminado de la biblioteca",
        "unable_to_remove_game": "No se pudo eliminar el juego",
        "game_added": "{name} añadido ✔",
        "game_added_to_library": "{name} añadido a la biblioteca",
        "add_game_failed": "Error al añadir el juego",
        "unable_to_add_game": "No se pudo añadir el juego",
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
        "ready": "तैयार",
        "menu_diagnostics": "निदान",
        "menu_sensors": "सेंसर",
        "menu_help_mangohud": "MangoHud सहायता",
        "menu_help": "सहायता",
        "menu_requirements": "आवश्यकताएँ",
        "menu_about_proton": "Proton के बारे में",
        "menu_about": "के बारे में",
        "already_stopping": "{name} पहले से बंद हो रहा है",
        "stop_already_in_progress": "सभी चल रहे गेम पहले से बंद हो रहे हैं",
        "select_game_to_stop": "रोकने के लिए गेम चुनें",
        "select_game_to_stop_detail": "कई गेम अभी चल रहे हैं। वह गेम चुनें जिसे आप रोकना चाहते हैं।",
        "confirm_stop_title": "चल रहे गेम को रोकें?",
        "confirm_stop_detail": "सहेजी न गई प्रगति खो सकती है। ({name})",
        "cancel": "रद्द करें",
        "stop_game": "रोकें",
        "stopping_game": "{name} रोका जा रहा है...",
        "no_active_game": "कोई सक्रिय गेम नहीं",
        "running_game": "{name} चल रहा है...",
        "game_finished": "{name} समाप्त हो गया",
        "lutris_export_completed": "Lutris निर्यात पूरा हुआ",
        "lutris_export_failed": "Lutris निर्यात विफल हुआ",
        "missing_game_path": "गेम का पथ उपलब्ध नहीं है",
        "unknown_game": "अज्ञात गेम",
        "launching_game": "{name} शुरू हो रहा है...",
        "launch_failed": "शुरू करने में विफल: {error}",
        "launch_failed_short": "गेम शुरू नहीं किया जा सका",
        "updating": "अपडेट हो रहा है...",
        "game_removed_from_library": "{name} को लाइब्रेरी से हटा दिया गया",
        "unable_to_remove_game": "गेम को हटाया नहीं जा सका",
        "game_added": "{name} जोड़ा गया ✔",
        "game_added_to_library": "{name} को लाइब्रेरी में जोड़ा गया",
        "add_game_failed": "गेम जोड़ने में विफल",
        "unable_to_add_game": "गेम जोड़ा नहीं जा सका",
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
        "ready": "Bereit",
        "menu_diagnostics": "Diagnose",
        "menu_sensors": "Sensoren",
        "menu_help_mangohud": "Hilfe zu MangoHud",
        "menu_help": "Hilfe",
        "menu_requirements": "Voraussetzungen",
        "menu_about_proton": "Über Proton",
        "menu_about": "Über",
        "already_stopping": "{name} wird bereits beendet",
        "stop_already_in_progress": "Alle laufenden Spiele werden bereits beendet",
        "select_game_to_stop": "Spiel zum Beenden auswählen",
        "select_game_to_stop_detail": "Mehrere Spiele laufen derzeit. Wählen Sie das Spiel aus, das Sie beenden möchten.",
        "confirm_stop_title": "Laufendes Spiel beenden?",
        "confirm_stop_detail": "Nicht gespeicherter Fortschritt könnte verloren gehen. ({name})",
        "cancel": "Abbrechen",
        "stop_game": "Beenden",
        "stopping_game": "{name} wird beendet...",
        "no_active_game": "Kein aktives Spiel",
        "running_game": "{name} wird ausgeführt...",
        "game_finished": "{name} wurde beendet",
        "lutris_export_completed": "Lutris-Export abgeschlossen",
        "lutris_export_failed": "Lutris-Export fehlgeschlagen",
        "missing_game_path": "Spielpfad fehlt",
        "unknown_game": "Unbekanntes Spiel",
        "launching_game": "{name} wird gestartet...",
        "launch_failed": "Start fehlgeschlagen: {error}",
        "launch_failed_short": "Spiel konnte nicht gestartet werden",
        "updating": "Aktualisierung...",
        "game_removed_from_library": "{name} wurde aus der Bibliothek entfernt",
        "unable_to_remove_game": "Spiel konnte nicht entfernt werden",
        "game_added": "{name} hinzugefügt ✔",
        "game_added_to_library": "{name} wurde zur Bibliothek hinzugefügt",
        "add_game_failed": "Hinzufügen des Spiels fehlgeschlagen",
        "unable_to_add_game": "Spiel konnte nicht hinzugefügt werden",
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
        "ready": "Prêt",
        "menu_diagnostics": "Diagnostics",
        "menu_sensors": "Capteurs",
        "menu_help_mangohud": "Aide MangoHud",
        "menu_help": "Aide",
        "menu_requirements": "Prérequis",
        "menu_about_proton": "À propos de Proton",
        "menu_about": "À propos",
        "already_stopping": "{name} est déjà en cours d'arrêt",
        "stop_already_in_progress": "Tous les jeux en cours sont déjà en train de s'arrêter",
        "select_game_to_stop" : "Choisir un jeu à arrêter",
        "select_game_to_stop_detail" : "Plusieurs jeux sont actuellement en cours. Sélectionnez celui que vous souhaitez arrêter.",
        "confirm_stop_title": "Arrêter le jeu ?",
        "confirm_stop_detail": "La progression non sauvegardée sera perdue. ({name})",
        "cancel": "Annuler",
        "stop_game": "Arrêter",
        "stopping_game": "Arrêt de {name}...",
        "no_active_game": "Aucun jeu en cours",
        "running_game": "{name} est en cours d'exécution...",
        "game_finished": "{name} est terminé",
        "lutris_export_completed": "Export Lutris terminé",
        "lutris_export_failed": "Échec de l'export Lutris",
        "missing_game_path": "Chemin du jeu manquant",
        "unknown_game": "Jeu inconnu",
        "launching_game": "Lancement de {name}...",
        "launch_failed": "Échec du lancement : {error}",
        "launch_failed_short": "Impossible de lancer le jeu",
        "updating": "Mise à jour...",
        "game_removed_from_library": "{name} retiré de la bibliothèque",
        "unable_to_remove_game": "Impossible de supprimer le jeu",
        "game_added": "{name} ajouté ✔",
        "game_added_to_library": "{name} ajouté à la bibliothèque",
        "add_game_failed": "Échec de l'ajout du jeu",
        "unable_to_add_game": "Impossible d'ajouter le jeu",
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
        "run_started": "Exécution démarrée",
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
        "ready": "就绪",
        "menu_diagnostics": "诊断",
        "menu_sensors": "传感器",
        "menu_help_mangohud": "MangoHud 帮助",
        "menu_help": "帮助",
        "menu_requirements": "系统要求",
        "menu_about_proton": "关于 Proton",
        "menu_about": "关于",
        "already_stopping": "{name} 正在停止中",
        "stop_already_in_progress": "所有正在运行的游戏都已在停止中",
        "select_game_to_stop": "选择要停止的游戏",
        "select_game_to_stop_detail": "当前有多个游戏正在运行。请选择您要停止的游戏。",
        "confirm_stop_title": "停止正在运行的游戏？",
        "confirm_stop_detail": "未保存的进度可能会丢失。({name})",
        "cancel": "取消",
        "stop_game": "停止",
        "stopping_game": "正在停止 {name}...",
        "no_active_game": "没有正在运行的游戏",
        "running_game": "正在运行 {name}...",
        "game_finished": "{name} 已结束",
        "lutris_export_completed": "Lutris 导出完成",
        "lutris_export_failed": "Lutris 导出失败",
        "missing_game_path": "缺少游戏路径",
        "unknown_game": "未知游戏",
        "launching_game": "正在启动 {name}...",
        "launch_failed": "启动失败：{error}",
        "launch_failed_short": "无法启动游戏",
        "updating": "正在更新...",
        "game_removed_from_library": "已从游戏库中移除 {name}",
        "unable_to_remove_game": "无法移除游戏",
        "game_added": "已添加 {name} ✔",
        "game_added_to_library": "已将 {name} 添加到游戏库",
        "add_game_failed": "添加游戏失败",
        "unable_to_add_game": "无法添加游戏",
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
