from ctf.diffstruct.AbstractDiffStruct import AbstractDiffStruct
from ctf.constants import FileType


class OVALDiffStruct(AbstractDiffStruct):
    def __init__(self, absolute_path):
        super().__init__(absolute_path)
        self.file_type = FileType.OVAL
        self.rule = None
        self.affected_rules = set()
        self.product = None
        self.profile = None

    def fill_tests(self, tests):
        if self.affected_rules:
            tests.add_rules_test(self.absolute_path, self.profile, self.product,
                                 list(self.affected_rules), "bash")