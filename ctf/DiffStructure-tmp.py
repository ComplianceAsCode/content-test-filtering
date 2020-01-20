from abc import ABC, abstractmethod


class AbstractDiffStruct(ABC):
    def __init__(self):
        self.file_path = None
        self.file_name = None
        self.rules = {}
        self.products = {}
        self.file_type = None
    
    @abstractmethod
    def compute_dependencies(self):
        pass
