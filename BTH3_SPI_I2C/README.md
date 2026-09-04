# BTH3 – Giao tiếp UART giữa 2 Arduino (ARD1 ↔ ARD2) & Đổi tốc độ Baud bằng nút nhấn

Bài thực hành thuộc học phần Truyền thông IoT. Gồm 2 phần code Arduino (viết bằng Proteus/Arduino IDE), mỗi phần nằm trong một thư mục riêng.

## Cấu trúc thư mục

```
BTH3_SPI_I2C/
├── bai21/
│   ├── adr1.ino          # Code cho Arduino 1 (ARD1)
│   └── bai21.pdsprj      # File mô phỏng Proteus
├── Bai22/
│   ├── bai22_.ino        # Code đổi baudrate bằng nút nhấn
│   └── bai22_.pdsprj     # File mô phỏng Proteus
└── README.md
```

## Bài 21 – Cầu nối UART giữa PC và ARD2 qua ARD1

File: [bai21/adr1.ino](bai21/adr1.ino)

- ARD1 dùng `SoftwareSerial` (chân RX=9, TX=8) để giao tiếp với ARD2, còn `Serial` (UART cứng) để giao tiếp với PC/Virtual Terminal.
- Chức năng: ARD1 đóng vai trò cầu nối (bridge) hai chiều —
  - Ký tự PC gõ vào Serial Monitor → được chuyển tiếp sang ARD2 qua `toARD2.write()`.
  - Dữ liệu ARD2 gửi phản hồi → được chuyển ngược về PC qua `Serial.write()`.
- Baudrate: 9600 cho cả hai cổng.

## Bài 22 – Đổi tốc độ Baud bằng nút nhấn (nhấn giữ / nhấn nhanh)

File: [Bai22/bai22_.ino](Bai22/bai22_.ino)

- Nút nhấn ở chân D2 (INPUT_PULLUP), LED báo trạng thái ở chân D13.
- Nhấn giữ nút ≥ 3 giây: chuyển đổi giữa 2 chế độ:
  - **Chế độ VẬN HÀNH** (mode 0): hoạt động bình thường.
  - **Chế độ CẤU HÌNH** (mode 1): LED nháy 3 lần báo hiệu đã vào chế độ cấu hình.
- Trong chế độ CẤU HÌNH, nhấn nhanh (click) để chọn tốc độ baud:
  - 1 click → baudrate 9600 (LED chớp 1 lần).
  - ≥2 click (trong vòng 500ms) → baudrate 115200 (LED chớp 2 lần).
- Sau khi chọn, chương trình gọi lại `Serial.begin(baud)` với tốc độ mới và in ra baudrate hiện tại.

## Cách mô phỏng

1. Mở file `.pdsprj` tương ứng bằng Proteus.
2. Biên dịch file `.ino` bằng Arduino IDE (hoặc Sketch → Export compiled Binary) để lấy file `.hex`, nạp vào chip trong Proteus.
3. Chạy mô phỏng và quan sát Virtual Terminal / LED.
