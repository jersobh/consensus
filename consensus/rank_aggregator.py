from collections import Counter
from .base import ConsensusStrategy

class RankedConsensus(ConsensusStrategy):
    def combine(self, results):
        ranks = Counter()
        for r in results:
            for i, choice in enumerate(r.get("ranked_choices", [])):
                ranks[choice.strip().lower()] += (len(r["ranked_choices"]) - i)
        return ranks.most_common(1)[0][0] if ranks else None