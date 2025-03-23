from abc import ABC, abstractmethod

class ConsensusStrategy(ABC):
    @abstractmethod
    def combine(self, results):
        pass