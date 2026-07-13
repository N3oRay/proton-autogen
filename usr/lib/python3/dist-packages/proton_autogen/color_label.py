from rich.text import Text
import re


from gi.repository import Pango

def insert_colored_text(buffer, text):
    tag_table = buffer.get_tag_table()

    def ensure_tag(name, **props):
        if tag_table.lookup(name) is None:
            buffer.create_tag(name, **props)

    # Création des tags une seule fois
    ensure_tag(
        "title",
        foreground="#5fd7ff",
        weight=Pango.Weight.BOLD,
    )

    ensure_tag(
        "section",
        foreground="#ffd75f",
        weight=Pango.Weight.BOLD,
    )

    ensure_tag(
        "green",
        foreground="#5fff87",
    )

    ensure_tag(
        "link",
        foreground="#62a0ea",
        underline=Pango.Underline.SINGLE,
    )

    ensure_tag(
        "command",
        foreground="#57e389",
        family="monospace",
    )

    ensure_tag(
        "separator",
        foreground="#77767b",
    )

    buffer.set_text("")

    for line in text.splitlines():
        end = buffer.get_end_iter()

        if line == "PROTON-AUTOGEN":
            buffer.insert_with_tags_by_name(end, line + "\n", "title")

        elif line.isupper() and line.strip():
            buffer.insert_with_tags_by_name(end, line + "\n", "section")

        elif line.startswith("✓"):
            buffer.insert_with_tags_by_name(end, "✓ ", "green")
            end = buffer.get_end_iter()
            buffer.insert(end, line[2:] + "\n")

        elif line.startswith("http://") or line.startswith("https://"):
            buffer.insert_with_tags_by_name(end, line + "\n", "link")

        elif line.startswith("sudo "):
            buffer.insert_with_tags_by_name(end, line + "\n", "command")

        elif set(line) == {"─"}:
            buffer.insert_with_tags_by_name(end, line + "\n", "separator")

        else:
            buffer.insert(end, line + "\n")

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
