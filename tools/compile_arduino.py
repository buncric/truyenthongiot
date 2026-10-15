"""Compile every working sketch. Excludes supplied projects and archived work."""
import concurrent.futures, json, os, shutil, subprocess, argparse, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def targets():
    for p in sorted(ROOT.glob('BTH*/**/*.ino')):
        if any(x in p.parts for x in ['project-goc','build','firmware']): continue
        lab=p.relative_to(ROOT).parts[0]
        if lab.startswith(('BTH02','BTH03','BTH05')): board='esp8266:esp8266:nodemcuv2' if 'ESP8266' in p.name else 'arduino:avr:uno'
        elif lab.startswith('BTH14'): board='esp32:esp32:esp32'
        elif lab.startswith(('BTH12','BTH13')): board='esp8266:esp8266:d1_mini'
        else:continue
        yield p,board
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cli',default='arduino-cli');ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--filter',default='');args=ap.parse_args()
    out=ROOT/'artifacts/arduino';out.mkdir(parents=True,exist_ok=True)
    def compile_one(target):
        p,board=target;relative=str(p.relative_to(ROOT)).replace('\\','/');dest=out/p.parent.name;dest.mkdir(exist_ok=True)
        # ESP32 3.3.12 export hooks invoke Windows PowerShell, broken on some hosts.
        # Normal compile still links and creates the binary in Arduino's build cache.
        export=[] if board.startswith('esp32:') else ['--output-dir',str(dest)]
        r=subprocess.run([args.cli,'compile','--fqbn',board,'--warnings','all','--jobs','2',*export,str(p.parent)],capture_output=True,text=True,encoding='utf-8',errors='replace')
        (dest/'compile.log').write_text(r.stdout+r.stderr,encoding='utf-8')
        if r.returncode==0 and board=='arduino:avr:uno':
            firmware=p.parent/'firmware';firmware.mkdir(exist_ok=True)
            for binary in dest.glob('*.hex'):shutil.copy2(binary,firmware/binary.name)
        row={'sketch':relative,'board':board,'passed':r.returncode==0,'source_sha256':hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'source_sha256_normalization':'LF','log':str((dest/'compile.log').relative_to(ROOT)).replace('\\','/')}
        print(('PASS ' if row['passed'] else 'FAIL ')+relative,flush=True);return row
    selected=[t for t in targets() if args.filter in str(t[0])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:results=list(pool.map(compile_one,selected))
    report=out/'results.json'
    if args.filter and report.exists():
        combined={x['sketch']:x for x in json.loads(report.read_text(encoding='utf-8'))}
        combined.update({x['sketch']:x for x in results});all_results=list(combined.values())
    else:all_results=results
    report.write_text(json.dumps(all_results,indent=2),encoding='utf-8')
    raise SystemExit(0 if all(x['passed'] for x in results) else 1)
if __name__=='__main__':main()
