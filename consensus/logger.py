import json
from .types import RoundResult

class ConsensusReport:
    def __init__(self):
        self.rounds = []

    def log_round(self, result: RoundResult):
        self.rounds.append({
            "round": result.round_number,
            "responses": [
                {"answer": r.answer, "reason": r.reason} for r in result.responses
            ]
        })

    def to_json(self):
        return json.dumps({"rounds": self.rounds}, indent=2)

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.to_json())