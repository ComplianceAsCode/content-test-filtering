from abc import ABC, abstractmethod
from ctf.diff import git_wrapper


class AbstractDiffStruct(ABC):
    def __init__(self, filepath):
        self.absolute_path = git_wrapper.repo_path + "/" + filepath
        self.file_type = None
    
    @abstractmethod
    def fill_tests(self, tests):
        pass
