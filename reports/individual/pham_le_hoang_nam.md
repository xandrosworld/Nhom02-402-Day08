# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Phạm Lê Hoàng Nam
**MSSV:** 2A202600416
**Vai trò trong nhóm:** Documentation Owner
**Ngày nộp:** 13/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong lab Day 08, phần việc chính của tôi tập trung vào hai hướng:

- Bổ sung công cụ tiền xử lý tài liệu.
- Hoàn thiện tài liệu kiến trúc.

Ở nhánh code, tôi phát triển `preprocess_pdf.py` để convert PDF sang Markdown bằng AI, hỗ trợ cả CLI lẫn web mode. Script cho phép nhập từ file local hoặc URL, tự tách nội dung theo token để tránh quá giới hạn context, sau đó format lại Markdown theo các ràng buộc (heading, list, table, code block, công thức). Tôi cũng thiết kế fallback khi gọi model: ưu tiên Anthropic, nếu lỗi thì chuyển sang OpenAI để pipeline không bị dừng.

Ở nhánh tài liệu, tôi cập nhật `docs/architecture.md` phần Indexing Pipeline: điền quyết định chunking (size, overlap, strategy), mô tả metadata và gắn pipeline diagram theo flow triển khai thực tế của nhóm.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi hiểu rõ hơn mối liên hệ chặt giữa chất lượng dữ liệu đầu vào và hiệu năng RAG ở bước retrieval/generation.

Trước đây tôi nghĩ embedding model là yếu tố quyết định chính, nhưng khi làm thực tế tôi thấy chunking và metadata ảnh hưởng rất lớn đến việc truy hồi đúng bằng chứng:

- Chunk quá dài: câu trả lời dễ loãng.
- Chunk quá ngắn hoặc cắt sai ranh giới: mất ý quan trọng.

Tôi cũng hiểu vì sao cần tách rõ pipeline theo từng giai đoạn (preprocess, chunk, embed, store) để dễ debug và tối ưu độc lập. Ngoài ra, từ việc viết tài liệu kiến trúc, tôi nhận ra documentation không chỉ để "mô tả lại" mà còn là công cụ đồng bộ quyết định kỹ thuật trong nhóm, giúp các sprint sau triển khai nhất quán hơn.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều khiến tôi ngạc nhiên là việc convert PDF tưởng đơn giản nhưng thực tế có rất nhiều edge case:

- Bố cục nhiều cột.
- Bảng bị vỡ cấu trúc.
- Heading bị nhận diện sai.

Vì vậy, nếu không chuẩn hóa sau khi extract thì Markdown output rất nhiễu, kéo theo chunking kém chất lượng.

Khó khăn lớn nhất của tôi là cân bằng giữa độ "đẹp" của Markdown và tính ổn định của pipeline. Ví dụ, prompt format quá tham vọng có thể tạo output đẹp hơn nhưng tăng rủi ro hallucination hoặc lệch nội dung gốc. Thêm nữa, trong quá trình cập nhật architecture, tôi phải đảm bảo số liệu (như số chunk mỗi tài liệu, tham số chunk size/overlap) bám sát code hiện tại thay vì điền theo giả định. Việc này mất thời gian kiểm tra chéo nhưng giúp tài liệu có độ tin cậy cao hơn.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** "SLA xử lý ticket P1 là bao lâu?"

**Phân tích:**

Đây là câu hỏi tốt để đánh giá toàn bộ chuỗi RAG vì có thông tin định lượng rõ ràng và nằm trong tài liệu chuyên biệt (`sla_p1_2026.txt`).

Ở bước retrieval, kỳ vọng hệ thống phải đưa được chunk thuộc section SLA/Priority thay vì chunk FAQ tổng quát. Khi kiểm tra scorecard, tôi tập trung vào ba tiêu chí:

1. context recall có lấy đúng nguồn SLA không,
2. faithfulness có bám vào evidence hay tự suy diễn,
3. citation có trỏ đúng file/section.

Nếu top-k search đủ rộng nhưng top-k select/rerank không tốt, mô hình dễ chọn chunk liên quan "ticket" nhưng không chứa mốc thời gian P1, dẫn đến câu trả lời chung chung. Ngược lại, khi chunking theo section + paragraph và có overlap hợp lý, thông tin "P1" và "thời gian phản hồi/xử lý" thường nằm cùng ngữ cảnh, giúp câu trả lời chính xác hơn.

Từ góc nhìn tài liệu, tôi thấy câu hỏi này cũng phù hợp để kiểm chứng quyết định chunking trong Sprint 1, vì chỉ cần cắt sai ranh giới là độ chính xác giảm ngay.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ làm ba việc:

1. Bổ sung bước hậu kiểm Markdown tự động (lint heading, table consistency, broken list) trước khi index.
2. Mở rộng `docs/architecture.md` bằng sơ đồ chi tiết hơn cho cả nhánh baseline và variant tuning.
3. Thêm dashboard nhỏ để theo dõi chất lượng index theo từng lần build (số chunk, phân bố metadata, tỉ lệ missing fields).

Các phần này sẽ giúp nhóm debug nhanh hơn và tái lập kết quả dễ hơn.
