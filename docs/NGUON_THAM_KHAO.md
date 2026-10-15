# Nguồn kỹ thuật kiểm tra thêm

Tài liệu chính là13PDF của môn học trong tai-lieu-goc; mã mới được viết theo yêu cầu của các bài. Các nguồn chính thức dưới đây dùng để đối chiếu những chỗ API/hướng dẫn có thể thay đổi, kiểm tra ngày15/10/2026.

- [Home Assistant: thay đổi hỗ trợ Supervised từ2025.12](https://www.home-assistant.io/blog/2025/12/03/release-202512/)
- [Home Assistant OS trên Windows/VM](https://www.home-assistant.io/installation/windows/)
- [ESPHome OTA và port theo chip](https://esphome.io/components/ota/esphome/)
- [ESPHome: cấu trúc OTA platform](https://esphome.io/components/ota/)
- [Zigbee2MQTT: toàn bộ cấu hình](https://www.zigbee2mqtt.io/guide/configuration/all-settings.html)
- [node-coap: tài liệu thư viện và Observe/Blockwise](https://github.com/coapjs/node-coap)
- [RFC7641: Observe](https://www.rfc-editor.org/info/rfc7641/)
- [RFC7959: Blockwise](https://www.rfc-editor.org/info/rfc7959/)
- [Arduino SPI](https://docs.arduino.cc/language-reference/en/functions/communication/SPI/)
- [PubSubClient: mã nguồn phiên bản đã cài](https://github.com/knolleary/pubsubclient/tree/v2.8)

Phiên bản thư viện thực dùng để compile/test ghi trong KIEM_THU.md và package-lock.json; không mặc định link latest trong PDF vẫn tương ứng API cũ.

## Zigbee và cách trình bày bài thực hành

- [Wireshark Wiki — SampleCaptures](https://wiki.wireshark.org/SampleCaptures): nguồn bản ghi `zigbee-join-authenticate.pcap.gz` dùng để đọc Association và APS ở bài 6. Các địa chỉ và frame được phân tích từ file này, tách với lần thử CC2531 trên máy.
- [Wireshark-CC2531 của Andre B. Oliveira](https://github.com/andrebdo/wireshark-cc2531): cách nối dongle có firmware sniffer vào Wireshark bằng WinUSB/extcap.
- [Ghi chép Wireshark của hoangdh](https://github.com/hoangdh/Wireshark): tham khảo cách chia thao tác thành đoạn ngắn, đặt hình cạnh phần đang giải thích.
- [Báo cáo thực hành Mạng máy tính — Lab 2](https://dev.tailieu.vn/doc/bao-cao-thuc-hanh-mang-may-tinh-bai-lab-2-1696774.html): tham khảo bố cục bài thực hành, gồm cấu hình, kết quả và nhận xét. Nội dung phân tích và số liệu trong repo được viết từ các lần kiểm tra của bài, không chép phần kết quả của báo cáo này.
