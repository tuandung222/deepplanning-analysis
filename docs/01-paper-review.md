# Review Paper DeepPlanning

## Thông tin chính

- Tên: **DeepPlanning: Benchmarking Long-Horizon Agentic Planning with Verifiable Constraints**
- Nhóm tác giả: Qwen Team
- Paper: https://arxiv.org/abs/2601.18137

## Bài toán paper nhắm tới

Paper lập luận rằng nhiều benchmark agent hiện tại thiên về:
- step-level reasoning cục bộ,
- chưa đủ nặng về tối ưu ràng buộc toàn cục (thời gian, ngân sách),
- thiếu môi trường yêu cầu thu thập thông tin chủ động qua tool/API.

DeepPlanning được đề xuất để lấp khoảng trống đó.

## Contribution chính

1. Đề xuất benchmark long-horizon thực tế với **ràng buộc có thể kiểm chứng** (verifiable constraints).
2. Thiết kế 2 domain bổ sung nhau:
- **Travel Planning**: tối ưu lịch trình nhiều ngày với constraint không-thời gian và tài chính.
- **Shopping Planning**: tối ưu tổ hợp sản phẩm + coupon.
3. Đưa pipeline đánh giá tự động, có scoring rõ ràng từ output model.
4. Mở dữ liệu + mã nguồn để tái lập thí nghiệm.

## Điểm đặc biệt

- Không chỉ đánh giá “agent có trả lời được không”, mà đánh giá tính hợp lệ theo nhiều tầng constraint.
- Có cơ chế one-vote-veto trong một số thước đo (chỉ 1 lỗi có thể làm fail case).
- Bắt model phải dùng tool để lấy state môi trường thay vì “đoán”.

## Vì sao benchmark này khó

- Horizon dài: nhiều bước, nhiều quyết định phụ thuộc nhau.
- Constraint chồng chéo: local đúng chưa chắc global đúng.
- Action-space lớn: nhiều API/tool và dữ liệu nền.
- Đánh giá strict: sai định dạng hoặc sai constraint dễ mất điểm mạnh.

## Kết luận review ngắn

DeepPlanning mạnh ở tính thực dụng cho agent planning: cấu trúc task gần thực tế, đánh giá tự động, và có độ khó đủ cao để phân tách rõ năng lực model/agent design.
