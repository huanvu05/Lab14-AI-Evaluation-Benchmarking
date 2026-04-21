# 🧠 Individual Reflection – Task B: AI Evaluation Engine
> Vũ Văn Huân - X03 - C401 - 2A202600348
## 👤 Thông tin

* **Vai trò:** AI Engineer (Evaluation System)
* **Phụ trách:** Multi-Judge Evaluation, Benchmark Engine, Regression System

---

# 🚀 1. Những gì đã thực hiện

## 1.1. Xây dựng Multi-Judge Evaluation System

Tôi đã triển khai hệ thống đánh giá sử dụng nhiều mô hình (Multi-Judge), bao gồm:

* Judge chính sử dụng ChatGPT (qua GitHub Token)
* Judge phụ sử dụng Google Gemini
* Fallback thông qua OpenRouter để đảm bảo hệ thống không bị gián đoạn khi gặp lỗi rate limit (429)

### Điểm nổi bật:

* Thiết kế cơ chế **consensus scoring** để tổng hợp điểm từ nhiều judge
* Tính toán **agreement rate** nhằm đo độ đồng thuận giữa các mô hình
* Xử lý conflict khi các judge có đánh giá khác nhau

---

## 1.2. Thiết kế Evaluation Engine

Hệ thống Evaluation được xây dựng theo pipeline:

```
Query → Retrieval → Agent Answer → Multi-Judge → Final Score
```

Trong đó:

* Agent sử dụng thông tin từ Retrieval để sinh câu trả lời
* Judge đánh giá dựa trên:

  * Correctness
  * Faithfulness (bám context)
  * Relevance

---

## 1.3. Async Benchmark System

Tôi đã xây dựng hệ thống benchmark chạy bất đồng bộ:

* Sử dụng `asyncio` + `Semaphore` để kiểm soát concurrency
* Có cơ chế batching để tránh rate limit
* Tối ưu thời gian chạy < 2 phút cho 50+ test cases

### Kết quả:

* Hệ thống có thể xử lý nhiều request song song
* Giảm đáng kể thời gian evaluation so với chạy tuần tự

---

## 1.4. Regression & Auto Release Gate

Triển khai hệ thống so sánh giữa hai phiên bản Agent:

* So sánh:

  * Average Score
  * Retrieval Metrics
  * Latency

### Logic quyết định:

* Nếu phiên bản mới tốt hơn → Release
* Nếu kém hơn → Rollback

---

## 1.5. Failure Analysis & 5 Whys

Tôi đã xây dựng cơ chế phân tích lỗi:

* Phân loại lỗi:

  * Retrieval error
  * Hallucination
  * Reasoning error

* Áp dụng phương pháp **5 Whys** để tìm nguyên nhân gốc rễ

---

# ⚠️ 2. Những vấn đề gặp phải

## 2.1. Fake Evaluation (Vấn đề nghiêm trọng ban đầu)

Ban đầu hệ thống gặp lỗi:

* Agent trả lời dạng template (không phải câu trả lời thật)
* Judge luôn cho điểm 10/10
* Retrieval đạt 100% cho mọi test case

👉 Điều này dẫn đến hệ thống **không phản ánh đúng chất lượng AI**

---

## 2.2. Judge không độc lập

* Các judge ban đầu có xu hướng cho điểm giống nhau
* Agreement rate = 100% (không thực tế)

👉 Nguyên nhân:

* Prompt tương tự nhau
* Logic đánh giá chưa đủ khác biệt

---

## 2.3. Leakage Ground Truth

* Một số trường hợp vô tình sử dụng `expected_answer` trong quá trình đánh giá
* Khiến judge bị bias và cho điểm cao bất thường

---

## 2.4. Rate Limit (429 Errors)

* Khi gọi API nhiều lần (GPT, Gemini), hệ thống bị lỗi 429

### Giải pháp:

* Áp dụng exponential backoff
* Thiết kế fallback sang OpenRouter

---

# 🛠️ 3. Cách khắc phục

## 3.1. Sửa Agent

* Loại bỏ hoàn toàn template response
* Buộc Agent phải generate câu trả lời từ context thực tế

---

## 3.2. Sửa Judge

* Không truyền `expected_answer` vào judge

* Chỉ sử dụng:

  * Query
  * Context
  * Answer

* Thiết kế prompt khác nhau cho từng judge

---

## 3.3. Tạo tín hiệu đánh giá thực

* Chấp nhận:

  * câu trả lời sai
  * disagreement giữa judge
  * score không hoàn hảo

👉 Giúp hệ thống phản ánh đúng chất lượng

---

## 3.4. Cải thiện robustness

* Thêm fallback LLM (OpenRouter)
* Retry logic khi gặp lỗi API
* Logging rõ ràng các failure case

---

# 📊 4. Kết quả đạt được

Sau khi cải tiến:

* Hệ thống có thể:

  * Đánh giá thực chất chất lượng câu trả lời
  * Phát hiện hallucination
  * Phân biệt rõ các mức độ đúng/sai

* Benchmark chạy ổn định với async

* Có khả năng mở rộng lên production

---

# 🧠 5. Bài học rút ra

## 🔥 1. Evaluation khó hơn xây Agent

* Việc đánh giá AI không đơn giản là “so sánh đúng/sai”
* Cần thiết kế hệ thống đo lường đáng tin cậy

---

## 🔥 2. Perfect score = dấu hiệu nguy hiểm

* Score quá đẹp thường là dấu hiệu hệ thống bị sai logic
* Một hệ thống tốt phải có:

  * lỗi
  * disagreement
  * variance

---

## 🔥 3. Multi-Judge là bắt buộc

* Không thể tin vào 1 model duy nhất
* Cần nhiều góc nhìn để đánh giá khách quan

---

## 🔥 4. Production mindset rất quan trọng

* Phải xử lý:

  * rate limit
  * latency
  * cost
  * failure

---

# 🏁 6. Kết luận

Task B giúp tôi hiểu sâu về:

* Cách xây dựng hệ thống đánh giá AI thực tế
* Những vấn đề khó trong evaluation (bias, hallucination, overfitting)
* Cách thiết kế hệ thống robust, scalable

Hệ thống hiện tại đã tiến gần tới một **AI Evaluation Factory thực tế**, không chỉ chạy được mà còn có khả năng phản ánh đúng chất lượng của AI Agent.
