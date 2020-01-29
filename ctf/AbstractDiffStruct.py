from abc import ABC, abstractmethod


class AbstractDiffStruct(ABC):
    def __init__(self, file_path, file_name):
        self.file_path = file_path
        self.file_name = file_name 
        self.file_type = None
    
    @abstractmethod
    def compute_dependencies(self):
        pass
