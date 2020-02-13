from ctf.AbstractDiffStruct import AbstractDiffStruct
from ctf.constants import FileType


class BashDiffStruct(AbstractDiffStruct):
    def __init__(self, absolute_path):
        super().__init__(absolute_path)
        self.file_type = FileType.BASH
        self.rule = None
        self.product = None
        self.profile = None

    def fill_tests(self, tests):
        if self.product:
            tests.add_product_build(self.absolute_path, self.product)
        if self.rule:
            tests.add_rules_test(self.absolute_path, self.profile,
                                 self.product, [self.rule], "bash")