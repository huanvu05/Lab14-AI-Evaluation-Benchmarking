import asyncio
import os
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

OPEN_ROUTER = os.getenv("OPEN_ROUTER")

class MainAgent:
    """
    Agent RAG sử dụng LLM thực tế (OpenRouter) để sinh câu trả lời.
    """
    def __init__(self):
        self.name = "SupportAgent-v1"
        try:
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPEN_ROUTER,
            )
        except Exception:
            self.client = None

    async def generate_thought(self, query: str, context: str) -> str:
        if not self.client:
            return "Tôi không thể kết nối tới LLM để trả lời câu hỏi của bạn."
            
        prompt = f"""You are a helpful assistant.

Context:
{context}

Question:
{query}

Answer concisely and factually based ONLY on the context:"""
        try:
            resp = await asyncio.wait_for(
                self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="anthropic/claude-3-haiku",
                    temperature=0.3
                ), timeout=10.0
            )
            return resp.choices[0].message.content
        except Exception as e:
            return "Lỗi phản hồi do hệ thống quá tải."

    async def query(self, question: str, override_context: str = None, override_sources: List[str] = None) -> Dict:
        """
        Thực thi RAG pipeline bằng API thực tế lấy câu trả lời.
        """
        # Nếu không truyền vào context thực tế, fallback dùng mock context cho V1 Baseline
        context_str = override_context if override_context else "Tài liệu ngân hàng quy định lãi suất vay mua nhà là 7.5%."
        sources = override_sources if override_sources else ["policy_handbook.pdf"]
        
        answer = await self.generate_thought(question, context_str)
        
        return {
            "answer": answer,
            "contexts": [context_str],
            "metadata": {
                "model": "claude-3-haiku",
                "tokens_used": 150,
                "sources": sources
            }
        }

if __name__ == "__main__":
    agent = MainAgent()
    async def test():
        resp = await agent.query("Làm thế nào để đổi mật khẩu?")
        print(resp)
    asyncio.run(test())
