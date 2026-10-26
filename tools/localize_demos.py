"""Ersetzt in den Demo-Apps externe Schriften (Google Fonts) und Bibliotheken (cdnjs) durch lokale Kopien.

Die App-Repos sind eigenständige Einzeldateien und laden Schriften/Bibliotheken von außen.
Auf der Website sollen keine fremden Server angefragt werden (Datenschutzerklärung: Schriften lokal).
Aufruf: python3 tools/localize_demos.py <ordner-mit-demos>  (idempotent)
"""
import re, sys
from pathlib import Path

FONTS = """<style>
@font-face { font-family: "Figtree"; font-style: normal; font-weight: 300 900; font-display: swap; src: url(shared-files/figtree-latin-wght-normal.woff2) format("woff2-variations"); }
@font-face { font-family: "Geist"; font-style: normal; font-weight: 100 900; font-display: swap; src: url(shared-files/geist-latin-wght-normal.woff2) format("woff2-variations"); }
@font-face { font-family: "JetBrains Mono"; font-style: normal; font-weight: 100 800; font-display: swap; src: url(shared-files/jetbrains-mono-latin-wght-normal.woff2) format("woff2-variations"); }
</style>"""
LIBS = {
    "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js": "shared-files/xlsx.full.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js": "shared-files/jspdf.umd.min.js",
}

def localize(path: Path) -> bool:
    s = path.read_text(encoding="utf-8"); o = s
    s = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>\n?', "", s)
    s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">', FONTS, s)
    for a, b in LIBS.items():
        s = s.replace(a, b)
    s = re.sub(r'\s*integrity="[^"]*"', "", s) if s != o else s
    if s != o:
        path.write_text(s, encoding="utf-8")
    return s != o

if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "site/demos")
    for p in sorted(root.glob("*.html")):
        if localize(p):
            print("lokalisiert:", p.name)
