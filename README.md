# Consensus

**Consensus** is a Langchain-compatible framework that enables deliberative decision-making among multiple LLMs (Large Language Models). It supports parallel execution, multiple rounds of reasoning, peer feedback, and customizable strategies like majority vote, weighted confidence, and ranked choice.

---

## ✨ Features

- 🔄 Combine multiple LLMs' answers for a final consensus  
- ⚙️ Strategies: `majority`, `weighted`, `ranked`  
- 🔁 Multi-round deliberation (automatic or fixed rounds)  
- 🗣 Peer feedback: each model can see what others answered  
- 🧠 Uses `Runnable` chains (`prompt | llm`) – fully compatible with Langchain 0.2+  
- 🧾 JSON export of all responses, rounds, and reasoning  

---

## 🚀 Installation

```bash
pip install git+https://github.com/jersobh/consensus.git
```

Or if installing from a local clone:

```bash
Copiar
Editar
git clone https://github.com/jersobh/consensus.git
cd consensus
pip install -e .
```

## 🧪 Example 

```python
from langchain.prompts import PromptTemplate
from langchain_community.llms.fake import FakeListLLM
from consensus.core import Consensus
import asyncio

prompt = PromptTemplate.from_template(\"\"\"
Q: {question}

{peer_answers}

Please answer as fully and clearly as possible.
\"\"\")

llm1 = prompt | FakeListLLM(responses=["Answer A."])
llm2 = prompt | FakeListLLM(responses=["Answer B."])
llm3 = prompt | FakeListLLM(responses=["Answer A."])

engine = Consensus(
    llms=[llm1, llm2, llm3],
    strategy="majority",
    rounds=None,  # Runs until agreement
    enable_peer_feedback=True
)

async def run():
    result = await engine.get_consensus("What is the capital of France?")
    print("Final consensus answer:", result)
    print("\\nDeliberation Report:")
    print(engine.report.to_json())

if __name__ == "__main__":
    asyncio.run(run())

```


## 📊 Strategies
|Strategy|Description|
|---|---|
|majority  |	Picks the most frequent final answer|
|weighted  |	Uses confidence scores (if provided)|
|ranked    |    Aggregates ranked preferences|

Made with ❤️ by Jeff Andrade (jersobh)