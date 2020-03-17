from ctf.diffstruct.AbstractDiffStruct import AbstractDiffStruct
from ctf.constants import FileType


class OVALDiffStruct(AbstractDiffStruct):
    def __init__(self, absolute_path):
        super().__init__(absolute_path)
        self.file_type = FileType.OVAL
        self.rule = None
        self.product = None
        self.profile = None
