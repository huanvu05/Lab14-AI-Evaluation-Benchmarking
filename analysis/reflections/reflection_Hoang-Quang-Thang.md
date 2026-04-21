# 📝 Reflection (Person A) - Data & Retrieval Master

## Khó khăn khi định nghĩa Ground Truth cho các câu hỏi mập mờ (Adversarial)
Khi tạo ra các câu hỏi bẫy (ví dụ: "Lãi suất vay mua ô tô?" trong khi dữ liệu chỉ có mua nhà), việc gắn nhãn `ground_truth_doc_id` gây ra một số băn khoăn:
1. **Nên gán rỗng hay gán tài liệu gần nhất?** Nếu gán rỗng (không có tài liệu), hệ thống tìm kiếm (RAG) khi bốc ra tài liệu nhà sẽ bị đánh giá là sai hoàn toàn (Hit Rate = 0). Tuy nhiên, trong thực tế, Agent cần đọc tài liệu "vay nhà" để có căn cứ trả lời "Chúng tôi không có dịch vụ vay ô tô".
2. **Quyết định:** Tôi chọn cách gán `ground_truth_doc_id` bằng tài liệu bị ám chỉ sai (`doc_vay_nha`). Cách này đo lường được xem VectorDB có lôi ra đúng tài liệu có tính liên quan cao nhất hay không để LLM làm nhiệm vụ Judge.

## Khó khăn khi tính điểm MRR (Mean Reciprocal Rank) cho Multi-hop
1. **Bản chất của Multi-hop:** Các câu hỏi Hard (Multi-hop) yêu cầu từ 2 documents trở lên (VD: `doc_vay_tin_chap`, `doc_tiet_kiem`).
2. **Cách tính MRR:** Công thức nguyên bản của MRR là `1/Rank` của document đúng *đầu tiên* xuất hiện. Tuy nhiên, đối với câu hỏi cần 2 tài liệu, việc tìm thấy 1 tài liệu ở Top 1 (MRR = 1.0) không đảm bảo mô hình có đủ thông tin để trả lời câu hỏi đa bước (vì tài liệu số 2 có thể bị rớt khỏi Top 5).
3. **Bài học rút ra:** MRR là một chỉ số tốt cho Single-hop (tìm 1 tài liệu duy nhất). Đối với Multi-hop query, ta có thể cần phải kết hợp thêm `Recall@K` (tìm được TẤT CẢ các tài liệu cần thiết trong Top K) thì mới bao quát được chất lượng của Retriever.
