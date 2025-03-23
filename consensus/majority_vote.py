from collections import Counter
from .base import ConsensusStrategy

class MajorityVoteConsensus(ConsensusStrategy):
    def combine(self, results):
        answers = [r['text'].strip().lower() for r in results]
        most_common = Counter(answers).most_common(1)
        return most_common[0][0] if most_common else None