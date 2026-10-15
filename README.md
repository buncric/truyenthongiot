# Truyền thông trong IoT - Các project thực hành

Bộ mã nguồn và hướng dẫn tiếng Việt theo toàn bộ tài liệu được cung cấp: **13 PDF / 174 trang**, chia thành **11 thư mục bài thực hành, 31 mục hướng dẫn**. Mỗi mục có chuẩn bị, nối dây/cấu hình, các bước kèm hình, tiêu chí kiểm tra, giải thích và trả lời câu hỏi.

**Bắt đầu:** [chạy nhanh và chuẩn bị môi trường](docs/BAT_DAU.md) · [đối chiếu yêu cầu](docs/DOI_CHIEU.md) · [kết quả kiểm thử và giới hạn](docs/KIEM_THU.md) · [toàn bộ tài liệu và hình gốc](tai-lieu-goc/README.md).

## Hình ảnh và mô hình thực hành

**[Ảnh Wireshark thực tế và file bắt gói](docs/wireshark-thuc-te/README.md):** 18 ảnh, 11 file PCAPNG cho 9 bài MQTT, CoAP và bảo mật. Có phân tích theo số frame, Polling/Observe 60 giây, ghép Block2 2048 byte, TLS và thử replay/kết nối lại. Traffic chạy thật giữa các chương trình trên PC; dữ liệu cảm biến là mô phỏng.

[Bài 8.1 theo ảnh ESP32-S3 thực tế](BTH08_WIFI/8.1.md) có 7 ảnh thao tác và 2 ảnh mạch bạn cung cấp. [30 cảnh Blender 3D](mo-phong-3d/README.md) minh họa các bài còn lại, kèm file `.blend` chỉnh sửa được và hình theo từng bước. [Ảnh linh kiện trên mạng](docs/linh-kien/README.md) ghi nguồn, tác giả và giấy phép; [84 hình giao diện/mạch trích PDF](docs/giao-dien-goc/README.md) giúp đối chiếu các nút và màn hình phần mềm.

Mô hình 3D hướng dẫn bố trí và luồng tín hiệu; kết quả chạy thật được ghi riêng trong [kiểm thử](docs/KIEM_THU.md). Với board ESP32-S3 hiện có, bài 8.3 bổ sung cấu hình DHT11 và bài 8.4 hướng dẫn chọn entity RGB thực tế.

## Danh mục project

| Bài thực hành | Project | Các mục |
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

Tài liệu nguồn **không có bài 7 và bài 11**; repository không tự đặt nội dung cho hai bài này. Hai PDF cài Debian và Home Assistant/MQTT Broker được tích hợp vào phần chuẩn bị của bài 6.

## Dùng các project

- **Arduino/ESP:** mở `.ino` trong thư mục cùng tên, cài đúng core/thư viện và biên dịch cho board ghi trong hướng dẫn. Nếu có `config.example.h`, sao thành `config.local.h` và nhập thông tin mạng của bạn. Với AVR, thư mục `firmware/` chứa HEX biên dịch từ mã mới để dùng Proteus.
- **Proteus và Packet Tracer:** các file người dùng cung cấp được giữ tại `project-goc/` của bài 2, 3, 4. Retarget Program File/HEX theo máy của bạn. Các bài mới yêu cầu thao tác trên simulator có hướng dẫn cấu hình cụ thể; không có file `.pkt` hay ảnh kết quả được tạo giả.
- **Phần mềm PC:** từ gốc repo chạy `npm ci`, sau đó `npm run demo --workspace iot-bluetooth-web` hoặc `npm start --workspace iot-coap-labs`.
- **Linux/NS-3:** bài 9 có script cài cố định ns-3.43; bài 10 có mã LTE/EPC, traffic generator, NetAnim và trình phân tích FlowMonitor.
- **ESPHome/HA:** dùng YAML ở bài 8, sao secrets.example.yaml thành secrets.yaml và điền thông tin cục bộ. Biến thể [ESP32-S3 đã có](BTH_WIFI_ESPHOME/README.md) được giữ lại.

## Trạng thái và nguồn hình

Mã nguồn và hướng dẫn đã được soạn; phần đã chạy kiểm thử được ghi riêng trong [KIEM_THU.md](docs/KIEM_THU.md). Compile thành công không đồng nghĩa đã nạp board và đo thực. Mỗi hình `*-buoc-*.png` là minh họa thao tác do repo biên soạn. Hình trang PDF là tài liệu gốc. Dữ liệu DEMO/simulated được ghi nhãn, không dùng làm số đo cảm biến thật.

## Nội dung có từ trước

Các file UART cũ ở gốc, thư mục 1.2, BareMinimum và hình chụp cũ vẫn được giữ. Thư mục `BTH3_SPI_I2C` cũ thực chất chứa UART đã chuyển nguyên trạng sang [luu-tru/uart-truoc-khi-phan-loai](luu-tru/uart-truoc-khi-phan-loai). Code mới đúng SPI/I²C ở BTH03_SPI_I2C. Các file nguồn trên ổ D ngoài checkout không bị sửa.

## Chạy kiểm tra

```bash
npm ci
npm run check
npm test
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/validate_repo.py
python tools/compile_arduino.py --cli arduino-cli --jobs 2
```

[Danh mục máy đọc được](docs/catalog.json) liệt kê từng mục và số bước. Không commit mật khẩu, CA private key, network key Zigbee hoặc capture chứa thông tin thật.
