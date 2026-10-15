// Single-client UDP fault injector, default loopback. Drop an actual reply on the wire.
const dgram=require('node:dgram');
function start({port=5684,targetPort=5683,drop=1,host='127.0.0.1'}={}){
 const incoming=dgram.createSocket('udp4'),outgoing=dgram.createSocket('udp4');let client,remaining=drop;
 incoming.on('message',(packet,rinfo)=>{client=rinfo;console.log('FORWARD request MID',packet.readUInt16BE(2));outgoing.send(packet,targetPort,'127.0.0.1');});
 outgoing.on('message',packet=>{if(remaining>0){remaining--;console.log('DROP reply MID',packet.readUInt16BE(2));return;}if(client)incoming.send(packet,client.port,client.address);});
 incoming.on('error',console.error);outgoing.on('error',console.error);const ready=new Promise(resolve=>incoming.bind(port,host,resolve));
 return {ready,close:()=>new Promise(resolve=>{incoming.close(()=>outgoing.close(resolve));})};
}
if(require.main===module)start({drop:Number(process.env.DROP||1),host:process.env.HOST||'127.0.0.1'});
module.exports={start};
