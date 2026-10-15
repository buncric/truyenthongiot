# Bài tập thực hành Truyền thông trong IoT

Đây là nơi em lưu chương trình, hình ảnh và ghi chép khi làm các bài thực hành của môn Truyền thông trong IoT. Các bài được chia theo đề, từ UART, SPI/I²C đến MQTT, CoAP và bảo mật. Trong từng bài có sơ đồ nối dây, cách chạy và phần nhận xét sau khi kiểm tra.

[Chuẩn bị môi trường](docs/BAT_DAU.md) · [Đối chiếu với đề](docs/DOI_CHIEU.md) · [Ghi chép kiểm tra chương trình](docs/KIEM_THU.md) · [Tài liệu môn học](tai-lieu-goc/README.md).

## Những phần đã làm

Ở phần [MQTT, CoAP và bảo mật](docs/wireshark-thuc-te/README.md), em chạy các chương trình trên PC rồi mở bản ghi bằng Wireshark để phân tích. Có 18 ảnh và 11 file PCAPNG, trong đó thấy được Retain/Last Will, CoAP gửi lại, Polling/Observe, Block2, TLS và phản hồi khi phát lại lệnh. Các số liệu cảm biến trong phần này là dữ liệu mô phỏng.

[Bài 8.1](BTH08_WIFI/8.1.md) ghi lại cách tạo thiết bị ESPHome và nạp cho ESP32-S3 bằng USB, kèm bảy ảnh thao tác và hai ảnh board. Phần [LTE](BTH10_NB_IOT_LTE/ket-qua/README.md) có bảng kết quả sáu cấu hình NS-3 đã chạy trên GitHub Actions.

Với Zigbee, em hiện chỉ có USB CC2531. Dongle đã nhận trong Wireshark nhưng lần quét ngắn chưa thu gói, nên em dùng [bản ghi mẫu để đọc MAC/NWK và quá trình join](BTH06_ZIGBEE/ket-qua/README.md).

Những phần chưa đủ linh kiện có [hình Blender 3D](mo-phong-3d/README.md) để xem cách bố trí và luồng tín hiệu. Đây là hình minh họa; kết quả chạy chương trình được ghi riêng trong từng bài. [Ảnh linh kiện tham khảo](docs/linh-kien/README.md) và [hình trích từ đề](docs/giao-dien-goc/README.md) có đường dẫn nguồn đi kèm.

## Các bài thực hành

| Bài thực hành | Nội dung | Các mục |
|---|---|---|
| 2 | [Bài thực hành 2 - UART](BTH02_UART/README.md) | 2.1, 2.2, 2.3 |
| 3 | [Bài thực hành 3 - SPI và I²C](BTH03_SPI_I2C/README.md) | 3.1, 3.2, 3.3 |
| 4 | [Bài thực hành 4 - Ethernet và TCP/IP](BTH04_ETHERNET_TCPIP/README.md) | 4.1, 4.2, 4.3 |
| 5 | [Bài thực hành 5 - Bluetooth](BTH05_BLUETOOTH/README.md) | 5.1, 5.2, 5.3, 5.4 |
| 6 | [Bài thực hành 6 - Zigbee](BTH06_ZIGBEE/README.md) | 6.1, 6.2, 6.3 |
| 8 | [Bài thực hành 8 - Wi-Fi / ESPHome](BTH08_WIFI/README.md) | 8.1, 8.2, 8.3, 8.4 |
| 9 | [Bài thực hành 9 - Cài NS-3 / NetAnim](BTH09_NS3/README.md) | 9.1 |
| 10 | [Bài thực hành 10 - NB-IoT / LTE](BTH10_NB_IOT_LTE/README.md) | 10.1 |
| 12 | [Bài thực hành 12 - MQTT](BTH12_MQTT/README.md) | 12.1, 12.2, 12.3 |
| 13 | [Bài thực hành 13 - CoAP](BTH13_COAP/README.md) | 13.1, 13.2, 13.3 |
| 14 | [Bài thực hành 14 - Bảo mật](BTH14_BAO_MAT/README.md) | 14.1, 14.2, 14.3 |

Đề được giao không có bài 7 và bài 11. Hai tài liệu cài Debian và Home Assistant/MQTT Broker được đặt trong phần chuẩn bị của bài 6.

## Mở và chạy chương trình

- **Arduino/ESP:** mở `.ino` trong thư mục cùng tên, cài đúng core/thư viện và biên dịch cho board ghi trong hướng dẫn. Nếu có `config.example.h`, sao thành `config.local.h` và nhập thông tin mạng của bạn. Với AVR, thư mục `firmware/` chứa HEX biên dịch từ mã mới để dùng Proteus.
- **Proteus và Packet Tracer:** file project ban đầu nằm trong `project-goc/` của bài 2, 3, 4. Khi mở trên máy khác, cần chọn lại đường dẫn HEX trong Program File. Các mục chưa chạy lại trên phần mềm được ghi trong phần kết quả của bài.
- **Phần mềm PC:** từ gốc repo chạy `npm ci`, sau đó `npm run demo --workspace iot-bluetooth-web` hoặc `npm start --workspace iot-coap-labs`.
- **Linux/NS-3:** bài 9 có script cài cố định ns-3.43; bài 10 có mã LTE/EPC, traffic generator, NetAnim và trình phân tích FlowMonitor.
- **ESPHome/HA:** dùng YAML ở bài 8, sao secrets.example.yaml thành secrets.yaml và điền thông tin cục bộ. Biến thể [ESP32-S3 đã có](BTH_WIFI_ESPHOME/README.md) được giữ lại.

## Ghi chú khi xem bài

Mỗi bài ghi rõ phần đã chạy và phần còn cần thử trên mạch. Em giữ log biên dịch, file bắt gói và số liệu ở các thư mục kết quả để tiện đối chiếu. Bảng tổng hợp phiên bản công cụ và các lần kiểm tra nằm trong [KIEM_THU.md](docs/KIEM_THU.md).

## Các file cũ

Các file UART cũ ở gốc, thư mục 1.2, BareMinimum và ảnh trước đây vẫn được giữ. Phần UART từng đặt trong thư mục `BTH3_SPI_I2C` được chuyển sang [thư mục lưu trữ](luu-tru/uart-truoc-khi-phan-loai); các bài SPI/I²C hiện nằm ở BTH03_SPI_I2C.

## Chạy kiểm tra

```bash
npm ci
npm run check
npm test
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/validate_repo.py
python tools/compile_arduino.py --cli arduino-cli --jobs 2
```

[Danh sách các mục](docs/catalog.json) lưu số bài và đường dẫn để tiện kiểm tra. Thông tin Wi-Fi, khóa riêng và khóa mạng được để trong file cấu hình cục bộ.
