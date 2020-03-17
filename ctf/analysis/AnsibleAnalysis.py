import re
import logging
import yaml
from deepdiff import DeepDiff
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.diffstruct.AnsibleDiff import AnsibleDiffStruct

logger = logging.getLogger("content_test_filtering.diff_analysis")


class AnsibleAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = AnsibleDiffStruct(self.filepath)
        self.rule_name = re.match(r".+/(\w+)/ansible/\w+\.yml$", self.filepath).group(1)


    @staticmethod
    def is_valid(filepath):
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
        templated = False if lines else True
        return templated


    def load_diff(self):
        diff = DeepDiff(self.content_before, self.content_after)
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
                self.add_product_test(self.rule_name)
                continue
            # Not important comment
            if re.match(r"^(\+|-)\s*#.*$", line):
                continue
            self.add_rule_test(self.rule_name)


    def analyse_ansible(self):
        changes = self.get_changes()
        # Check all changed lines
        for line in changes:
            if re.match(r"^(\+|-)\s*$", line):
                continue
            if re.match(r"^(\+|-)\s*#\s*(platform|reboot|strategy|complexity|disruption)\s*=\s*.*$", line):
                self.add_product_test(self.rule_name)
                continue
            if re.match(r"^(\+|-)\s*#.*$", line):
                continue
            if re.match(r"^(\+|-)\s*-?\s*name\s*:\s*\S+.*$", line):
                continue
            self.add_rule_test(self.rule_name)
            

    def process_analysis(self):
        logger.info("Analyzing ansible file " + self.filepath)

        if self.is_added():
            self.add_product_test(self.rule_name)
            self.add_rule_test(self.rule_name)
            return
        elif self.is_removed():
            return

        was_templated = self.is_templated(self.content_before)
        is_templated = self.is_templated(self.content_after)

        if was_templated and is_templated: # Was and is templated
            self.analyse_template()
        elif any([was_templated, is_templated]): # Templatization changed
            self.add_product_test(self.rule_name)
            self.add_rule_test(self.rule_name)
        else: # Not templated
            self.analyse_ansible()
