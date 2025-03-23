from langchain.prompts import PromptTemplate
from langchain_community.llms.fake import FakeListLLM
from langchain_core.runnables import Runnable

from consensus.core import Consensus
import asyncio

# Prompt with room for peer feedback
prompt = PromptTemplate.from_template("""
Q: {question}

{peer_answers}

Respond in the following JSON format:

{{
  "answer": "...",
  "reason": "..."
}}
""")

# Simulate models with predefined responses across rounds.
# Note: The responses are now valid JSON strings.
llm1 = prompt | FakeListLLM(responses=[
    '{"answer": "Paris", "reason": "Paris is the capital."}', 
    '{"answer": "Paris", "reason": "Still confident."}'
])
llm2 = prompt | FakeListLLM(responses=[
    '{"answer": "Lyon", "reason": "Lyon is important."}', 
    '{"answer": "Paris", "reason": "Majority says Paris."}'
])
llm3 = prompt | FakeListLLM(responses=[
    '{"answer": "Marseille", "reason": "Marseille is a coastal hub."}', 
    '{"answer": "Paris", "reason": "Convinced by peers."}'
])

# Create consensus engine with feedback and multi-round support.
# rounds=None means it will loop until all models agree.
engine = Consensus(
    llms=[llm1, llm2, llm3],
    strategy="majority",
    rounds=None,
    enable_peer_feedback=True
)

async def run():
    final_answer = await engine.get_consensus("What is the capital of France?")
    print("Final consensus answer:", final_answer)
    print("\nDeliberation Report:")
    print(engine.report.to_json())

if __name__ == "__main__":
    asyncio.run(run())
