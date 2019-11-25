import logging
import yaml
from deepdiff import DeepDiff
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.DiffStructure import DiffFileType

logger = logging.getLogger("content-test-filtering.diff_analysis")


class ProfileAnalysis(AbstractAnalysis):
    def process_analysis(self):
        logger.info("Analyzing profile file " + self.file_name)
        self.diff_structure.diff_type = DiffFileType.PROFILE
        data_map_before = yaml.load(self.content_before)
        data_map_after = yaml.load(self.content_after)
        deep_diff = DeepDiff(data_map_before, data_map_after, ignore_order=True)
        for key, value in deep_diff['iterable_item_removed'].items():
            if "'selections'" in key:
                self.diff_structure.rules_removed.append(value)
