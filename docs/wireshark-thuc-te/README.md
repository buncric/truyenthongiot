# Ghi chép thực hành Wireshark: MQTT, CoAP và bảo mật

Ngày 16/10/2026, em chạy các chương trình MQTT và CoAP trên máy Windows, dùng TShark/Npcap bắt gói rồi mở lại trong Wireshark 4.6.9 để đọc từng trường. Phần này lưu 11 file PCAPNG và 18 ảnh cho chín bài 12.1–12.3, 13.1–13.3, 14.1–14.3.

Các chương trình trao đổi qua 127.0.0.1. MQTT dùng Aedes 0.51.3 và MQTT.js 5.14.1, CoAP dùng coap 1.4.1. Vai trò cảm biến, thiết bị và dashboard đều được chạy bằng chương trình PC; những giá trị nhiệt độ trong payload là dữ liệu mô phỏng.

[File phân tích số liệu](analysis.json) · [Danh sách PCAP và SHA256](capture-report.json) · [Danh sách ảnh](screenshots.json) · [Chương trình thí nghiệm](../../tools/wireshark/traffic.cjs).

## Cách em mở bản ghi

1. Tải file `.pcapng` của ca cần xem; trong Wireshark dùng **File → Open**. Các bản ghi này dùng adapter Loopback.
2. Nhập bộ lọc hiển thị `coap || mqtt || tls`, nhấn Enter. Dùng `coap`, `mqtt`, hoặc `tcp.port == 8883` khi muốn xem riêng từng giao thức.
3. Click đúng **số frame** ghi dưới mỗi bài. Mở tam giác ở khung chi tiết bên trái: CoAP hoặc MQ Telemetry Transport Protocol hoặc TLS. Khung bytes bên phải thể hiện dữ liệu nhận thật.
4. Với CoAP proxy5684, làm **Analyze → Decode As → UDP port 5684 → CoAP**. Trong lần thử này, proxy gửi CoAP thường qua cổng 5684 nên cần chọn lại giao thức.
5. Xem số gói ở status bar; đối chiếu CSV bên dưới để có số frame, thời gian, MID/token, topic/payload. Tổng số frame MQTT còn gồm TCP handshake, ACK và đóng kết nối, nên lớn hơn số PUBLISH.

Khi tự bắt lại, chọn **Adapter for loopback traffic capture** cho các chương trình PC này. Wi-Fi không thấy traffic 127.0.0.1. Hình sau là giao diện ban đầu, trước khi chọn adapter:

![Giao diện Wireshark ban đầu](00-giao-dien-wireshark.png)

## Các file đã lưu

| Bài / lần thử | Frame toàn capture | PCAP mở được | Log ứng dụng | Packet CSV |
|---|---:|---|---|---|
| 12.1 | 54 | [12.1.pcapng](12.1.pcapng) | [Log](12.1.log) | [CSV](12.1-packets.csv) |
| 12.2 | 62 | [12.2.pcapng](12.2.pcapng) | [Log](12.2.log) | [CSV](12.2-packets.csv) |
| 12.3 | 77 | [12.3.pcapng](12.3.pcapng) | [Log](12.3.log) | [CSV](12.3-packets.csv) |
| 13.1-base | 4 | [13.1-base.pcapng](13.1-base.pcapng) | [Log](13.1-base.log) | [CSV](13.1-base-packets.csv) |
| 13.1-retry | 7 | [13.1-retry.pcapng](13.1-retry.pcapng) | [Log](13.1-retry.log) | [CSV](13.1-retry-packets.csv) |
| 13.2-observe | 24 | [13.2-observe.pcapng](13.2-observe.pcapng) | [Log](13.2-observe.log) | [CSV](13.2-observe-packets.csv) |
| 13.2-poll | 60 | [13.2-poll.pcapng](13.2-poll.pcapng) | [Log](13.2-poll.log) | [CSV](13.2-poll-packets.csv) |
| 13.3 | 32 | [13.3.pcapng](13.3.pcapng) | [Log](13.3.log) | [CSV](13.3-packets.csv) |
| 14.1 | 40 | [14.1.pcapng](14.1.pcapng) | [Log](14.1.log) | [CSV](14.1-packets.csv) |
| 14.2 | 50 | [14.2.pcapng](14.2.pcapng) | [Log](14.2.log) | [CSV](14.2-packets.csv) |
| 14.3 | 177 | [14.3.pcapng](14.3.pcapng) | [Log](14.3.log) | [CSV](14.3-packets.csv) |

## Bài 12.1 — MQTT telemetry

Em chạy một publisher và một subscriber, sau đó gửi ba mẫu nhiệt độ 28; 28,5 và 29°C. Đây là dữ liệu tạo trên PC, trong JSON có `simulated: true` và `source: "PC"` để phân biệt với số đo DHT11.

Ở file `12.1.pcapng`, em lọc `mqtt` và chọn frame **19**. Phần MQTT hiện topic `iot/lab1/sv01/sensor`, QoS 1 và Message Identifier; bên phải đọc được JSON trong khung bytes. Có 6 bản tin PUBLISH vì mỗi mẫu đi từ publisher tới broker rồi từ broker tới subscriber.

![Wireshark thực tế bài 12.1 — 12.1](12.1.png)

## Bài 12.2 — MQTT lệnh và trạng thái

Em gửi ON trước, chờ trạng thái trả về rồi mới gửi OFF. Trong `12.2.pcapng`, các frame **23/27** là lệnh ON đi qua broker trên topic `iot/lab2/sv01/cmd`. Phía nhận gửi trạng thái ON ở **29/33** trên topic `iot/lab2/sv01/state`.

Ảnh bên dưới chọn frame **33**; bytes `4f 4e` chính là chuỗi ON. Nhóm frame **37–47** ghi lại lần gửi OFF và phản hồi. Hai chương trình đã trao đổi được lệnh và trạng thái trên PC; phần LED cần kiểm tra thêm khi chạy sketch trên board.

![Wireshark thực tế bài 12.2 — 12.2](12.2.png)

## Bài 12.3 — MQTT Retain và Last Will

Đầu tiên em cho một client gửi trạng thái rồi mới mở client thứ hai để nhận. Client đến muộn CONNECT ở frame **36**, SUBSCRIBE ở **42** và nhận ngay `online` ở **46**, sau đó nhận state ON ở **50**. Khi mở frame 46, cờ **Retain: Set** cho thấy đây là bản tin broker đã lưu.

Tiếp theo em chủ động đóng socket của client thiết bị mà không gửi MQTT DISCONNECT. Broker phát `offline` ở frame **58/60**, đúng với Last Will đã đăng ký. Ở ảnh thứ hai, payload offline đọc được trong khung bytes. Bản tin chuyển cho subscriber đang nghe có Retain=0; điều này khác với bản retained gửi cho một subscriber vừa đăng ký.

Qua lần thử này, em thấy Retain giúp client mới biết trạng thái gần nhất, còn Last Will báo việc mất kết nối bất thường. File `12.3.pcapng` có cả hai tình huống để xem lại.

![Wireshark thực tế bài 12.3 — 12.3](12.3.png)

![Wireshark thực tế bài 12.3 — 12.3-last-will](12.3-last-will.png)

## Bài 13.1 — CoAP NON, CON và retransmission

Em thử NON trước rồi CON trong `13.1-base.pcapng`. Hai frame **1–2** là NON POST và phản hồi NON; **3–4** là CON POST và ACK 2.04. Như vậy có thể nhìn trực tiếp sự khác nhau ở trường Type của CoAP.

Đến lần thử mất phản hồi, em cho proxy ở cổng **5684** bỏ ACK đầu tiên. Khi mở `13.1-retry.pcapng`, Wireshark ban đầu nhận cổng này là DTLS. Em vào **Analyze → Decode As → UDP port 5684 → CoAP** để đọc đúng dữ liệu đang gửi trong bài.

Client phát request ở frame **1**, proxy chuyển sang server ở **2**, server trả ACK ở **3** nhưng proxy bỏ gói đó. Vì chưa nhận được phản hồi, client gửi lại ở **4**, giữ nguyên MID **9552** và token, sau khoảng **2,199484 giây**. Đến frame **7**, phản hồi mới tới client. ACK ở frame 3 chỉ tới proxy, nên chưa thể coi đó là lần client nhận thành công.

![Wireshark thực tế bài 13.1 — 13.1-base](13.1-base.png)

![Wireshark thực tế bài 13.1 — 13.1-decode-as](13.1-decode-as.png)

![Wireshark thực tế bài 13.1 — 13.1-retry](13.1-retry.png)

## Bài 13.2 — CoAP Polling và Observe trong 60 giây

Em chạy Polling và Observe riêng, mỗi chương trình hoạt động trong **60 giây**. Server dùng nhiệt độ mô phỏng và đổi giá trị mỗi 5 giây. Với Polling, client gửi GET khoảng 2 giây một lần; bản ghi có **30 GET và 30 phản hồi**, tổng cộng 60 gói.

Với Observe, client chỉ gửi **1 GET đăng ký**. Sau phản hồi đầu, server gửi thêm **11 notification**, đi kèm **11 ACK rỗng**, tổng cộng 24 gói. Token `d6d72a92e60bd4a1` giữ nguyên trong quan hệ Observe, còn MID thay đổi theo notification mới.

Ở cấu hình này, Observe giảm được các lần hỏi khi giá trị chưa đổi. Em đếm cả ACK khi so sánh để tránh chỉ nhìn số request. TShark được đặt giới hạn 63 giây nhằm bao trùm phần khởi động và dọn dẹp của cửa sổ ứng dụng 60 giây.

![Wireshark thực tế bài 13.2 — 13.2-poll](13.2-poll.png)

![Wireshark thực tế bài 13.2 — 13.2-observe](13.2-observe.png)

| Phương pháp | GET | Response đầu | Notification tiếp theo | ACK rỗng | Tổng gói CoAP |
|---|---:|---:|---:|---:|---:|
| Polling / 60 s | 30 | 30 | 0 | 0 | 60 |
| Observe / 60 s | 1 | 1 | 11 | 11 | 24 |

## Bài 13.3 — CoAP Block2 và ghép đủ 2 KB

Server trả tài nguyên `/firmware` gồm **2048 byte A**. Em cho client nhận từng block 128 byte; trong `13.3.pcapng` có **16 GET và 16 ACK Content**, tổng cộng 32 gói.

Ở frame **2**, Block2 có NUM=0, M=1 và size=128. Đến frame **32**, NUM=15 và M=0, nghĩa là đã đến block cuối. Khi mở phần ghép dữ liệu, Wireshark hiện **16 Blocks (2048 bytes)** cùng tab **Reassembled CoAP blocks (2048 bytes)** như ảnh thứ hai.

Em kiểm tra thêm nội dung và SHA256 bằng chương trình, kết quả nhận đủ 2048 byte A. Tên đường dẫn `/firmware` dùng cho bài học Block2; dữ liệu toàn A này không phải file để nạp vào vi điều khiển.

![Wireshark thực tế bài 13.3 — 13.3](13.3.png)

![Wireshark thực tế bài 13.3 — 13.3-ghép-du-2048-byte](13.3-ghép-du-2048-byte.png)

## Bài 14.1 — MQTT plaintext và MQTT qua TLS

Em tạo hai kết nối trong `14.1.pcapng` để so sánh trực tiếp. Với cổng **1883**, frame **4** là CONNECT và hiện được username/password mẫu; frame **8** cho thấy topic và payload của PUBLISH. Tài khoản dùng trong bài là chuỗi thử nghiệm công khai.

Với cổng **8883**, frame **21** là Client Hello, **23** là Server Hello. Sau đó các gói mang Application Data mã hóa; ảnh thứ hai mở frame **27** và thấy **Encrypted Application Data**. Client đã kiểm tra CA và địa chỉ 127.0.0.1 trong SAN của chứng chỉ tự sinh.

Một chỗ dễ nhầm là trường legacy record version vẫn có thể hiện 0x0303/TLS 1.2 trong phiên TLS 1.3. Em đối chiếu phiên bản được thương lượng thay vì chỉ đọc trường đó; [RFC 8446, mục 5.1](https://www.rfc-editor.org/rfc/rfc8446.html#section-5.1) giải thích cách dùng giá trị legacy này.

![Wireshark thực tế bài 14.1 — 14.1-plaintext](14.1-plaintext.png)

![Wireshark thực tế bài 14.1 — 14.1](14.1.png)

## Bài 14.2 — MQTT phát lại lệnh và kiểm tra độ mới

Em gửi một payload OPEN có HMAC ở frame **19**, rồi phát lại nguyên nội dung ở **29**. Broker chuyển tới receiver tại **23/33**. Hai lần giữ nguyên `time`, `nonce`, `seq=1` và `mac`.

Lần đầu receiver trả **ACCEPT** ở frame **25**. Đến lần phát lại, nó trả **REJECT replay/stale/MAC** ở **35**; log ghi nguyên nhân là sequence đã dùng. Hai ảnh bên dưới chọn đúng hai bản tin phản hồi đó, có thể đọc chuỗi ở khung bytes.

Kết quả cho thấy kiểm tra sequence đã chặn được payload trùng trong tiến trình PC. Em chưa thử reset ESP32 ở đây, nên phần giữ sequence bằng NVS vẫn là nội dung cần kiểm tra khi nạp sketch lên board.

![Wireshark thực tế bài 14.2 — 14.2-accept](14.2-accept.png)

![Wireshark thực tế bài 14.2 — 14.2](14.2.png)

## Bài 14.3 — MQTT tải giới hạn và phục hồi kết nối

Em cho client `pc-reconnecting-client` kết nối, gửi **10 lệnh ON/OFF** với khoảng nghỉ 100 ms giữa các lần phát, rồi chủ động ngắt socket của chính client đó. Log ghi nhận lần kết nối lại sau khoảng **0,5 giây**.

Trong Wireshark, CONNECT đầu nằm ở frame **15**, CONNECT tiếp theo ở **150**, cả hai dùng cùng Client ID. Sau đó frame **154** đăng ký lại topic, **156/162** gửi trạng thái online. Hai ảnh cho phép đối chiếu trước và sau lúc ngắt.

Lần này em thử cơ chế reconnect của MQTT.js trên PC. Khoảng 0,5 giây là tham số của client đang chạy; chưa dùng kết quả này để đánh giá backoff hoặc watchdog của firmware ESP32.

![Wireshark thực tế bài 14.3 — 14.3-ket-noi-dau](14.3-ket-noi-dau.png)

![Wireshark thực tế bài 14.3 — 14.3](14.3.png)

## Tái lập bằng mã nguồn

Cài Node.js và Python, cùng Wireshark/Npcap có adapter Loopback. Cài phụ thuộc gốc và phụ thuộc thí nghiệm riêng. Chứng chỉ/private key tạo trong thư mục tạm, không đưa lên Git. Username/password trong bản ghi là **lab-user / lab-only-not-a-real-password**, chỉ là chuỗi mẫu của thí nghiệm; broker loopback không dùng chúng để kiểm tra xác thực.

```powershell
npm ci
npm ci --prefix tools/wireshark
$labCertDir = Join-Path $env:TEMP "iot-wire-certs"
New-Item -ItemType Directory -Force $labCertDir | Out-Null
& "C:\Program Files\Git\usr\bin\openssl.exe" req -x509 -newkey rsa:2048 -sha256 -days 2 -nodes -keyout "$labCertDir/server.key" -out "$labCertDir/server.crt" -subj "/CN=localhost/O=PC Loopback Lab" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
python tools/wireshark/capture.py --cert-dir "$labCertDir"
python tools/wireshark/analyze.py
```

Thay đường dẫn OpenSSL theo nơi cài. Nếu chỉ chạy một ca, thêm tên cuối lệnh capture, ví dụ `13.1-retry`. Lệnh capture sẽ ghi lại file cùng tên; lưu riêng kết quả cũ nếu cần giữ nhiều lần đo. Mọi listener của script ràng buộc 127.0.0.1 và được đóng khi thí nghiệm kết thúc. Sau khi bắt xong, em mở từng file trong Wireshark và chụp lại phần cần phân tích.

## Những phần còn làm tiếp

- **Bài 6.1–6.3:** CC2531 đã nhận và dùng được các lệnh sniffer, nhưng lần quét ngắn chưa thu gói. Em dùng [bản ghi Zigbee mẫu](../../BTH06_ZIGBEE/ket-qua/README.md) để đọc MAC/NWK và quá trình join.
- **Bài 8.2:** IP ESP và Home Assistant trong ảnh cũ chưa truy cập được tại thời điểm kiểm tra. Phần này sẽ làm tiếp khi xác định được IP hiện tại và hai thiết bị online.
- Các ca MQTT/bảo mật ở đây xác minh giao thức bằng client PC; kiểm tra LED, cảm biến, NVS và reconnect của board vẫn làm theo hướng dẫn phần cứng của từng bài.

SHA256 ghi lại tính nguyên vẹn của file và ảnh. Nhật ký dùng UTC; giờ Việt Nam = UTC+7.
