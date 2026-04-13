# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13  

**Config:**
retrieval_mode = "dense"
chunk_size = ~500-800 tokens
overlap = ~100 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = claude-sonnet-4-6


**Scorecard Baseline:**

| Metric | Average Score |
|--------|--------------|
| Faithfulness | 3.80 /5 |
| Answer Relevance | 4.70 /5 |
| Context Recall | 5.00 /5 |
| Completeness | 4.60 /5 |

---

**Câu hỏi yếu nhất:**

- q09 (ERR-403-AUTH): Không có trong tài liệu → hệ thống trả lời “không đủ dữ liệu”
- q10 (Refund VIP): Thiếu thông tin → completeness thấp
- q06 (Escalation): Trả lời chưa đúng trọng tâm → relevance thấp

---

**Giả thuyết nguyên nhân (Error Tree):**

- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu
- [x] Retrieval: Dense không xử lý tốt keyword đặc biệt
- [x] Retrieval: Một số query không có trong docs
- [ ] Generation: Prompt chưa đủ chặt
- [ ] Context quá dài

---

## Variant 1 (Sprint 3)

**Ngày:** 2026-04-13  

**Biến thay đổi:** Hybrid + Rerank  

---

**Lý do chọn biến này:**

Hybrid giúp kết hợp:
- Dense → hiểu ngữ nghĩa  
- Sparse → match keyword (SLA, ERR code)

Rerank giúp:
- chọn chunk phù hợp hơn  
- giảm noise trong context  

---

**Config thay đổi:**
retrieval_mode = "hybrid"
top_k_search = 10
top_k_select = 3
use_rerank = True


---

**Scorecard Variant 1:**

| Metric | Baseline | Variant | Delta |
|--------|----------|---------|-------|
| Faithfulness | 3.80 | 3.80 | 0 |
| Answer Relevance | 4.70 | 4.60 | -0.10 |
| Context Recall | 5.00 | 5.00 | 0 |
| Completeness | 4.60 | 4.60 | 0 |

---

## Nhận xét

- Hybrid giữ nguyên recall = 5.0 → không bỏ sót dữ liệu  
- Rerank cải thiện một số câu:
  - q01 (SLA)
  - q06 (Escalation)

Tuy nhiên:

- q07 bị fail → mất chunk quan trọng  
- q10 vẫn thiếu thông tin  
- Relevance giảm nhẹ  

---

## Phân tích nguyên nhân

- Rerank loại bỏ chunk đúng trong một số trường hợp  
- Context diversity bị giảm  
- Hybrid chưa cải thiện rõ rệt so với dense  

---

## Kết luận

Variant chưa outperform baseline.

- Baseline ổn định hơn  
- Hybrid + rerank chưa được tune tốt  
- Rerank cần điều chỉnh thêm (top_k hoặc scoring)

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất trong pipeline**
   → Rerank làm mất chunk quan trọng  

2. **Biến ảnh hưởng lớn nhất**
   → Retrieval strategy  

3. **Nếu có thêm 1 giờ**
   → Tăng top_k_search và top_k_select  
   → Thử query transformation thay rerank  