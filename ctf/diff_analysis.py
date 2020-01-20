import logging
import re
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.ProfileAnalysis import ProfileAnalysis
from ctf.AnsibleAnalysis import AnsibleAnalysis

logger = logging.getLogger("content-test-filtering.diff_analysis")


def analyse_file(file_record):
    file_analyzer = None

    if file_record["file_path"].endswith(".profile"):
        file_analyzer = ProfileAnalysis(file_record)
    elif re.match(r".+/ansible/\w+\.yml", file_record["file_path"]):
        file_analyzer = AnsibleAnalysis(file_record)
    elif re.match(r".+/bash/\w+.sh", file_record["file_path"]):
        raise NotImplementedError
    elif re.match(r".+/oval/\w+.xml", file_record["file_path"]):
        raise NotImplementedError
    else:
        return None

    return file_analyzer.analyse()
