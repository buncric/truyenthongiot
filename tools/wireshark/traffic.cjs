// Actual sockets on 127.0.0.1 only. Never writes, synthesizes or edits a pcap.
// Software stand-ins for devices are explicitly labelled in payloads and logs.
const net=require('node:net'),tls=require('node:tls'),fs=require('node:fs'),crypto=require('node:crypto');
const {once}=require('node:events');
const root=require('node:path').resolve(__dirname,'../..');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const mode=process.argv[2],certDir=process.argv[3];
const clients=[],servers=[];let broker,service,proxy;
const log=(...s)=>console.log(new Date().toISOString(),...s);
async function mqttSetup(){
 const aedes=require('aedes');broker=aedes({id:'PC-LOOPBACK-LAB'});
 broker.on('clientError',(c,e)=>log('CLIENT_ERROR',c?.id,e.message));
 broker.on('publish',(p,c)=>{if(c)log('PUBLISH',c.id,p.topic,p.payload.toString());});
 const server=net.createServer(broker.handle);await new Promise(r=>server.listen(1883,'127.0.0.1',r));servers.push(server);
 if(mode==='14.1'){
  const secure=tls.createServer({key:fs.readFileSync(certDir+'/server.key'),cert:fs.readFileSync(certDir+'/server.crt')},broker.handle);
  await new Promise(r=>secure.listen(8883,'127.0.0.1',r));servers.push(secure);
 }
 log('BROKER Aedes 0.51.3, loopback only. PC software clients, no ESP/HA hardware.');
}
async function connect(id,extra={}){
 const mqtt=require('mqtt');const url=extra.secure?'mqtts://127.0.0.1:8883':'mqtt://127.0.0.1:1883';
 const c=mqtt.connect(url,{clientId:id,protocolVersion:4,reconnectPeriod:0,connectTimeout:3000,username:'lab-user',password:'lab-only-not-a-real-password',...extra});
 clients.push(c);await once(c,'connect');return c;
}
const pub=(c,topic,payload,extra={})=>new Promise((r,j)=>c.publish(topic,payload,{qos:1,...extra},e=>e?j(e):r()));
const sub=(c,topic)=>new Promise((r,j)=>c.subscribe(topic,{qos:1},e=>e?j(e):r()));
const close=c=>new Promise(r=>c.end(false,{},r));
async function mqttCases(){
 await mqttSetup();
 if(mode==='12.1'){
  const listener=await connect('pc-ha-subscriber');await sub(listener,'iot/lab1/sv01/sensor');
  const sensor=await connect('pc-simulated-sensor');
  for(let i=0;i<3;i++){await pub(sensor,'iot/lab1/sv01/sensor',JSON.stringify({temp:28+i*.5,hum:65,simulated:true,source:'PC'}));await wait(350);}
 }else if(mode==='12.2'){
  const device=await connect('pc-led-device'),ui=await connect('pc-dashboard');
  await sub(device,'iot/lab2/sv01/cmd');await sub(ui,'iot/lab2/sv01/state');
  device.on('message',(t,p)=>{const cmd=p.toString();log('PC_LED_STATE',cmd);pub(device,'iot/lab2/sv01/state',cmd).catch(console.error);});
  for(const cmd of ['ON','OFF']){await pub(ui,'iot/lab2/sv01/cmd',cmd);await wait(450);}
 }else if(mode==='12.3'){
  const watcher=await connect('pc-watch-will');await sub(watcher,'iot/lab3/sv01/#');
  const d=await connect('pc-will-device',{will:{topic:'iot/lab3/sv01/status',payload:'offline',qos:1,retain:true}});
  await pub(d,'iot/lab3/sv01/status','online',{retain:true});await pub(d,'iot/lab3/sv01/state','ON',{retain:true});
  const late=await connect('pc-late-subscriber');await sub(late,'iot/lab3/sv01/#');await wait(450);
  log('FAULT: close TCP without MQTT DISCONNECT');d.stream.destroy();await wait(650);
 }else if(mode==='14.1'){
  const plain=await connect('pc-plaintext');await pub(plain,'iot/security/sv01/sensor',JSON.stringify({simulated:true,transport:'plaintext',temp:28.5}));await close(plain);
  const secure=await connect('pc-tls-verified',{secure:true,ca:fs.readFileSync(certDir+'/server.crt'),rejectUnauthorized:true});
  await pub(secure,'iot/security/sv01/sensor',JSON.stringify({simulated:true,transport:'tls',temp:28.5}));await wait(350);
  log('TLS CA verified; no trust store modification, no TLS key-log file.');
 }else if(mode==='14.2'){
  const receiver=await connect('pc-hmac-verifier'),sender=await connect('pc-command-sender');await sub(receiver,'iot/security/sv01/cmd');
  const key=crypto.randomBytes(32);let highest=0;
  receiver.on('message',(t,p)=>{const d=JSON.parse(p);const canonical=`${d.cmd}|${d.time}|${d.nonce}|${d.seq}`;const expected=crypto.createHmac('sha256',key).update(canonical).digest('hex');
   const valid=crypto.timingSafeEqual(Buffer.from(d.mac),Buffer.from(expected));
   const result=valid&&Math.abs(Date.now()/1000-d.time)<=10&&d.seq>highest?'ACCEPT':'REJECT replay/stale/MAC';
   if(result==='ACCEPT')highest=d.seq;log('PC_VERIFIER',result,'seq',d.seq);pub(receiver,'iot/security/sv01/result',result).catch(console.error);
  });
  const d={cmd:'OPEN',time:Math.floor(Date.now()/1000),nonce:crypto.randomBytes(8).toString('hex'),seq:1};
  d.mac=crypto.createHmac('sha256',key).update(`${d.cmd}|${d.time}|${d.nonce}|${d.seq}`).digest('hex');
  const payload=JSON.stringify(d);await pub(sender,'iot/security/sv01/cmd',payload);await wait(400);await pub(sender,'iot/security/sv01/cmd',payload);await wait(500);
  log('Same payload replayed. This PC test does not validate ESP GPIO or NVS persistence.');
 }else if(mode==='14.3'){
  const watcher=await connect('pc-resilience-watch');await sub(watcher,'iot/resilience/sv01/#');
  const d=await connect('pc-reconnecting-client',{reconnectPeriod:500});await sub(d,'iot/resilience/sv01/cmd');
  for(let i=0;i<10;i++){await pub(watcher,'iot/resilience/sv01/cmd',i%2?'ON':'OFF');await wait(100);}
  const reconnect=once(d,'connect');log('FAULT: terminate only test client socket');d.stream.destroy();await reconnect;log('RECONNECTED');
  await pub(d,'iot/resilience/sv01/state','online');await wait(400);
 }
}
async function coapCases(){
 const coap=require(root+'/node_modules/coap'),packet=require(root+'/node_modules/coap-packet');
 service=require(root+'/BTH13_COAP/node/server.cjs').start({port:5683,interval:5000});await service.ready;
 const agent=new coap.Agent({type:'udp4'});
 const request=(path,opt={})=>new Promise((resolve,reject)=>{const q=coap.request({hostname:'127.0.0.1',port:5683,pathname:path,agent,...opt});q.on('error',reject);q.on('response',resolve);q.end(opt.method==='POST'?'temp=30.5;simulated=true':undefined);});
 try{
  if(mode==='13.1-base'){
   for(const confirmable of [false,true]){const r=await request('/sensor/temp',{method:'POST',confirmable});log(confirmable?'CON':'NON',r.code,r.payload.toString());await wait(300);}
  }else if(mode==='13.1-retry'){
   proxy=require(root+'/BTH13_COAP/node/drop-proxy.cjs').start();await proxy.ready;
   const r=await request('/sensor/temp',{port:5684,method:'POST',confirmable:true});log('RETRY_RESULT',r.code,r.payload.toString());
  }else if(mode==='13.2-poll'){
   for(let i=0;i<30;i++){const begin=Date.now();const r=await request('/sensor/temp');log('POLL',i+1,r.payload.toString());await wait(Math.max(0,2000-(Date.now()-begin)));}
  }else if(mode==='13.2-observe'){
   const r=await request('/sensor/temp',{observe:true});let count=0;r.on('data',d=>log('NOTIFY',++count,d.toString()));await wait(60000);r.close();
  }else if(mode==='13.3'){
   const udp=require('node:dgram').createSocket('udp4');await new Promise(r=>udp.bind(0,'127.0.0.1',r));let all=Buffer.alloc(0);
   try{for(let n=0;n<16;n++){
    const encoded=Buffer.from([(n<<4)|3]);const raw=packet.generate({messageId:1000+n,token:Buffer.from([4,2]),code:'0.01',confirmable:true,options:[{name:'Uri-Path',value:Buffer.from('firmware')},{name:'Block2',value:encoded}]});
    const incoming=new Promise((r,j)=>{const timer=setTimeout(()=>j(Error('block timeout')),2000);udp.once('message',b=>{clearTimeout(timer);r(packet.parse(b));});});udp.send(raw,5683,'127.0.0.1');const response=await incoming;
    if(response.payload.length!==128)throw Error('Expected 128B block');all=Buffer.concat([all,response.payload]);log('BLOCK',n,'BYTES',response.payload.length);await wait(80);
   }if(!all.equals(Buffer.alloc(2048,65)))throw Error('Reassembly mismatch');log('REASSEMBLY_PASS',all.length,'SHA256',crypto.createHash('sha256').update(all).digest('hex'));
   }finally{udp.close();}
  }
 }finally{
  // Closing an Observe response may already close its agent's UDP socket.
  try{agent.close();}catch(e){if(e.code!=='ERR_SOCKET_DGRAM_NOT_RUNNING')throw e;}
  if(proxy)await proxy.close();await service.close();service=null;
 }
}
(async()=>{
 try{if(mode.startsWith('13.'))await coapCases();else await mqttCases();log('EXPERIMENT_PASS',mode);}
 catch(e){console.error(e);process.exitCode=1;}
 finally{
  for(const c of clients)if(!c.disconnected)await close(c);
  if(broker)await new Promise(r=>broker.close(r));
  for(const s of servers)if(s.listening)await new Promise(r=>s.close(r));
  setTimeout(()=>process.exit(process.exitCode||0),100).unref();
 }
})();
