import sys
import os
from dotenv import load_dotenv
import asyncio
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.output_parsers.json import SimpleJsonOutputParser, JsonOutputParser
from consensus.core import Consensus
from consensus.types import ModelResponse

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
grok_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

for key, name in [(gemini_api_key, "GEMINI_API_KEY"), (grok_api_key, "GROQ_API_KEY"), (openai_api_key, "OPENAI_API_KEY")]:
    if not key:
        print(f"{name} is not set. Exiting.")
        sys.exit(1)

# Prompt template with escaped curly braces for literal JSON
prompt = PromptTemplate.from_template("""
Q: {question}

{peer_answers}

Respond in the following JSON format:

{{
  "answer": "...",
  "reason": "..."
}}
""")

# Chain each model with the prompt and a JSON output parser
llm1 = prompt | ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", api_key=SecretStr(gemini_api_key)) | JsonOutputParser(pydantic_object=ModelResponse)
llm2 = prompt | ChatGroq(model="llama-3.1-8b-instant", api_key=SecretStr(grok_api_key)) | JsonOutputParser(pydantic_object=ModelResponse)
llm3 = prompt | ChatOpenAI(model="gpt-4o", api_key=SecretStr(openai_api_key)) | JsonOutputParser(pydantic_object=ModelResponse)

# Create consensus engine with multi-round support and peer feedback enabled
engine = Consensus(
    llms=[llm1, llm2, llm3],
    strategy="majority",
    rounds=10, # Max number of rounds
    enable_peer_feedback=True # peers can see other peers answers
)

async def run():
    question = """
A single-phase lighting circuit has an installed power of 1,100 VA and runs inside a PVC conduit embedded in a masonry wall. 
Alongside it, insulated conductors from another circuit are present. The conductors are copper, the ambient temperature is 35°C, and the voltage is 220 V. Determine the conductor's cross-sectional area and the circuit breaker's nominal current for this circuit.
"""
    final_answer = await engine.get_consensus(question)
    print("Final consensus answer:")
    print(final_answer)
    print("\nDeliberation Report:")
    print(engine.report.to_json())

if __name__ == "__main__":
    asyncio.run(run())
