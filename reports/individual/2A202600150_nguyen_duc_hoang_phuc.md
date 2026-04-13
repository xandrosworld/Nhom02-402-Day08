# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Đức Hoàng Phúc  
**MSSV:** 2A202600150  
**Vai trò trong nhóm:** Eval Owner  
**Ngày nộp:** 2026-04-13  
**Độ dài yêu cầu:** 500–800 từ  

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong lab này, tôi đảm nhận vai trò Eval Owner, chịu trách nhiệm xây dựng và hoàn thiện hệ thống đánh giá cho pipeline RAG. Cụ thể, tôi đã implement các hàm scoring gồm: faithfulness, answer relevance, context recall và completeness trong file eval.py. Sau đó, tôi chạy toàn bộ pipeline với 10 câu hỏi test để tạo scorecard baseline và variant. Tôi cũng thực hiện A/B comparison giữa dense retrieval và hybrid + rerank để phân tích sự khác biệt về hiệu năng. Ngoài ra, tôi tổng hợp kết quả vào các file báo cáo như scorecard_baseline.md, scorecard_variant.md và tuning-log.md. Vai trò của tôi giúp nhóm hiểu rõ điểm mạnh, điểm yếu của hệ thống và định hướng tuning tiếp theo.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi hiểu rõ hơn cách đánh giá một hệ thống RAG một cách có hệ thống thay vì chỉ nhìn vào câu trả lời. Tôi nhận ra rằng retrieval quality (đặc biệt là context recall) đóng vai trò rất quan trọng, vì nếu retrieve sai thì generation cũng sẽ sai. Ngoài ra, tôi hiểu rõ sự khác biệt giữa các metric như faithfulness (độ bám context) và relevance (độ đúng câu hỏi), vì một câu trả lời có thể đúng chủ đề nhưng vẫn không grounded. Tôi cũng học được cách thiết kế A/B testing trong RAG, chỉ thay đổi một biến (ví dụ hybrid hoặc rerank) để xác định nguyên nhân cải thiện hay suy giảm hiệu năng.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều khiến tôi ngạc nhiên là mặc dù hybrid retrieval và rerank được kỳ vọng sẽ cải thiện chất lượng, nhưng trong thực tế variant lại không tốt hơn baseline. Cụ thể, rerank đôi khi loại bỏ các chunk quan trọng, dẫn đến câu trả lời bị thiếu thông tin hoặc fail hoàn toàn. Điều này cho thấy tuning RAG không đơn giản và các thành phần có thể ảnh hưởng lẫn nhau. Khó khăn lớn nhất của tôi là thiết kế các hàm scoring sao cho phản ánh đúng chất lượng câu trả lời mà không cần dùng LLM-as-judge. Việc xử lý các trường hợp đặc biệt như câu hỏi không có trong tài liệu (recall = None) cũng cần cân nhắc kỹ để không làm sai lệch kết quả đánh giá.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** Approval Matrix để cấp quyền hệ thống là tài liệu nào?

**Phân tích:**

Ở câu hỏi này, baseline (dense retrieval) hoạt động tốt hơn variant. Baseline có thể retrieve được đúng chunk liên quan đến tài liệu access control, từ đó sinh ra câu trả lời tương đối đầy đủ (faithfulness = 4, completeness = 4). Tuy nhiên, ở variant (hybrid + rerank), hệ thống lại trả lời “không đủ dữ liệu”, mặc dù context recall vẫn đạt 5.0. Điều này cho thấy vấn đề không nằm ở retrieval mà nằm ở bước rerank. Cụ thể, rerank đã loại bỏ chunk quan trọng chứa thông tin về Approval Matrix, dẫn đến context cuối cùng không đủ để LLM trả lời. Đây là một failure mode điển hình của RAG pipeline: rerank làm mất thông tin quan trọng khi chỉ giữ top-k nhỏ. Trường hợp này cho thấy cần phải cân bằng giữa precision và recall, hoặc tăng top_k_select để tránh mất context quan trọng.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ thử cải thiện variant bằng cách tăng top_k_search và top_k_select để giảm rủi ro mất context khi rerank. Ngoài ra, tôi muốn thử query transformation để tăng khả năng match các câu hỏi có keyword đặc biệt. Cuối cùng, tôi sẽ tích hợp LLM-as-judge để đánh giá chính xác hơn thay vì chỉ dùng heuristic scoring.