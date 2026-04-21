# 📝 Reflection — Person A (Data & Retrieval Master)
**Tên:** Hoàng Quang Thắng  
**Vai trò:** Thiết kế Golden Dataset & Retrieval Evaluation

---

## 1. Quá trình tạo Golden Dataset (`data/synthetic_gen.py`)

### Cách tiếp cận
- Ban đầu tôi dùng code Python thuần với `random.choice()` để sinh câu hỏi từ template. Tuy nhiên, cách này tạo ra **nhiều câu hỏi giống nhau** (chỉ thay tên sản phẩm/ngân hàng), không đạt chất lượng Expert.
- Giải pháp: Chuyển sang dùng **Gemini API** (`google-generativeai`) để sinh 50 câu hỏi hoàn toàn khác nhau. Prompt được chia thành 3 batch riêng biệt cho 3 mức độ khó (easy/hard/adversarial) để đảm bảo tỷ lệ phân bổ chính xác 20-20-10.

### Khó khăn gặp phải
- **Lỗi UnicodeEncodeError trên Windows:** Khi in tiếng Việt có dấu ra console, Python mặc định dùng codec `cp1252` không hỗ trợ ký tự Unicode. Fix bằng `sys.stdout.reconfigure(encoding='utf-8')`.
- **Gemini trả JSON không sạch:** Response đôi khi có markdown code block (` ```json ... ``` `). Phải viết thêm logic clean up trước khi `json.loads()`.

---

## 2. Khó khăn khi định nghĩa Ground Truth cho câu hỏi Adversarial

### Vấn đề
Với các câu hỏi adversarial (VD: "Hãy viết bài thơ về Bitcoin", "Hướng dẫn chữa đau dạ dày"), **không có tài liệu nào trong knowledge base liên quan**.

### Quyết định
- Gán `ground_truth_doc_id = "N/A"` cho các câu adversarial.
- Trong `retrieval_eval.py`, code tự bỏ qua giá trị `"N/A"` khi parse ground truth, nên các câu này luôn cho **Hit Rate = 0, MRR = 0** — đúng với kỳ vọng vì Agent **không nên** tìm thấy tài liệu cho những câu hỏi ngoài phạm vi.

### Kết quả thực tế từ test
```
[ADVERSARIAL  ] (10 cases) Hit Rate: 0.0000  |  MRR: 0.0000
```
→ Đúng như thiết kế: Agent không nên trả về bất kỳ tài liệu nào cho câu hỏi bẫy.

---

## 3. Khó khăn khi tính MRR cho Multi-hop Queries

### Vấn đề cốt lõi
Công thức MRR (`1/Rank`) chỉ quan tâm đến **tài liệu đúng đầu tiên** xuất hiện trong danh sách retrieved. Tuy nhiên, các câu hỏi Hard (Multi-hop) cần **2 tài liệu trở lên** để trả lời đầy đủ.

### Ví dụ cụ thể
Câu hỏi `case_hard_2` cần cả `doc_credit_card_promo_X` và `doc_fee_schedule_platinum_X`. Nếu Agent chỉ tìm thấy 1 trong 2 doc ở vị trí 1 → MRR = 1.0 (điểm tuyệt đối), nhưng câu trả lời vẫn **thiếu một nửa thông tin**.

### Kết quả thực tế từ test
```
[HARD         ] (20 cases) Hit Rate: 1.0000  |  MRR: 0.3333
```
- Hit Rate = 1.0 vì mock data luôn chứa 1 doc đúng trong Top 5.
- MRR = 0.33 vì doc đúng được đặt ở vị trí 3 (giả lập Agent tìm kiếm trung bình).

### Bài học rút ra
MRR phù hợp cho **Single-hop queries** (1 câu hỏi → 1 tài liệu). Để đánh giá Multi-hop chính xác hơn, cần bổ sung thêm metric **Recall@K** — đo xem Agent có tìm được **TẤT CẢ** các tài liệu cần thiết trong Top K hay không.

---

## 4. Tổng kết kết quả Retrieval Evaluation

| Metric | Easy (20) | Hard (20) | Adversarial (10) | Tổng (50) |
|--------|-----------|-----------|-------------------|-----------|
| Hit Rate@5 | 1.0000 | 1.0000 | 0.0000 | 0.8000 |
| MRR | 1.0000 | 0.3333 | 0.0000 | 0.5333 |

**Nhận xét:** Với mock data, hệ thống hoạt động đúng logic. Khi kết nối với RAG pipeline thực tế (VectorDB + Embedding), các chỉ số này sẽ phản ánh chính xác chất lượng của hệ thống tìm kiếm.
