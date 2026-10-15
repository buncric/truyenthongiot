# Kết quả LTE đã chạy trên GitHub Actions

Đây là số liệu mô phỏng NS-3 thực, không phải số liệu từ mạng di động hoặc board thật. Nguồn: [run thành công](https://github.com/buncric/truyenthongiot/actions/runs/38747166217), commit f80cf0b. Job LTE biên dịch trên Ubuntu24.04 với libns3-dev của distribution, chạy6 cấu hình. Mã mô phỏng giống phần thân của lte-lab1.cc hiện tại; hướng dẫn cài local cố định ns-3.43 để người học tái lập API.

| Cấu hình (UE / khoảng cách m / thời gian s) | IP flows | TX packets | RX packets | Tỷ lệ nhận | Trễ trung bình ms |
|---|---:|---:|---:|---:|---:|
| ue1-distance20-time10 | 1 | 90 | 90 | 100% | 14.0 |
| ue5-distance20-time10 | 5 | 450 | 450 | 100% | 16.0 |
| ue10-distance20-time10 | 10 | 900 | 900 | 100% | 18.5 |
| ue1-distance100-time10 | 1 | 90 | 90 | 100% | 14.0 |
| ue1-distance500-time10 | 1 | 90 | 90 | 100% | 14.0 |
| ue1-distance20-time20 | 1 | 190 | 190 | 100% | 14.0 |

## Diễn giải

- Tăng từ1 lên5 và10UE, tổng lưu lượng tăng tương ứng; trễ trung bình tăng14→16→18.5ms trong cấu hình tải nhẹ này.
- Đổi khoảng cách20→100→500m trong trường hợp1UE chưa làm thay đổi tỷ lệ nhận hoặc trễ trung bình. Không suy ra khoảng cách không ảnh hưởng LTE nói chung; tải, mô hình propagation và tài nguyên hiện tại vẫn đáp ứng được các gói nhỏ.
- Tăng simTime10→20s cho1UE tăng số packet90→190: nguồn bắt đầu ở1s và dừng ởsimTime, chu kỳ100ms. Không lấy simTime làm thời gian ứng dụng phát từ0s.
- Tỷ lệ nhận100% trong6 cấu hình chỉ mô tả các lần mô phỏng này, không là cam kết mạng không mất gói hoặc kết quả đoNB-IoT.

CSV/JSON ở đây lấy từ annotation công khai của job. XMLFlowMonitor, XMLNetAnim và CSV từngflow có trong artifact **lte-results** của run trên; GitHub có thể yêu cầu đăng nhập để tải và artifact có thời hạn lưu. Muốn tạo lại, chạy tools/run_lte_experiments.py với binary đã build hoặc chạy lại workflow. Không tự tạo XML khi chưa chạy mô phỏng.
