"""Run the three requested LTE parameter studies and collect real metrics."""
from pathlib import Path
import argparse,csv,importlib.util,json,os,subprocess
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('flow',ROOT/'BTH10_NB_IOT_LTE/analyze_flow.py');flow=importlib.util.module_from_spec(spec);spec.loader.exec_module(flow)
CASES=[(1,20,10),(5,20,10),(10,20,10),(1,100,10),(1,500,10),(1,20,20)]
def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',default=str(ROOT/'artifacts/lte'));a=p.parse_args()
    binary=Path(a.binary).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    environment={'runner':os.environ.get('RUNNER_OS','local'),'platform':os.uname().sysname if hasattr(os,'uname') else os.name}
    try:environment['ns3_version']=subprocess.check_output(['pkg-config','--modversion','ns3-core'],text=True).strip()
    except (FileNotFoundError,subprocess.CalledProcessError):environment['ns3_version']='see local build tag'
    (out/'environment.json').write_text(json.dumps(environment,indent=2),encoding='utf-8')
    if os.environ.get('GITHUB_ACTIONS'):print('::notice title=LTE environment::'+json.dumps(environment),flush=True)
    aggregate=[]
    for n,duration_distance,t in CASES:
        name=f'ue{n}-distance{duration_distance}-time{t}';dest=out/name;dest.mkdir(exist_ok=True)
        subprocess.run([str(binary),f'--nUe={n}',f'--distance={duration_distance}',f'--simTime={t}'],cwd=dest,check=True,timeout=120)
        rows=flow.analyze(dest/'lte-lab1.xml')
        if not rows or not sum(x['txPackets'] for x in rows):raise RuntimeError(f'{name}: no generated traffic')
        for row in rows:aggregate.append({'case':name,'nUe':n,'distance_m':duration_distance,'simTime_s':t,**row})
        with (dest/'flow-summary.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        tx=sum(x['txPackets'] for x in rows);rx=sum(x['rxPackets'] for x in rows)
        mean=sum(x['mean_delay_ms']*x['rxPackets'] for x in rows)/rx if rx else 0
        result={'case':name,'flows':len(rows),'txPackets':tx,'rxPackets':rx,'delivery_ratio':rx/tx,'mean_delay_ms':mean}
        print(json.dumps(result),flush=True)
        # A public check annotation makes the measured summary accessible through the GitHub API.
        if os.environ.get('GITHUB_ACTIONS'):print('::notice title=LTE measured result::'+json.dumps(result),flush=True)
    with (out/'all-flows.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(aggregate[0]));writer.writeheader();writer.writerows(aggregate)
if __name__=='__main__':main()
