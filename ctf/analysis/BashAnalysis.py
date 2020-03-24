import re
import logging
import shlex
from deepdiff import DeepDiff
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.diffstruct.BashDiff import BashDiffStruct

logger = logging.getLogger("content-test-filtering.diff_analysis")


class BashAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = BashDiffStruct(self.filepath)
        rule_name_match = re.match(r".+/((?:\w|_|-)+)/bash/((?:\w|_|-)+)\.sh$",
                                   self.filepath)
        if rule_name_match.group(2) == "shared":
            self.rule_name = rule_name_match.group(1)
        else:
            self.rule_name = rule_name_match.group(2)

    @staticmethod
    def is_valid(filepath):
        if re.match(r".*/bash/\w+\.sh$", filepath):
            return True
        return False

    def is_templated(self, content):
        no_templates = re.sub(r"^\s*{{{(.|\n)+?}}}\s*$", "", content,
                              flags=re.MULTILINE)
        lines = no_templates.split("\n")
        # Delete empty and commented lines
        lines = [line for line in lines if not re.match(r"^\s*(\s*|#.*)$", line)]
        # If no lines left - only important code was template -> templated
        templated = not lines
        return templated

    def load_diff(self):
        diff = DeepDiff(self.content_before, self.content_after)
        diff = diff["values_changed"]["root"]["diff"]
        return diff

    def get_unidiff_changes(self, diff):
        # Remove unified diff header
        no_header = re.sub(r"^(\+\+\+\s*|---\s*|@@.+@@)\n", "", diff,
                           flags=re.MULTILINE)
        # Remove lines that we not changed
        changes = re.sub(r"^[^+-].*\n?", "", no_header, flags=re.MULTILINE)
        changes = re.sub(r"^\s*\n", "", changes, flags=re.MULTILINE)
        changes = [line for line in changes.split("\n") if line.strip() != ""]
        return changes

    def get_changes(self):
        diff = self.load_diff()
        changes = self.get_unidiff_changes(diff)
        return changes

    def analyse_template(self):
        changes = self.get_changes()

        # Check all changed lines
        for line in changes:
            # Added/removed empty line
            if re.match(r"^(\+|-)\s*$", line):
                continue
            # Important comment
            if re.match(r"^(\+|-)\s*#\s*(platform|reboot|strategy|complexity|disruption)\s*=\s*.*$", line):
                self.add_product_test(self.rule_name)
                continue
            # Not important comment
            if re.match(r"^(\+|-)\s*#.*$", line):
                continue
            self.add_rule_test(self.rule_name)

    def analyse_bash(self):
        tokens_before = shlex.shlex(self.content_before)
        tokens_after = shlex.shlex(self.content_after)

        # Read tokens from old and new bash file
        token_before = tokens_before.get_token()
        token_after = tokens_after.get_token()
        while token_before and token_after:
            if token_before != token_after:  # Something has changed
                break
            token_before = tokens_before.get_token()
            token_after = tokens_after.get_token()
        # If they are different
        if token_before != token_after:
            self.add_product_test(self.rule_name)
            self.add_rule_test(self.rule_name)

    def process_analysis(self):
        logger.info("Analyzing bash file %s", self.filepath)

        if self.is_added():
            self.add_product_test(self.rule_name)
            self.add_rule_test(self.rule_name)
        elif self.is_removed():
            return

        was_templated = self.is_templated(self.content_before)
        is_templated = self.is_templated(self.content_after)

        if was_templated and is_templated:  # Was and is tempalted
            self.analyse_template()
        elif any([was_templated, is_templated]):  # Templatization changed
            self.add_product_test(self.rule_name)
            self.add_rule_test(self.rule_name)
        else:  # Not templated
            self.analyse_bash()
