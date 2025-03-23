from collections import defaultdict
from .base import ConsensusStrategy

class WeightedConfidenceConsensus(ConsensusStrategy):
    def combine(self, results):
        scores = defaultdict(float)
        for r in results:
            text = r['text'].strip().lower()
            confidence = r.get('confidence', 1.0)
            scores[text] += confidence
        return max(scores, key=scores.get) if scores else None