import re
import logging
from deepdiff import DeepDiff
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.OVALDiff import OVALDiffStruct

logger = logging.getLogger("content-test-filtering.diff_analysis")


class OVALAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = OVALDiffStruct(self.absolute_path)

    def is_templated(self, content):
        no_templates = re.sub(r"^\s*{{{(.|\n)+?}}}\s*$", "", content, flags=re.MULTILINE)
        no_comments = re.sub(r"^\s*<\!--(.|\n)+?-->\s*$", "", no_templates, flags=re.MULTILINE)
        lines = no_comments.split("\n")
        lines = [line for line in lines if not re.match(r"\s*(\s*|#.*)$", line)]
        templated = False if lines else True
        return templated

    def load_diff(self):
        diff = DeepDiff(self.content_before, self.content_after)
        diff = diff["values_changed"]["root"]["diff"]

        return diff

    def get_unidiff_changes(self, diff):
        no_header = re.sub(r"^(\+\+\+\s*|---\s*|@@.+@@)\n", "", diff, flags=re.MULTILINE)
        changes = re.sub(r"^[^+-].*\n?", "", no_header, flags=re.MULTILINE)
        changes = re.sub(r"^\s*\n", "", changes, flags=re.MULTILINE)
        changes = [line for line in changes.split("\n") if line.strip() != ""]

        return changes


    def analyse_template(self):
        diff = self.load_diff()
        changes = self.get_unidiff_changes(diff)

        pass

    def analyse_oval(self):
        pass

    def process_analysis(self):
        logger.info("Analyzing OVAL file " + self.filepath)

        was_templated = self.is_templated(self.content_before)
        is_templated = self.is_templated(self.content_after)

        if was_templated and is_templated:
            self.analyse_template()
        elif any([was_templated, is_templated]):
            raise NotImplementedError
        else:
            self.analyse_oval()

