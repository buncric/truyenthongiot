import importlib.util, unittest, tempfile, json, hashlib, hmac
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
flow=module('flow','BTH10_NB_IOT_LTE/analyze_flow.py')
commands=module('commands','BTH14_BAO_MAT/python/commands.py')
class AnalysisTests(unittest.TestCase):
    def test_time_units_and_flow_metrics(self):
        for value,expected in [('1000000000ns',1),('+2e3ms',2),('500us',.0005)]:self.assertAlmostEqual(flow.seconds(value),expected)
        xml='<FlowMonitor><FlowStats><Flow flowId="1" txPackets="10" rxPackets="8" txBytes="1280" rxBytes="1024" timeFirstTxPacket="+1e9ns" timeLastRxPacket="+3e9ns" delaySum="+80ms" minDelay="+1ms" maxDelay="+20ms" /></FlowStats><Ipv4FlowClassifier><Flow flowId="1" sourceAddress="1.0.0.2" destinationAddress="7.0.0.2" /></Ipv4FlowClassifier></FlowMonitor>'
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'synthetic-test-only.xml';p.write_text(xml);row=flow.analyze(p)[0]
        self.assertEqual(row['sourceAddress'],'1.0.0.2');self.assertEqual(row['delivery_ratio'],.8);self.assertAlmostEqual(row['mean_delay_ms'],10);self.assertAlmostEqual(row['throughput_kbps'],4.096)
    def test_empty_capture_is_not_a_fake_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'empty.xml';p.write_text('<FlowMonitor/>');self.assertEqual(flow.analyze(p),[])
    def test_signed_fields_are_authenticated(self):
        value=commands.sign('OPEN',1700000000,'0123456789abcdef',123,'unit-test-key')
        expected=hmac.new(b'unit-test-key',b'OPEN|1700000000|0123456789abcdef|123',hashlib.sha256).hexdigest()
        self.assertEqual(value['mac'],expected)
        for args in [('CLOSE',1700000000,'0123456789abcdef',123),('OPEN',1700000001,'0123456789abcdef',123),('OPEN',1700000000,'1123456789abcdef',123),('OPEN',1700000000,'0123456789abcdef',124)]:
            self.assertNotEqual(commands.sign(*args,'unit-test-key')['mac'],expected)
if __name__=='__main__':unittest.main()
