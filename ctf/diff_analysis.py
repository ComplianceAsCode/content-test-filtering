import logging
import re
from .AbstractAnalysis import AbstractAnalysis
from .ProfileAnalysis import ProfileAnalysis

logger = logging.getLogger("content-test-filtering.diff_analysis")


def analyse_file(file_record):
    file_analyzer = None
    print("+" + file_record[1] + "+")

    if file_record[1].endswith(".profile"):
        file_analyzer = ProfileAnalysis(file_record)

    return file_analyzer.analyse()
