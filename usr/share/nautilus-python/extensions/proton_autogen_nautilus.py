"""Extension Nautilus : entrées de clic droit pour proton-autogen.

 - « Open with Proton-Autogen » : `proton-autogen <fichier>`
   (lance le programme ; sa configuration est créée au premier lancement)
 - « Add to Proton-Autogen »    : `proton-autogen addux <fichier>`
   (ajoute le programme et ouvre l'interface sur son éditeur)

Compatible nautilus-python 3.0 (Nautilus < 43) et 4.0 (GTK4, Nautilus >= 43).
"""
import os
import shutil
import subprocess

import gi

try:
    gi.require_version("Nautilus", "4.0")
except ValueError:
    gi.require_version("Nautilus", "3.0")

from gi.repository import GObject, Nautilus

EXTS = (".exe", ".msi", ".bat", ".lnk")

# Libellés du menu : (« Open with », « Add to »)
_LABELS = {
    "en": ("Open with Proton-Autogen", "Add to Proton-Autogen"),
    "bg": ("Отваряне с Proton-Autogen", "Добавяне към Proton-Autogen"),
    "de": ("Mit Proton-Autogen öffnen", "Zu Proton-Autogen hinzufügen"),
    "el": ("Άνοιγμα με το Proton-Autogen", "Προσθήκη στο Proton-Autogen"),
    "es": ("Abrir con Proton-Autogen", "Añadir a Proton-Autogen"),
    "fi": ("Avaa Proton-Autogenilla", "Lisää Proton-Autogeniin"),
    "fr": ("Exécuter avec Proton-Autogen", "Ajouter à Proton-Autogen"),
    "hi": ("Proton-Autogen के साथ खोलें", "Proton-Autogen में जोड़ें"),
    "hu": ("Megnyitás a Proton-Autogennel", "Hozzáadás a Proton-Autogenhez"),
    "it": ("Apri con Proton-Autogen", "Aggiungi a Proton-Autogen"),
    "ja": ("Proton-Autogenで開く", "Proton-Autogenに追加"),
    "ko": ("Proton-Autogen으로 열기", "Proton-Autogen에 추가"),
    "ku": ("Bi Proton-Autogen veke", "Li Proton-Autogen zêde bike"),
    "nl": ("Openen met Proton-Autogen", "Toevoegen aan Proton-Autogen"),
    "pl": ("Otwórz za pomocą Proton-Autogen", "Dodaj do Proton-Autogen"),
    "pt": ("Abrir com Proton-Autogen", "Adicionar ao Proton-Autogen"),
    "pt_BR": ("Abrir com Proton-Autogen", "Adicionar ao Proton-Autogen"),
    "ru": ("Открыть с помощью Proton-Autogen", "Добавить в Proton-Autogen"),
    "th": ("เปิดด้วย Proton-Autogen", "เพิ่มไปยัง Proton-Autogen"),
    "uk": ("Відкрити за допомогою Proton-Autogen", "Додати до Proton-Autogen"),
    "vi": ("Mở bằng Proton-Autogen", "Thêm vào Proton-Autogen"),
    "zh_CN": ("使用 Proton-Autogen 打开", "添加到 Proton-Autogen"),
    "zh_TW": ("使用 Proton-Autogen 開啟", "新增至 Proton-Autogen"),
}

# Variantes sans région vers la langue la plus probable.
_ALIASES = {"zh": "zh_CN"}


def _locale_candidates():
    """Locales demandées, dans l'ordre de priorité de gettext."""
    raw = os.environ.get("LANGUAGE", "").split(":")
    raw += [os.environ.get(v, "") for v in ("LC_ALL", "LC_MESSAGES", "LANG")]
    for value in raw:
        code = value.split(".")[0].split("@")[0].strip()
        if code and code not in ("C", "POSIX"):
            yield code
            if "_" in code:
                yield code.split("_")[0]


def _labels():
    for code in _locale_candidates():
        code = _ALIASES.get(code, code)
        if code in _LABELS:
            return _LABELS[code]
    return _LABELS["en"]


def _binary():
    return shutil.which("proton-autogen") or "/usr/bin/proton-autogen"


class ProtonAutogenExtension(GObject.GObject, Nautilus.MenuProvider):

    @staticmethod
    def _spawn(*args):
        # Liste d'arguments (jamais de shell) : chemins avec espaces sûrs.
        subprocess.Popen(
            [_binary(), *args],
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    def _on_run(self, _menu, path):
        self._spawn(path)

    def _on_addux(self, _menu, path):
        self._spawn("addux", path)

    def get_file_items(self, *args):
        # 3.0 : (window, files) ; 4.0 : (files,) -> la liste est toujours en dernier.
        files = args[-1]
        if len(files) != 1:
            return []

        f = files[0]
        if f.get_uri_scheme() != "file" or not f.get_name().lower().endswith(EXTS):
            return []

        path = f.get_location().get_path()
        label_run, label_add = _labels()

        run_item = Nautilus.MenuItem(
            name="ProtonAutogen::Open",
            label=label_run,
            tip="Run this Windows program (added to the library on first launch)",
        )
        run_item.connect("activate", self._on_run, path)

        add_item = Nautilus.MenuItem(
            name="ProtonAutogen::AddUx",
            label=label_add,
            tip="Add this program to Proton-Autogen and open it in the interface",
        )
        add_item.connect("activate", self._on_addux, path)

        return [run_item, add_item]
