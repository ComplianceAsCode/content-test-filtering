import logging
import re
from abc import ABC, abstractmethod

logger = logging.getLogger("content-test-filtering.diff_analysis")

class AbstractAnalysis(ABC):
    @abstractmethod
    def analyse(self):
        pass


class ProfileAnalysis(AbstractAnalysis):
    def analyse(self):
        logger.info("Analyzing profile file")



def analyse_file(file_record):
    file_analyzer = None
    print("+" + file_record[1] + "+")

    if file_record[1].endswith(".profile"):
        file_analyzer = ProfileAnalysis()

    file_analyzer.analyse()
