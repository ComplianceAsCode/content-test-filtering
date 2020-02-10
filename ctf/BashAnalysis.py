import logging
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.BashDiff import BashDiffStruct

logger = logging.getLogger("content-test-filtering.diff_analysis")


class BashAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = BashDiffStruct(self.absolute_path)

    def process_analysis(self):
        logger.info("Analyzing bash file " + self.filepath)
