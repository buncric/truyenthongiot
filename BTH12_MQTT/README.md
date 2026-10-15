# Bài thực hành 12 - MQTT

[Ảnh Wireshark thực tế và file PCAPNG](../docs/wireshark-thuc-te/README.md): telemetry, cmd/state, Retain và Last Will chạy qua broker trên PC. Từng bài bên dưới có ảnh và số frame để đối chiếu.

Mỗi sketch có config.example.h; điền config.local.h riêng. Code không cần ArduinoJson cho dữ liệu mẫu vì JSON nhỏ được định dạng bằng snprintf.

## Các bài thực hành

- [12.1. Publish dữ liệu và phân tích gói MQTT](12.1.md)
- [12.2. Điều khiển hai chiều với topic cmd/state](12.2.md)
- [12.3. Retain, Last Will và trạng thái sau reset](12.3.md)

Mỗi bài gồm linh kiện, bảng nối dây/cấu hình, thao tác từng bước có hình, kết quả cần kiểm tra và giải thích. Xem [trạng thái kiểm thử](../docs/KIEM_THU.md) trước khi dùng các kết quả.
