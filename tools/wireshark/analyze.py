"""Extract packet facts from the genuine captures; fail if expected evidence is absent."""
from pathlib import Path
import csv,datetime,hashlib,io,json,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/wireshark-thuc-te'
TSHARK=r'C:\Program Files\Wireshark\tshark.exe'
FIELDS=['frame.number','frame.time_relative','ip.src','ip.dst','tcp.srcport','tcp.dstport','udp.srcport','udp.dstport','coap.type','coap.code','coap.mid','coap.token','coap.opt.observe','coap.opt.block_number','coap.opt.block_mflag','coap.opt.block_size','coap.block_payload','mqtt.msgtype','mqtt.clientid','mqtt.topic','mqtt.msg','mqtt.retain','tls.handshake.type','tls.record.content_type','_ws.col.Info']
summary=[];packets={}
for meta in json.loads((OUT/'capture-report.json').read_text()):
 case=meta['case'];pcap=OUT/(case+'.pcapng')
 assert hashlib.sha256(pcap.read_bytes()).hexdigest()==meta['sha256'],case
 cmd=[TSHARK,'-r',str(pcap),'-d','udp.port==5684,coap','-T','fields','-E','quote=d']
 for f in FIELDS:cmd+=['-e',f]
 result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',check=True)
 rows=[dict(zip(FIELDS,r)) for r in csv.reader(io.StringIO(result.stdout),delimiter='\t')]
 assert all(r['ip.src']=='127.0.0.1' and r['ip.dst']=='127.0.0.1' for r in rows),case
 packets[case]=rows
 with (OUT/(case+'-packets.csv')).open('w',encoding='utf-8-sig',newline='') as output:
  writer=csv.DictWriter(output,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
 def count(field,value):return sum(r[field].split(',').count(value) for r in rows)
 facts={'case':case,'frames':len(rows),'coap_packets':sum(bool(r['coap.type']) for r in rows),'mqtt_publish_packets':count('mqtt.msgtype','3'),'tls_packets':sum(bool(r['tls.record.content_type']) for r in rows)}
 if case=='13.1-base':
  assert count('coap.type','1')==2 and count('coap.type','0')==1 and count('coap.type','2')==1
  facts['result']='NON POST + NON response; CON POST + ACK response'
 if case=='13.1-retry':
  requests=[r for r in rows if r['udp.dstport']=='5684' and r['coap.type']=='0']
  assert len(requests)==2 and requests[0]['coap.mid']==requests[1]['coap.mid'] and requests[0]['coap.token']==requests[1]['coap.token']
  facts.update(mid=requests[0]['coap.mid'],retry_delay_s=round(float(requests[1]['frame.time_relative'])-float(requests[0]['frame.time_relative']),6),request_frames=[r['frame.number'] for r in requests])
 if case=='13.2-poll':
  facts.update(get_requests=count('coap.code','1'),content_responses=count('coap.code','69'),application_window_s=60)
  assert facts['get_requests']==30 and facts['content_responses']==30
 if case=='13.2-observe':
  content=[r for r in rows if r['coap.code']=='69'];assert len(content)>=3
  assert count('coap.code','1')==1 and len({r['coap.token'] for r in content})==1
  facts.update(get_requests=1,content_responses=len(content),initial_responses=1,subsequent_notifications=len(content)-1,empty_acks=count('coap.code','0'),application_window_s=60,token=content[0]['coap.token'])
 if case=='13.3':
  response=[r for r in rows if r['coap.code']=='69'];assert [int(r['coap.opt.block_number']) for r in response]==list(range(16))
  payload=b''.join(bytes.fromhex(r['coap.block_payload'].replace(':','')) for r in response)
  assert payload==b'A'*2048 and all(r['coap.opt.block_size']=='3' for r in response)
  assert [r['coap.opt.block_mflag'] for r in response]==['1']*15+['0']
  facts.update(blocks=16,block_size_bytes=128,reassembled_bytes=len(payload),payload_sha256=hashlib.sha256(payload).hexdigest())
 if case.startswith(('12.','14.')):
  decoded=[]
  for r in rows:
   if r['mqtt.msg']:
    try:decoded.append({'frame':r['frame.number'],'topic':r['mqtt.topic'],'text':bytes.fromhex(r['mqtt.msg'].replace(':','')).decode('utf8'),'retain':r['mqtt.retain']})
    except (ValueError,UnicodeDecodeError):pass
  facts['messages']=decoded
  if case=='12.1':assert any('"simulated":true' in m['text'] for m in decoded)
  if case=='12.2':assert {'ON','OFF'} <= {m['text'] for m in decoded if m['topic'].endswith('/state')}
  if case=='12.3':assert any(m['text']=='offline' for m in decoded) and any(m['retain']=='True' for m in decoded)
  if case=='14.1':assert count('tls.handshake.type','1')>=1 and count('tls.handshake.type','2')>=1 and any('plaintext' in m['text'] for m in decoded)
  if case=='14.2':
   commands=[m['text'] for m in decoded if m['topic'].endswith('/cmd')];assert len(commands)>=2 and len(set(commands))==1
   assert any(m['text']=='ACCEPT' for m in decoded) and any(m['text'].startswith('REJECT') for m in decoded)
   facts['identical_replayed_command']=True
  if case=='14.3':
   connections=[r for r in rows if '1' in r['mqtt.msgtype'].split(',') and r['mqtt.clientid']=='pc-reconnecting-client']
   assert len(connections)==2
   facts['test_client_connect_count']=len(connections)
 facts['verification']='PASS';summary.append(facts)
(OUT/'analysis.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps([{'case':r['case'],'frames':r['frames'],'verification':r['verification']} for r in summary],indent=2))
