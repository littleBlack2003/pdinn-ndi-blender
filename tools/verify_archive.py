from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'ARCHIVE_MANIFEST.json').read_text())
for r in m['files']:
 p=root/r['path'];assert p.is_file(),r['path'];assert p.stat().st_size==r['bytes'],r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
print(f"PASS: {len(m['files'])} archived payload files match SHA256")
