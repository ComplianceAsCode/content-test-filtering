import logging
import re
from .AbstractAnalysis import AbstractAnalysis
from .ProfileAnalysis import ProfileAnalysis
from .AnsibleAnalysis import AnsibleAnalysis

logger = logging.getLogger("content-test-filtering.diff_analysis")


def analyse_file(options, file_record):
    file_analyzer = None
    print("+" + file_record["filepath"] + "+")

    if file_record["filepath"].endswith(".profile"):
        file_analyzer = ProfileAnalysis(options, file_record)
    elif re.match(r".+/ansible/.+\.yml",file_record["filepath"]):
        file_analyzer = AnsibleAnalysis(options, file_record)
    else:
        return

    return file_analyzer.analyse()
