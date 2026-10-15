"""Refresh screenshot provenance; exercise articles are maintained manually."""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/wireshark-thuc-te'
screens=json.loads((OUT/'screenshots.json').read_text(encoding='utf8'))
byfile={row['file']:row for row in screens}
for path in OUT.glob('*.png'):
    row=byfile.setdefault(path.name,{
        'file':path.name,
        'source':'Unmodified Wireshark window screenshot via computer-use',
        'captured_utc':datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat(),
    })
    row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/'screenshots.json').write_text(json.dumps(list(byfile.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Updated screenshot hashes; report text preserved.')
