from abc import ABC, abstractmethod
from ctf.diff import git_wrapper
from ctf.constants import FileType


class AbstractDiffStruct(ABC):
    def __init__(self, filepath):
        self.absolute_path = git_wrapper.repo_path + "/" + filepath
        self.file_type = FileType.NONE
        self.product = None
        self.rule = None
        self.sanity = False
        self.other_affected_rules = []
        self.affected_files = []
