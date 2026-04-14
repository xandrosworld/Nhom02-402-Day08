# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** Nhóm 02 — Lớp 402

**Thành viên:**

| Tên | MSSV | Vai trò |
|-----|------|---------|
| Mai Tấn Thành | 2A202600127 | Tech Lead |
| Hồ Nhất Khoa | 2A202600066 | Grading & Evaluation Owner |
| Đặng Tùng Anh | 2A202600026 | Retrieval Owner |
| Nguyễn Đức Hoàng Phúc | 2A202600150 | Eval Owner |
| Phạm Lê Hoàng Nam | 2A202600416 | Documentation Owner |

**Ngày nộp:** 13/04/2026  
**Repo:** https://github.com/xandrosworld/Nhom02-402-Day08  
**Độ dài:** ~800 từ

---

## 1. Pipeline nhóm đã xây dựng

**Chunking decision:**

Nhóm sử dụng chiến lược chunking theo **ranh giới paragraph** (`\n\n`) thay vì cắt cứng theo số ký tự. Kích thước chunk dao động ~500–800 token với overlap ~100 token. Quyết định này xuất phát từ thực tế bộ tài liệu policy có cấu trúc rõ ràng theo điều khoản — nếu cắt giữa điều khoản, một chunk sẽ thiếu ngữ cảnh và làm giảm chất lượng retrieval. Tổng kết quả: **29 chunks** từ 5 tài liệu, mỗi chunk có đầy đủ 4 metadata fields: `source`, `section`, `department`, `effective_date`.

**Embedding model:**

Nhóm chọn **VoyageAI `voyage-multilingual-2`** thay vì OpenAI `text-embedding-3-small`. Lý do: bộ tài liệu có nội dung tiếng Việt lẫn tiếng Anh (tên section, mã lỗi, ký hiệu kỹ thuật), nên cần model đa ngôn ngữ được train chuyên biệt. Vector store là **ChromaDB** (PersistentClient) với similarity metric cosine. Để đảm bảo embedding space nhất quán, hàm `get_embedding()` từ `index.py` được import trực tiếp vào `rag_answer.py` — không viết lại riêng.

**Retrieval variant (Sprint 3):**

Nhóm triển khai **Hybrid Retrieval + Rerank**. Hybrid kết hợp Dense (VoyageAI embedding) và Sparse (BM25 với regex tokenizer) thông qua thuật toán **Reciprocal Rank Fusion (RRF)**. Rerank sử dụng Voyage AI Rerank API. Lý do chọn: corpus chứa cả ngôn ngữ tự nhiên (policy) lẫn keyword đặc thù (SLA, mã lỗi ERR-403), Dense đơn thuần dễ bỏ sót keyword chính xác.

---

## 2. Quyết định kỹ thuật quan trọng nhất

**Quyết định: Có nên dùng Voyage Reranker hay cross-encoder local?**

**Bối cảnh vấn đề:**

Sau Sprint 2, nhóm nhận thấy Dense retrieval trả về đúng nguồn (context recall = 5.0/5) nhưng faithfulness chỉ đạt 3.80/5 — cho thấy vấn đề không phải ở chỗ "không tìm thấy", mà ở chỗ chunk đúng chưa được ưu tiên đúng vị trí trong context. Nhóm cân nhắc thêm bước Rerank.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|------------|
| Cross-encoder local (`sentence-transformers/ms-marco`) | Không cần API, chạy offline | Nặng (~400MB), chậm trên máy yếu, cần GPU để nhanh |
| Voyage AI Rerank API | Nhẹ, nhanh, cùng provider với embedding | Tốn thêm API call, phụ thuộc kết nối mạng |
| Không rerank, tăng top_k_select | Đơn giản, ít rủi ro | Context dài hơn, tăng nguy cơ "lost in the middle" |

**Phương án đã chọn và lý do:**

Nhóm chọn **Voyage AI Rerank API** vì cùng provider với embedding model — đảm bảo tính nhất quán của representation space. Điều này quan trọng hơn việc tiết kiệm một API call, vì reranker từ cùng provider hiểu ngữ nghĩa vector tốt hơn cross-encoder train trên corpus tiếng Anh thuần.

**Bằng chứng từ scorecard:**

Kết quả thực tế cho thấy rerank cải thiện câu q01 (SLA) — faithfulness tăng từ 4 → 5, và cải thiện q06 (Escalation). Tuy nhiên, rerank cũng làm giảm một số câu khác (q07, q10) vì loại bỏ chunk cần thiết. Delta tổng thể âm nhẹ: Faithfulness giảm 0.20, Completeness giảm 0.10. Kết luận: rerank ở cấu hình hiện tại chưa được tune đủ — cần tăng `top_k_select` để tránh mất chunk quan trọng.

---

## 3. Kết quả grading questions

Pipeline chạy đủ 10 câu với cấu hình Hybrid + Voyage Reranker trong khung giờ quy định. Timestamp log: 16:12–16:13 ngày 13/04/2026.

**Ước tính điểm raw:** ~72–78 / 98

**Câu tốt nhất:** `gq03` (Flash Sale + đã kích hoạt → hoàn tiền không?) — Pipeline xác định đúng hai exception đồng thời từ Điều 3, trả lời đầy đủ, có citation `[1]`. Lý do thành công: câu hỏi khớp trực tiếp với section rõ ràng trong `policy_refund_v4.txt`, chunking theo paragraph giữ nguyên cấu trúc điều khoản.

**Câu khó nhất:** `gq06` (P1 lúc 2am → cấp quyền tạm thời) — Câu cross-document multi-hop cần kết hợp thông tin từ `sla_p1_2026.txt` và `access_control_sop.txt`. Pipeline trả lời được nhờ Hybrid + Rerank lấy đủ context từ cả hai nguồn, nhưng có thể bị Partial vì câu trả lời bị cắt ở cuối do giới hạn max_tokens.

**Câu gq07 (abstain):** Pipeline trả lời đúng — nêu rõ không có điều khoản phạt trong tài liệu, giải thích lý do, gợi ý cần tra Partner Agreement hoặc OLA. Nhờ system prompt có constraint EVIDENCE-ONLY và temperature=0, Claude Sonnet 4.6 không suy diễn thêm con số. Kết quả kỳ vọng: **10/10**.

---

## 4. A/B Comparison — Baseline vs Variant

**Biến đã thay đổi:** Retrieval strategy — chuyển từ Dense sang Hybrid kết hợp Rerank để đánh giá tác động tổng thể của việc cải thiện retrieval pipeline.

| Metric | Baseline | Variant | Delta |
|--------|----------|---------|-------|
| Faithfulness | 3.80 / 5 | 3.60 / 5 | **-0.20** |
| Answer Relevance | 4.60 / 5 | 4.60 / 5 | 0 |
| Context Recall | 5.00 / 5 | 5.00 / 5 | 0 |
| Completeness | 4.70 / 5 | 4.60 / 5 | **-0.10** |

**Kết luận:**

Variant chưa outperform baseline. Context Recall giữ nguyên 5.0/5 ở cả hai — Hybrid không làm giảm recall, xác nhận BM25 + RRF không bỏ sót source. Tuy nhiên, Faithfulness giảm 0.20 do Reranker loại bỏ chunk quan trọng trong một số câu (q07, q10). Baseline ổn định hơn trong cấu hình hiện tại. Cần tăng `top_k_select` từ 3 lên 5 trước khi bật Rerank để tránh mất context.

---

## 5. Phân công và đánh giá nhóm

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Mai Tấn Thành | `index.py` (embedding, chunking, ChromaDB), `rag_answer.py` (dense retrieval, LLM call), config `.env` & `run_grading.py` | 1, 2 |
| Đặng Tùng Anh | `retrieve_sparse()` (BM25 + regex tokenizer), `retrieve_hybrid()` (RRF), tích hợp 5 retrieval mode | 3 |
| Hồ Nhất Khoa | `run_grading.py` (checkpoint), `build_grounded_prompt()`, `transform_query()`, `rerank()` (Voyage API), `demo_ui.py` (Gradio) | 3, 4 |
| Nguyễn Đức Hoàng Phúc | `eval.py` (4 scoring functions), chạy scorecard baseline + variant, A/B comparison, `tuning-log.md` | 4 |
| Phạm Lê Hoàng Nam | `preprocess_pdf.py` (PDF→Markdown CLI + web), `docs/architecture.md` (chunking decisions, diagram) | 1, 4 |

**Điều nhóm làm tốt:**

Phân chia sprint rõ ràng ngay từ đầu giúp tránh block lẫn nhau. Tech Lead hoàn thành `index.py` và `rag_answer.py` trước — unblock toàn bộ nhóm ở Sprint 2. Cơ chế checkpoint trong grading script đảm bảo không mất kết quả nếu pipeline crash. Pipeline end-to-end chạy ổn định và abstain đúng câu gq07.

**Điều nhóm làm chưa tốt:**

Merge conflict trên Git xảy ra nhiều lần do nhiều người chỉnh cùng file trong cùng thời điểm — cần quy ước rõ hơn về ownership từng file. Thời gian debug môi trường (encoding Windows, Python version, thư viện) chiếm khá nhiều thời gian của Sprint 1 và 2, ảnh hưởng đến thời gian tuning ở Sprint 3.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì?

**Cải tiến 1 — Tăng top_k_select từ 3 → 5 trước khi rerank:** Scorecard cho thấy Reranker làm giảm faithfulness 0.20 vì loại bỏ chunk quan trọng. Tăng pool trước khi rerank giúp giữ lại context cần thiết mà vẫn hưởng lợi từ reranking.

**Cải tiến 2 — Query Decomposition cho câu cross-document:** Câu gq06 cần thông tin từ hai nguồn (`sla_p1_2026`, `access_control_sop`). Tách thành sub-query "P1 on-call procedure" và "emergency access grant" rồi merge kết quả sẽ tăng recall đáng kể — từ evidence trong scorecard, cross-doc query là weakness lớn nhất của Dense retrieval đơn thuần.

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
