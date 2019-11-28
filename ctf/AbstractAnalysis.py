from abc import ABC, abstractmethod
from ctf.DiffStructure import DiffStructure


class AbstractAnalysis(ABC):
    def __init__(self, file_record):
        self.diff_structure = DiffStructure()
        self.filepath = file_record["filepath"]
        self.content_before = file_record["file_before"]
        self.content_after = file_record["file_after"]

    @abstractmethod
    def process_analysis(self):
        pass

    def analyse(self):
        self.process_analysis()
        return self.diff_structure
