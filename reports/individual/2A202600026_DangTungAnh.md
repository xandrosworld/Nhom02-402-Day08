# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đặng Tùng Anh
**MSSV:** 2A202600026
**Vai trò trong nhóm:** Retrieval Owner
**Ngày nộp:** 13/04/2026

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong buổi Lab này, tôi chịu trách nhiệm chính về phần **Retrieval (Truy xuất dữ liệu)** cho Sprint 3. Các đầu việc cụ thể tôi đã hoàn thành bao gồm:
1.  **Triển khai Hybrid Retrieval**: Xây dựng hàm `retrieve_sparse` sử dụng thuật toán BM25 (thư viện `rank-bm25`) và kết hợp với Dense Retrieval thông qua thuật toán **Reciprocal Rank Fusion (RRF)** để tối ưu hóa kết quả tìm kiếm.
2.  **Tối ưu hóa Tokenization**: Phát hiện và xử lý lỗi tìm kiếm từ khóa chính xác khi các thuật toán mặc định bị gây nhiễu bởi dấu câu (ví dụ: `(IT-ACCESS)`). Tôi đã chuyển sang dùng regex tokenizer để làm sạch dữ liệu.
3.  **Tích hợp Pipeline 5 chế độ**: Cập nhật hàm `rag_answer` và khối `main` để người dùng có thể linh hoạt chọn giữa: Dense, Sparse, Hybrid, Hybrid+Rerank, và Hybrid+Transform.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau buổi Lab, tôi đã hiểu sâu sắc về sự khác biệt giữa **Semantic Search** (Tìm kiếm theo ý nghĩa) và **Keyword Search** (Tìm kiếm theo từ khóa). 
*   Tôi nhận ra rằng dù Vector Search (Dense) rất mạnh trong việc hiểu ngữ cảnh, nhưng nó vẫn có thể bỏ lỡ các mã định danh viết tắt hoặc mã lỗi đặc thù nếu score không đủ cao. 
*   Việc kết hợp Hybrid bằng RRF thực sự là một cải thiện lớn cho độ chính xác của hệ thống RAG, giúp tận dụng được cả hai thế giới. 
*   Ngoài ra, tôi cũng hiểu rõ hơn về tầm quan trọng của các bước bổ trợ như **Reranking** (hậu xử lý) và **Query Transformation** (tiền xử lý) trong việc tinh chỉnh "phễu" dữ liệu trước khi đưa vào LLM.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều làm tôi bất ngờ nhất là sức ảnh hưởng của **Tokenization** đối với BM25. Ban đầu, khi dùng `.split()` mặc định, hệ thống hoàn toàn không tìm thấy cụm từ `"IT-ACCESS"` chỉ vì trong văn bản nó nằm trong dấu ngoặc đơn `(IT-ACCESS)`. Điều này dạy cho tôi bài học rằng dữ liệu đầu vào cần được làm sạch và chuẩn hóa cực kỳ kỹ lưỡng trước khi đưa vào các thuật toán thống kê.

Về khó khăn, việc xử lý **Git Conflict** trong một môi trường nhóm làm việc song song cường độ cao thực sự là một thử thách. Có những lúc vừa giải quyết xong conflict để chuẩn bị push thì server lại có bản cập nhật mới. Việc này đòi hỏi kỹ năng quản lý nhánh và giao tiếp tốt giữa các thành viên để tránh ghi đè code của nhau.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** "Dự án IT-ACCESS là gì?"

**Phân tích:** 
Đây là một câu hỏi điển hình để kiểm chứng sức mạnh của Hybrid Retrieval. Trong giai đoạn Baseline (chỉ dùng Dense), kết quả trả về thường bị "nhiễu" bởi các đoạn văn bản nói chung về bộ phận IT hoặc quy trình access review rộng hơn (score ~0.40). 

Khi áp dụng Hybrid với bộ tách từ Regex:
*   **BM25** đã bắt đúng 100% từ khóa `IT-ACCESS` tại Section 7 (Công cụ liên quan) và đẩy nó lên top nhờ điểm tần suất từ. 
*   **RRF** giúp kết hợp kết quả này với Dense, tạo ra một danh sách Context "sách" và trúng đích nhất. 
*   **Kết quả**: LLM không còn bị ảo giác và đã trả lời chính xác `IT-ACCESS` là tên project trên Jira dùng để quản lý ticket, thay vì trả lời mơ hồ hoặc từ chối trả lời như ở bản cũ. Điều này giúp cải thiện trực tiếp chỉ số **Context Recall** và **Answer Relevance**.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ triển khai thêm bước **Query Decomposition** (phân rã câu hỏi) một cách triệt để hơn cho các mode Transform. Hiện tại expansion mới chỉ hỗ trợ tìm các từ đồng nghĩa, nhưng nếu gặp câu hỏi phức tạp (ví dụ: "So sánh SLA P1 và quy trình hoàn tiền"), việc tách thành hai sub-queries sẽ giúp Retrieval lấy được context cho cả hai chủ đề một cách chính xác hơn nữa.
