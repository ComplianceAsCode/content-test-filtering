import re
import logging
from deepdiff.diff import DeepDiff
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.constants import FileType

logger = logging.getLogger("content-test-filtering.diff_analysis")


class RuleYmlAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct.file_type = FileType.RULEYML
        self.rule_name = re.match(r".+/([\w|-]+)/rule.yml$",
                                  self.filepath).group(1)

    @staticmethod
    def can_analyse(filepath):
        if re.match("^(?!shared/).+/rule.yml$", filepath):
            return True
        return False

    def process_analysis(self):
        logger.debug("Analyzing rule.yml file %s", self.filepath)
        logger.debug("Rule name: %s", self.rule_name)

        if self.is_added():
            msg = "Rule %s added." % self.rule_name
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
            return self.diff_struct
        elif self.is_removed():
            msg = "Rule %s was deleted" % self.rule_name
            self.diff_struct.add_rule_log(self.rule_name, msg)
            return self.diff_struct

        before_start = re.search(r"^\s*template:", self.content_before, re.MULTILINE)
        after_start = re.search(r"^\s*template:", self.content_after, re.MULTILINE)
        # No template section found, no tests selected
        if type(before_start) is type(after_start) and before_start is None:
            return self.diff_struct
        # Template section either added or removed
        elif before_start is None or after_start is None:
            msg = "Template section has been removed/added in %s" % self.rule_name
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
            return self.diff_struct
        # Both sections with template section, do diff
        content_before = self.content_before[before_start.start():]
        content_after = self.content_after[after_start.start():]
        diff = DeepDiff(content_before, content_after)

        if diff:
            msg = "Template section has been changed in %s" % self.rule_name
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)

        return self.diff_struct
