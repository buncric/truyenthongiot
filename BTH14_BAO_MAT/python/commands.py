"""Bounded experiments against a broker you administer; credentials from environment."""
import argparse, hashlib, hmac, ipaddress, json, os, secrets, time
from pathlib import Path
def sign(cmd, timestamp, nonce, sequence, key):
    canonical=f'{cmd}|{timestamp}|{nonce}|{sequence}'.encode()
    return {'cmd':cmd,'time':timestamp,'nonce':nonce,'seq':sequence,'mac':hmac.new(key.encode(),canonical,hashlib.sha256).hexdigest()}
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['vulnerable','signed','replay','load']);p.add_argument('--host',default='127.0.0.1');p.add_argument('--command',choices=['OPEN','CLOSE'],default='OPEN');p.add_argument('--count',type=int,default=20);p.add_argument('--rate',type=float,default=5);p.add_argument('--file',type=Path,default=Path('data/last-command.json'));a=p.parse_args()
    host=ipaddress.ip_address(a.host)
    if not(host.is_loopback or host.is_private):p.error('Use the IP of your private laboratory broker')
    if not 1<=a.count<=200 or not .1<=a.rate<=20:p.error('count 1..200, rate 0.1..20 msg/s')
    import paho.mqtt.client as mqtt
    c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.username_pw_set(os.environ.get('MQTT_USER','mqtt-user'),os.environ['MQTT_PASSWORD'])
    c.connect(str(host),1883,30);c.loop_start()
    try:
      if a.mode=='signed':
        key=os.environ['HMAC_KEY'];payload=sign(a.command,int(time.time()),secrets.token_hex(8),time.time_ns()//1000000,key)
        a.file.parent.mkdir(parents=True,exist_ok=True);a.file.write_text(json.dumps(payload))
      elif a.mode=='replay':payload=json.loads(a.file.read_text())
      else:payload=a.command
      topic='iot/resilience/sv01/cmd' if a.mode=='load' else 'iot/security/sv01/cmd'
      for i in range(a.count if a.mode=='load' else 1):
        message=('ON' if i%2 else 'OFF') if a.mode=='load' else (json.dumps(payload) if isinstance(payload,dict) else payload)
        info=c.publish(topic,message,qos=1);info.wait_for_publish(timeout=5)
        if not info.is_published():raise TimeoutError('MQTT publish not acknowledged')
        print(i+1,topic,message)
        if a.mode=='load':time.sleep(1/a.rate)
    finally:c.disconnect();c.loop_stop()
if __name__=='__main__':main()
