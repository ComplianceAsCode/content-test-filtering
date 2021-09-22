import re
import logging
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.analysis.BashAnalysis import BashAnalysis
from ctf.constants import FileType

logger = logging.getLogger("content-test-filtering.diff_analysis")


class TestScenarioAnalysis(BashAnalysis):
    def __init__(self, file_record):
        AbstractAnalysis.__init__(self, file_record)
        self.diff_struct.file_type = FileType.TEST_SCENARIO
        self.rule_name = re.match(r".+/([\w|-]+)/tests/[\w|-]+\.(?:fail|pass)\.sh",
                                  self.filepath).group(1)

    @staticmethod
    def can_analyse(filepath):
        if re.match(r"shared/templates/.+/tests/.*", filepath):
            return False
        if re.match(r".*/tests/[\w|-]+\.(?:pass|fail)\.sh", filepath):
            return True
        return False

    def analyse_comments(self):
        changes = self.get_changes()

        for line in changes:
            # Only important change in comments are platform/packages metadata update
            if re.match(r"^(\+|-)\s*#\s*(platform|packages)\s*=\s*.*$", line):
                msg = "Test scenario metadata changed."
                self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
                self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
                return

    def process_analysis(self):
        logger.debug("Analyzing test scenario %s", self.filepath)
        logger.debug("Test scenario for rule: %s", self.rule_name)

        if self.is_added():
            msg = "Test scenario newly added."
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
            return self.diff_struct
        elif self.is_removed():
            msg = "Test scenario %s has been removed." % self.filepath
            self.diff_struct.add_rule_log(self.rule_name, msg)
            return self.diff_struct

        self.analyse_comments()
        self.analyse_bash()

        return self.diff_struct
