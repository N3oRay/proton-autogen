#!/usr/bin/env python3
#game_editor.py
import gi
import os
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk


from proton_autogen.backend import save_game_config
from proton_autogen.backend import find_all_protons
from proton_autogen.desc import set_tooltip
from proton_autogen.editor import list_prefixes_ux
from proton_autogen.profiles.init import VALID_PROFILES
from proton_autogen.i18n import tr

# Valeur par défaut appliquée quand MangoHud est activé sans fps_limit défini
DEFAULT_FPS_LIMIT = 60

# Clés déjà gérées ailleurs dans l'éditeur : on ne les propose pas dans le
# champ "variables d'environnement personnalisées" pour éviter les doublons
# / conflits avec la logique interne (prefix, mangohud, gpu...).
RESERVED_ENV_KEYS = set()

# -----------------------------
# GAME EDITOR WINDOW
# -----------------------------
class GameEditor(Gtk.Window):

    def __init__(self, app, game, lang):
        super().__init__(application=app)
        self.set_title("Edit Game Profile")
        self.set_default_size(520, 420)
        #self.set_resizable(True)
        self.on_saved = None
        self.on_protondb_requested = None   # 👈 nouveau
        self.set_size_request(520, 420)
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
        # PROFILE SELECT
        # -------------------------
        self.profile = Gtk.DropDown.new_from_strings(self.profile_model)
        set_tooltip(self.profile, "profile", self.lang) # new

        current_profile = self.game.get("exe_type", "dx11")

        if current_profile in self.profile_model:
            self.profile.set_selected(self.profile_model.index(current_profile))

        root.append(self._row("Profile", self.profile))

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

        root.append(self._row("Proton", self.proton))

        # -------------------------
        # PREFIX MODE
        # -------------------------
        self.prefix = Gtk.DropDown.new_from_strings(self.prefix_model)
        set_tooltip(self.prefix, "prefix", self.lang)

        current_prefix = self.game.get("prefix", {}).get("name", "main")


        if current_prefix in self.prefix_model:
            self.prefix.set_selected(self.prefix_model.index(current_prefix))
        root.append(self._row("Prefix", self.prefix))

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
        root.append(app_id_row)

        # État initial : bouton visible seulement si un AppID est déjà renseigné
        self._on_app_id_changed(self.app_id_entry)

        # -------------------------
        # TOGGLES
        # -------------------------
        features = self.game.get("features", {})

        # FAVORITE
        self.favorite = Gtk.CheckButton(label=tr("add_to_favorites"))
        self.favorite.add_css_class("feature-toggle")
        self.favorite.set_active(
            self.game.get("favorite", False)
        )

        set_tooltip(self.favorite, "favorite", self.lang)
        # MANGO
        self.mangohud = Gtk.CheckButton(label=tr("enable_mangohud"))
        self.mangohud.add_css_class("feature-toggle")
        self.mangohud.set_active(features.get("mangohud", False))
        set_tooltip(self.mangohud, "mangohud", self.lang)  #new code
        self.mangohud.connect("toggled", self.on_mangohud_toggled)

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

        self.fps_limit_row = self._row("FPS limit", self.fps_limit)
        self.fps_limit_row.set_sensitive(self.mangohud.get_active())
        # GAMEMODE
        self.gamemode = Gtk.CheckButton(label=tr("enable_gamemode"))
        self.gamemode.add_css_class("feature-toggle")
        self.gamemode.set_active(features.get("gamemode", False))
        set_tooltip(self.gamemode, "gamemode", self.lang) #new code
        # GAMESCOPE
        self.gamescope = Gtk.CheckButton(label=tr("enable_gamescope"))
        self.gamescope.add_css_class("feature-toggle")
        self.gamescope.set_active(features.get("gamescope", False))
        set_tooltip(self.gamescope, "gamescope", self.lang)

        # INHIBIT SLEEP (verrou anti-veille) — n'a d'effet que si le
        # mode global (Réglages > Comportement) est réglé sur
        # "Par jeu" ; sinon "Jamais"/"Toujours" prime sur ce toggle.
        self.inhibit_sleep = Gtk.CheckButton(
            label=tr("enable_inhibit_sleep") or "Empêcher la mise en veille"
        )
        self.inhibit_sleep.add_css_class("feature-toggle")
        self.inhibit_sleep.set_active(features.get("inhibit_sleep", False))
        self.inhibit_sleep.set_tooltip_text(
            tr("inhibit_sleep_tooltip")
            or "Empêche l'écran de s'éteindre et la mise en veille pendant "
               "que ce jeu tourne. N'a d'effet que si le mode global "
               "(Réglages > Comportement) est réglé sur « Par jeu »."
        )


        # -------------------------
        # GPU MODE
        # -------------------------
        self.gpu = Gtk.DropDown.new_from_strings(self.gpu_model)

        current_gpu = features.get("gpu", "auto")

        if current_gpu in self.gpu_model:
            self.gpu.set_selected(self.gpu_model.index(current_gpu))

        set_tooltip(self.gpu, "gpu", self.lang)

        root.append(self._row("GPU Mode", self.gpu))

        root.append(self.favorite)
        root.append(self.mangohud)
        root.append(self.fps_limit_row)
        root.append(self.gamemode)
        root.append(self.gamescope)
        root.append(self.inhibit_sleep)

        # -------------------------
        # CUSTOM ENVIRONMENT VARIABLES
        # -------------------------
        env_label = Gtk.Label(label=tr("custom_env_label"), xalign=0)
        env_label.add_css_class("form-label")
        root.append(env_label)

        custom_env = self._existing_custom_env()
        env_text = "\n".join(f"{k}={v}" for k, v in custom_env.items())

        self.env_buffer = Gtk.TextBuffer()
        self.env_buffer.set_text(env_text)

        self.env_view = Gtk.TextView(buffer=self.env_buffer)
        self.env_view.add_css_class("editor-env-view")
        self.env_view.set_monospace(True)
        set_tooltip(self.env_view, "custom_env", self.lang)

        env_scroll = Gtk.ScrolledWindow()
        env_scroll.set_min_content_height(90)
        env_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        env_scroll.set_child(self.env_view)
        root.append(env_scroll)

        self.env_error_label = Gtk.Label(xalign=0)
        self.env_error_label.add_css_class("error-label")
        self.env_error_label.set_visible(False)
        root.append(self.env_error_label)

        # -------------------------
        # SAVE BUTTON
        # -------------------------
        save_btn = Gtk.Button(label=tr("save_configuration"))
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self.on_save)

        root.append(save_btn)

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
        data = self.game.copy()

        features = self.game.get("features", {}).copy()

        features.update({
            "mangohud": self.mangohud.get_active(),
            "fps_limit": int(self.fps_limit.get_value()),
            "gamemode": self.gamemode.get_active(),
            "gamescope": self.gamescope.get_active(),
            "inhibit_sleep": self.inhibit_sleep.get_active(),
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
