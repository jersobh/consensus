import asyncio
import json
import ast
from typing import List, Optional
from langchain_core.runnables import Runnable
from .majority_vote import MajorityVoteConsensus
from .weighted_vote import WeightedConfidenceConsensus
from .rank_aggregator import RankedConsensus
from .types import RoundResult, ModelResponse
from .logger import ConsensusReport

class Consensus:
    def __init__(
        self,
        llms: List[Runnable],
        strategy: str = "majority",
        rounds: Optional[int] = None,
        enable_peer_feedback: bool = False
    ):
        self.llms = llms
        self.strategy_name = strategy
        self.rounds = rounds
        self.enable_peer_feedback = enable_peer_feedback
        self.report = ConsensusReport()

        if strategy == "majority":
            self.strategy = MajorityVoteConsensus()
        elif strategy == "weighted":
            self.strategy = WeightedConfidenceConsensus()
        elif strategy == "ranked":
            self.strategy = RankedConsensus()
        else:
            raise ValueError("Unsupported consensus strategy")

    async def _call_model(self, llm: Runnable, question: str, peer_context: Optional[str] = None, round_num: int = 1) -> ModelResponse:
        prompt_vars = {
            "question": question,
            "peer_answers": peer_context or ""
        }
        try:
            response = await llm.ainvoke(prompt_vars)
            content = response.content if hasattr(response, "content") else str(response)

            # First, try standard JSON parsing
            try:
                data = json.loads(content)
            except Exception as json_error:
                # Fallback: use ast.literal_eval to handle Python-style dicts (with single quotes)
                try:
                    data = ast.literal_eval(content)
                    # Re-dump to a JSON string and parse it to ensure proper format
                    data = json.loads(json.dumps(data))
                except Exception as ast_error:
                    return ModelResponse(answer="ERROR", reason=f"Invalid JSON: {json_error} | Raw: {content[:200]}")
            # Ensure that the 'answer' field is a string
            ans = data.get("answer")
            if not isinstance(ans, str):
                ans = json.dumps(ans)
            reason = data.get("reason", "")
            return ModelResponse(answer=ans.strip(), reason=str(reason).strip())
        except Exception as e:
            return ModelResponse(answer="ERROR", reason=f"Exception: {str(e)}")

    async def get_consensus(self, question: str):
        history = []
        current_answers = [None] * len(self.llms)
        round_index = 0

        while True:
            round_index += 1
            peer_contexts = []
            for i in range(len(self.llms)):
                peer_lines = [
                    f"- Peer {j+1}: {resp.answer}"
                    for j, resp in enumerate(current_answers) if j != i and resp is not None
                ]
                peer_contexts.append("\n".join(peer_lines) if peer_lines else "")
            tasks = [
                self._call_model(self.llms[i], question, peer_contexts[i], round_index)
                for i in range(len(self.llms))
            ]
            current_answers = await asyncio.gather(*tasks)
            result = RoundResult(round_number=round_index, responses=current_answers)
            history.append(result)
            self.report.log_round(result)
            all_agree = all(r.answer == current_answers[0].answer for r in current_answers)
            if self.rounds:
                if round_index >= self.rounds:
                    break
            elif all_agree:
                break
        return self.strategy.combine([{"text": r.answer} for r in current_answers])
