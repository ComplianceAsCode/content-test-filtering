from abc import ABC, abstractmethod


class AbstractDiffStruct(ABC):
    def __init__(self, absolute_path):
        self.absolute_path = absolute_path
        self.file_type = None
    
    @abstractmethod
    def fill_tests(self, tests):
        pass
