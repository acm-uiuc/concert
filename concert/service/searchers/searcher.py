from abc import ABC, abstractmethod

class Searcher(ABC):
    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def search(self, query, part, max_results):
        pass