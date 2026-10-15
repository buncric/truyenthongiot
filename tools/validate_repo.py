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
