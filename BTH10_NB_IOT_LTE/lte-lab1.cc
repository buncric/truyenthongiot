// LTE/EPC baseline, not an NB-IoT radio model. Tested API target: ns-3.43.
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/lte-module.h"
#include "ns3/mobility-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/netanim-module.h"
using namespace ns3;
int main(int argc,char* argv[]){
 uint16_t nUe=1;double distance=20,simTime=10;
 CommandLine cmd(__FILE__);cmd.AddValue("nUe","Number of UEs",nUe);cmd.AddValue("distance","UE distance in metres",distance);cmd.AddValue("simTime","Traffic stop time in seconds",simTime);cmd.Parse(argc,argv);
 NS_ABORT_MSG_IF(nUe<1 || nUe>100 || distance<0 || simTime<=1,"Use nUe=1..100, distance>=0, simTime>1");
 auto lte=CreateObject<LteHelper>();auto epc=CreateObject<PointToPointEpcHelper>();lte->SetEpcHelper(epc);
 NodeContainer enbs,ues,remote;enbs.Create(1);ues.Create(nUe);remote.Create(1);
 InternetStackHelper internet;internet.Install(remote);internet.Install(ues);
 PointToPointHelper p2p;p2p.SetDeviceAttribute("DataRate",StringValue("1Gbps"));p2p.SetChannelAttribute("Delay",TimeValue(MilliSeconds(10)));
 auto link=p2p.Install(epc->GetPgwNode(),remote.Get(0));Ipv4AddressHelper addr;addr.SetBase("1.0.0.0","255.255.255.0");addr.Assign(link);
 Ipv4StaticRoutingHelper routing;auto hostRoute=routing.GetStaticRouting(remote.Get(0)->GetObject<Ipv4>());hostRoute->AddNetworkRouteTo(Ipv4Address("7.0.0.0"),Ipv4Mask("255.0.0.0"),1);
 MobilityHelper mobility;mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");mobility.Install(enbs);mobility.Install(ues);
 enbs.Get(0)->GetObject<MobilityModel>()->SetPosition(Vector(0,0,0));
 for(uint16_t i=0;i<nUe;i++)ues.Get(i)->GetObject<MobilityModel>()->SetPosition(Vector(distance,i*5,0));
 auto enbDevices=lte->InstallEnbDevice(enbs);auto ueDevices=lte->InstallUeDevice(ues);auto ueIPs=epc->AssignUeIpv4Address(ueDevices);
 ApplicationContainer sinks,sources;
 for(uint16_t i=0;i<nUe;i++){
  auto ueRoute=routing.GetStaticRouting(ues.Get(i)->GetObject<Ipv4>());ueRoute->SetDefaultRoute(epc->GetUeDefaultGatewayAddress(),1);lte->Attach(ueDevices.Get(i),enbDevices.Get(0));
  uint16_t port=9000+i;PacketSinkHelper sink("ns3::UdpSocketFactory",InetSocketAddress(Ipv4Address::GetAny(),port));sinks.Add(sink.Install(ues.Get(i)));
  UdpClientHelper source(ueIPs.GetAddress(i),port);source.SetAttribute("Interval",TimeValue(MilliSeconds(100)));source.SetAttribute("MaxPackets",UintegerValue(100000));source.SetAttribute("PacketSize",UintegerValue(128));sources.Add(source.Install(remote.Get(0)));
 }
 sinks.Start(Seconds(.2));sources.Start(Seconds(1));sources.Stop(Seconds(simTime));sinks.Stop(Seconds(simTime+1));
 NodeContainer endpoints;endpoints.Add(ues);endpoints.Add(remote);FlowMonitorHelper flows;auto monitor=flows.Install(endpoints);
 AnimationInterface anim("lte.xml");anim.UpdateNodeDescription(enbs.Get(0),"eNodeB");for(uint16_t i=0;i<nUe;i++)anim.UpdateNodeDescription(ues.Get(i),"UE"+std::to_string(i));
 Simulator::Stop(Seconds(simTime+1));Simulator::Run();monitor->CheckForLostPackets();monitor->SerializeToXmlFile("lte-lab1.xml",true,true);Simulator::Destroy();
}
