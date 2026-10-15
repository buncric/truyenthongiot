# Kiểm thử và giới hạn thực nghiệm

Cập nhật ngày 16/10/2026. Không coi compile/test trên PC là bằng chứng board thật đã chạy.

## Đã thực hiện trên máy hiện tại

| Kiểm tra | Kết quả |
|---|---|
| Arduino CLI: 21 sketch mới | PASS compile/link cho board liệt kê dưới đây |
| NS-3 Linux GitHub Actions | PASS compile +6 cấu hình LTE; [số liệu và nguồn](../BTH10_NB_IOT_LTE/ket-qua/README.md) |
| Node.js syntax (`npm run check`) | PASS |
| Web Bluetooth backend ở chế độ DEMO | PASS HTTP connect/disconnect, kiểm tra lệnh, lỗi trạng thái và luồng WebSocket |
| CoAP server/client chạy UDP thật trên loopback | PASS CON/NON, 4.04, Observe ít nhất hai notification |
| CoAP Block2 | PASS 2048 byte A; kiểm tra cả reassembly của thư viện và 16 request block128byte |
| CoAP mất phản hồi | PASS proxy drop một reply; client CON gửi lại và nhận cached reply |
| Python unittest (3 test) | PASS quy đổi đơn vị/FlowMonitor, file không có flow, các trường được ràng buộc trong HMAC |
| ESPHome 2026.9.1 `config` | PASS YAML Wemos, ESP32-S3 RGB và ESP32-S3 RGB + DHT11 với secrets thử sinh riêng ngoài repo; chưa compile/flash ESPHome firmware |
| SerialPort native binding Windows | PASS load và liệt kê được cổng; chưa mở cổng thiết bị để tránh chiếm phiên đang dùng |
| npm audit sau cập nhật ws8.22.0 | 0 vulnerability được báo ở thời điểm kiểm tra |
| Tài liệu | 31 mục chính, 139 hình theo bước (132 render Blender + 7 ảnh thao tác 8.1), 2 ảnh mạch thật 8.1; kiểm tra liên kết và SHA256 của 13 PDF nguồn |

Node integration test dùng socket thật; dữ liệu nhiệt độ của demo là mô phỏng. Fixture XML của unittest chỉ dùng kiểm tra công thức, không được xuất như kết quả LTE đo thật.

## Chưa có bằng chứng thực nghiệm

- Chưa upload/nạp board qua COM, chưa đo LED/DHT/RTC/MAX7219 hoặc điện áp ngoài mạch.
- Chưa mở/chạy GUI Proteus và Packet Tracer trong phiên này. File người dùng cung cấp được giữ nguyên; các bài4.2/4.3 có hướng dẫn và bảng conditions nhưng chưa có bản Save As .pkt hoàn tất được xác nhận.
- Chưa cài Debian/HAOS vào VM, ghép dongle/thiết bị Zigbee, thu pcap Zigbee hoặc Wi-Fi thật.
- NS-3 chưa chạy Linux cục bộ, nhưng đã build/run thành công trên GitHub Actions. Bảng số liệu mô phỏng thật và đường dẫn artifact nằm trong bài10; không thay cho đo mạng LTE/NB-IoT thực.
- Chưa có broker/chứng chỉ lab thật để đo TLS handshake; chưa kiểm tra replay/NVS/watchdog trên board.

## Môi trường compile Arduino

Arduino AVR core1.8.8, ESP8266 core3.1.2, ESP32 core3.3.12. RTClib2.1.4, Adafruit BusIO1.17.4, LiquidCrystal_I2C2.0.0, DHT sensor library1.4.7, Adafruit Unified Sensor1.1.15, PubSubClient2.8, ArduinoJson7.4.3.

ESP32 compile/link bình thường thành công. Bước export với `--output-dir` của core3.3.12 gọi Windows PowerShell bị lỗi thiếu assembly trên host; công cụ compile trong repo bỏ bước export cho ESP32 và ghi log của compile/link thành công. Không sửa core hoặc Windows để né lỗi. Binary AVR mới được lưu trong firmware/; binary ESP dùng cấu hình placeholder không được quảng bá như firmware đã cấu hình mạng thật.

| Sketch | FQBN | Compile | Log |
|---|---|---|---|
| [BTH02_UART/2.1_ESP8266_Bridge/2.1_ESP8266_Bridge.ino](../BTH02_UART/2.1_ESP8266_Bridge/2.1_ESP8266_Bridge.ino) | `esp8266:esp8266:nodemcuv2` | PASS | [log](build-logs/2.1_ESP8266_Bridge/compile.txt) |
| [BTH02_UART/2.1_UNO_LED/2.1_UNO_LED.ino](../BTH02_UART/2.1_UNO_LED/2.1_UNO_LED.ino) | `arduino:avr:uno` | PASS | [log](build-logs/2.1_UNO_LED/compile.txt) |
| [BTH02_UART/2.2_Baud_Button/2.2_Baud_Button.ino](../BTH02_UART/2.2_Baud_Button/2.2_Baud_Button.ino) | `arduino:avr:uno` | PASS | [log](build-logs/2.2_Baud_Button/compile.txt) |
| [BTH03_SPI_I2C/3.1_RTC_Serial/3.1_RTC_Serial.ino](../BTH03_SPI_I2C/3.1_RTC_Serial/3.1_RTC_Serial.ino) | `arduino:avr:uno` | PASS | [log](build-logs/3.1_RTC_Serial/compile.txt) |
| [BTH03_SPI_I2C/3.2_Alarm_Clock/3.2_Alarm_Clock.ino](../BTH03_SPI_I2C/3.2_Alarm_Clock/3.2_Alarm_Clock.ino) | `arduino:avr:uno` | PASS | [log](build-logs/3.2_Alarm_Clock/compile.txt) |
| [BTH03_SPI_I2C/3.3_MAX7219/3.3_MAX7219.ino](../BTH03_SPI_I2C/3.3_MAX7219/3.3_MAX7219.ino) | `arduino:avr:uno` | PASS | [log](build-logs/3.3_MAX7219/compile.txt) |
| [BTH05_BLUETOOTH/5.1_AT_Bridge/5.1_AT_Bridge.ino](../BTH05_BLUETOOTH/5.1_AT_Bridge/5.1_AT_Bridge.ino) | `arduino:avr:uno` | PASS | [log](build-logs/5.1_AT_Bridge/compile.txt) |
| [BTH05_BLUETOOTH/5.3_LED_Control/5.3_LED_Control.ino](../BTH05_BLUETOOTH/5.3_LED_Control/5.3_LED_Control.ino) | `arduino:avr:uno` | PASS | [log](build-logs/5.3_LED_Control/compile.txt) |
| [BTH05_BLUETOOTH/5.4_DHT11/5.4_DHT11.ino](../BTH05_BLUETOOTH/5.4_DHT11/5.4_DHT11.ino) | `arduino:avr:uno` | PASS | [log](build-logs/5.4_DHT11/compile.txt) |
| [BTH12_MQTT/12.1_Telemetry/12.1_Telemetry.ino](../BTH12_MQTT/12.1_Telemetry/12.1_Telemetry.ino) | `esp8266:esp8266:d1_mini` | PASS | [log](build-logs/12.1_Telemetry/compile.txt) |
| [BTH12_MQTT/12.2_LED_Command/12.2_LED_Command.ino](../BTH12_MQTT/12.2_LED_Command/12.2_LED_Command.ino) | `esp8266:esp8266:d1_mini` | PASS | [log](build-logs/12.2_LED_Command/compile.txt) |
| [BTH12_MQTT/12.3_Retain_LWT/12.3_Retain_LWT.ino](../BTH12_MQTT/12.3_Retain_LWT/12.3_Retain_LWT.ino) | `esp8266:esp8266:d1_mini` | PASS | [log](build-logs/12.3_Retain_LWT/compile.txt) |
| [BTH13_COAP/13.1_CON/13.1_CON.ino](../BTH13_COAP/13.1_CON/13.1_CON.ino) | `esp8266:esp8266:d1_mini` | PASS | [log](build-logs/13.1_CON/compile.txt) |
| [BTH13_COAP/13.1_NON/13.1_NON.ino](../BTH13_COAP/13.1_NON/13.1_NON.ino) | `esp8266:esp8266:d1_mini` | PASS | [log](build-logs/13.1_NON/compile.txt) |
| [BTH13_COAP/13.2_Observe/13.2_Observe.ino](../BTH13_COAP/13.2_Observe/13.2_Observe.ino) | `esp8266:esp8266:d1_mini` | PASS | [log](build-logs/13.2_Observe/compile.txt) |
| [BTH13_COAP/13.2_Poll/13.2_Poll.ino](../BTH13_COAP/13.2_Poll/13.2_Poll.ino) | `esp8266:esp8266:d1_mini` | PASS | [log](build-logs/13.2_Poll/compile.txt) |
| [BTH13_COAP/13.3_Blockwise/13.3_Blockwise.ino](../BTH13_COAP/13.3_Blockwise/13.3_Blockwise.ino) | `esp8266:esp8266:d1_mini` | PASS | [log](build-logs/13.3_Blockwise/compile.txt) |
| [BTH14_BAO_MAT/14.1_TLS/14.1_TLS.ino](../BTH14_BAO_MAT/14.1_TLS/14.1_TLS.ino) | `esp32:esp32:esp32` | PASS | [log](build-logs/14.1_TLS/compile.txt) |
| [BTH14_BAO_MAT/14.2_Anti_Replay/14.2_Anti_Replay.ino](../BTH14_BAO_MAT/14.2_Anti_Replay/14.2_Anti_Replay.ino) | `esp32:esp32:esp32` | PASS | [log](build-logs/14.2_Anti_Replay/compile.txt) |
| [BTH14_BAO_MAT/14.2_Vulnerable/14.2_Vulnerable.ino](../BTH14_BAO_MAT/14.2_Vulnerable/14.2_Vulnerable.ino) | `esp32:esp32:esp32` | PASS | [log](build-logs/14.2_Vulnerable/compile.txt) |
| [BTH14_BAO_MAT/14.3_Resilience/14.3_Resilience.ino](../BTH14_BAO_MAT/14.3_Resilience/14.3_Resilience.ino) | `esp32:esp32:esp32` | PASS | [log](build-logs/14.3_Resilience/compile.txt) |

## Tái lập

```bash
npm ci
npm run check
npm test
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/validate_repo.py
python tools/compile_arduino.py --cli arduino-cli --jobs 2
```

`arduino-results.json` lưu hash source .ino và board; các log build nằm trong build-logs/. Khi đổi .ino/header/config hoặc core, phải compile lại. Các file cấu hình cần credential thật sử dụng example để kiểm tra compile, không mặc định kết nối thành công.

## Bổ sung hình thực tế và mô hình Blender

- Bài 8.1: 7 ảnh thao tác người dùng cung cấp (2 ảnh đã che mật khẩu), 2 ảnh board thật giữ nguyên. Ảnh chứng minh trạng thái LED nhìn thấy; chưa có ảnh giao diện web tương ứng để xác nhận thao tác điều khiển từ xa.
- 30 cảnh `.blend` thực sự dựng và render bằng Blender 4.5.14 LTS; 132 ảnh 1800×1200 gắn theo bước. Đã xem toàn bộ 30 cảnh ở bản tổng quan, kiểm tra thêm các cảnh chi tiết và mở lại file Blender để render. Các cảnh là mô hình hình học và diễn họa luồng tín hiệu, chưa mô phỏng mạch điện hay chạy firmware.
- 84 hình UI/mạch trích đúng vùng hình trong PDF gốc, có manifest ghi PDF, trang và tọa độ. 3 ảnh linh kiện Commons giữ nguyên, có tác giả và giấy phép; nguồn ảnh bổ sung dẫn trực tiếp tới trang chủ sở hữu.
- Nguồn Python dựng cảnh, file Blender, JPEG và manifest đều nằm trong [thư mục mô phỏng](../mo-phong-3d/README.md). Không coi góc camera hoặc hạt tín hiệu trên timeline là dữ liệu đo.

[Báo cáo mở lại 30 file Blender và kiểm tra đủ 132 mốc bước](blender-results.json). Có thể tái lập bằng `blender -b --python-exit-code 1 --python tools/check_blender.py` từ thư mục gốc repo; chương trình render lại ba cảnh đại diện vào thư mục tạm, không ghi đè kết quả thực nghiệm.
