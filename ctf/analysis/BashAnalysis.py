import re
import logging
import shlex
from deepdiff import DeepDiff
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.constants import FileType

logger = logging.getLogger("content-test-filtering.diff_analysis")


class BashAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct.file_type = FileType.BASH
        rule_name_match = re.match(r".+/((?:\w|-)+)/bash/((?:\w|-)+)\.sh$",
                                   self.filepath)
        if rule_name_match.group(1) == "fixes":
            self.rule_name = rule_name_match.group(2)
        else:
            self.rule_name = rule_name_match.group(1)

    @staticmethod
    def can_analyse(filepath):
        if re.match(r"^(?!shared/).*/bash/\w+\.sh$", filepath):
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
        if not diff:  # Nothing changed (just moved without changes)
            return ""
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
                self.diff_struct.add_changed_product_by_rule(
                    self.rule_name, msg="Metadata changed in bash remediation.")
                continue
            # Not important comment
            if re.match(r"^(\+|-)\s*#.*$", line):
                continue
            self.diff_struct.add_changed_rule(
                self.rule_name, msg="Template usage changed in ansible remediation.")

    def analyse_bash(self):
        tokens_before = shlex.shlex(self.content_before, posix=True)
        tokens_after = shlex.shlex(self.content_after, posix=True)

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
            msg = "Found change in bash remediation."
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)

    def process_analysis(self):
        logger.debug("Analyzing bash file %s", self.filepath)
        logger.debug("Rule name: %s", self.rule_name)

        if self.is_added():
            msg = "Bash remediation is newly added."
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
            return self.diff_struct
        elif self.is_removed():
            msg = "Bash remediation was deleted. No test for it will be selected."
            self.diff_struct.add_rule_log(self.rule_name, msg)
            return self.diff_struct

        was_templated = self.is_templated(self.content_before)
        is_templated = self.is_templated(self.content_after)

        if was_templated and is_templated:  # Was and is tempalted
            self.analyse_template()
        elif any([was_templated, is_templated]):  # Templatization changed
            msg = "Templatization usage changed."
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
        else:  # Not templated
            self.analyse_bash()

        return self.diff_struct
