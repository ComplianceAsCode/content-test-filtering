import logging
import re
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.ProfileAnalysis import ProfileAnalysis
from ctf.AnsibleAnalysis import AnsibleAnalysis
from ctf.BashAnalysis import BashAnalysis
from ctf.PythonAnalysis import PythonAnalysis
from ctf.OVALAnalysis import OVALAnalysis
#from ctf.JinjaAnalysis import JinjaAnalysis

logger = logging.getLogger("content-test-filtering.diff_analysis")


def analyse_file(file_record):
    file_analyzer = None

    # Profile file
    if file_record["file_path"].endswith(".profile"):
        file_analyzer = ProfileAnalysis(file_record)
    # Ansible remediation
    elif re.match(r".+/ansible/\w+\.yml$", file_record["file_path"]):
        file_analyzer = AnsibleAnalysis(file_record)
    # Bash remediation
    elif re.match(r".+/bash/\w+\.sh$", file_record["file_path"]):
        file_analyzer = BashAnalysis(file_record)
    # XML (OVAL language)
    elif re.match(r".+/oval/\w+\.xml$", file_record["file_path"]):
        file_analyzer = OVALAnalysis(file_record)
    # Python
    elif re.match(r".+\.py$", file_record["file_path"]):
        file_analyzer = PythonAnalysis(file_record)
    # Jinja macro
    elif file_record["file_path"].endswith(".jinja"):
        # Import Jinja analysis only when needed (prevent cyclic dependencies)
        from ctf.JinjaAnalysis import JinjaAnalysis
        file_analyzer = JinjaAnalysis(file_record)
    else:
        return None

    return file_analyzer.analyse()
