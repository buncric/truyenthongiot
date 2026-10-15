"""Capture bounded protocol experiments with installed TShark/Npcap, not synthetic pcaps.

Run from any directory. npm install --prefix tools/wireshark is required.
Certificates are created outside Git and used only by the loopback TLS listener.
"""
from pathlib import Path
import argparse,datetime,json,os,shutil,subprocess,time,hashlib
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--tshark',default=r'C:\Program Files\Wireshark\tshark.exe');p.add_argument('--cert-dir',required=True);p.add_argument('--node-path');p.add_argument('cases',nargs='*');a=p.parse_args()
cases=[('13.1-base',4),('13.1-retry',8),('13.3',5),('12.1',5),('12.2',5),('12.3',5),('14.1',5),('14.2',5),('14.3',7),('13.2-poll',63),('13.2-observe',63)]
out=ROOT/'docs/wireshark-thuc-te';out.mkdir(exist_ok=True)
env=os.environ.copy()
if a.node_path:env['NODE_PATH']=a.node_path
report=[]
for case,duration in cases:
 if a.cases and case not in a.cases:continue
 cap=out/(case+'.pcapng');log=out/(case+'.log');meta=out/(case+'-capture.log')
 bpf='udp port 5683 or udp port 5684' if case.startswith('13.') else 'tcp port 1883 or tcp port 8883'
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with meta.open('w') as err:
  capture=subprocess.Popen([a.tshark,'-i',r'\Device\NPF_Loopback','-f',bpf,'-a',f'duration:{duration}','-w',str(cap)],stdout=subprocess.DEVNULL,stderr=err)
  try:
   time.sleep(1)
   with log.open('w',encoding='utf8') as output:
    proc=subprocess.run(['node',str(Path(__file__).with_name('traffic.cjs')),case,a.cert_dir],stdout=output,stderr=subprocess.STDOUT,env=env,timeout=duration+8)
   capture.wait(timeout=duration+5)
   if proc.returncode or capture.returncode:raise RuntimeError(f'{case}: application={proc.returncode}, capture={capture.returncode}; see logs')
  finally:
   if capture.poll() is None:capture.terminate();capture.wait(timeout=5)
 result=subprocess.run([a.tshark,'-r',str(cap),'-T','fields','-e','frame.number'],capture_output=True,text=True,check=True)
 count=len(result.stdout.splitlines())
 if not count:raise RuntimeError('Empty capture '+case)
 row={'case':case,'interface':'Npcap loopback','filter':bpf,'started_utc':started,'duration_limit_s':duration,'frames':count,'sha256':hashlib.sha256(cap.read_bytes()).hexdigest(),'source':'real PC application sockets; no physical ESP or HA','result':'PASS'}
 (out/(case+'.json')).write_text(json.dumps(row,indent=2)+'\n',encoding='utf8');report.append(row);print(json.dumps(row),flush=True)
if report:
 all_rows=[]
 for candidate in out.glob('*.json'):
  if candidate.name=='capture-report.json':continue
  row=json.loads(candidate.read_text(encoding='utf8'))
  if isinstance(row,dict) and 'case' in row and 'sha256' in row:all_rows.append(row)
 (out/'capture-report.json').write_text(json.dumps(sorted(all_rows,key=lambda r:r['case']),indent=2)+'\n',encoding='utf8')
