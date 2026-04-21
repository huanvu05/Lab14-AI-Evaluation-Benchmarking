### 👥 PHÂN CÔNG CHÍNH THỨC
### 👨‍💻 PERSON A – DATA + RETRIEVAL + DATA ENGINEERING

### Vai trò: Data Engineer / Retrieval Engineer

### 📁 OWN FOLDER STRUCTURE (KHÔNG ĐƯỢC ĐỤNG PERSON B)
data/
  synthetic_gen.py
  golden_set.jsonl

retrieval/
  evaluator.py
  metrics.py
  retriever_eval_runner.py

reports/
  retrieval_report.json
### 🧠 TASK 1 – Synthetic Dataset Generation
📄 File: data/synthetic_gen.py
🎯 Làm gì:
Sinh 50–100 test cases
Mỗi case phải có:
{
  "id": "q1",
  "query": "...",
  "ground_truth_doc_id": "doc_12",
  "expected_answer": "..."
}
⚙️ Logic bắt buộc:
Có 4 loại câu hỏi:
fact-based
multi-hop
tricky (adversarial)
paraphrase
Ensure coverage retrieval edge cases
💡 Điểm cao:
Có “hard cases” để test failure retrieval
Có mapping doc_id rõ ràng
Không random noise
### 🧠 TASK 2 – Retrieval Evaluation Engine
📄 File: retrieval/evaluator.py
🎯 Làm gì:
Input:
query
retrieved docs
ground truth doc id
📊 Metrics:
1. Hit Rate
Top-K có chứa correct doc không
2. MRR
Reciprocal rank của correct doc
📄 File: retrieval/metrics.py
🎯 Làm gì:
Implement metric functions:
def hit_rate(retrieved, ground_truth)
def mean_reciprocal_rank(results)
📄 File: retrieval/retriever_eval_runner.py
🎯 Làm gì:
Loop toàn bộ golden set
Call retriever
Collect metrics
Save report:
reports/retrieval_report.json
🏆 CÁCH ĐỂ PERSON A ĐẠT ĐIỂM CAO

✔ Có phân tích:

Retrieval failure cases
Chunking issues
Query ambiguity

✔ Có số liệu:

Hit Rate @1 / @5 / @10
MRR average

✔ Có conclusion:

Retrieval ảnh hưởng generation như thế nào
### 👨‍💻 PERSON B – AI EVALUATION + BENCHMARK + REGRESSION

### Vai trò: AI Engineer / Backend / Evaluation System Architect

### 📁 OWN FOLDER STRUCTURE (KHÔNG ĐỤNG PERSON A)
evaluation/
  judges/
    gpt_judge.py
    claude_judge.py

  consensus.py
  evaluator_engine.py

benchmark/
  async_runner.py
  benchmark.py

regression/
  compare.py
  release_gate.py

analysis/
  failure_analysis.md
### 🧠 TASK 1 – Multi-Judge System
📄 evaluation/judges/gpt_judge.py
🎯 Làm gì:
Call LLM GPT để chấm:
correctness
faithfulness
relevance

Output:

{
  "score": 0-10,
  "reason": "..."
}
📄 evaluation/judges/claude_judge.py
Same interface nhưng model khác
Mục tiêu: diversity judge
📄 evaluation/consensus.py
🎯 Làm gì:
Combine 2 judges:
final_score = (gpt_score + claude_score) / 2
+ nâng cao:
Agreement rate:
abs(gpt - claude) < threshold
### 🧠 TASK 2 – Evaluation Engine Core
📄 evaluation/evaluator_engine.py
🎯 Pipeline:
query → retrieval context → agent answer → judges → final score
Output:
{
  "query": "",
  "answer": "",
  "score": 8.2,
  "judge_details": {...}
}
### ⚡ TASK 3 – Async Benchmark System
📄 benchmark/async_runner.py
🎯 Làm gì:
Run 50+ eval cases parallel
Yêu cầu:
asyncio / multiprocessing
batch processing
timeout handling
📄 benchmark/benchmark.py
Output:
reports/benchmark_results.json

Bao gồm:

latency
cost
score distribution
failure rate
### 🔁 TASK 4 – REGRESSION SYSTEM
📄 regression/compare.py
🎯 So sánh V1 vs V2:
Score delta
Retrieval delta
Latency delta
📄 regression/release_gate.py
🎯 Logic quyết định:
if score_v2 > score_v1 and cost <= threshold:
    RELEASE
else:
    ROLLBACK
### 🧠 TASK 5 – FAILURE ANALYSIS
📄 analysis/failure_analysis.md
🎯 Bắt buộc có:
1. Failure clustering:
retrieval error
hallucination
reasoning error
2. 5 Whys format:
Problem: Wrong answer
Why 1: retrieval wrong
Why 2: chunk mismatch
Why 3: bad splitting
Why 4: no overlap
Why 5: ingestion pipeline weak
🏆 CÁCH ĐỂ PERSON B ĐẠT ĐIỂM CAO

✔ Có Multi-Judge + Consensus
✔ Có Async benchmark thật sự chạy nhanh
✔ Có regression logic rõ ràng
✔ Có auto release gate
✔ Có failure analysis sâu (5 Whys đúng bản chất hệ thống)

### 🚨 QUY TẮC KHÔNG ĐƯỢC VI PHẠM

❌ Không dùng chung file giữa 2 người
❌ Không hardcode result
❌ Không thiếu Retrieval metrics
❌ Không chỉ 1 judge

### ⚙️ FINAL ARCHITECTURE FLOW
### PERSON A:
  Dataset → Retrieval → Metrics

          ↓

### PERSON B:
  Agent → Judges → Benchmark → Regression → Report
### 🏆 STRATEGY ĐỂ ĐẠT >90/100
### 🔥 MUST HAVE:
Multi-Judge system
Retrieval metrics (MRR + Hit Rate)
Async evaluation
Regression system
🔥 DIFFERENCE MAKER:
Failure clustering thông minh
5 Whys sâu đến root cause thật
Release gate logic rõ ràng
Benchmark nhanh + cost tracking