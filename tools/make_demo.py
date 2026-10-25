"""Erzeugt die Website-Fassung einer Demo-App.

Aufruf: python3 tools/make_demo.py <quelle.html> <ziel.html>
Die Quelle ist die App-Datei aus claude.ai (ohne <head>). Die Website-Fassung
- läuft immer im Demo-Modus (Beispieldaten nur im Browser des Besuchers),
- lädt Schriften und Bibliotheken von der eigenen Domain statt von Google oder cdnjs,
- zeigt oben eine schmale Demo-Leiste mit Link zur Kontaktseite.
"""
import re, sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()

title = "Demo: Reklamationen & Workflows | Nexvio"
s = re.sub(r"<title>.*?</title>\n?", "", s, count=1)
s = re.sub(r'<link rel="preconnect"[^>]*>\n?', "", s)
s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^"]*">\n?', "", s)
s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
s = s.replace("https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js", "assets/xlsx.full.min.js")
s = s.replace("https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js", "assets/jspdf.umd.min.js")
s = s.replace("const KEY = 'devunox-apps-demo-v1';", "const KEY = 'nexvio-demo-qm-v1';")
s = s.replace("'Devunox'", "'Muster GmbH'")
assert "googleapis" not in s and "cdnjs" not in s, "externe Quelle übrig"

fonts = "".join(
    f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(assets/fonts/{file}-latin-{w}-normal.woff2) format('woff2')}}\n"
    for fam, file, ws in [("Figtree", "figtree", (400, 500, 600, 700, 800)), ("Geist", "geist-sans", (400, 500, 600, 700))] for w in ws)
fonts += "@font-face{font-family:'JetBrains Mono';font-style:normal;font-weight:500;font-display:swap;src:url(../assets/fonts/jetbrains-mono-latin-500-normal.woff2) format('woff2')}\n"

bar_css = """.demo-bar{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:4px 14px;padding:8px max(16px,env(safe-area-inset-left,0px));background:#17181C;color:#E8EAF2;font:500 13px/1.4 'Figtree',system-ui,sans-serif;text-align:center}
.demo-bar b{color:#fff}.demo-bar a{color:#C9BEFF;text-decoration:underline;text-underline-offset:2px}.demo-bar a:hover{color:#fff}
@media (max-width:760px){.demo-bar .db-x{display:none}}
"""
bar = ('<div class="demo-bar" role="note"><span><b>Demo</b> mit Beispieldaten. '
       '<span class="db-x">Ihre Eingaben bleiben nur in Ihrem Browser.</span></span>'
       '<a href="../de/kontakt">So etwas für Ihr Unternehmen? Projekt anfragen</a>'
       '<a href="../de/demos">Alle Demos</a></div>\n')

head = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="Klickbare Demo: Kunden- und Lieferantenreklamationen nach 8D, Freigabe-Workflows, Aufgaben mit Erinnerungen und Stammdaten per Excel-Upload.">
<meta name="robots" content="noindex, follow">
<style>
{fonts}{bar_css}</style>
</head>
<body>
"""
first_div = s.index('<div class="shell"')
open(dst, "w", encoding="utf-8").write(head + s[:first_div] + bar + s[first_div:] + "\n</body>\n</html>\n")
print("ok", dst)
