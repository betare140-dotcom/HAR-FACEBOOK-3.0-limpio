"""Embed the repository's trusted web files without relative asset URLs."""
from pathlib import Path
import re

_SCRIPT = re.compile(r'<script\b[^>]*\bsrc="([^"]+)"[^>]*>\s*</script>', re.I)
_STYLE = re.compile(r'<link\b[^>]*\brel="stylesheet"[^>]*\bhref="([^"]+)"[^>]*>', re.I)


def build_html(directory: Path | None = None) -> str:
    root = (directory or Path(__file__).parent).resolve()

    def read_asset(name: str) -> str:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Falta un archivo del paquete: {name}")
        return path.read_text(encoding="utf-8")

    html = read_asset("index.html")
    scripts = []

    def collect_script(match: re.Match) -> str:
        code = read_asset(match.group(1))
        if "</script" in code.lower():
            raise ValueError("Un módulo contiene un cierre de script no permitido.")
        scripts.append("<script>\n" + code + "\n</script>")
        return ""

    def inline_style(match: re.Match) -> str:
        css = read_asset(match.group(1))
        if "</style" in css.lower():
            raise ValueError("La hoja de estilos contiene un cierre no permitido.")
        return "<style>\n" + css + "\n</style>"

    html = _SCRIPT.sub(collect_script, html)
    html = _STYLE.sub(inline_style, html)
    if "</body>" not in html:
        raise ValueError("index.html no contiene un cuerpo completo.")
    # Classic scripts execute in the same order as index.html, after its DOM.
    return html.replace("</body>", "\n".join(scripts) + "\n</body>", 1)
