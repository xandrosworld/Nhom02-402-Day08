# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Hồ Nhất Khoa
**MSSV:** 2A202600066
**Vai trò trong nhóm:** Grading & Evaluation Owner (Sprint 4), Sprint 3 Support
**Ngày nộp:** 13/04/2026

---

## 1. Tôi đã làm gì trong lab này?

Trong lab này tôi đảm nhận vai trò **Grading & Evaluation Owner**, chịu trách nhiệm một phần thi đấu thực chiến cuối buổi (Sprint 4). Cụ thể, tôi đã:

- **Cải tiến `run_grading.py`**: Script tự động hóa quá trình nộp bài thi — nhận câu hỏi từ `data/grading_questions.json`, gọi pipeline `rag_answer()` với cấu hình mạnh nhất (Hybrid + Voyage Reranker), và lưu output theo đúng format 7 trường bắt buộc của BTC (`id`, `question`, `answer`, `sources`, `chunks_retrieved`, `retrieval_mode`, `timestamp`). Tôi tích hợp cơ chế **checkpoint** (lưu file JSON sau mỗi câu) để tránh mất dữ liệu nếu pipeline crash giữa chừng trong 60 phút thi.
- **Kiểm thử toàn diện pipeline**: Xây dựng bộ câu hỏi thử nghiệm dựa trên SCORING.md, chạy grading run đầy đủ 10 câu và xác minh output format khớp 100% với yêu cầu.
- **Xây dựng giao diện Demo UI (`demo_ui.py`)**: Sử dụng Gradio để tạo giao diện Chat trực quan cho buổi demo, tích hợp hiển thị citation (nguồn tài liệu) sau mỗi câu trả lời.
- **Hỗ trợ Sprint 3**: Implement `build_grounded_prompt()` với vai trò CS/IT Helpdesk chuyên nghiệp, quy tắc EVIDENCE-ONLY và định dạng bullet-points; implement `transform_query()` (3 chiến lược: expansion, decomposition, HyDE); implement `rerank()` sử dụng Voyage AI Rerank API thay vì cross-encoder local.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Sau lab này, tôi hiểu sâu hơn về tầm quan trọng của **format output nhất quán trong pipeline RAG**. Lúc đầu khi tôi đề xuất thêm field `use_rerank` vào JSON log để "minh bạch hơn với BTC", tôi đã bị nhắc nhở kịp thời rằng script chấm tự động của giảng viên rất nhạy cảm với schema — thêm dù chỉ một field trái phép có thể làm vỡ toàn bộ quá trình parse và nhóm bị 0 điểm oan. Bài học này giúp tôi hiểu rõ hơn rằng trong các hệ thống production, **API contract là bất khả xâm phạm** — cải tiến phải diễn ra ở lớp xử lý bên trong (logic gọi pipeline), không phải ở schema đầu ra.

Ngoài ra, tôi cũng hiểu rõ hơn về **vòng lặp Retrieval → Rerank → Generation**. Khi thêm Voyage Reranker vào pipeline, câu trả lời cho các câu hỗn hợp như gq06 (cross-document, multi-hop) được cải thiện rõ rệt — điều mà chỉ với dense retrieval đơn thuần, pipeline thường chỉ lấy được thông tin từ một tài liệu và bỏ sót nửa còn lại.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Điều tôi bất ngờ nhất là **sự không tương thích giữa phiên bản Python và thư viện `voyageai`**. Máy tính của tôi cài sẵn Python 3.14 làm mặc định hệ thống, trong khi `voyageai>=0.3.7` chỉ hỗ trợ đến Python <3.14. Dù đã tạo môi trường ảo Python 3.12, khi gõ lệnh `pip install` mà không kích hoạt venv, máy vẫn tự động cài vào Python 3.14 và gây lỗi `No matching distribution found`. Vấn đề này làm mất khoảng 15-20 phút để debug và giải quyết bằng cách sử dụng trực tiếp `.venv\Scripts\pip` thay vì `pip` toàn cục.

Một khó khăn khác là khi tích hợp Gradio phiên bản 6.0 — cú pháp `theme` trong `ChatInterface.__init__()` đã bị deprecated và chuyển sang `launch()`. Đây là ví dụ điển hình của breaking changes trong thư viện open-source mà documentation chặng giữa thường không cập nhật kịp.

---

## 4. Phân tích câu hỏi gq07 trong scorecard

**Câu hỏi gq07:** *"Công ty sẽ phạt bao nhiêu nếu team IT vi phạm cam kết SLA P1?"*

Đây là câu **Hallucination Bait** — thông tin về mức phạt không tồn tại trong bất kỳ tài liệu nào được index. Pipeline của nhóm đã xử lý **đúng** (Abstain) và nhận 10/10 điểm. Tuy nhiên, cần phân tích kỹ tại sao pipeline có thể sai ở đây:

**Failure mode tiềm ẩn:** Khi query "vi phạm SLA P1" được embed bằng `voyage-multilingual-2`, vector của nó có cosine similarity cao với các chunk mô tả *quy trình* xử lý P1 (first response 15 phút, resolution 4 giờ). Nếu model LLM nhận context này và không có system prompt đủ chặt, nó có thể suy diễn: *"Quá hạn resolution → có thể có penalty"* và bịa ra con số từ prior knowledge (ví dụ: "phạt 10% doanh thu").

**Lý do pipeline của nhóm đúng:** System prompt trong `build_grounded_prompt()` có quy tắc số 2 rất cụ thể: *"ABSTAIN: Nếu context thiếu thông tin, hãy thẳng thắn từ chối và TUYỆT ĐỐI KHÔNG chế tạo thêm số liệu/quy trình."* Nhờ constraint này, Claude Sonnet 4.6 nhận ra rằng ba chunks được retrieve chỉ mô tả SLA target và quy trình — không đề cập penalty — và đã từ chối trả lời một cách minh bạch, giải thích rõ thiếu data, đồng thời gợi ý hướng tra cứu thêm (Partner Agreement, OLA nội bộ).

**Đề xuất cải tiến:** Nếu pipeline sai ở câu này (hallucinate), root cause thường nằm ở generation layer chứ không phải retrieval — vì không có chunk nào chứa "penalty" để retrieve. Fix phù hợp: tăng thêm một ví dụ concrete trong system prompt về cách abstain khi thấy context chứa thông tin *liên quan* nhưng không trả lời *trực tiếp* câu hỏi.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Nếu có thêm 60 phút, tôi sẽ hoàn thiện **`eval.py`** để implement LLM-as-Judge tự động đánh giá từng câu trong `grading_run.json`. Cụ thể: gọi Claude với prompt so sánh `answer` của pipeline với `expected_answer` trong `grading_questions.json`, chấm điểm theo rubric Full/Partial/Zero/Penalty, và xuất `results/scorecard_*.md` tổng hợp. Điều này vừa giúp nhóm nhận +2 điểm bonus, vừa tạo feedback loop tức thì để cải tiến pipeline ngay trong buổi lab thay vì phải chờ giảng viên chấm.
