#!/usr/bin/env python3
#game_editor.py
import gi
import os
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GLib

from proton_autogen.profiles.def_env import ENV_VARS_BY_NAME

from proton_autogen.backend import save_game_config
from proton_autogen.backend import find_all_protons
from proton_autogen.ux.desc import set_tooltip
from proton_autogen.editor import list_prefixes_ux
from proton_autogen.profiles.init import VALID_PROFILES
from proton_autogen.i18n import tr
from proton_autogen.ux import cover_manager
from proton_autogen.ux import adw_rows
from proton_autogen.ux.adw_rows import USE_ADW

# Valeur par défaut appliquée quand MangoHud est activé sans fps_limit défini
DEFAULT_FPS_LIMIT = 60

# Résolutions fixes proposées pour Gamescope.
# Les valeurs sont enregistrées dans la configuration par application.
# L'entrée « Automatique » est ajoutée en tête par
# _build_gamescope_resolutions() car son libellé est traduit (i18n).
GAMESCOPE_FIXED_RESOLUTIONS = [
    ("PC — 800 × 600 (600p)", "800x600"),
    ("PC — 1280 × 720 (720p)", "1280x720"),
    ("PC — 1366 × 768", "1366x768"),
    ("PC — 1600 × 900", "1600x900"),
    ("PC — 1680 × 1050", "1680x1050"),
    ("PC — 1680 × 1200", "1680x1200"),
    ("PC — 1920 × 1080 (1080p)", "1920x1080"),
    ("PC — 2560 × 1440 (1440p)", "2560x1440"),
    ("PC — 3440 × 1440 (UWQHD)", "3440x1440"),
    ("PC — 3840 × 2160 (4K)", "3840x2160"),
    ("Steam Deck — 1280 × 800", "1280x800"),
]

# Clés déjà gérées ailleurs dans l'éditeur : on ne les propose pas dans le
# champ "variables d'environnement personnalisées" pour éviter les doublons
# / conflits avec la logique interne (prefix, mangohud, gpu...).
RESERVED_ENV_KEYS = set()


def _env_query_matches(query: str, haystack: str) -> bool:
    """Recherche "tous les mots" : chaque mot saisi doit apparaître dans
    le nom ou la description (insensible à la casse). Une requête vide
    correspond à tout."""
    return all(token in haystack for token in query.lower().split())

# -----------------------------
# GAME EDITOR WINDOW
# -----------------------------
# Onglets transparents : Adwaita peint par défaut le contenu, l'en-tête et
# les zones de défilement d'un Gtk.Notebook en blanc. On les rend
# transparents pour laisser apparaître le fond du thème actif.
# Limité à la fenêtre de l'éditeur ; priorité APPLICATION - 1 : un thème peut
# toujours surcharger ces règles (même convention que game_biblio).
_TABS_CSS = b"""
.editor-window notebook,
.editor-window notebook > stack,
.editor-window notebook > header,
.editor-window notebook > header > tabs > tab,
.editor-window notebook scrolledwindow,
.editor-window notebook scrolledwindow > viewport {
    background: transparent;
    background-color: transparent;
}
"""
_tabs_css_loaded = False


def _load_tabs_css():
    global _tabs_css_loaded
    if _tabs_css_loaded:
        return
    display = Gdk.Display.get_default()
    if display is None:
        return
    provider = Gtk.CssProvider()
    provider.load_from_data(_TABS_CSS)
    Gtk.StyleContext.add_provider_for_display(
        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION - 1
    )
    _tabs_css_loaded = True


class GameEditor(Gtk.Window):

    def __init__(self, app, game, lang):
        super().__init__(application=app)
        self.set_title("Edit Game Profile")
        self.set_default_size(520, 560)
        #self.set_resizable(True)
        self.on_saved = None
        self.on_protondb_requested = None   # 👈 nouveau
        self.on_memory_requested = None     # 👈 ouvre le gestionnaire de sauvegardes
        self.set_size_request(520, 520)
        self.add_css_class("editor-window")
        self.profile_model = VALID_PROFILES
        self.prefix_model = list_prefixes_ux()
        self.gpu_model = [
            "auto",
            "safe",
            "balanced",
            "performance",
            "extreme"
        ]

        self.game = game
        self.lang = lang

        # Jaquette (vue Bibliothèque) : l'image choisie n'est importée dans
        # le dossier de données qu'à l'enregistrement, pour ne pas laisser
        # de fichier orphelin si l'utilisateur annule.
        self._cover_current = self.game.get("cover_image")   # chemin déjà stocké
        self._cover_new_src = None                           # image fraîchement choisie
        self._cover_removed = False

        self.build_ui()

    # -------------------------
    # UI
    # -------------------------
    def build_ui(self):

        frame = Gtk.Frame()
        frame.add_css_class("editor-form")

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=12,
            margin_bottom=12,
            margin_start=12,
            margin_end=12,
        )

        frame.set_child(root)
        self.set_child(frame)

        # -------------------------
        # TITLE
        # -------------------------
        title = Gtk.Label(label=self.game.get("name", "Game"))
        title.add_css_class("title-4")
        root.append(title)

        # -------------------------
        # ONGLETS
        #   1. Préférences      : profil, Proton, prefix, AppID, jaquette,
        #                         GPU, favori
        #   2. Réglages avancés : MangoHud, GameMode, Gamescope, veille,
        #                         sauvegardes
        #   3. Réglages Expert  : variables d'environnement personnalisées
        # Chaque page défile seule : un accordéon déplié ne rallonge plus
        # la fenêtre. Le bouton d'enregistrement reste toujours visible.
        # -------------------------
        page_prefs = self._new_tab_page()
        page_advanced = self._new_tab_page()
        page_expert = self._new_tab_page()

        _load_tabs_css()
        self.notebook = Gtk.Notebook()
        self.notebook.set_vexpand(True)
        for page, key, fallback in (
            (page_prefs, "editor_tab_preferences", "Préférences"),
            (page_advanced, "editor_tab_advanced", "Réglages avancés"),
            (page_expert, "editor_tab_expert", "Réglages Expert"),
        ):
            self.notebook.append_page(
                self._wrap_tab_page(page),
                Gtk.Label(label=tr(key) or fallback),
            )
        root.append(self.notebook)

        # -------------------------
        # PROFILE SELECT
        # -------------------------
        self.profile = Gtk.DropDown.new_from_strings(self.profile_model)
        set_tooltip(self.profile, "profile", self.lang) # new

        current_profile = self.game.get("exe_type", "dx11")

        if current_profile in self.profile_model:
            self.profile.set_selected(self.profile_model.index(current_profile))

        page_prefs.append(self._row("Profile", self.profile))

        # -------------------------
        # PROTON SELECT (simplifié)
        # -------------------------
        #self.proton = Gtk.Entry()
        #self.proton.set_text(self.game.get("proton", "GE-Proton"))

        self.protons = find_all_protons()
        self.proton_names = [os.path.basename(p) for p in self.protons]
        self.proton = Gtk.DropDown.new_from_strings(self.protons)
        set_tooltip(self.proton, "proton", self.lang) # new

        current = self.game.get("proton", "")
        if current in self.protons:
            self.proton.set_selected(self.protons.index(current))

        page_prefs.append(self._row("Proton", self.proton))

        # -------------------------
        # PREFIX MODE
        # -------------------------
        self.prefix = Gtk.DropDown.new_from_strings(self.prefix_model)
        set_tooltip(self.prefix, "prefix", self.lang)

        current_prefix = self.game.get("prefix", {}).get("name", "main")


        if current_prefix in self.prefix_model:
            self.prefix.set_selected(self.prefix_model.index(current_prefix))
        page_prefs.append(self._row("Prefix", self.prefix))

        # -------------------------
        # STEAM APP ID + PROTONDB (même ligne)
        # -------------------------
        self.app_id_entry = Gtk.Entry()
        self.app_id_entry.set_placeholder_text(tr("app_id_placeholder"))
        self.app_id_entry.set_max_length(10)
        self.app_id_entry.set_width_chars(10)
        #self.app_id_entry.set_hexpand(True)
        self.app_id_entry.set_text(str(self.game.get("app_id", "") or ""))
        set_tooltip(self.app_id_entry, "app_id", self.lang)
        self.app_id_entry.connect("changed", self._on_app_id_changed)

        self.protondb_btn = Gtk.Button(label="📊 ProtonDB")
        #self.protondb_btn.add_css_class("suggested-action")
        self.protondb_btn.add_css_class("section-toggle")
        self.protondb_btn.connect("clicked", self.on_show_protondb)

        app_id_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        app_id_label = Gtk.Label(label="Steam AppID", xalign=0)
        app_id_label.set_width_chars(12)
        app_id_label.add_css_class("form-label")

        app_id_row.append(app_id_label)
        app_id_row.append(self.app_id_entry)
        app_id_row.append(self.protondb_btn)
        page_prefs.append(app_id_row)

        # État initial : bouton visible seulement si un AppID est déjà renseigné
        self._on_app_id_changed(self.app_id_entry)

        # -------------------------
        # COVER (vue Bibliothèque)
        # -------------------------
        page_prefs.append(self._build_cover_row())
        page_prefs.append(self.cover_hint)

        # -------------------------
        # TOGGLES
        # -------------------------
        features = self.game.get("features", {})

        # FAVORITE
        self.favorite = adw_rows.new_switch(
            tr("add_to_favorites"), self.game.get("favorite", False)
        )

        set_tooltip(self.favorite, "favorite", self.lang)
        # MANGO
        self.mangohud = adw_rows.new_switch(
            tr("enable_mangohud"), features.get("mangohud", False)
        )
        set_tooltip(self.mangohud, "mangohud", self.lang)  #new code
        # "notify::active" existe pour CheckButton comme pour AdwSwitchRow.
        self.mangohud.connect(
            "notify::active", lambda w, _p: self.on_mangohud_toggled(w)
        )

        # FPS LIMIT (visible seulement si MangoHud est actif)
        fps_limit = features.get("fps_limit", DEFAULT_FPS_LIMIT)
        fps_adjustment = Gtk.Adjustment(
            value=fps_limit,
            lower=0,
            upper=1000,
            step_increment=1,
            page_increment=10,
        )
        self.fps_limit = Gtk.SpinButton()
        self.fps_limit.add_css_class("fps-spinbutton")
        self.fps_limit.set_adjustment(fps_adjustment)
        self.fps_limit.set_numeric(True)
        set_tooltip(self.fps_limit, "fps_limit", self.lang)

        if USE_ADW:
            # Le réglage FPS se loge à droite de l'interrupteur MangoHud :
            # pas de ligne supplémentaire, le menu reste compact.
            self.fps_limit_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            self.fps_limit_row.set_valign(Gtk.Align.CENTER)
            self.fps_limit_row.append(Gtk.Label(label="FPS"))
            self.fps_limit_row.append(self.fps_limit)
            self.mangohud.add_suffix(self.fps_limit_row)
        else:
            self.fps_limit_row = self._row("FPS limit", self.fps_limit)
        self.fps_limit_row.set_sensitive(self.mangohud.get_active())

        # GAMEMODE
        self.gamemode = adw_rows.new_switch(
            tr("enable_gamemode"), features.get("gamemode", False)
        )
        set_tooltip(self.gamemode, "gamemode", self.lang) #new code

        # GAMESCOPE
        self.gamescope = adw_rows.new_switch(
            tr("enable_gamescope"), features.get("gamescope", False)
        )
        set_tooltip(self.gamescope, "gamescope", self.lang)

        # Résolutions Gamescope :
        #   - résolution interne : -w / -h
        #   - résolution de sortie : -W / -H
        self.gamescope_resolutions = self._build_gamescope_resolutions()
        resolution_labels = [
            label for label, _value in self.gamescope_resolutions
        ]

        self.gamescope_internal_resolution = Gtk.DropDown.new_from_strings(
            resolution_labels
        )
        self.gamescope_output_resolution = Gtk.DropDown.new_from_strings(
            resolution_labels
        )

        self._select_gamescope_resolution(
            self.gamescope_internal_resolution,
            features.get("gamescope_internal_resolution", "auto"),
        )
        self._select_gamescope_resolution(
            self.gamescope_output_resolution,
            features.get("gamescope_output_resolution", "auto"),
        )

        self.gamescope_internal_resolution.set_tooltip_text(
            tr("gamescope_internal_resolution_tooltip")
            or "Résolution de rendu interne Gamescope (-w/-h)."
        )
        self.gamescope_output_resolution.set_tooltip_text(
            tr("gamescope_output_resolution_tooltip")
            or "Résolution de sortie Gamescope (-W/-H). « Automatique » "
               "conserve la détection automatique de l'écran."
        )

        self.gamescope_internal_row = self._row(
            tr("gamescope_internal_resolution")
            or "Résolution interne (-w/-h)",
            self.gamescope_internal_resolution,
        )
        self.gamescope_output_row = self._row(
            tr("gamescope_output_resolution")
            or "Résolution de sortie (-W/-H)",
            self.gamescope_output_resolution,
        )

        # Upscaling FSR : -F fsr
        self.gamescope_fsr = Gtk.Switch()
        self.gamescope_fsr.set_valign(Gtk.Align.CENTER)
        self.gamescope_fsr.set_halign(Gtk.Align.START)
        self.gamescope_fsr.set_active(
            bool(features.get("gamescope_fsr", False))
        )
        self.gamescope_fsr.set_tooltip_text(
            tr("gamescope_fsr_tooltip")
            or "Upscaling AMD FSR (-F fsr). Utile lorsque la résolution "
               "interne est inférieure à la résolution de sortie."
        )

        # Limiteur de FPS : -r (0 = désactivé)
        try:
            _gs_fps = int(features.get("gamescope_fps_limit", 0))
        except (TypeError, ValueError):
            _gs_fps = 0
        self.gamescope_fps_limit = Gtk.SpinButton()
        self.gamescope_fps_limit.add_css_class("fps-spinbutton")
        self.gamescope_fps_limit.set_adjustment(
            Gtk.Adjustment(
                value=max(0, min(_gs_fps, 1000)),
                lower=0,
                upper=1000,
                step_increment=1,
                page_increment=10,
            )
        )
        self.gamescope_fps_limit.set_numeric(True)
        self.gamescope_fps_limit.set_tooltip_text(
            tr("gamescope_fps_limit_tooltip")
            or "Limite le taux de rafraîchissement du jeu dans Gamescope "
               "(-r). 0 = désactivé."
        )

        # Capture forcée du curseur : --force-grab-cursor
        # Activée par défaut, comme avant l'ajout de cette option.
        self.gamescope_force_grab_cursor = Gtk.Switch()
        self.gamescope_force_grab_cursor.set_valign(Gtk.Align.CENTER)
        self.gamescope_force_grab_cursor.set_halign(Gtk.Align.START)
        self.gamescope_force_grab_cursor.set_active(
            bool(features.get("gamescope_force_grab_cursor", True))
        )
        self.gamescope_force_grab_cursor.set_tooltip_text(
            tr("gamescope_force_grab_cursor_tooltip")
            or "Utilise toujours le mode souris relatif "
               "(--force-grab-cursor)."
        )

        self.gamescope_fsr_row = self._row(
            tr("gamescope_fsr") or "Activer l'upscaling FSR",
            self.gamescope_fsr,
        )
        self.gamescope_fps_limit_row = self._row(
            tr("gamescope_fps_limit")
            or "Limiteur de taux de rafraîchissement",
            self.gamescope_fps_limit,
        )
        self.gamescope_force_grab_cursor_row = self._row(
            tr("gamescope_force_grab_cursor")
            or "Forcer la capture du curseur",
            self.gamescope_force_grab_cursor,
        )

        # Aligne les contrôles de l'accordéon en colonne, quelle que soit
        # la longueur des libellés traduits.
        _gs_label_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        for _gs_row in (
            self.gamescope_internal_row,
            self.gamescope_output_row,
            self.gamescope_fsr_row,
            self.gamescope_fps_limit_row,
            self.gamescope_force_grab_cursor_row,
        ):
            _gs_label_group.add_widget(_gs_row.get_first_child())

        self.gamescope_settings = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )
        self.gamescope_settings.set_margin_start(12)
        self.gamescope_settings.set_margin_top(2)
        self.gamescope_settings.set_margin_bottom(4)
        self.gamescope_settings.append(self.gamescope_internal_row)
        self.gamescope_settings.append(self.gamescope_output_row)
        self.gamescope_settings.append(self.gamescope_fsr_row)
        self.gamescope_settings.append(self.gamescope_fps_limit_row)
        self.gamescope_settings.append(self.gamescope_force_grab_cursor_row)

        # Accordéon : les champs ne sont visibles que si Gamescope est activé.
        self.gamescope_revealer = Gtk.Revealer()
        self.gamescope_revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_DOWN
        )
        self.gamescope_revealer.set_transition_duration(200)
        self.gamescope_revealer.set_child(self.gamescope_settings)

        self.gamescope.connect(
            "notify::active",
            lambda *_args: self._update_gamescope_settings_visibility(),
        )
        self.gamescope_revealer.connect(
            "notify::child-revealed",
            lambda *_args: self._on_gamescope_revealer_done(),
        )
        # État initial sans animation.
        _gs_active = self.gamescope.get_active()
        self.gamescope_revealer.set_visible(_gs_active)
        self.gamescope_revealer.set_reveal_child(_gs_active)

        # INHIBIT SLEEP (verrou anti-veille) — n'a d'effet que si le
        # mode global (Réglages > Comportement) est réglé sur
        # "Par jeu" ; sinon "Jamais"/"Toujours" prime sur ce toggle.
        self.inhibit_sleep = adw_rows.new_switch(
            tr("enable_inhibit_sleep") or "Empêcher la mise en veille",
            features.get("inhibit_sleep", False),
        )
        self.inhibit_sleep.set_tooltip_text(
            tr("inhibit_sleep_tooltip")
            or "Empêche l'écran de s'éteindre et la mise en veille pendant "
               "que ce jeu tourne. N'a d'effet que si le mode global "
               "(Réglages > Comportement) est réglé sur « Par jeu »."
        )

        # SAVE BACKUP PROMPT (détection de sauvegardes en fin de session)
        # Activé par défaut : contrairement à inhibit_sleep, c'est une
        # fonctionnalité de protection des données, pas une préférence de
        # confort — on préfère prévenir l'utilisateur par défaut et le
        # laisser désactiver au cas par cas.
        self.save_backup_prompt = adw_rows.new_switch(
            tr("enable_save_backup_prompt") or "Proposer une sauvegarde en fin de partie",
            features.get("save_backup_prompt", True),
        )
        self.save_backup_prompt.set_tooltip_text(
            tr("save_backup_prompt_tooltip")
            or "À la fermeture du jeu, proton-autogen détecte si les "
               "fichiers de sauvegarde ont changé et propose de les "
               "sauvegarder. Désactivez si ce jeu ne sauvegarde pas de "
               "façon détectable ou si vous ne voulez pas être sollicité."
        )

        # MEMORY (bouton) — ouvre immédiatement le gestionnaire de
        # sauvegardes pour ce jeu : backup manuel + historique des
        # sauvegardes précédentes. Volontairement à côté du toggle
        # ci-dessus : l'un contrôle la détection automatique en fin de
        # partie, l'autre donne un accès direct et à la demande.
        self.memory_btn = Gtk.Button(label=tr("memory_button") or "🧠 Memory")
        self.memory_btn.add_css_class("section-toggle")
        self.memory_btn.set_tooltip_text(
            tr("memory_button_tooltip")
            or "Ouvre le gestionnaire de sauvegardes de ce jeu : "
               "sauvegarder maintenant ou retrouver vos sauvegardes "
               "précédentes."
        )
        self.memory_btn.connect("clicked", self._on_memory_clicked)

        if USE_ADW:
            self.memory_btn.set_valign(Gtk.Align.CENTER)
            self.save_backup_prompt.add_suffix(self.memory_btn)
            save_backup_row = self.save_backup_prompt
        else:
            save_backup_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            save_backup_row.append(self.save_backup_prompt)
            save_backup_row.append(self.memory_btn)

        # -------------------------
        # GPU MODE
        # -------------------------
        self.gpu = Gtk.DropDown.new_from_strings(self.gpu_model)

        current_gpu = features.get("gpu", "auto")

        if current_gpu in self.gpu_model:
            self.gpu.set_selected(self.gpu_model.index(current_gpu))

        set_tooltip(self.gpu, "gpu", self.lang)

        page_prefs.append(self._row("GPU Mode", self.gpu))

        # Favori : onglet « Préférences » (sous le mode GPU)
        if USE_ADW:
            favorite_list = adw_rows.new_switch_list()
            adw_rows.list_add(favorite_list, self.favorite)
            page_prefs.append(favorite_list)
        else:
            page_prefs.append(self.favorite)

        # Onglet « Réglages avancés »
        if USE_ADW:
            # Liste scindée en deux pour loger l'accordéon Gamescope
            # directement sous son interrupteur.
            switches = adw_rows.new_switch_list()
            for row in (self.mangohud, self.gamemode, self.gamescope):
                adw_rows.list_add(switches, row)
            page_advanced.append(switches)

            page_advanced.append(self.gamescope_revealer)

            switches_after = adw_rows.new_switch_list()
            for row in (self.inhibit_sleep, save_backup_row):
                adw_rows.list_add(switches_after, row)
            page_advanced.append(switches_after)
        else:
            page_advanced.append(self.mangohud)
            page_advanced.append(self.fps_limit_row)
            page_advanced.append(self.gamemode)
            page_advanced.append(self.gamescope)
            page_advanced.append(self.gamescope_revealer)
            page_advanced.append(self.inhibit_sleep)
            page_advanced.append(save_backup_row)

        # -------------------------
        # CUSTOM ENVIRONMENT VARIABLES
        # -------------------------
        env_label = Gtk.Label(label=tr("custom_env_label"), xalign=0)
        env_label.add_css_class("form-label")
        env_label.set_hexpand(True)

        env_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        env_header.append(env_label)
        env_header.append(self._build_env_search_button())
        page_expert.append(env_header)

        custom_env = self._existing_custom_env()
        env_text = "\n".join(f"{k}={v}" for k, v in custom_env.items())

        self.env_buffer = Gtk.TextBuffer()
        self.env_buffer.set_text(env_text)

        # ---------------------------------------------------------
        # CUSTOM ENVIRONMENT VARIABLES - SYNTAX HIGHLIGHTING
        # ---------------------------------------------------------

        # Variable connue dans ENV_VARS
        self.env_known_tag = self.env_buffer.create_tag(
            "env-known",
            foreground="#78A9FF",
        )

        self.env_buffer.connect(
            "changed",
            self._highlight_custom_env,
        )

        # Première coloration
        self._highlight_custom_env(self.env_buffer)


        self.env_view = Gtk.TextView(buffer=self.env_buffer)
        self.env_view.add_css_class("editor-env-view")
        self.env_view.set_monospace(True)
        set_tooltip(self.env_view, "custom_env", self.lang)
        self._setup_env_hover_tooltip()

        env_scroll = Gtk.ScrolledWindow()
        env_scroll.set_min_content_height(160)
        env_scroll.set_vexpand(True)
        env_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        env_scroll.set_child(self.env_view)
        page_expert.append(env_scroll)

        self.env_error_label = Gtk.Label(xalign=0)
        self.env_error_label.add_css_class("error-label")
        self.env_error_label.set_visible(False)
        page_expert.append(self.env_error_label)

        # -------------------------
        # SAVE BUTTON
        # -------------------------
        save_btn = Gtk.Button(label=tr("save_configuration"))
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self.on_save)

        root.append(save_btn)

    # -------------------------
    # TABS HELPERS
    # -------------------------
    @staticmethod
    def _new_tab_page():
        """Colonne verticale qui contient les champs d'un onglet."""
        return Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=12,
            margin_bottom=12,
            margin_start=12,
            margin_end=12,
        )

    @staticmethod
    def _wrap_tab_page(page):
        """Enveloppe une page dans un défilement vertical (si trop haute)."""
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)
        scroller.set_child(page)
        return scroller

    # -------------------------
    # GAMESCOPE RESOLUTION HELPERS
    # -------------------------
    @staticmethod
    def _build_gamescope_resolutions():
        """Liste (libellé, valeur) : « Automatique » traduit + résolutions fixes."""
        auto_label = (
            tr("gamescope_resolution_auto")
            or "Automatique (détection de l'écran)"
        )
        return [(auto_label, "auto")] + list(GAMESCOPE_FIXED_RESOLUTIONS)

    def _select_gamescope_resolution(self, dropdown, value):
        """Sélectionne la résolution enregistrée, ou Automatique si inconnue."""
        values = [
            resolution for _label, resolution in self.gamescope_resolutions
        ]

        try:
            index = values.index(value)
        except ValueError:
            index = 0

        dropdown.set_selected(index)

    def _get_gamescope_resolution(self, dropdown):
        """Renvoie la valeur enregistrable de la résolution sélectionnée."""
        index = dropdown.get_selected()

        if index >= len(self.gamescope_resolutions):
            return "auto"

        return self.gamescope_resolutions[index][1]

    def _update_gamescope_settings_visibility(self):
        """Déplie / replie les champs Gamescope selon l'interrupteur."""
        if self.gamescope.get_active():
            self.gamescope_revealer.set_visible(True)
            self.gamescope_revealer.set_reveal_child(True)
        else:
            self.gamescope_revealer.set_reveal_child(False)

    def _on_gamescope_revealer_done(self):
        """Une fois replié, masque le Revealer pour supprimer l'espacement."""
        if (not self.gamescope_revealer.get_reveal_child()
                and not self.gamescope_revealer.get_child_revealed()):
            self.gamescope_revealer.set_visible(False)

    # -------------------------
    # SHOW PROTONDB
    # -------------------------
    def on_show_protondb(self, btn):
        app_id = self.app_id_entry.get_text().strip() or self.game.get("app_id")
        if not app_id:
            return

        # Peuple game["protondb"] (thread + cache, côté Dashboard) pour
        # que le badge apparaisse dans la liste au prochain refresh.
        if self.on_protondb_requested:
            self.on_protondb_requested(self.game)

        Gtk.UriLauncher(uri=f"https://www.protondb.com/app/{app_id}").launch(self, None, None)

    # -------------------------
    # COVER (vue Bibliothèque)
    # -------------------------
    def _build_cover_row(self):
        self.cover_preview = Gtk.Picture()
        self.cover_preview.set_size_request(64, 96)
        self.cover_preview.set_content_fit(Gtk.ContentFit.COVER)
        self.cover_preview.add_css_class("editor-cover-preview")

        choose_btn = Gtk.Button(label=tr("cover_choose") or "Choisir une image…")
        choose_btn.add_css_class("section-toggle")
        choose_btn.connect("clicked", self._on_cover_choose)

        self.cover_clear_btn = Gtk.Button(label=tr("cover_remove") or "Retirer l'image")
        self.cover_clear_btn.add_css_class("section-toggle")
        self.cover_clear_btn.connect("clicked", self._on_cover_clear)

        buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        buttons.set_valign(Gtk.Align.CENTER)
        buttons.append(choose_btn)
        buttons.append(self.cover_clear_btn)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_tooltip_text(
            tr("cover_tooltip")
            or "Image affichée dans la vue Bibliothèque. Format conseillé : "
               "portrait 2:3 (l'image est recadrée au centre)."
        )
        box.append(self.cover_preview)
        box.append(buttons)

        self.cover_hint = Gtk.Label(xalign=0)
        self.cover_hint.add_css_class("error-label")
        self.cover_hint.set_visible(False)

        self._refresh_cover_preview()

        return self._row(tr("cover_label") or "Cover", box)

    def _displayed_cover(self):
        """Chemin de l'image à montrer dans l'aperçu (ou None)."""
        if self._cover_removed:
            return None
        return self._cover_new_src or self._cover_current

    def _refresh_cover_preview(self):
        path = self._displayed_cover()
        texture = None

        if path and os.path.isfile(path):
            texture = cover_manager.load_texture_sync(path, 64, 96)

        self.cover_preview.set_paintable(texture)
        self.cover_clear_btn.set_sensitive(bool(path))

    def _on_cover_choose(self, _btn):
        image_filter = Gtk.FileFilter()
        image_filter.set_name(tr("cover_filter_images") or "Images")
        image_filter.add_pixbuf_formats()

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(image_filter)

        dialog = Gtk.FileDialog()
        dialog.set_title(tr("cover_choose") or "Choisir une image…")
        dialog.set_filters(filters)
        dialog.set_default_filter(image_filter)
        dialog.open(self, None, self._on_cover_chosen)

    def _on_cover_chosen(self, dialog, result):
        try:
            gfile = dialog.open_finish(result)
        except GLib.Error:
            return  # dialogue fermé sans choix

        path = gfile.get_path() if gfile else None
        if not path:
            return

        if not cover_manager.is_supported_image(path):
            self.cover_hint.set_text(
                "⚠ " + (tr("cover_invalid") or "Image non supportée ou illisible")
            )
            self.cover_hint.set_visible(True)
            return

        self.cover_hint.set_visible(False)
        self._cover_new_src = path
        self._cover_removed = False
        self._refresh_cover_preview()

    def _on_cover_clear(self, _btn):
        self.cover_hint.set_visible(False)
        self._cover_new_src = None
        self._cover_removed = True
        self._refresh_cover_preview()

    def _resolve_cover_for_save(self):
        """
        Applique le choix de jaquette et retourne le chemin à enregistrer
        (None = aucune jaquette). En cas d'échec d'import, l'ancienne
        jaquette est conservée.
        """
        previous = self._cover_current

        if self._cover_removed:
            cover_manager.remove_cover(previous)
            return None

        if self._cover_new_src:
            stored = cover_manager.import_cover(
                self._cover_new_src, self.game["path"]
            )
            if stored:
                if previous and previous != stored:
                    cover_manager.remove_cover(previous)
                return stored

        return previous

    # -------------------------
    # MEMORY (gestionnaire de sauvegardes)
    # -------------------------
    def _on_memory_clicked(self, _btn):
        if self.on_memory_requested:
            self.on_memory_requested(self.game)

    # -------------------------
    # MANGOHUD / FPS LIMIT
    # -------------------------
    def on_mangohud_toggled(self, checkbutton):
        self.fps_limit_row.set_sensitive(checkbutton.get_active())
    # -------------------------
    # PROTONDB BOUTON VISIBLE
    # -------------------------
    def _on_app_id_changed(self, entry):
        self.protondb_btn.set_visible(bool(entry.get_text().strip()))

    # -------------------------
    # CUSTOM ENV HELPERS
    # -------------------------
    def _highlight_custom_env(self, buffer: Gtk.TextBuffer) -> None:
        """
        Colorie les noms de variables d'environnement connues.

        Une variable présente dans ENV_VARS est affichée avec la couleur
        env-known. Les variables inconnues utilisent env-unknown.
        """
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()

        # Supprime les anciennes couleurs
        buffer.remove_tag(
            self.env_known_tag,
            start,
            end,
        )

        text = buffer.get_text(start, end, False)

        offset = 0

        for raw_line in text.splitlines(True):
            line = raw_line.rstrip("\r\n")

            if not line.strip() or line.lstrip().startswith("#"):
                offset += len(raw_line)
                continue

            if "=" not in line:
                offset += len(raw_line)
                continue

            key, _, _ = line.partition("=")
            key = key.strip()

            if not key:
                offset += len(raw_line)
                continue

            # Position réelle du KEY dans le TextBuffer.
            key_start_offset = offset + (
                len(key) - len(key.lstrip())
            )

            key_end_offset = key_start_offset + len(key)

            key_start = buffer.get_iter_at_offset(
                key_start_offset
            )
            key_end = buffer.get_iter_at_offset(
                key_end_offset
            )

            if key in ENV_VARS_BY_NAME:
                buffer.apply_tag(
                    self.env_known_tag,
                    key_start,
                    key_end,
                )


            offset += len(raw_line)

    # -------------------------
    # RECHERCHE DE VARIABLES (bouton + popover)
    # -------------------------
    def _build_env_search_button(self) -> Gtk.MenuButton:
        """Bouton "Rechercher une variable" : ouvre une liste filtrable de
        toutes les variables connues avec leur description. Un clic sur une
        variable l'ajoute dans le champ (ou y place le curseur si elle y est
        déjà)."""
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        content.append(Gtk.Image.new_from_icon_name("system-search-symbolic"))
        content.append(Gtk.Label(label=tr("env_search_button")))

        button = Gtk.MenuButton()
        button.set_child(content)
        button.add_css_class("section-toggle")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_size_request(500, -1)

        self._env_search_entry = Gtk.SearchEntry()
        self._env_search_entry.set_placeholder_text(tr("env_search_placeholder"))
        box.append(self._env_search_entry)

        self._env_list = Gtk.ListBox()
        self._env_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._env_list.set_activate_on_single_click(True)
        self._env_list.set_filter_func(
            lambda row: _env_query_matches(
                self._env_search_entry.get_text(), row.search_text
            )
        )

        self._env_rows = []
        for name in sorted(ENV_VARS_BY_NAME):
            meta = ENV_VARS_BY_NAME[name]
            description = tr(meta["i18n"])

            title = Gtk.Label(xalign=0)
            title.set_markup(f"<b><tt>{GLib.markup_escape_text(name)}</tt></b>")

            desc = Gtk.Label(label=description, xalign=0)
            desc.set_wrap(True)
            desc.set_max_width_chars(60)
            desc.set_opacity(0.75)

            row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            row_box.set_margin_top(4)
            row_box.set_margin_bottom(4)
            row_box.append(title)
            row_box.append(desc)

            row = Gtk.ListBoxRow()
            row.set_child(row_box)
            row.env_name = name
            row.search_text = f"{name} {description}".lower()
            self._env_list.append(row)
            self._env_rows.append(row)

        self._env_scroll = Gtk.ScrolledWindow()
        self._env_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._env_scroll.set_min_content_height(320)
        self._env_scroll.set_child(self._env_list)
        box.append(self._env_scroll)

        self._env_empty_label = Gtk.Label(label=tr("env_search_no_result"))
        self._env_empty_label.set_opacity(0.75)
        self._env_empty_label.set_visible(False)
        box.append(self._env_empty_label)

        self._env_popover = Gtk.Popover()
        self._env_popover.set_child(box)
        button.set_popover(self._env_popover)

        self._env_search_entry.connect("search-changed", self._on_env_search_changed)
        self._env_search_entry.connect("activate", self._on_env_search_enter)
        self._env_search_entry.connect("next-match", lambda *_: self._env_move_selection(1))
        self._env_search_entry.connect("previous-match", lambda *_: self._env_move_selection(-1))
        self._env_search_entry.connect("stop-search", lambda *_: self._env_popover.popdown())
        self._env_list.connect("row-activated", self._on_env_row_activated)
        self._env_popover.connect("show", self._on_env_popover_show)

        return button

    def _env_visible_rows(self) -> list:
        query = self._env_search_entry.get_text()
        return [r for r in self._env_rows if _env_query_matches(query, r.search_text)]

    def _on_env_popover_show(self, _popover):
        self._env_search_entry.set_text("")
        self._env_search_entry.grab_focus()
        self._on_env_search_changed(self._env_search_entry)

    def _on_env_search_changed(self, _entry):
        self._env_list.invalidate_filter()
        visible = self._env_visible_rows()
        self._env_empty_label.set_visible(not visible)
        self._env_scroll.get_vadjustment().set_value(0)

        if visible:
            self._env_list.select_row(visible[0])
        else:
            self._env_list.unselect_all()

    def _env_move_selection(self, step: int):
        """Flèches haut/bas dans le champ de recherche : déplace la sélection
        parmi les résultats visibles et la garde dans la zone visible."""
        visible = self._env_visible_rows()
        if not visible:
            return

        current = self._env_list.get_selected_row()
        index = visible.index(current) if current in visible else -1
        row = visible[max(0, min(len(visible) - 1, index + step))]
        self._env_list.select_row(row)

        ok, rect = row.compute_bounds(self._env_list)
        if ok:
            adj = self._env_scroll.get_vadjustment()
            top, bottom = rect.get_y(), rect.get_y() + rect.get_height()
            if top < adj.get_value():
                adj.set_value(top)
            elif bottom > adj.get_value() + adj.get_page_size():
                adj.set_value(bottom - adj.get_page_size())

    def _on_env_search_enter(self, _entry):
        row = self._env_list.get_selected_row()
        if row is not None and row in self._env_visible_rows():
            self._insert_env_var(row.env_name)

    def _on_env_row_activated(self, _listbox, row):
        self._insert_env_var(row.env_name)

    def _insert_env_var(self, name: str) -> None:
        """Ajoute "NAME=" dans le champ, prêt à recevoir la valeur. Si la
        variable est déjà saisie, place simplement le curseur en fin de sa
        ligne au lieu de créer un doublon."""
        buf = self.env_buffer
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)

        offset = 0
        for line in text.split("\n"):
            key, sep, _ = line.partition("=")
            if sep and key.strip() == name:
                buf.place_cursor(buf.get_iter_at_offset(offset + len(line)))
                break
            offset += len(line) + 1
        else:
            prefix = "" if (not text or text.endswith("\n")) else "\n"
            buf.insert(buf.get_end_iter(), f"{prefix}{name}=")
            buf.place_cursor(buf.get_end_iter())

        self._env_popover.popdown()
        self.env_view.grab_focus()
        self.env_view.scroll_mark_onscreen(buf.get_insert())

    # -------------------------
    # DESCRIPTION AU SURVOL
    # -------------------------
    def _setup_env_hover_tooltip(self) -> None:
        """Affiche la description d'une variable connue quand la souris
        survole son nom dans le champ. Hors d'un nom connu, l'info-bulle
        générale du champ est restaurée."""
        self._env_default_tooltip = self.env_view.get_tooltip_text()
        self._env_hover_key = None

        motion = Gtk.EventControllerMotion()
        motion.connect("motion", self._on_env_view_motion)
        motion.connect("leave", lambda *_: self._set_env_hover_key(None))
        self.env_view.add_controller(motion)

    def _on_env_view_motion(self, _ctrl, x, y):
        bx, by = self.env_view.window_to_buffer_coords(
            Gtk.TextWindowType.WIDGET, int(x), int(y)
        )
        found, it = self.env_view.get_iter_at_position(bx, by)[:2]
        key = None

        if found:
            line_start = it.copy()
            line_start.set_line_offset(0)
            line_end = line_start.copy()
            if not line_end.ends_line():
                line_end.forward_to_line_end()

            line = self.env_buffer.get_text(line_start, line_end, False)
            name, sep, _ = line.partition("=")

            # Seulement quand le pointeur est sur le nom, pas sur la valeur.
            if sep and it.get_line_offset() <= len(name) and name.strip() in ENV_VARS_BY_NAME:
                key = name.strip()

        self._set_env_hover_key(key)

    def _set_env_hover_key(self, key) -> None:
        if key == self._env_hover_key:
            return
        self._env_hover_key = key

        if key:
            description = tr(ENV_VARS_BY_NAME[key]["i18n"])
            self.env_view.set_tooltip_markup(
                f"<b>{GLib.markup_escape_text(key)}</b>\n"
                f"{GLib.markup_escape_text(description)}"
            )
        else:
            self.env_view.set_tooltip_text(self._env_default_tooltip)

        self.env_view.trigger_tooltip_query()

    def _existing_custom_env(self) -> dict:
        """Variables d'environnement déjà enregistrées pour ce jeu,
        hors clés réservées."""
        env = self.game.get("env", {}) or {}
        return {
            k: v for k, v in env.items()
            if k not in RESERVED_ENV_KEYS
        }

    def _parse_custom_env(self) -> tuple[dict, list[str]]:
        """
        Parse le contenu du champ "variables d'environnement personnalisées".

        Format attendu : une variable par ligne, "KEY=VALUE".
        Les lignes vides et celles commençant par '#' sont ignorées.

        Returns:
            (env_dict, errors) où errors contient un message par ligne invalide.
        """
        start = self.env_buffer.get_start_iter()
        end = self.env_buffer.get_end_iter()
        raw_text = self.env_buffer.get_text(start, end, False)

        env = {}
        errors = []

        for line_no, raw_line in enumerate(raw_text.splitlines(), start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                errors.append(f"Line {line_no}: expected KEY=VALUE, got '{line}'")
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            if not key:
                errors.append(f"Line {line_no}: empty variable name")
                continue

            if not key.replace("_", "").isalnum() or key[0].isdigit():
                errors.append(f"Line {line_no}: invalid variable name '{key}'")
                continue

            if key in RESERVED_ENV_KEYS:
                errors.append(f"Line {line_no}: '{key}' is a reserved variable")
                continue

            env[key] = value

        return env, errors

    # -------------------------
    # UI HELPERS
    # -------------------------
    def _row(self, label_text, widget):

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=label_text, xalign=0)
        label.set_width_chars(12)
        label.add_css_class("form-label")

        row.append(label)
        row.append(widget)

        return row

    # -------------------------
    # SAVE LOGIC
    # -------------------------

    def on_save(self, _btn):

        # Valider les variables d'environnement personnalisées AVANT de
        # toucher quoi que ce soit : en cas d'erreur, on affiche le
        # problème et on annule la sauvegarde plutôt que d'écrire une
        # config à moitié invalide.
        custom_env, env_errors = self._parse_custom_env()

        if env_errors:
            self.env_error_label.set_text("⚠ " + " | ".join(env_errors))
            self.env_error_label.set_visible(True)
            # L'erreur s'affiche dans l'onglet « Réglages Expert » :
            # y basculer pour qu'elle soit visible.
            self.notebook.set_current_page(2)
            self.env_view.grab_focus()
            return

        self.env_error_label.set_visible(False)

        proton = ""
        if self.protons and self.proton.get_selected() >= 0:
            proton = self.protons[self.proton.get_selected()]

        exe_type = self.profile_model[self.profile.get_selected()] if self.profile.get_selected() >= 0 else "dx11"
        prefix = self.prefix_model[self.prefix.get_selected()] if self.prefix.get_selected() >= 0 else "main"

        gpu = (
            self.gpu_model[self.gpu.get_selected()]
            if self.gpu.get_selected() >= 0
            else "auto"
        )
        cover_image = self._resolve_cover_for_save()

        data = self.game.copy()

        features = self.game.get("features", {}).copy()

        features.update({
            "mangohud": self.mangohud.get_active(),
            "fps_limit": int(self.fps_limit.get_value()),
            "gamemode": self.gamemode.get_active(),
            "gamescope": self.gamescope.get_active(),
            "gamescope_internal_resolution": self._get_gamescope_resolution(
                self.gamescope_internal_resolution
            ),
            "gamescope_output_resolution": self._get_gamescope_resolution(
                self.gamescope_output_resolution
            ),
            "gamescope_fsr": self.gamescope_fsr.get_active(),
            "gamescope_fps_limit": int(
                self.gamescope_fps_limit.get_value()
            ),
            "gamescope_force_grab_cursor":
                self.gamescope_force_grab_cursor.get_active(),
            "inhibit_sleep": self.inhibit_sleep.get_active(),
            "save_backup_prompt": self.save_backup_prompt.get_active(),
            "gpu": gpu
        })

        # Le champ "variables d'environnement" affiché à l'utilisateur est
        # la source de vérité : ce qui est écrit dedans (déjà validé et
        # filtré des clés réservées par _parse_custom_env) devient le
        # contenu final de data["env"].
        env = dict(custom_env)

        data.update({
            "path": self.game["path"],
            "name": self.game.get("name"),
            "favorite": self.favorite.get_active(),
            "exe_type": exe_type,
            "proton": proton,
            "prefix": {
                "name": prefix
            },
            "app_id": self.app_id_entry.get_text().strip() or None,
            "cover_image": cover_image,
            "features": features,
            "env": env,
        })

        # "protondb" contient un objet ProtonDBInfo : converti en dict
        # simple (JSON-sérialisable) avant sauvegarde. list_programs_ux()
        # le reconstruit en ProtonDBInfo au chargement suivant.
        protondb = data.get("protondb")
        if protondb is not None:
            data["protondb"] = protondb.to_dict() if hasattr(protondb, "to_dict") else protondb


        save_game_config(data)

        if self.on_saved:
            self.on_saved(data)

        self.close()
