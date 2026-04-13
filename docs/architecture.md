# Architecture — RAG Pipeline (Day 08 Lab)

> Template: Điền vào các mục này khi hoàn thành từng sprint.
> Deliverable của Documentation Owner.

---

## 1. Tổng quan kiến trúc

[Raw Docs (PDF / TXT)]
->
[Preprocess: PDF → Markdown → Clean Text]
->
[index.py: Chunk → Embed → Store]
->
[ChromaDB Vector Store]
->
[rag_answer.py: Query → Retrieve → Rerank → Generate]
->
[Grounded Answer + Citation]


**Mô tả ngắn gọn:**

> Nhóm xây dựng một hệ thống RAG để trả lời câu hỏi nội bộ dựa trên tài liệu policy.
> Hệ thống giúp nhân viên tra cứu nhanh SLA, refund policy, access control.
> Đặc biệt, hệ thống có bước tiền xử lý PDF → Markdown để cải thiện chất lượng retrieval.

---

## 2. Indexing Pipeline (Sprint 1) (Pham Le Hoang Nam edit)

### Tài liệu được index

| File                     | Nguồn                    | Department  | Số chunk |
| ------------------------ | ------------------------ | ----------- | -------- |
| `policy_refund_v4.txt`   | policy/refund-v4.pdf     | CS          | 6        |
| `sla_p1_2026.txt`        | support/sla-p1-2026.pdf  | IT          | 5        |
| `access_control_sop.txt` | it/access-control-sop.md | IT Security | 7        |
| `it_helpdesk_faq.txt`    | support/helpdesk-faq.md  | IT          | 6        |
| `hr_leave_policy.txt`    | hr/leave-policy-2026.pdf | HR          | 5        |

👉 Tổng: **29 chunks**

---

### Quyết định chunking

| Tham số           | Giá trị         | Lý do                                          |
| ----------------- | --------------- | ---------------------------------------------- |
| Chunk size        | ~500–800 tokens | Đảm bảo đủ context nhưng không quá dài         |
| Overlap           | ~100 tokens     | Giữ continuity giữa các chunk                  |
| Chunking strategy | section-based   | Giữ cấu trúc logic tài liệu policy             |
| Metadata fields   | source, section, department, effective_date | phục vụ filter và citation |

---

### Preprocessing (Feature bổ sung)

**PDF → Markdown pipeline:**

- Parse PDF bằng `unstructured`
- Convert thành text có structure (heading, list, table)
- Chunk theo token
- Dùng LLM format thành Markdown chuẩn

👉 Mục tiêu:
- Giữ cấu trúc tài liệu
- Tránh mất thông tin khi parse PDF
- Cải thiện chất lượng retrieval

---

### Embedding model

- **Model**: VoyageAI embedding
- **Vector store**: ChromaDB (PersistentClient)
- **Similarity metric**: Cosine

---

## 3. Retrieval Pipeline (Sprint 2 + 3)

### Baseline (Sprint 2)

| Tham số      | Giá trị                      |
| ------------ | ---------------------------- |
| Strategy     | Dense (embedding similarity) |
| Top-k search | 10                           |
| Top-k select | 3                            |
| Rerank       | Không                        |

---

### Variant (Sprint 3)

| Tham số         | Giá trị | Thay đổi so với baseline |
| --------------- | ------- | ------------------------ |
| Strategy        | Hybrid  | Kết hợp dense + BM25     |
| Top-k search    | 10      | Không đổi                |
| Top-k select    | 3       | Không đổi                |
| Rerank          | Có      | Thêm bước rerank         |
| Query transform | Không   | Không đổi                |

---

**Lý do chọn variant:**

> Corpus chứa cả ngôn ngữ tự nhiên (policy) và keyword cụ thể (SLA, ERR-403).
> Hybrid giúp tăng recall khi query có keyword mismatch.
> Rerank giúp chọn chunk phù hợp hơn.

---

## 4. Generation (Sprint 2)

### Grounded Prompt Template
Answer only from the retrieved context below.
If the context is insufficient, say you do not know.
Cite the source field when possible.
Keep your answer short, clear, and factual.

Question: {query}

Context:
[1] {source} | {section} | score={score}
{chunk_text}

Answer:

---

### LLM Configuration

| Tham số     | Giá trị              |
| ----------- | -------------------- |
| Model       | claude-sonnet-4-6    |
| Temperature | 0                    |
| Max tokens  | 512                  |

---

## 5. Failure Mode Checklist

| Failure Mode   | Triệu chứng                         | Cách kiểm tra |
| -------------- | ----------------------------------- | ------------- |
| Index lỗi      | Retrieve sai tài liệu               | Kiểm tra metadata |
| Chunking tệ    | Chunk cắt giữa điều khoản           | Inspect chunk |
| Retrieval lỗi  | Không tìm thấy source               | Context recall |
| Rerank lỗi     | Mất chunk đúng                      | So sánh baseline vs variant |
| Generation lỗi | Answer không grounded               | Faithfulness |
| Token overload | Missing info (lost in the middle)   | Kiểm tra context length |

---

## 6. Diagram

```mermaid
graph LR
    A[Raw Docs] --> B[PDF → Markdown Preprocess]
    B --> C[Chunking]
    C --> D[Embedding]
    D --> E[ChromaDB]

    F[User Query] --> G[Query Processing]
    G --> H[Dense Retrieval]
    G --> I[Sparse Retrieval]
    H --> J[Merge (Hybrid)]
    I --> J

    J --> K[Rerank]
    K --> L[Top-K Select]

    L --> M[Build Context]
    M --> N[Prompt]
    N --> O[LLM]
    O --> P[Answer + Citation]
```
---

## 7. Nhận xét từ Evaluation
Context recall đạt 5.0 → retrieval rất tốt
Hybrid không cải thiện rõ rệt so với baseline
Rerank đôi khi loại bỏ chunk quan trọng → giảm quality

=> Kết luận:

Pipeline hoạt động tốt end-to-end, và cần tune thêm rerank để đạt hiệu quả cao hơn