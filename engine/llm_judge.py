import asyncio
import os
import json
import random
from typing import Dict, Any
import random

from openai import AsyncOpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize APIs
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPEN_ROUTER = os.getenv("OPEN_ROUTER")
GOOGLE_TOKEN = os.getenv("GOOGLE_TOKEN")

if GOOGLE_TOKEN:
    genai.configure(api_key=GOOGLE_TOKEN)

try:
    github_client = AsyncOpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )
except Exception:
    github_client = None

try:
    openrouter_client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPEN_ROUTER,
    )
except Exception:
    openrouter_client = None

async def safe_api_call(call_func, fallback_func=None):
    """
    RATE LIMIT HANDLING (MANDATORY). Exponential backoff handler for 429 RateLimitErrors.
    """
    wait = 1
    for retry in range(2):
        try:
            # Setting a harsh timeout so a lagging model doesn't block evaluation pipeline
            return await asyncio.wait_for(call_func(), timeout=5.0)
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "rate limit" in err_str or "timeout" in err_str or "quota" in err_str:
                await asyncio.sleep(wait)
                wait *= 2
            else:
                if fallback_func:
                    print(f"Primary failed with {type(e).__name__}, using fallback.")
                    return await fallback_func()
                raise e
    
    if fallback_func:
        print("Rate limits exhausted, falling back.")
        return await fallback_func()
    return "5.0"

class LLMJudge:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.rubrics = {
            "correctness": "Chấm điểm từ 0-10 dựa trên độ chính xác so với Ground Truth.",
            "faithfulness": "Chấm điểm từ 0-10 dựa trên việc câu trả lời có trung thành với retrieved context không.",
            "relevance": "Chấm điểm từ 0-10 dựa trên độ liên quan của câu trả lời với câu hỏi."
        }

    async def _call_openrouter(self, prompt: str) -> str:
        async def api_call():
            resp = await openrouter_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="anthropic/claude-3-haiku",
                temperature=0.0
            )
            return resp.choices[0].message.content
        return await safe_api_call(api_call)

    async def _call_github(self, prompt: str) -> str:
        async def api_call():
            resp = await github_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o",
                temperature=0.0
            )
            return resp.choices[0].message.content
        return await safe_api_call(api_call, fallback_func=lambda: self._call_openrouter(prompt))

    async def _call_gemini(self, prompt: str) -> str:
        async def api_call():
            model = genai.GenerativeModel('gemini-2.5-flash')
            resp = await model.generate_content_async(prompt)
            return resp.text
        return await safe_api_call(api_call, fallback_func=lambda: self._call_openrouter(prompt))

    def _parse_score(self, text: str) -> float:
        import re
        match = re.search(r"(\d+(\.\d+)?)", text)
        if match:
            return min(max(round(float(match.group(1)), 2), 0.0), 10.0)
        return 5.0

    def _apply_heuristic_penalties(self, answer: str, context: str, score: float) -> float:
        """Heuristic rule-based penalties."""
        ans_lower = answer.lower()
        if "theo hệ thống" in ans_lower or "đây là câu trả lời tốt" in ans_lower or "xin lỗi" in ans_lower:
            return min(score, 3.0)
            
        if "không có thông tin" in ans_lower and len(context) > 20: 
            # Có context nhưng agent bảo không có
            score -= 3.0
            
        if len(answer) > 200 and len(context) < 50:
            # Answer quá dài mà context quá ngắn -> Khả năng hallucination cao
            score -= 4.0
            
        return min(max(round(score, 2), 0.0), 10.0)

    async def _gpt_judge(self, question: str, answer: str, context: str) -> float:
        """Judge 1: Primary Judge (ChatGPT via GITHUB_TOKEN)"""
        prompt = f"""Evaluate the AI's answer based ONLY on the provided Context and Question. 
Return ONLY a JSON object: {{"score": <0-10 number>, "reason": "<explanation>"}}

EVALUATION CRITERIA:
1. Correctness: Does it directly answer the user's question?
2. Faithfulness: Are all facts strictly grounded in the Context?
3. Completeness: Does it provide the necessary details from the Context?

Question: {question}
Context: {context}
AI Answer: {answer}
"""
        text = await self._call_github(prompt)
        score = self._parse_score(text)
        return self._apply_heuristic_penalties(answer, context, score)

    async def _heuristic_judge(self, question: str, answer: str, context: str) -> float:
        """Judge 2: Diverse Secondary Judge (Gemini via GOOGLE_TOKEN)"""
        prompt = f"""You are an extremely strict evaluator focusing on DETECTING HALLUCINATION.
Does the Answer contain information NOT explicitly present in the Context?
Is the reasoning logical relative to the Question?

Provide ONLY a single numeric score from 0-10.
0 = Severe Hallucination / Contradiction.
10 = Perfectly grounded and reasoned.

[Question]: {question}
[Context]: {context}
[Answer]: {answer}
"""
        text = await self._call_gemini(prompt)
        score = self._parse_score(text)
        return self._apply_heuristic_penalties(answer, context, score)

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str, context: str = "") -> Dict[str, Any]:
        """
        CONSENSUS ENGINE
        """
        score_a, score_b = await asyncio.gather(
            self._gpt_judge(question, answer, context),
            self._heuristic_judge(question, answer, context)
        )
        
        avg_score = round((score_a + score_b) / 2, 2)
        
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
        pass
