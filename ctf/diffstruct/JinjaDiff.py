from ctf.diffstruct.AbstractDiffStruct import AbstractDiffStruct
from ctf.constants import FileType


class JinjaDiffStruct(AbstractDiffStruct):
    def __init__(self, absolute_path):
        super().__init__(absolute_path)
        self.file_type = FileType.JINJA
        self.affected_files_diffs = []

    def fill_tests(self, tests):
        pass