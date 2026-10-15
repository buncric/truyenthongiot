"""Check the newly organized labs, source hashes, Markdown links and step figures."""
from pathlib import Path
import hashlib,json,re,urllib.parse
ROOT=Path(__file__).resolve().parents[1]
LABS=['BTH02_UART','BTH03_SPI_I2C','BTH04_ETHERNET_TCPIP','BTH05_BLUETOOTH','BTH06_ZIGBEE','BTH08_WIFI','BTH09_NS3','BTH10_NB_IOT_LTE','BTH12_MQTT','BTH13_COAP','BTH14_BAO_MAT']
errors=[];documents=[];steps=0
for lab in LABS:
    assert (ROOT/lab/'README.md').is_file(),lab
    for md in (ROOT/lab).rglob('*.md'):
        if 'project-goc' in md.parts:continue
        documents.append(md)
        if re.fullmatch(r'\d+\.\d+\.md',md.name):
            text=md.read_text(encoding='utf-8');count=len(re.findall(r'^### Bước ',text,re.M));figures=len(re.findall(r'!\[Bước ',text))
            if not count or count!=figures:errors.append(f'{md}: {count} steps, {figures} figures')
            steps+=count
documents.extend([ROOT/'README.md',*list((ROOT/'docs').glob('*.md')),*list((ROOT/'tai-lieu-goc').glob('*.md'))])
documents.extend([ROOT/'mo-phong-3d/README.md',*list((ROOT/'docs/giao-dien-goc').glob('*.md')),*list((ROOT/'docs/linh-kien').glob('*.md'))])
scene_manifest=ROOT/'mo-phong-3d/manifest.json'
wire=ROOT/'docs/wireshark-thuc-te'
documents.append(wire/'README.md')
for manifest,suffix,key in [('capture-report.json','.pcapng','case'),('screenshots.json','','file')]:
    for row in json.loads((wire/manifest).read_text(encoding='utf-8')):
        asset=wire/(row[key]+suffix)
        if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest()!=row['sha256']:
            errors.append(f'Wireshark evidence missing or changed: {asset.name}')
if scene_manifest.exists():
    scenes=json.loads(scene_manifest.read_text(encoding='utf-8'))
    catalog=json.loads((ROOT/'docs/catalog.json').read_text(encoding='utf-8'))
    expected={r['id']:r for r in catalog if r['id']!='8.1'}
    if {r['id'] for r in scenes}!=set(expected):errors.append('Blender scenes do not cover the exercise catalog')
    for row in scenes:
        blend=ROOT/'mo-phong-3d'/row['blend']
        if not blend.exists():errors.append(f'Missing Blender file: {blend}')
        if row['renders']!=expected[row['id']]['steps']:errors.append(f"Blender step count: {row['id']}")
        for i in range(row['renders']):
            if not (blend.parent/f'buoc-{i+1:02}.jpg').exists():errors.append(f"Missing Blender render {row['id']} step {i+1}")
for md in documents:
    for target in re.findall(r'\]\(([^\n)]+)\)',md.read_text(encoding='utf-8')):
        if target.startswith(('http://','https://','mailto:','#')):continue
        target=urllib.parse.unquote(target.split('#')[0].strip('<>'))
        if not (md.parent/target).exists():errors.append(f'{md.relative_to(ROOT)}: missing {target}')
for row in json.loads((ROOT/'tai-lieu-goc/manifest.json').read_text(encoding='utf-8')):
    p=ROOT/'tai-lieu-goc'/row['file']
    if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append(f'Source changed: {p.name}')
for p in ROOT.glob('BTH*/**/config.local.h'):errors.append(f'Local secret must not be committed: {p}')
print(json.dumps({'documents_checked':len(documents),'step_figures':steps,'errors':errors},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
