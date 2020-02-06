from ctf.AbstractDiffStruct import AbstractDiffStruct
from ctf.constants import FileType


class ProfileDiffStruct(AbstractDiffStruct):
    def __init__(self, absolute_path):
        super().__init__(absolute_path)
        self.file_type = FileType.YAML
        self.product = None
        self.profile = None
        self.base_profile = None
        self.added_rules = set()
        self.removed_rules = set()

    def fill_tests(self, tests):
        if self.profile and self.product:
            tests.add_profile_test(self.absolute_path, self.profile, self.product)
        if self.added_rules:
            tests.add_rules_test(self.absolute_path, self.profile, self.product, self.added_rules)