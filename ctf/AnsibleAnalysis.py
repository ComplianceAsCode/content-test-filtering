import re
import logging
import yaml
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.DiffStructure_old import AnsibleDiffStruct

logger = logging.getLogger("content-test-filtering.diff_analysis")


class AnsibleAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_structure = AnsibleDiffStruct()
        self.calculate_properties()

    def calculate_properties(self):
        rule_id = re.search(r".+/(.+)/ansible/.+\.yml", self.filepath)
        print(rule_id.group(1))
        self.diff_structure.rule = rule_id.group(1)

    def process_analysis(self):
        logger.info("Analyzing ansible file " + self.filepath)
