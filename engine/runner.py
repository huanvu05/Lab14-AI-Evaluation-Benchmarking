import asyncio
import time
from typing import List, Dict

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge

    async def run_single_test(self, test_case: Dict, semaphore: asyncio.Semaphore) -> Dict:
        async with semaphore:
            start_time = time.perf_counter()
            
            try:
                # 1. Gọi Agent (with configurable timeout)
                response = await asyncio.wait_for(self.agent.query(test_case["query"]), timeout=10.0)
                latency = time.perf_counter() - start_time
                
                context = " ".join(response.get("contexts", []))
                
                # 2. Chạy RAGAS/Retrieval metrics
                retrieval_data = [{
                    "ground_truth_doc_id": test_case.get("ground_truth_doc_id", ""),
                    "retrieved_ids": response.get("metadata", {}).get("sources", [])
                }]
                ragas_scores = await self.evaluator.evaluate_batch(retrieval_data)
                
                # 3. Chạy Multi-Judge with context
                judge_result = await self.judge.evaluate_multi_judge(
                    question=test_case["query"], 
                    answer=response.get("answer", ""), 
                    ground_truth=test_case.get("expected_answer", ""),
                    context=context
                )
                
                return {
                    "test_case": test_case["query"],
                    "agent_response": response.get("answer", ""),
                    "latency": round(latency, 4),
                    "ragas": {
                        "retrieval": {
                            "hit_rate": ragas_scores["avg_hit_rate"],
                            "mrr": ragas_scores["avg_mrr"]
                        }
                    },
                    "judge": judge_result,
                    "status": "fail" if judge_result["final_score"] < 5 else "pass"
                }
            except Exception as e:
                latency = time.perf_counter() - start_time
                return {
                    "test_case": test_case.get("query", "Unknown"),
                    "agent_response": f"ERROR: {str(e)}",
                    "latency": round(latency, 4),
                    "ragas": {"retrieval": {"hit_rate": 0.0, "mrr": 0.0}},
                    "judge": {
                        "final_score": 0.0,
                        "agreement_rate": 0.0,
                        "is_conflict": False,
                        "conflict_reason": str(e),
                        "individual_scores": {}
                    },
                    "status": "error"
                }

    async def run_all(self, dataset: List[Dict], batch_size: int = 20) -> List[Dict]:
        """
        Chạy song song bằng asyncio.gather với Semaphore để kiểm soát concurrency tốt hơn.
        """
        semaphore = asyncio.Semaphore(batch_size)
        tasks = [self.run_single_test(case, semaphore) for case in dataset]
        
        results = await asyncio.gather(*tasks)
        return list(results)
