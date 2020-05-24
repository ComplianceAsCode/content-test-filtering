import re
import logging
from deepdiff import DeepDiff
from ctf.constants import FileType
from ctf.analysis.AbstractAnalysis import AbstractAnalysis

logger = logging.getLogger("content-test-filtering.diff_analysis")


class AnsibleAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct.file_type = FileType.YAML
        self.rule_name = re.match(r".+/((?:\w|-)+)/ansible/\w+\.yml$",
                                  self.filepath).group(1)

    @staticmethod
    def can_analyse(filepath):
        if re.match(r".+/ansible/\w+\.yml$", filepath):
            return True
        return False

    def is_templated(self, content):
        # Delete template {{{ ... }}}
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
        # Remove lines that were not changed
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
                    self.rule_name, msg="Metadata changed in ansible remediation.")
                continue
            # Not important comment
            if re.match(r"^(\+|-)\s*#.*$", line):
                continue
            self.diff_struct.add_changed_rule(
                self.rule_name, msg="Template usage changed in ansible remediation.")

    def analyse_ansible(self):
        changes = self.get_changes()
        # Check all changed lines
        for line in changes:
            if re.match(r"^(\+|-)\s*$", line):
                continue
            if re.match(r"^(\+|-)\s*#\s*(platform|reboot|strategy|complexity|disruption)\s*=\s*.*$", line):
                self.diff_struct.add_changed_product_by_rule(
                    self.rule_name, msg="Metadata changed in ansible remediation.")
                continue
            if re.match(r"^(\+|-)\s*#.*$", line):
                continue
            if re.match(r"^(\+|-)\s*-?\s*name\s*:\s*\S+.*$", line):
                continue
            self.diff_struct.add_changed_rule(
                self.rule_name, msg="Ansible remediation changed.")

    def process_analysis(self):
        logger.debug("Analyzing ansible file %s", self.filepath)
        logger.debug("Rule name: %s", self.rule_name)

        if self.is_added():
            msg = "Ansible remediation newly added."
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
            return self.diff_struct
        elif self.is_removed():
            msg = "Ansible remediation for %s was deleted." % self.rule_name
            self.diff_struct.add_rule_log(self.rule_name, msg)
            return self.diff_struct

        was_templated = self.is_templated(self.content_before)
        is_templated = self.is_templated(self.content_after)

        if was_templated and is_templated:  # Was and is templated
            self.analyse_template()
        elif any([was_templated, is_templated]):  # Templatization changed
            msg = "Templatazation usage changed."
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
        else:  # Not templated
            self.analyse_ansible()

        return self.diff_struct
