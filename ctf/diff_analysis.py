import logging
import re
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.ProfileAnalysis import ProfileAnalysis
from ctf.AnsibleAnalysis import AnsibleAnalysis

logger = logging.getLogger("content-test-filtering.diff_analysis")


def analyse_file(file_record):
    file_analyzer = None

    if file_record["filepath"].endswith(".profile"):
        file_analyzer = ProfileAnalysis(file_record)
    elif re.match(r".+/ansible/\w+\.yml", file_record["filepath"]):
        file_analyzer = AnsibleAnalysis(file_record)
    else:
        return None

    return file_analyzer.analyse()
