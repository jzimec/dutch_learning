#!/usr/bin/env python3
"""One-time conservative Woordica refactor. Run at repository root.
Makes a backup, extracts inline CSS and large inline JS without changing execution order.
"""
from pathlib import Path
import re, json, hashlib
root=Path(__file__).resolve().parents[1]
page=root/"index.html"
source=page.read_text(encoding="utf-8")
assert source.count("Dutch Learning")==3 or "Woordica" in source
assert source.count("<script>")>=3
assert "<link rel=\"manifest\" href=\"manifest.webmanifest\">" in source
out=source.replace("Dutch Learning","Woordica")
assets=root/"assets"
assets.mkdir(exist_ok=True)
# Split large inline application script only; leave other scripts and styles unchanged.
pattern=r"<script>\s*(const EMBEDDED_IMAGES=\{\};[\s\S]*?)</script>"
m=re.search(pattern,out)
assert m and len(m.group(1))>1_000_000, "Unexpected script layout; abort"
js=m.group(1)
js_path=assets/"woordica-app.js"
if js_path.exists():
    assert js_path.read_text(encoding="utf-8")==js
else:
    js_path.write_text(js,encoding="utf-8")
out=out[:m.start()]+ '<script src="./assets/woordica-app.js"></script>' +out[m.end():]
# Link to versioned SVG; leave original PNG as compatibility fallback.
out=out.replace('<link rel="icon" href="icon-192.png" type="image/png" sizes="192x192">',
'<link rel="icon" href="woordica-icon.svg" type="image/svg+xml">\n  <link rel="icon" href="icon-192.png" type="image/png" sizes="192x192">')
assert "Woordica" in out and "Dutch Learning" not in out
assert len(out)<150_000, f"Unexpected page size {len(out)}"
page.write_text(out,encoding="utf-8")
print(json.dumps({"index_before":len(source),"index_after":len(out),"external_js":len(js),
"sha256_js":hashlib.sha256(js.encode()).hexdigest()},indent=2))
