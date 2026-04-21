from typing import List, Dict
import json

def load_golden(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, retrieved_docs: List[str], ground_truth: List[str], k: int = 5) -> Dict[str, float]:
        """
        Tính tỷ lệ tìm trúng đích trong Top K.
        Trả về kết quả dưới dạng Dict.
        """
        top_k_retrieved = retrieved_docs[:k]
        hit = any(doc_id in top_k_retrieved for doc_id in ground_truth)
        return {"hit_rate": 1.0 if hit else 0.0}

    def calculate_mrr(self, retrieved_docs: List[str], ground_truth: List[str]) -> Dict[str, float]:
        """
        Tính Mean Reciprocal Rank (chỉ số ưu tiên document đúng nằm ở vị trí cao).
        Trả về kết quả dưới dạng Dict.
        
        ========================================
        GIẢI THÍCH CÔNG THỨC MRR (Mean Reciprocal Rank):
        ========================================
        MRR = 1 / Rank
        
        Trong đó Rank là vị trí xuất hiện (chỉ số đếm từ 1) của TÀI LIỆU ĐÚNG ĐẦU TIÊN
        được tìm thấy trong danh sách tài liệu mà Agent trả về (retrieved_docs).
        
        Ví dụ:
        - Nếu document đúng nằm ở vị trí số 1 -> Rank = 1 -> MRR = 1/1 = 1.0 (Tuyệt đối)
        - Nếu document đúng nằm ở vị trí số 2 -> Rank = 2 -> MRR = 1/2 = 0.5
        - Nếu document đúng nằm ở vị trí số 3 -> Rank = 3 -> MRR = 1/3 = 0.33
        - Nếu không có document đúng nào xuất hiện -> MRR = 0.0
        
        Chỉ số này đặc biệt quan trọng vì trải nghiệm người dùng sẽ tốt hơn 
        rất nhiều nếu kết quả đúng xuất hiện ngay đầu tiên thay vì phải kéo xuống dưới.
        """
        for i, doc_id in enumerate(retrieved_docs):
            if doc_id in ground_truth:
                return {"mrr": 1.0 / (i + 1)}
        return {"mrr": 0.0}

    async def evaluate_batch(self, dataset: List[Dict]) -> Dict[str, float]:
        """
        Chạy eval cho toàn bộ bộ dữ liệu.
        Dataset cần có trường 'ground_truth_doc_id' và 'retrieved_ids'.
        """
        if not dataset:
            return {"avg_hit_rate": 0.0, "avg_mrr": 0.0}
            
        total_hit_rate = 0.0
        total_mrr = 0.0
        count = len(dataset)
        
        for item in dataset:
            # Parse ground_truth từ dạng string (VD: "doc1, doc2" hoặc "doc1+doc2")
            gt_raw = str(item.get("ground_truth_doc_id", ""))
            gt_docs = [doc.strip() for doc in gt_raw.replace('+', ',').split(',') if doc.strip()]
            
            # Lấy danh sách retrieved_ids (Mặc định là rỗng nếu chưa chạy qua RAG)
            retrieved_docs = item.get("retrieved_ids", [])
            
            # Tính điểm
            hit_res = self.calculate_hit_rate(retrieved_docs, gt_docs, k=5)
            mrr_res = self.calculate_mrr(retrieved_docs, gt_docs)
            
            total_hit_rate += hit_res["hit_rate"]
            total_mrr += mrr_res["mrr"]

        return {
            "avg_hit_rate": round(total_hit_rate / count, 4),
            "avg_mrr": round(total_mrr / count, 4)
        }

if __name__ == "__main__":
    import asyncio
    
    async def test_evaluator():
        print("Đang load dữ liệu test từ data/golden_set.jsonl...")
        try:
            dataset = load_golden("data/golden_set.jsonl")
        except FileNotFoundError:
            print("Không tìm thấy file. Hãy chạy python data/synthetic_gen.py trước!")
            return
            
        print(f"Đã load {len(dataset)} câu hỏi. Đang giả lập (mock) kết quả tìm kiếm từ Agent...")
        
        # Giả lập Agent tìm kiếm:
        # - Cho 25 câu đầu: Tìm trúng đích ở vị trí số 1 (Hit=1, MRR=1.0)
        # - Cho 15 câu tiếp: Tìm trúng đích ở vị trí số 3 (Hit=1, MRR=0.333)
        # - Cho 10 câu cuối: Không tìm thấy (Hit=0, MRR=0.0)
        for i, item in enumerate(dataset):
            gt_raw = str(item.get("ground_truth_doc_id", ""))
            gt_docs = [doc.strip() for doc in gt_raw.replace('+', ',').split(',') if doc.strip()]
            
            if not gt_docs:
                item["retrieved_ids"] = []
                continue
                
            true_doc = gt_docs[0]
            if i < 25:
                item["retrieved_ids"] = [true_doc, "doc_fake_1", "doc_fake_2"] # Vị trí 1
            elif i < 40:
                item["retrieved_ids"] = ["doc_fake_1", "doc_fake_2", true_doc] # Vị trí 3
            else:
                item["retrieved_ids"] = ["doc_fake_1", "doc_fake_2", "doc_fake_3"] # Không có
                
        evaluator = RetrievalEvaluator()
        results = await evaluator.evaluate_batch(dataset)
        
        print("\n=== KẾT QUẢ TEST EVALUATOR ===")
        print(f"Trung bình Hit Rate: {results['avg_hit_rate']}")
        print(f"Trung bình MRR:      {results['avg_mrr']}")
        
    asyncio.run(test_evaluator())
