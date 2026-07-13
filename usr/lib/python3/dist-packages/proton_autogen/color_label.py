from rich.text import Text

import re
from gi.repository import Pango

def insert_changelog_text(buffer, text):

    tag_table = buffer.get_tag_table()

    def tag(name, **props):
        if tag_table.lookup(name) is None:
            buffer.create_tag(name, **props)


    # ==========================
    # Tags changelog
    # ==========================

    tag(
        "changelog_title",
        foreground="#5fd7ff",
        weight=Pango.Weight.BOLD
    )

    tag(
        "changelog_item",
        foreground="#ffffff"
    )

    tag(
        "changelog_add",
        foreground="#57e389"
    )

    tag(
        "changelog_fix",
        foreground="#ffbe6f"
    )

    tag(
        "changelog_author",
        foreground="#c061cb"
    )

    tag(
        "changelog_date",
        foreground="#99c1f1"
    )

    tag(
        "changelog_version",
        foreground="#ffd75f",
        weight=Pango.Weight.BOLD
    )


    buffer.set_text("")


    for line in text.splitlines():

        end = buffer.get_end_iter()
        s = line.strip()


        # Ligne vide
        if not s:
            buffer.insert(end, "\n")
            continue


        # Version Debian
        if re.match(
            r"^proton-autogen\s+\([0-9.]+\)",
            s,
            re.IGNORECASE
        ):

            buffer.insert_with_tags_by_name(
                end,
                line,
                "changelog_title"
            )

            buffer.insert(
                buffer.get_end_iter(),
                "\n"
            )

            continue


        # Ajouts
        if s.startswith("* Added"):

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "changelog_add"
            )

            continue


        # Améliorations
        if s.startswith("* Improved") or \
           s.startswith("* Enhanced") or \
           s.startswith("* Optimized") or \
           s.startswith("* Refined"):

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "changelog_item"
            )

            continue


        # Corrections
        if s.startswith("* Fixed"):

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "changelog_fix"
            )

            continue


        # Signature Debian
        if s.startswith("--"):

            parts = line.split("  ", 1)

            buffer.insert_with_tags_by_name(
                end,
                parts[0],
                "changelog_author"
            )

            if len(parts) > 1:

                buffer.insert_with_tags_by_name(
                    buffer.get_end_iter(),
                    "  " + parts[1] + "\n",
                    "changelog_date"
                )

            else:
                buffer.insert(
                    buffer.get_end_iter(),
                    "\n"
                )

            continue


        # Texte normal
        buffer.insert(
            end,
            line + "\n"
        )

def insert_about_text(buffer, text):

    tag_table = buffer.get_tag_table()

    def tag(name, **props):
        if tag_table.lookup(name) is None:
            buffer.create_tag(name, **props)


    # ==========================
    # Tags About
    # ==========================

    tag(
        "about_title",
        foreground="#5fd7ff",
        weight=Pango.Weight.BOLD,
        size_points=16
    )

    tag(
        "about_section",
        foreground="#ffd75f",
        weight=Pango.Weight.BOLD
    )

    tag(
        "about_separator",
        foreground="#77767b"
    )

    tag(
        "about_text",
        foreground="#ffffff"
    )

    tag(
        "about_check",
        foreground="#57e389",
        weight=Pango.Weight.BOLD
    )

    tag(
        "about_value",
        foreground="#f9f06b"
    )

    tag(
        "about_link",
        foreground="#62a0ea",
        underline=Pango.Underline.SINGLE
    )

    tag(
        "about_command",
        foreground="#57e389",
        family="monospace"
    )


    buffer.set_text("")


    # Sections reconnues
    sections = {
        "POINTS FORTS",
        "AUTEUR",
        "LICENCE",
        "DÉPÔT GITHUB",
        "PPA",
    }


    for line in text.splitlines():

        end = buffer.get_end_iter()
        stripped = line.strip()


        # Ligne vide
        if not stripped:
            buffer.insert(end, "\n")
            continue


        # Titre
        if stripped == "PROTON-AUTOGEN":

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "about_title"
            )

            continue


        # Séparateurs
        if set(stripped) <= {"─", "━"}:

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "about_separator"
            )

            continue


        # Sections
        if stripped in sections:

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "about_section"
            )

            continue


        # Liste ✓
        if stripped.startswith("✓"):

            buffer.insert_with_tags_by_name(
                end,
                "✓",
                "about_check"
            )

            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(),
                line[1:] + "\n",
                "about_text"
            )

            continue


        # URL
        if stripped.startswith(
            ("http://", "https://")
        ):

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "about_link"
            )

            continue


        # Commande PPA
        if stripped.startswith("sudo "):

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "about_command"
            )

            continue


        # Valeurs simples auteur/licence
        if stripped in (
            "N3oray",
            "MIT"
        ):

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "about_value"
            )

            continue


        # Texte normal
        buffer.insert_with_tags_by_name(
            end,
            line + "\n",
            "about_text"
        )


def insert_sensor_text(buffer, text):

    tag_table = buffer.get_tag_table()

    def tag(name, **props):
        if tag_table.lookup(name) is None:
            buffer.create_tag(name, **props)


    # ==========================
    # Tags sensors
    # ==========================

    tag(
        "sensor_title",
        foreground="#c061cb",
        weight=Pango.Weight.BOLD
    )

    tag(
        "sensor_name",
        foreground="#62a0ea"
    )

    tag(
        "temperature",
        foreground="#57e389",
        weight=Pango.Weight.BOLD
    )

    tag(
        "temperature_warn",
        foreground="#ffbe6f",
        weight=Pango.Weight.BOLD
    )

    tag(
        "temperature_hot",
        foreground="#f66151",
        weight=Pango.Weight.BOLD
    )

    tag(
        "sensor_label",
        foreground="#ffffff"
    )

    tag(
        "separator",
        foreground="#77767b"
    )


    buffer.set_text("")


    # ==========================
    # Analyse
    # ==========================

    for line in text.splitlines():

        end = buffer.get_end_iter()
        stripped = line.strip()


        # Ligne vide
        if not stripped:
            buffer.insert(end, "\n")
            continue


        # === coretemp ===
        if re.match(r"^===.*===$", stripped):

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "sensor_title"
            )

            continue


        # Séparateur éventuel
        if set(stripped) <= {"─", "━"}:

            buffer.insert_with_tags_by_name(
                end,
                line + "\n",
                "separator"
            )

            continue


        # Ligne température
        temp = re.search(
            r"(\d+\.\d+)\s*°C",
            line
        )


        if temp:

            value = float(temp.group(1))

            before = line[:temp.start()]
            temp_value = temp.group(0)
            after = line[temp.end():]


            # Nom du capteur
            buffer.insert_with_tags_by_name(
                end,
                before,
                "sensor_name"
            )


            # Couleur température
            if value >= 80:
                color = "temperature_hot"

            elif value >= 65:
                color = "temperature_warn"

            else:
                color = "temperature"


            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(),
                temp_value,
                color
            )


            # Label
            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(),
                after + "\n",
                "sensor_label"
            )

            continue


        # Texte restant
        buffer.insert(
            end,
            line + "\n"
        )
#------------------------------------------------------------------------------------------------------

def insert_colored_text(buffer, text):

    tag_table = buffer.get_tag_table()

    def tag(name, **props):
        if tag_table.lookup(name) is None:
            buffer.create_tag(name, **props)

    # ==========================
    # Tags
    # ==========================

    tag("title",
        foreground="#5fd7ff",
        weight=Pango.Weight.BOLD)

    tag("section",
        foreground="#ffd75f",
        weight=Pango.Weight.BOLD)

    tag("sensor",
        foreground="#c061cb",
        weight=Pango.Weight.BOLD)

    tag("separator",
        foreground="#77767b")

    tag("key",
        foreground="#f9f06b",
        weight=Pango.Weight.BOLD)

    tag("value",
        foreground="#ffffff")

    tag("green",
        foreground="#57e389")

    tag("red",
        foreground="#f66151",
        weight=Pango.Weight.BOLD)

    tag("temperature",
        foreground="#33d17a")

    tag("hot_temperature",
        foreground="#f66151",
        weight=Pango.Weight.BOLD)

    tag("command",
        foreground="#57e389",
        family="monospace")

    tag("option",
        foreground="#62a0ea")

    tag("link",
        foreground="#62a0ea",
        underline=Pango.Underline.SINGLE)

    tag("path",
        foreground="#99c1f1")

    tag("proton",
        foreground="#33d17a")

    tag("selected",
        foreground="#ffbe6f",
        weight=Pango.Weight.BOLD)

    tag("note",
        foreground="#f9f06b")

    tag("env",
        foreground="#c061cb",
        weight=Pango.Weight.BOLD)


    buffer.set_text("")


    # ==========================
    # Rendu
    # ==========================

    for line in text.splitlines():

        end = buffer.get_end_iter()
        s = line.strip()


        # Ligne vide
        if not s:
            buffer.insert(end, "\n")
            continue


        # Séparateurs
        if set(s) <= {"─", "━"}:
            buffer.insert_with_tags_by_name(
                end, line + "\n", "separator")
            continue


        # Titres
        if s in (
            "PROTON-AUTOGEN",
            "PROTON-AUTOGEN - AIDE",
            "proton-autogen diagnostic"
        ):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "title")
            continue


        # Sections === xxx ===
        if re.match(r"^===.*===$", s):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "sensor")
            continue


        # Sections aide / diagnostics
        if (
            s.isupper()
            and len(s) > 2
            and not s.startswith("PROTON")
        ):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "section")
            continue


        # Variables environnement
        if s in (
            "STEAM_COMPAT_DATA_PATH",
            "WINEPREFIX"
        ):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "env")
            continue


        # Températures
        m = re.search(r"(\d+\.\d+)\s*°C", line)

        if m:

            temp = float(m.group(1))

            buffer.insert(
                end,
                line[:m.start()]
            )

            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(),
                m.group(0),
                "hot_temperature"
                if temp >= 70
                else "temperature"
            )

            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(),
                line[m.end():] + "\n",
                "value"
            )

            continue


        # URL
        if s.startswith(("http://", "https://")):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "link")
            continue


        # Chemins
        if s.startswith("/"):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "path")
            continue


        # [selected]
        if "[selected]" in line:

            a, b = line.split("[selected]", 1)

            buffer.insert(end, a)

            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(),
                "[selected]",
                "selected"
            )

            buffer.insert(
                buffer.get_end_iter(),
                b + "\n"
            )

            continue


        # yes/no
        if re.search(r"\b(yes|no)\b", line):

            parts = re.split(
                r"\b(yes|no)\b",
                line,
                maxsplit=1
            )

            buffer.insert(end, parts[0])

            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(),
                parts[1],
                "green"
                if parts[1] == "yes"
                else "red"
            )

            buffer.insert(
                buffer.get_end_iter(),
                parts[2] + "\n"
            )

            continue


        # Commandes
        if s.startswith(
            (
                "proton-autogen",
                "gamescope",
                "sudo "
            )
        ):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "command")
            continue


        # Options
        if s.startswith("--"):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "option")
            continue


        # Notes
        if s.startswith("- "):
            buffer.insert_with_tags_by_name(
                end, line + "\n", "note")
            continue


        # Clé : valeur
        if ":" in line:

            key, value = line.split(":", 1)

            buffer.insert_with_tags_by_name(
                end,
                key,
                "key"
            )

            buffer.insert(
                buffer.get_end_iter(),
                ":"
            )

            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(),
                value + "\n",
                "value"
            )

            continue


        # Proton
        if "Proton" in line or "GE-" in line:
            buffer.insert_with_tags_by_name(
                end, line + "\n", "proton")
            continue


        # Défaut
        buffer.insert(
            end,
            line + "\n"
        )

def colorize(text: str) -> Text:
    t = Text()

    for line in text.splitlines():
        # Ligne vide
        if not line.strip():
            t.append("\n")
            continue

        # Titre principal
        if line == "PROTON-AUTOGEN":
            t.append(line, style="bold cyan")
            t.append("\n")
            continue

        # Séparateurs
        if set(line) == {"─"}:
            t.append(line, style="bright_black")
            t.append("\n")
            continue

        # Titres de section
        if line.isupper() and "─" not in line:
            t.append(line, style="bold yellow")
            t.append("\n")
            continue

        # URL
        if line.startswith("http"):
            t.append(line, style="underline blue")
            t.append("\n")
            continue

        # Commande
        if line.startswith("sudo "):
            t.append(line, style="green")
            t.append("\n")
            continue

        # Liste ✓
        if line.startswith("✓"):
            t.append("✓ ", style="green")
            t.append(line[2:])
            t.append("\n")
            continue

        # Texte normal
        t.append(line)
        t.append("\n")

    return t
