const {test}=require('node:test'),assert=require('node:assert/strict'),{once}=require('node:events');
const coap=require('coap'),packet=require('coap-packet'),dgram=require('node:dgram');
const {start:coapStart}=require('../BTH13_COAP/node/server.cjs');
const {start:proxyStart}=require('../BTH13_COAP/node/drop-proxy.cjs');
const {start:webStart}=require('../BTH05_BLUETOOTH/web/server.cjs');
const WebSocket=require('ws');
test('Bluetooth demo validates LED commands and streams explicitly simulated readings',async()=>{
 const app=webStart({port:0,demo:true});await once(app.server,'listening');const url=`http://127.0.0.1:${app.server.address().port}`;
 const send=(p,body)=>fetch(url+p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 try{
  assert.equal((await send('/led',{command:'on'})).status,409);
  assert.equal((await fetch(url)).status,200);
  const c=await send('/connect',{});assert.deepEqual(await c.json(),{connected:true,demo:true});
  assert.equal((await send('/connect',{})).status,409);
  assert.equal((await send('/led',{command:'reboot'})).status,400);
  assert.equal((await send('/led',{command:'on'})).status,200);
  const ws=new WebSocket(url.replace('http:','ws:'));
  const sample=await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('No sensor stream')),3500);ws.on('message',data=>{const value=JSON.parse(data);if('temp' in value){clearTimeout(timeout);resolve(value);}});ws.on('error',reject);});
  assert.equal(sample.demo,true);assert.ok(sample.temp>25&&sample.temp<31);ws.close();
  assert.equal((await send('/disconnect',{})).status,200);
  assert.equal((await send('/led',{command:'off'})).status,409);
 }finally{await app.close();}
});
test('CoAP CON/NON, missing reply, Observe and all Block2 bytes',{timeout:20000},async()=>{
 const service=coapStart({port:15683,interval:100});await service.ready;
 const agent=new coap.Agent({type:'udp4'});
 const request=(pathname,options={})=>new Promise((resolve,reject)=>{const req=coap.request({hostname:'127.0.0.1',port:15683,pathname,agent,...options});req.on('error',reject);req.on('response',resolve);req.end(options.method==='POST'?'temp=30.5':undefined);});
 try{
  for(const confirmable of [true,false]){const response=await request('/sensor/temp',{method:'POST',confirmable});assert.equal(response.code,'2.04');assert.equal(response.payload.toString(),'OK');}
  const missing=await request('/missing');assert.equal(missing.code,'4.04');
  const firmware=await request('/firmware');assert.equal(firmware.payload.length,2048);assert.ok(firmware.payload.equals(Buffer.alloc(2048,65)));
  const obs=await request('/sensor/temp',{observe:true});
  await new Promise((resolve,reject)=>{let count=0;const timeout=setTimeout(()=>reject(Error('Missing observe notifications')),2000);obs.on('data',()=>{if(++count>=2){clearTimeout(timeout);resolve();}});});obs.close();
  // Explicit 128-byte Block2 requests mirror the ESP path rather than relying on agent reassembly.
  const udp=dgram.createSocket('udp4');await new Promise(resolve=>udp.bind(0,'127.0.0.1',resolve));
  try{let all=Buffer.alloc(0);
   for(let block=0;block<16;block++){
    const opt=(block<<4)|3,encoded=opt>255?Buffer.from([opt>>8,opt&255]):Buffer.from([opt]);
    const raw=packet.generate({messageId:1000+block,token:Buffer.from([4,2]),code:'0.01',confirmable:true,options:[{name:'Uri-Path',value:Buffer.from('firmware')},{name:'Block2',value:encoded}]});
    const incoming=new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Block timeout')),1500);udp.once('message',d=>{clearTimeout(timer);resolve(packet.parse(d));});});udp.send(raw,15683,'127.0.0.1');const response=await incoming;
    assert.equal(response.payload.length,128);const b=response.options.find(x=>x.name==='Block2').value;let value=0;for(const byte of b)value=(value<<8)|byte;
    assert.equal(value>>4,block);assert.equal(Boolean(value&8),block<15);all=Buffer.concat([all,response.payload]);
   }assert.ok(all.equals(Buffer.alloc(2048,65)));
  }finally{udp.close();}
  // Drop first response on wire; a real CON client retransmits and receives the cached reply.
  const proxy=proxyStart({port:15684,targetPort:15683,drop:1});await proxy.ready;
  const retryStart=Date.now();try{const response=await request('/sensor/temp',{port:15684,method:'POST',confirmable:true});assert.equal(response.code,'2.04');assert.ok(Date.now()-retryStart>=1800);}finally{await proxy.close();}
 }finally{agent.close();await service.close();}
});
