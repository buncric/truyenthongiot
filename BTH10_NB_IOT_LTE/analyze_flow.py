"""Parse actual ns-3 FlowMonitor XML; no fabricated metrics."""
import argparse,csv,re,xml.etree.ElementTree as ET
def seconds(value):
 m=re.fullmatch(r'([+\-0-9.eE]+)(ns|us|ms|s)',value)
 if not m:raise ValueError(f'Unknown time {value!r}')
 return float(m[1])*{'ns':1e-9,'us':1e-6,'ms':1e-3,'s':1}[m[2]]
def analyze(path):
 root=ET.parse(path).getroot();classifier={x.attrib['flowId']:x.attrib for x in root.findall('./Ipv4FlowClassifier/Flow')}
 rows=[]
 for flow in root.findall('./FlowStats/Flow'):
  f=flow.attrib;tx=int(f['txPackets']);rx=int(f['rxPackets']);elapsed=seconds(f['timeLastRxPacket'])-seconds(f['timeFirstTxPacket']) if rx else 0
  rows.append({'flowId':f['flowId'],'sourceAddress':classifier.get(f['flowId'],{}).get('sourceAddress',''),'destinationAddress':classifier.get(f['flowId'],{}).get('destinationAddress',''),'txPackets':tx,'rxPackets':rx,'txBytes':int(f['txBytes']),'rxBytes':int(f['rxBytes']),'delivery_ratio':rx/tx if tx else 0,'mean_delay_ms':seconds(f['delaySum'])*1000/rx if rx else 0,'min_delay_ms':seconds(f.get('minDelay','0ns'))*1000,'max_delay_ms':seconds(f.get('maxDelay','0ns'))*1000,'throughput_kbps':int(f['rxBytes'])*8/elapsed/1000 if elapsed>0 else 0})
 return rows
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('xml');p.add_argument('--csv',default='flow-summary.csv');a=p.parse_args();rows=analyze(a.xml)
 if not rows:raise SystemExit('No IP flow: check traffic generation, routes, simulation duration')
 with open(a.csv,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for row in rows:print(row)
