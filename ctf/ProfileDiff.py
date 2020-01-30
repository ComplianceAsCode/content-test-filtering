from ctf.AbstractDiffStruct import AbstractDiffStruct
from ctf.constants import FileType


class ProfileDiffStruct(AbstractDiffStruct):
    def __init__(self, file_path, file_name):
        super().__init__(file_path, file_name)
        self.file_type = FileType.YAML
        self.product = None
        self.profile = None
        self.base_profile = None
        self.added_rules = []
        self.removed_rules = []

    def compute_dependencies(self):
        pass

    def fill_tests(self, tests):
        tests[self.product] = self.profile
        pass
