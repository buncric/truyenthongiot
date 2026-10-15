# Bài thực hành 13 - CoAP

[Ảnh Wireshark thực tế và file PCAPNG](../docs/wireshark-thuc-te/README.md): CON/NON, retransmission, Polling/Observe 60 giây và ghép Block2 2048 byte trên PC. Từng bài bên dưới có ảnh và số frame để đối chiếu.

PDF mục D chỉ liệt kê13.1 nhưng các trang10–19 có13.2 và13.3: cả ba đã được triển khai. Header tự chứa có giới hạn một exchange,IPv4,token2byte và block128byte; không thay thư viện CoAP đầy đủ trong sản phẩm.

## Các bài thực hành

- [13.1. CON/NON, ACK và gửi lại khi mất phản hồi](13.1.md)
- [13.2. Polling và Observe](13.2.md)
- [13.3. Blockwise: nhận đầy đủ 2KB](13.3.md)

Mỗi bài gồm linh kiện, bảng nối dây/cấu hình, thao tác từng bước có hình, kết quả cần kiểm tra và giải thích. Xem [trạng thái kiểm thử](../docs/KIEM_THU.md) trước khi dùng các kết quả.
