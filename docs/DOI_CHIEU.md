# Đối chiếu toàn bộ yêu cầu

| Nguồn | Các yêu cầu được triển khai | Vị trí |
|---|---|---|
| BTH2_UART, trang3–7 | UART ESP8266↔Uno, đổi baud qua nút, mục DS1307 bị lặp | BTH02_UART/2.1–2.3.md; DS1307 dẫn sang3.1 |
| BTH3_SPI_I2C, trang3–9 | RTC Serial, báo thức4nút/EEPROM, MAX7219×4 | BTH03_SPI_I2C/3.1–3.3.md |
| BTH4, trang3–13 | Mạng nhà, đèn chuyển động, IDS còi/camera | BTH04_ETHERNET_TCPIP/4.1–4.3.md |
| BTH5, trang3–13 | AT HC05, COMảo, web LED, DHT11/WebSocket/chart | BTH05_BLUETOOTH/5.1–5.4.md |
| BTH6_ZigBee, trang3–11 | MAC/NWK, APS/ZCL On/Off/Report, Join/Key Transport | BTH06_ZIGBEE/6.1–6.3.md |
| BTH6_Cai_dat_DebianOS, toàn bộ17trang | VirtualBox, Debian, SSH | BTH06_ZIGBEE/CAI_DAT.md |
| BTH6_Cai_dat_HomeAssistant_MQTT_Broker, toàn bộ15trang | HA, broker pub/sub, dongle firmware/passthrough, Z2M/pairing | BTH06_ZIGBEE/CAI_DAT.md |
| BTH8, trang3–14 | ESPHome, Wireshark, sensor, automation | BTH08_WIFI/8.1–8.4.md |
| BTH9, toàn bộ5trang | Công cụLinux, NS-3, NetAnim và CLI | BTH09_NS3/9.1.md |
| BTH10, trang3–9 | LTE cơ bản, tăngUE/đổi khoảng cách/thời gian, FlowMonitor | BTH10_NB_IOT_LTE/10.1.md |
| BTH12, trang3–26 | telemetry, cmd/state, retain/LWT + câu hỏi | BTH12_MQTT/12.1–12.3.md |
| BTH13, trang3–19 | CON/NON/retry, Poll/Observe, Blockwise + câu hỏi | BTH13_COAP/13.1–13.3.md |
| BTH14, trang3–16 | TLS, replay và phòng vệ, tải hữu hạn/recovery/watchdog + câu hỏi | BTH14_BAO_MAT/14.1–14.3.md |

## Hiệu chỉnh so với ví dụ gốc

- Bài2 và5 ghi số bài nhỏ1.x; repo chuẩn hóa thành2.x và5.x. MụcI²C ởUART trùng3.1, giữ một triển khai và dẫn liên kết.
- Thư mục cũ mang tênSPI_I2C nhưng chứaUART được lưu trữ nguyên trạng; không gọiUART làSPI.
- HC05/06 làSPP, web dùng backendSerial. RX củaESP/HC05 vàKEY cần đúng mức3.3V.
- Báo thức sửa buffer định dạng để không tràn bộ nhớ; giữ nguyên code người dùng ởproject-goc để đối chiếu.
- Bài4 thống nhất tài khoản IoTServer và mật khẩuWPA2 tối thiểu8ký tự; trạng thái camera mô phỏng không được coi là video thật.
- Cài HA mới dùngHAOS vìSupervised hết hỗ trợ; đề gốc vẫn được bảo toàn để đối chiếu lịch sử.
- ESP8266 OTA mặc định8266, ESP32 là3232; capture unicast cần đúng điểm mạng, không chỉ cùngLAN.
- LTE thêm UDPapps/route đểFlowMonitor cóflow; không đổi kết quảLTE thànhNB-IoT.
- MQTT phân biệtretainstate,retainedcommand vàLWT; PubSubClient publishQoS0.
- CoAP có xử lýUDPloop,retry thật,Observe và nhận đủBlock2; mấtACK mô phỏng quaUDPproxy vìthư việncóthể tựACK.
- TLS kiểm chứngCA/SAN vàthời gian; replaydùngHMAC+sequencebềnvững, khôngchỉtimestamp; thửmấtkếtnối thaycho gây nhiễu/deauth.

Các nhận xét phiên bản tham khảo [nguồn chính thức](NGUON_THAM_KHAO.md). Các trường địa chỉ, frame number, số đo chỉ điền từ thí nghiệm thật.
