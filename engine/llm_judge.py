import asyncio
from typing import Dict, Any
import random

class LLMJudge:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        # Định nghĩa rubrics chi tiết cho các tiêu chí: Correctness, Faithfulness, Relevance
        self.rubrics = {
            "correctness": "Chấm điểm từ 0-10 dựa trên độ chính xác so với Ground Truth.",
            "faithfulness": "Chấm điểm từ 0-10 dựa trên việc câu trả lời có trung thành với retrieved context không. Phạt nặng (hallucination) nếu thêm thông tin ngoài lề.",
            "relevance": "Chấm điểm từ 0-10 dựa trên độ liên quan của câu trả lời với câu hỏi."
        }

    async def _gpt_judge(self, question: str, answer: str, ground_truth: str, context: str) -> float:
        """
        Judge 1: GPT-based (Mocked with heuristics for fast local testing simulating real OpenAI call).
        Evaluates correctness, faithfulness, relevance.
        """
        await asyncio.sleep(0.1) # Simulate network call
        if not answer or "xin lỗi" in answer.lower():
            return 3.0
            
        score = 8.0 # Base score for reasonable length
        if ground_truth and any(word.lower() in answer.lower() for word in ground_truth.split() if len(word) > 4):
            score += 1.5
            
        # Penalize hallucination if context is ignored but answer has facts
        if context and "không có thông tin" not in answer.lower() and len(answer) > (len(context) + 50):
            score -= 2.5 # Hallucination penalty
            
        return round(min(max(score + random.uniform(-0.5, +0.5), 0.0), 10.0), 2)

    async def _heuristic_judge(self, answer: str, context: str) -> float:
        """
        Judge 2: Heuristic/Rule-based Judge (Diverse Perspective).
        """
        await asyncio.sleep(0.05)
        score = 5.0
        
        # Rule 1: Length
        if len(answer) > 20: 
            score += 2.0
            
        # Rule 2: Overlap with context
        if context:
            overlap = len(set(answer.lower().split()) & set(context.lower().split()))
            if overlap > 3:
                score += 3.0
            elif len(answer) > 40 and overlap < 2:
                # Strong hallucination penalty
                score -= 4.0
                
        return round(min(max(score, 0.0), 10.0), 2)

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str, context: str = "") -> Dict[str, Any]:
        """
        CONSENSUS ENGINE: Gọi ít nhất 2 model/judges.
        Tính toán sự sai lệch. Nếu lệch > ngưỡng, đánh dấu Conflict.
        """
        # Gọi 2 judges song song
        score_a, score_b = await asyncio.gather(
            self._gpt_judge(question, answer, ground_truth, context),
            self._heuristic_judge(answer, context)
        )
        
        avg_score = round((score_a + score_b) / 2, 2)
        
        # Kiểm tra sự đồng thuận
        disagreement_threshold = 2.0
        score_diff = abs(score_a - score_b)
        is_conflict = score_diff > disagreement_threshold
        
        agreement_rate = 1.0 if not is_conflict else max(0.0, 1.0 - (score_diff / 5.0))
        
        return {
            "final_score": avg_score,
            "agreement_rate": round(agreement_rate, 2),
            "is_conflict": is_conflict,
            "conflict_reason": f"Disagreement (Diff={score_diff:.2f}) > {disagreement_threshold}" if is_conflict else None,
            "individual_scores": {
                "gpt_judge": score_a,
                "heuristic_judge": score_b
            }
        }

    async def check_position_bias(self, response_a: str, response_b: str):
        """
        Nâng cao: Thực hiện đổi chỗ response A và B để xem Judge có thiên vị vị trí không.
        """
        pass
