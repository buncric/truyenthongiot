const express=require('express');
const http=require('node:http');
const path=require('node:path');
const {SerialPort}=require('serialport');
const {WebSocketServer}=require('ws');
function start({port=3000,demo=false}={}) {
 const app=express(), server=http.createServer(app), wss=new WebSocketServer({server});
 let serial=null,connected=false,pending=false,buffer='',timer;
 app.use(express.json({limit:'2kb'}));
 app.use((req,res,next)=>{
  // Local application: do not accept cross-origin control requests.
  if(req.headers.origin && req.headers.origin!==`http://${req.headers.host}`)return res.sendStatus(403);
  next();
 });
 app.use(express.static(path.join(__dirname,'public')));
 const broadcast=data=>{for(const socket of wss.clients)if(socket.readyState===1)socket.send(JSON.stringify(data));};
 const status=()=>({connected,demo});
 app.get('/status',(_,res)=>res.json(status()));
 app.get('/ports',async(_,res)=>{try{res.json(demo?[{path:'DEMO'}]:await SerialPort.list());}catch(e){res.status(500).json({error:e.message});}});
 app.post('/connect',async(req,res)=>{
  if(connected||pending)return res.status(409).json({error:'Already connected or opening'});
  pending=true;
  try{
   if(!demo){
    const ports=await SerialPort.list();
    if(!ports.some(p=>p.path===req.body.port))throw Error('Choose an available serial port');
    serial=new SerialPort({path:req.body.port,baudRate:9600,autoOpen:false});
    serial.on('error',e=>broadcast({error:e.message}));
    await new Promise((resolve,reject)=>serial.open(e=>e?reject(e):resolve()));
    serial.on('close',()=>{connected=false;buffer='';broadcast(status());});
    serial.on('data',chunk=>{
     buffer+=chunk.toString();
     if(buffer.length>8192){buffer='';return;}
     let split;
     while((split=buffer.indexOf('\n'))!==-1){
      const line=buffer.slice(0,split).trim();buffer=buffer.slice(split+1);
      try{const value=JSON.parse(line);if(Number.isFinite(value.temp)&&Number.isFinite(value.hum))broadcast({...value,demo:false,time:Date.now()});}
      catch{broadcast({log:line});}
     }
    });
   } else timer=setInterval(()=>broadcast({temp:28+Math.sin(Date.now()/5000)*2,hum:65,demo:true,time:Date.now()}),1000);
   connected=true;broadcast(status());res.json(status());
  }catch(e){if(serial?.isOpen)serial.close();serial=null;res.status(400).json({error:e.message});}
  finally{pending=false;}
 });
 app.post('/led',(req,res)=>{
  if(!connected)return res.status(409).json({error:'Connect first'});
  if(!['on','off'].includes(req.body.command))return res.status(400).json({error:'Use on/off'});
  if(demo){broadcast({log:`DEMO LED ${req.body.command}`});return res.json({ok:true,demo:true});}
  serial.write(req.body.command+'\n',e=>{if(e)return res.status(500).json({error:e.message});serial.drain(e=>e?res.status(500).json({error:e.message}):res.json({ok:true,demo:false}));});
 });
 app.post('/disconnect',(req,res)=>{
  clearInterval(timer);
  if(pending)return res.status(409).json({error:'Port opening'});
  if(serial?.isOpen)return serial.close(e=>{if(e)return res.status(500).json({error:e.message});connected=false;serial=null;res.json(status());});
  connected=false;serial=null;broadcast(status());res.json(status());
 });
 wss.on('connection',socket=>socket.send(JSON.stringify(status())));
 server.listen(port,'127.0.0.1',()=>console.log(`Bluetooth lab http://127.0.0.1:${server.address().port} ${demo?'DEMO DATA':'SERIAL'}`));
 return {server,close:()=>new Promise(resolve=>{clearInterval(timer);if(serial?.isOpen)serial.close();for(const c of wss.clients)c.terminate();wss.close();server.close(resolve);})};
}
if(require.main===module)start({port:Number(process.env.PORT||3000),demo:process.argv.includes('--demo')});
module.exports={start};
