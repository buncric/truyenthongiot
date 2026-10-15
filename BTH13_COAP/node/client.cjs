const coap=require('coap');
const mode=process.argv[2]||'con',host=process.env.COAP_HOST||'127.0.0.1',port=Number(process.env.COAP_PORT||5683);
if(!['con','non','poll','observe','block'].includes(mode))throw Error('Use con/non/poll/observe/block');
const observe=mode==='observe';let timer;
function request(){
 const req=coap.request({hostname:host,port,pathname:mode==='block'?'/firmware':'/sensor/temp',method:['con','non'].includes(mode)?'POST':'GET',confirmable:mode!=='non',observe});
 req.on('error',e=>{console.error(e.message);process.exitCode=1;if(timer)clearInterval(timer);coap.globalAgent.close();});
 req.on('response',res=>{
  if(observe){res.on('data',d=>console.log('NOTIFY',d.toString()));setTimeout(()=>{res.close();coap.globalAgent.close();},20000);}
  else{console.log('RESPONSE',res.code,'bytes=',res.payload.length,mode==='block'?'':'payload='+res.payload.toString());if(mode!=='poll')coap.globalAgent.close();}
 });
 req.end(['con','non'].includes(mode)?'temp=30.5':undefined);
}
request();if(mode==='poll'){timer=setInterval(request,2000);setTimeout(()=>{clearInterval(timer);coap.globalAgent.close();},20000);}
