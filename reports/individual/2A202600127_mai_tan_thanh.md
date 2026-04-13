# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Mai Tấn Thành
**MSSV:** 2A202600127
**Vai trò trong nhóm:** Tech Lead
**Ngày nộp:** 13/04/2026
**Độ dài:** ~650 từ

---

## 1. Tôi đã làm gì trong lab này?

Với vai trò Tech Lead, tôi chịu trách nhiệm hai phần cốt lõi của pipeline: **Sprint 1 (Indexing)** và **Sprint 2 (Dense Retrieval + LLM Generation)**.

**Sprint 1 — `index.py`:** Tôi implement hàm `get_embedding()` sử dụng Voyage AI với model `voyage-multilingual-2` — lý do chọn model này là vì tài liệu có tiếng Việt, cần model đa ngôn ngữ tốt hơn so với OpenAI `text-embedding-3-small`. Tiếp theo, tôi implement `build_index()` dùng ChromaDB làm vector store local. Điểm kỹ thuật quan trọng là tôi cải thiện hàm `_split_by_size()` từ cách cắt theo số ký tự sang cắt theo ranh giới paragraph (`\n\n`), giúp giữ nguyên cấu trúc điều khoản mà không bị cắt giữa chừng. Kết quả: 29 chunks từ 5 tài liệu, tất cả đều có đủ metadata `source`, `section`, `effective_date`.

**Sprint 2 — `rag_answer.py`:** Tôi implement `retrieve_dense()` bằng cách embed câu hỏi với cùng model VoyageAI để đảm bảo embedding space nhất quán, sau đó query ChromaDB với cosine similarity. Hàm `call_llm()` được implement qua Anthropic Claude Sonnet 4.6 với `temperature=0` để output ổn định cho evaluation. Tôi cũng cập nhật toàn bộ config repo (`.env`, `.env.example`, `requirements.txt`) và tạo `run_grading.py` cho Nhất Khoa chạy lúc 17:00.

Phần việc của tôi là **unblocking dependency** — Nhất Khoa, Tùng Anh, Hoàng Phúc đều cần `index.py` và `rag_answer.py` chạy được để test code của mình.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

**Embedding space nhất quán là yêu cầu bắt buộc.** Trước lab này, tôi chỉ hiểu embedding là "biến text thành vector". Sau khi implement, tôi hiểu rằng khi index dùng model A, lúc query phải dùng đúng model A — nếu khác model, vector sẽ nằm trong không gian hoàn toàn khác và cosine similarity không còn ý nghĩa. Tôi giải quyết điều này bằng cách import `get_embedding` từ `index.py` vào `rag_answer.py` thay vì viết lại, đảm bảo cùng một hàm được dùng ở cả hai bước.

**Chunking ảnh hưởng trực tiếp đến chất lượng retrieval.** Cách cắt chunk tưởng đơn giản nhưng thực ra rất quan trọng. Nếu cắt giữa điều khoản, một chunk sẽ có nội dung không hoàn chỉnh, LLM sẽ thiếu bối cảnh. Chunking theo paragraph boundary giữ được logic của từng quy định.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

**Lỗi Unicode encoding trên Windows** là thứ mất thời gian nhất. Khi chạy `python index.py`, terminal Windows dùng encoding `cp1252` mặc định, không đọc được ký tự tiếng Việt trong print statement → crash ngay từ đầu. Giả thuyết ban đầu của tôi là lỗi trong code logic, tốn 10 phút debug mới phát hiện đây là vấn đề encoding của OS. Fix đơn giản: chạy với flag `python -X utf8 index.py`. Sau đó tôi nhận ra cần ghi chú này cho cả nhóm vì ai trên Windows cũng gặp.

**Khi push lên GitHub** có merge conflict ở `README.md` vì GitHub tự tạo README khi init repo. Phải dùng `git pull --allow-unrelated-histories` rồi `git checkout --ours` để giữ lại README của lab.

---

## 4. Phân tích câu hỏi gq07 trong scorecard

**Câu hỏi:** "Mức phạt vi phạm SLA P1 là bao nhiêu?"

Pipeline của nhóm trả lời: *"Tôi không tìm thấy thông tin về mức phạt vi phạm SLA P1 trong tài liệu được cung cấp."*

Đây là câu hỏi thiết kế để kiểm tra **anti-hallucination**. Tôi đã đọc toàn bộ 5 tài liệu — không có tài liệu nào đề cập đến mức phạt SLA. `sla_p1_2026.txt` chỉ mô tả quy trình xử lý và SLA targets (4 giờ for resolution), không có penalty clause.

Lỗi nào trong pipeline sẽ gây hallucinate? Nếu `call_llm()` dùng `temperature` cao, LLM có thể bịa ra con số như "10% phí hợp đồng". Việc dùng `temperature=0` và prompt "Answer only from the retrieved context" giúp tránh điều này.

Pipeline của nhóm **abstain đúng** → không bị trừ điểm penalty 50%.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Kết quả eval cho thấy câu **gq06** (P1 lúc 2am → cấp quyền tạm thời) cần thông tin từ **cả hai tài liệu**: `sla_p1_2026.txt` và `access_control_sop.txt`. Dense retrieval đơn thuần có thể bỏ sót một trong hai. Tôi sẽ thử **query expansion** — từ câu hỏi gốc, generate thêm 2-3 sub-query (ví dụ: "P1 on-call procedure", "emergency access grant") rồi merge kết quả. Đây là kỹ thuật bổ sung cho Hybrid Retrieval để tăng recall trên câu hỏi cross-document.
