### 🚀 Kế hoạch Triển khai Lab 14: AI Evaluation Factory

Dành riêng cho nhóm 2 người - Chiến lược "Zero-Conflict" (Không đụng file)

Mục tiêu của tài liệu này là tối ưu hóa sức lực của 2 người để đạt 100/100 điểm Expert. Chìa khóa thành công là chia tách hoàn toàn quyền sở hữu file (File Ownership) và giao tiếp với nhau thông qua một cấu trúc JSON duy nhất (API Contract).

### 🤝 THE HANDSHAKE: Giao kèo Dữ liệu (Thống nhất trước khi code)

Hai người không cần làm chung file, chỉ cần thống nhất 1 điều duy nhất: Định dạng file sinh ra từ Task A (Person A) để Task B (Person B) đọc vào.

File: data/golden_set.jsonl (Person A tạo ra, Person B chỉ đọc)

{"id": "case_1", "query": "Lãi suất vay mua nhà là bao nhiêu?", "expected_answer": "Khoảng 6.5%/năm", "ground_truth_doc_id": "doc_vay_nha_01", "difficulty": "easy"}


### 👤 PERSON A: DATA & RETRIEVAL MASTER

Nhiệm vụ: Đóng vai trò "Red Team" (người tạo ra bẫy) và kỹ sư đo lường hệ thống tìm kiếm (VectorDB).
Quyền sở hữu file (Person B tuyệt đối không sửa):

data/synthetic_gen.py

data/HARD_CASES_GUIDE.md

engine/retrieval_eval.py

analysis/reflections/reflection_PersonA.md

📝 Chi tiết công việc & Cách lấy điểm cao:

### 1. File data/synthetic_gen.py (Mục tiêu: Golden Dataset & SDG - 10đ)

Làm gì: Viết script tự động sinh ra file data/golden_set.jsonl với ít nhất 50 test cases.

Bí quyết điểm cao (Expert):

Không được dùng file tĩnh, phải có code Python sinh ra file JSONL.

Phải có tỷ lệ phân bổ độ khó (Difficulty Distribution). Ví dụ: 20 câu Dễ, 20 câu Khó (Multi-hop, cần 2 documents để trả lời), 10 câu Bẫy (Adversarial - từ ngữ mập mờ).

Bắt buộc phải có trường ground_truth_doc_id chính xác.

### 2. File engine/retrieval_eval.py (Mục tiêu: Retrieval Evaluation - 10đ)

Làm gì: Xây dựng module nhận đầu vào là danh sách các ID tài liệu Agent tìm được, so sánh với ground_truth_doc_id để chấm điểm tìm kiếm.

Hàm cần viết:

calculate_hit_rate(retrieved_docs, ground_truth, k=5): Tính tỷ lệ tìm trúng đích trong Top K.

calculate_mrr(retrieved_docs, ground_truth): Tính Mean Reciprocal Rank (chỉ số ưu tiên document đúng nằm ở vị trí cao).

Bí quyết điểm cao (Expert): Comment giải thích rõ ràng công thức MRR trong code. Trả về kết quả dưới dạng Dict để Person B dễ dàng gọi hàm.

### 3. Files Phân tích & Báo cáo

data/HARD_CASES_GUIDE.md: Liệt kê 3-5 câu hỏi bẫy khó nhất bạn đã tạo, giải thích vì sao nó có thể làm gãy hệ thống (Red Teaming).

reflection_PersonA.md: Viết về khó khăn khi định nghĩa Ground Truth cho các câu hỏi mập mờ và cách tính MRR.

### 👤 PERSON B: EVALUATION PIPELINE & ANALYST

Nhiệm vụ: Kỹ sư xây dựng "Nhà máy chấm điểm", chạy Async tốc độ cao, xử lý đa giám khảo và đưa ra quyết định Release.
Quyền sở hữu file (Person A tuyệt đối không sửa):

engine/llm_judge.py

engine/runner.py

main.py

analysis/failure_analysis.md

analysis/reflections/reflection_PersonB.md

📝 Chi tiết công việc & Cách lấy điểm cao:

### 1. File engine/llm_judge.py (Mục tiêu: Multi-Judge Consensus - 15đ)

Làm gì: Viết class hoặc hàm gọi API của ít nhất 2 Giám khảo LLM khác nhau (VD: GPT-4o-mini làm Judge 1, Claude-3-Haiku hoặc Prompt check Rule-based làm Judge 2).

Bí quyết điểm cao (Expert): - Tránh prompt sơ sài. Phải cung cấp query, expected_answer, và agent_answer cho giám khảo.

Viết logic calculate_consensus(score1, score2): Tính độ chênh lệch điểm. Nếu chênh nhau <= 2 điểm -> lấy trung bình. Nếu chênh > 2 -> gán cờ needs_human_review = True.

Đỉnh cao: Implement chỉ số toán học Cohen's Kappa (có thể dùng thư viện sklearn) để đo độ đồng thuận của 2 Judge.

### 2. File engine/runner.py (Mục tiêu: Performance Async - 10đ)

Làm gì: Viết hàm run_benchmark_async() sử dụng thư viện asyncio và aiohttp để gọi LLM Judge song song.

Bí quyết điểm cao (Expert): - Sử dụng asyncio.Semaphore(10) để giới hạn số luồng gọi cùng lúc (tránh lỗi Rate Limit 429 từ OpenAI/Anthropic).

Có bộ đếm token và nội suy ra Chi phí (Cost) cho lần chạy benchmark. Đo thời gian (Latency) phải < 2 phút cho 50 cases.

### 3. File main.py (Mục tiêu: Regression Testing - 10đ)

Làm gì: File thực thi chính. Import hàm của Person A và Person B.

Luồng chạy: Đọc dataset -> Chạy Retrieval Eval (Person A) -> Chạy LLM Judge Eval (Person B).

Bí quyết điểm cao (Expert): Viết thêm hàm auto_release_gate(metrics_v1, metrics_v2). Logic: Nếu MRR V2 > V1 VÀ Final Score V2 >= V1 -> In ra màn hình console [PASS] VERSION V2 IS READY FOR RELEASE.

### 4. Files Phân tích & Báo cáo (Mục tiêu: Failure Analysis - 5đ)

analysis/failure_analysis.md: Mở file benchmark_results.json sau khi chạy xong, lọc ra những câu bị dưới 5 điểm. Sử dụng phương pháp "5 Whys" (Hỏi tại sao 5 lần).
Ví dụ: Tại sao điểm thấp? -> Vì agent sinh ra hallucination. -> Tại sao hallucination? -> Vì context đưa vào bị sai. -> Tại sao context sai? -> Vì hệ thống Retrieval tìm sai doc (nhìn điểm Hit Rate bằng 0). -> Kết luận lỗi gốc (Root Cause): Ingestion/Chunking.

reflection_PersonB.md: Viết về cách khắc phục lỗi Rate Limit khi chạy Async, hoặc khó khăn khi dung hòa điểm số giữa 2 giám khảo.

### 🚦 QUY TRÌNH NỘP BÀI CHUẨN XÁC

Để chắc chắn pass check_lab.py:

### Person A chạy: python data/synthetic_gen.py (để sinh data).

### Person B chạy: python main.py (để sinh ra thư mục reports/ chứa summary.json).

### Cả hai cùng kiểm tra: python check_lab.py

Gom tất cả push lên Github. Đảm bảo file .env đã được đưa vào .gitignore.

Chúc 2 bạn trở thành cỗ máy AI Engineering hoàn hảo! 🚀