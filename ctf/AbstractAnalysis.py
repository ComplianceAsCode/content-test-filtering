from abc import ABC, abstractmethod
from ctf.DiffStructure import DiffStructure


class AbstractAnalysis(ABC):
    def __init__(self, file_record):
        self.file_name = file_record[1]
        self.content_before = file_record[2]
        self.content_after = file_record[3]
        self.diff_structure = DiffStructure(self.file_name)

    @abstractmethod
    def process_analysis(self):
        pass

    def analyse(self):
        self.process_analysis()
        return self.diff_structure
