"""Baut die Nexvio-Website: kopiert den Ordner site/ nach dist/.

Cloudflare Pages ruft dieses Skript bei jedem Push auf (Build command: python3 build.py,
Build output directory: dist). Es gibt keinen weiteren Build-Schritt.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "site", ROOT / "dist"

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)

# Demo-Apps ohne fremde Server ausliefern (Schriften und Bibliotheken lokal)
import sys
sys.path.insert(0, str(ROOT / "tools"))
from localize_demos import localize
for p in sorted((OUT / "demos").glob("*.html")):
    localize(p)
print(f"{sum(1 for p in OUT.rglob('*') if p.is_file())} Dateien nach {OUT} kopiert")
