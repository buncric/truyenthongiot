# Chuẩn bị và chạy nhanh

## Lấy mã nguồn

```bash
git clone git@github.com:buncric/truyenthongiot.git
cd truyenthongiot
```

Nếu đã có checkout, commit/cất thay đổi cá nhân trước khi cập nhật. Mở README của đúng bài trong bảng ở trang chính.

## Arduino IDE

1. Cài Arduino AVR Boards cho Uno, ESP8266 core 3.1.2 cho NodeMCU/D1 mini, ESP32 core 3.3.12 cho ESP32 DevKit. Những phiên bản này là môi trường compile ghi trong báo cáo; board khác có thể cần cấu hình khác.
2. Library Manager: RTClib 2.1.4 + Adafruit BusIO; LiquidCrystal_I2C 2.0.0; DHT sensor library 1.4.7 + Adafruit Unified Sensor; PubSubClient 2.8; ArduinoJson 7.4.3 cho replay. SPI/Wire/EEPROM/SoftwareSerial Uno đi theo core.
3. Mỗi thư mục sketch có file .ino cùng tên. Không mở đồng thời mọi .ino của các bài vào một sketch vì sẽ trùng setup/loop.
4. Chọn Board + Port, Verify trước, Upload sau. Dùng đúng cáp có truyền dữ liệu; nếu port bận, đóng Serial Monitor/backend đang giữ cổng.
5. Proteus Uno: dùng file HEX trong firmware của sketch mới, hoặc Export Compiled Binary từ Arduino IDE. Không nạp binary ESP vào model AVR.

## Demo web Bluetooth

```bash
npm ci
npm run demo --workspace iot-bluetooth-web
```

Mở http://127.0.0.1:3000, chọn DEMO, Connect. Trang hiển thị nhãn dữ liệu mô phỏng. Dừng Ctrl+C. Để dùng COM thực, chạy `npm start --workspace iot-bluetooth-web` và làm bài 5.3/5.4. Serial binding được kiểm tra trên máy Windows hiện tại; hệ điều hành khác có thể cần driver/quyền dialout.

## CoAP trên PC

Terminal thứ nhất:

```bash
npm start --workspace iot-coap-labs
```

Terminal thứ hai:

```bash
npm run client --workspace iot-coap-labs -- con
npm run client --workspace iot-coap-labs -- block
```

Khi dùng ESP, server phải nghe LAN. PowerShell: `$env:HOST='0.0.0.0'`, rồi chạy server; Linux: `HOST=0.0.0.0 npm start --workspace iot-coap-labs`. Cho phép UDP5683 từ mạng lab. Với proxy, UDP5684. Không tắt toàn bộ firewall chỉ để chạy một bài.

## Home Assistant / Zigbee / ESPHome

Đi theo BTH06_ZIGBEE/CAI_DAT.md trước; cài mới dùng HAOS VM. Không chạy script Supervised cũ lên host Windows. File secrets/config.local.h dùng giá trị riêng; bản example có placeholder để compile/đọc cấu trúc, chưa có khả năng kết nối mạng của bạn.

## Lưu kết quả từng lần làm

Sau khi chạy, tạo `ket-qua/` trong bài: ảnh mạch, trạng thái thiết bị, log Serial, file pcapng, project Save As hoặc XML. Bỏ/che credential và key trước khi commit. Đặt tên theo bài và bước, ghi board, phiên bản phần mềm, ngày thử và điều kiện thử. Sơ đồ hướng dẫn không thay cho ảnh đo thực.
