from DiffStructure-tmp import AbstractDiffStruct
from constants import FileType


class ProfileDiffStruct(AbstractDiffStruct):
    def __init__(self, file):
        super().__init__()
        self.file_type = FileType.YAML

    def compute_dependencies(self):
        pass