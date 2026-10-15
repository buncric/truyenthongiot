# Cài Debian, Home Assistant, Mosquitto và Zigbee2MQTT

Hai PDF bổ trợ nằm tại [tài liệu gốc](../tai-lieu-goc/README.md). Xem ảnh từng trang cài Debian ở gallery để đối chiếu đúng vị trí nút.

## 1. Debian 12 trong VirtualBox (phục vụ Linux và NS-3)

1. New → tên `iot-debian`, chọn Debian 64-bit và ISO netinst Debian 12 theo đề; bỏ unattended nếu muốn làm từng bước. RAM gợi ý 4 GB, 2 vCPU, đĩa ảo 32 GB trở lên. Đây là đĩa **ảo mới**, không chọn raw physical disk của máy thật.
2. Settings → Network → Bridged Adapter → card đang truy cập LAN. Nếu Wi-Fi bridge không hoạt động, dùng NAT để tải gói và thiết lập mạng riêng cho bài đo; ghi đúng topology.
3. Start → Graphical Install → English → Other → Asia → Vietnam → locale en_US.UTF-8 → American English.
4. Hostname `iot-debian`, domain để trống nếu không có domain. Tạo user thường và mật khẩu riêng; để root password trống nếu muốn user đầu dùng sudo theo trình cài Debian.
5. Guided – use entire disk → **đúng VBOX HARDDISK mới tạo** → All files in one partition → Finish → xác nhận ghi phân vùng lên đĩa ảo.
6. Không quét ISO bổ sung; chọn mirror `deb.debian.org`, proxy để trống nếu mạng không yêu cầu. Chọn SSH server + standard system utilities; desktop tùy nhu cầu NetAnim.
7. Cài GRUB vào đĩa ảo, tháo ISO, khởi động lại. Đăng nhập user và chạy:

```bash
sudo apt update
sudo apt install -y openssh-server net-tools
ip -br address
systemctl status ssh --no-pager
```

8. Trên Windows chạy `ssh TEN_USER@IP_VM` hoặc PuTTY Host Name=IP_VM, port22, SSH. Đối chiếu fingerprint khi lần đầu kết nối. Chụp ảnh IP và terminal đăng nhập thành công.

## 2. Home Assistant cho cài mới

PDF chỉ cách cài Supervised thủ công. Phương thức này đã hết hỗ trợ chính thức từ 2025.12; hướng dẫn mới chọn **Home Assistant OS VM** để vẫn có Supervisor, Apps/Add-ons và backup. Không chạy các lệnh thay DNS/xóa resolv.conf trong PDF lên máy hiện tại chỉ để vượt lỗi cài đặt.

1. Tải VDI Home Assistant OS từ [hướng dẫn Windows chính thức](https://www.home-assistant.io/installation/windows/). Tạo VM Linux64, tối thiểu 2 vCPU, 2 GB RAM (4GB thuận tiện), dùng VDI tải sẵn làm đĩa, bật EFI theo hướng dẫn HAOS. Cấu hình Bridged Adapter.
2. Khởi động VM, chờ console báo IP; mở `http://IP_HA:8123`. Tạo tài khoản quản trị riêng, đặt vị trí/múi giờ Asia/Ho_Chi_Minh.
3. Settings → Apps/Add-ons → Store → Mosquitto broker → Install. Trong Settings → People → Users tạo `mqtt-user` với mật khẩu riêng. Bật broker, xem Logs.
4. Settings → Devices & services → MQTT → cấu hình broker. Dùng Configure/Listen to a topic nghe `test_topic`; Publish `Hello, world!` vào chính topic. Phải nhận đúng payload. Tên menu có thể thay giữa Apps/Add-ons tùy phiên bản.
5. Store → menu Repositories → thêm `https://github.com/zigbee2mqtt/hassio-zigbee2mqtt`; cài bản Zigbee2MQTT ổn định, không cần Edge trừ khi thiết bị đòi tính năng chưa phát hành.

Nguồn thay đổi hỗ trợ: [Home Assistant 2025.12](https://www.home-assistant.io/blog/2025/12/03/release-202512/). Nếu lớp bắt buộc tái hiện Supervised, làm trên VM snapshot riêng và dùng PDF để đối chiếu lịch sử; repo không quảng bá đây là phương thức cài mới được hỗ trợ.

## 3. SONOFF Dongle-E và Zigbee2MQTT

1. Xác định **Dongle-E** (Silicon Labs) hay **Dongle-P** (TI) trên nhãn; không nạp firmware lẫn nhau. Sao lưu cấu hình/coordinator trước khi thay firmware. Dongle chạy coordinator và USB sniffer CC2531 là hai vai trò khác nhau trong bài này.
2. Nếu firmware hiện có được hỗ trợ thì không bắt buộc flash. Nếu cần, chọn đúng model tại công cụ SONOFF/Silicon Labs theo tài liệu nhà sản xuất, đóng chương trình giữ COM, nạp firmware coordinator NCP tương thích. Baud của Zigbee2MQTT phải khớp firmware (ví dụ115200 hoặc230400); không lấy một baud cố định cho mọi file .gbl.
3. VirtualBox Settings → USB → filter cho Dongle-E, passthrough vào HAOS. Dùng đường `/dev/serial/by-id/...` ổn định thay vì đoán ttyUSB0.
4. Trong màn hình onboarding/config Zigbee2MQTT, nhập broker `mqtt://core-mosquitto:1883`, user/password thực; adapter `ember`, port đúng dongle. Tham khảo `configuration.example.yaml`; đó là cấu hình Zigbee2MQTT **ứng dụng**, không dán tất cả khóa vào schema options của Add-on nếu Add-on không hỗ trợ. Thiết lập thông qua UI hoặc configuration.yaml trong data directory của add-on.
5. Network Key/PAN ID/Extended PAN ID dùng giá trị sinh mới khi dựng mạng mới; giữ nguyên khi mạng đã có thiết bị. Channel15 là giá trị lab mẫu; ghép sniffer đúng channel. Không thay key/channel trên mạng đã ghép thiết bị mà không có kế hoạch ghép lại.
6. Start → Logs xác nhận coordinator và broker kết nối, Open Web UI → Permit join trong khoảng thời gian ngắn → reset công tắc/đèn theo nhà sản xuất để ghép → đổi friendly name → đóng join. Home Assistant MQTT integration nhận discovery/entity.

Không commit network key thật hoặc coordinator_backup.json. [Cấu hình hiện hành Zigbee2MQTT](https://www.zigbee2mqtt.io/guide/configuration/all-settings.html).
