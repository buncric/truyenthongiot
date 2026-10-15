const coap=require('coap');
function start({port=5683,host='127.0.0.1',interval=5000}={}){
 let temp=30,observers=new Set();const server=coap.createServer({type:'udp4'});
 server.on('request',(req,res)=>{
  console.log(req.method,req.url,req.payload.toString());
  if(req.url==='/sensor/temp'&&req.method==='POST'){res.code='2.04';res.end('OK');return;}
  if(req.url==='/sensor/temp'&&req.method==='GET'){
   res.setOption('Content-Format','text/plain');
   if(req.headers.Observe===0){res.setOption('Observe',0);observers.add(res);res.on('finish',()=>observers.delete(res));res.on('close',()=>observers.delete(res));res.write(`temp=${temp.toFixed(1)}`);}
   else res.end(`temp=${temp.toFixed(1)}`);return;
  }
  if(req.url==='/firmware'&&req.method==='GET'){res.setOption('Content-Format','application/octet-stream');res.end(Buffer.alloc(2048,65));return;}
  res.code='4.04';res.end('Not Found');
 });
 const timer=setInterval(()=>{temp+=.5;for(const res of observers){try{res.write(`temp=${temp.toFixed(1)}`);}catch{observers.delete(res);}}},interval);
 const ready=new Promise(resolve=>server.listen(port,host,()=>{console.log(`CoAP ${host}:${port}; simulated temperature`);resolve();}));
 return {server,ready,close:()=>new Promise(resolve=>{clearInterval(timer);for(const res of observers)res.end();server.close(resolve);})};
}
if(require.main===module)start({port:Number(process.env.PORT||5683),host:process.env.HOST||'127.0.0.1'});
module.exports={start};
