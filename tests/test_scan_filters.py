"""scan_filters : dossiers ignorés par la recherche d'exécutables — sans GTK."""

import pytest

from proton_autogen import backend
from proton_autogen.utils import scan_filters
from proton_autogen.utils.scan_filters import (
    DEFAULT_EXCLUDED_DIRS,
    EXCLUDED_DIR_CATEGORIES,
    apply_rules,
    get_excluded_dirs,
    parse_user_rules,
)

pytestmark = pytest.mark.unit


# Ancien ensemble de backend.py, recopié TEL QUEL (y compris la virgule oubliée
# après "eclipse-installer", qui fusionnait deux noms en un seul).
_OLD_EXCLUDED_DIRS = {
    # cache / temp
    ".cache", "cache", "tmp", ".tmp", "temp", ".temp", "appcache", ".cargo", '.config', "configs",
    # dev
    "__pycache__", "node_modules", ".git", ".svn", "JAVA", "www", ".gnupg", ".p2", ".rpmdb", ".rustup", ".ssh", ".var", ".vnc", ".nuget", ".omnisharp", ".m2", ".pki", ".lime", ".java",
    ".eclipse", ".fltk", ".fonts", ".dotnet", ".dbus", ".config", ".icons", ".conky", ".swt", ".templateengine", ".themes", ".thunderbird", ".npm", ".gvfs",
    ".uno", "pipeline", "eclipse-workspace", "eclipse-installer"
    # personnal
    "Musique", "Modèles", "Images", "customFiles", "docs", "bsa", "pdf", "Serene-Conky", ".mozilla", "os", ".wavemonrc", "steal",

    # gaming
    ".steam", "dgVoodoo2", "deb-installer", "depotcache", "friends", "linux64", "linux32",

    # steam apps
    "steamui", "steamrt64", "steamrt32", "userdata", "ubuntu12_32", "ubuntu12_64", "resource", "package", "root", "sdk64", "bin64", "bin32", "bin", "clientui", "controller_base",

    # Proton
    "compatibilitytools.d",

    # backups
    "backup", "backups", "old", "recovery", "stockages", "zip", "tar", "Vidéos", "Modèles",

    # misc noise
    "drivers", "bios", "logs", "log", "old", "tmp", "www", "mail", "personnel", "virus", "malware",
}

# Les deux seuls noms dont le comportement change : la virgule oubliée les
# avait fusionnés en "eclipse-installerMusique" (donc aucun des deux n'était
# réellement ignoré).
_FIXED_BY_COMMA = {"eclipse-installer", "Musique"}

# Nom fantôme produit par la même virgule oubliée : aucun dossier réel ne
# s'appelle ainsi, il disparaît de l'ensemble.
_FUSED_NAME = "eclipse-installerMusique"


def _old_skips(name):
    """Prédicat de la boucle de scan d'origine."""
    return name in _OLD_EXCLUDED_DIRS or name.startswith(".")


def _new_skips(name, excluded=DEFAULT_EXCLUDED_DIRS):
    """Prédicat de la boucle de scan (inchangée dans backend.py)."""
    return name in excluded or name.startswith(".")


# --- l'ensemble par défaut --------------------------------------------------

def test_la_virgule_oubliee_fusionnait_deux_noms():
    assert _FUSED_NAME in _OLD_EXCLUDED_DIRS
    assert "eclipse-installer" not in _OLD_EXCLUDED_DIRS
    assert "Musique" not in _OLD_EXCLUDED_DIRS


def test_comportement_identique_sauf_les_deux_noms_corriges():
    names = set(_OLD_EXCLUDED_DIRS) | set(DEFAULT_EXCLUDED_DIRS) | {
        "Game", "Jeux", "Bin", "Resource", "Cache", ".hidden", "bin", "x", "",
        "eclipse-installerMusique",
    }

    for name in names:
        if name in _FIXED_BY_COMMA:
            assert _old_skips(name) is False
            assert _new_skips(name) is True, name
        elif name == _FUSED_NAME:
            assert _old_skips(name) is True
            assert _new_skips(name) is False
        else:
            assert _old_skips(name) == _new_skips(name), name


def test_aucune_entree_perdue_hors_dossiers_caches():
    lost = {
        n for n in _OLD_EXCLUDED_DIRS
        if not n.startswith(".") and n != _FUSED_NAME
    } - set(DEFAULT_EXCLUDED_DIRS)
    assert lost == set()


def test_chaque_nom_n_apparait_qu_une_fois():
    flat = [n for names in EXCLUDED_DIR_CATEGORIES.values() for n in names]
    duplicates = sorted({n for n in flat if flat.count(n) > 1})
    assert duplicates == []


def test_aucun_nom_de_dossier_cache_dans_les_defauts():
    # Déjà couverts par la règle générale « nom commençant par un point ».
    assert [n for n in DEFAULT_EXCLUDED_DIRS if n.startswith(".")] == []


def test_noms_valides():
    for n in DEFAULT_EXCLUDED_DIRS:
        assert n and n == n.strip() and "/" not in n, repr(n)


def test_les_defauts_sont_immuables():
    assert isinstance(DEFAULT_EXCLUDED_DIRS, frozenset)


# --- fichier utilisateur ----------------------------------------------------

def test_parse_ajouts_retraits_et_commentaires():
    text = """
    # commentaire complet
    MesFilms            # commentaire en fin de ligne
    Backups/
      -bin
    -  Resource

    -
    chemin/interdit
    """
    assert parse_user_rules(text) == [
        ("add", "MesFilms"),
        ("add", "Backups"),
        ("remove", "bin"),
        ("remove", "Resource"),
    ]


def test_un_diese_dans_un_nom_sans_espace_est_conserve():
    assert parse_user_rules("Jeux#1\n") == [("add", "Jeux#1")]


def test_les_regles_sont_appliquees_dans_l_ordre():
    assert "X" in apply_rules(set(), [("remove", "X"), ("add", "X")])
    assert "X" not in apply_rules(set(), [("add", "X"), ("remove", "X")])


def test_retirer_un_nom_absent_ne_plante_pas():
    assert apply_rules({"a"}, [("remove", "zzz")]) == frozenset({"a"})


def test_fichier_absent_renvoie_les_defauts(tmp_path):
    assert get_excluded_dirs(tmp_path / "nope.txt") is DEFAULT_EXCLUDED_DIRS


def test_fichier_vide_ou_commentaires_seuls_renvoie_les_defauts(tmp_path):
    f = tmp_path / "scan-excludes.txt"
    f.write_text("# rien\n\n", encoding="utf-8")
    assert get_excluded_dirs(f) == DEFAULT_EXCLUDED_DIRS


def test_ajout_et_retrait_via_fichier(tmp_path):
    f = tmp_path / "scan-excludes.txt"
    f.write_text("MesFilms\n-bin\n", encoding="utf-8")

    excluded = get_excluded_dirs(f)

    assert "MesFilms" in excluded
    assert "bin" not in excluded
    assert "resource" in excluded                       # le reste est intact
    assert excluded - {"MesFilms"} == DEFAULT_EXCLUDED_DIRS - {"bin"}


def test_fichier_mal_encode_ne_casse_rien(tmp_path):
    f = tmp_path / "scan-excludes.txt"
    f.write_bytes(b"\xff\xfe\x00bad")
    assert get_excluded_dirs(f) == DEFAULT_EXCLUDED_DIRS


def test_chemin_qui_est_un_dossier_ne_casse_rien(tmp_path):
    assert get_excluded_dirs(tmp_path) == DEFAULT_EXCLUDED_DIRS


def test_le_fichier_par_defaut_est_lu_a_l_appel(tmp_path, monkeypatch):
    f = tmp_path / "scan-excludes.txt"
    f.write_text("Perso\n", encoding="utf-8")
    monkeypatch.setattr(scan_filters, "USER_EXCLUDES_FILE", f)

    assert "Perso" in get_excluded_dirs()


# --- intégration avec la vraie recherche -----------------------------------

@pytest.fixture
def tree(tmp_path, monkeypatch):
    """Arborescence de test + fichier utilisateur redirigé vers tmp_path."""
    for rel in (
        "Jeux/Game/game.exe",
        "Jeux/Game/bin/inner.exe",          # « bin » : ignoré par défaut
        "Jeux/Game/resource/low.exe",       # « resource » : ignoré par défaut
        "Jeux/Game/Resource/Cap.exe",       # « Resource » : casse différente => scanné
        "Jeux/Backups/saved.exe",           # « Backups » ≠ « backups » (sensible à la casse)
        "Jeux/backups/saved2.exe",
        "Jeux/MesFilms/film.exe",
        "Jeux/.hidden/h.exe",
        "Jeux/Game/setup.exe",              # ignoré par NOM de fichier
        "Jeux/Game/unins000.exe",           # ignoré (préfixe unins)
        "Téléchargements/dl.exe",
    ):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"MZ")

    user_file = tmp_path / "scan-excludes.txt"
    monkeypatch.setattr(scan_filters, "USER_EXCLUDES_FILE", user_file)
    backend.find_windows_programs_ux_search.cache_clear()
    yield tmp_path, user_file
    backend.find_windows_programs_ux_search.cache_clear()


def _found(tmp_path):
    backend.find_windows_programs_ux_search.cache_clear()
    found = backend.find_windows_programs_ux_search(tmp_path)
    return {p[len(str(tmp_path)) + 1:] for p in found}


def test_recherche_par_defaut(tree):
    tmp_path, _ = tree

    assert _found(tmp_path) == {
        "Jeux/Game/game.exe",
        "Jeux/Game/Resource/Cap.exe",
        "Jeux/Backups/saved.exe",
        "Jeux/MesFilms/film.exe",
        "Téléchargements/dl.exe",
    }


def test_retirer_un_nom_par_defaut_le_rend_visible(tree):
    tmp_path, user_file = tree
    user_file.write_text("-bin\n-resource\n", encoding="utf-8")

    found = _found(tmp_path)

    assert "Jeux/Game/bin/inner.exe" in found
    assert "Jeux/Game/resource/low.exe" in found


def test_ajouter_un_nom_le_masque(tree):
    tmp_path, user_file = tree
    user_file.write_text("MesFilms\n", encoding="utf-8")

    found = _found(tmp_path)

    assert "Jeux/MesFilms/film.exe" not in found
    assert "Jeux/Game/game.exe" in found


def test_les_dossiers_caches_restent_ignores_meme_si_retires(tree):
    tmp_path, user_file = tree
    user_file.write_text("-.hidden\n", encoding="utf-8")

    assert "Jeux/.hidden/h.exe" not in _found(tmp_path)


def test_fichier_utilisateur_illisible_ne_change_pas_la_recherche(tree):
    tmp_path, user_file = tree
    user_file.write_bytes(b"\xff\xfe\x00bad")

    assert "Jeux/Game/game.exe" in _found(tmp_path)
    assert "Jeux/Game/bin/inner.exe" not in _found(tmp_path)
