#!/usr/bin/python3
import logging
import sys
from ctf import cli, diff_analysis, connect_to_labels, ContentTests
from ctf.diff import git_wrapper
import deepdiff

logger = logging.getLogger("content-test-filtering")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(levelname)s %(asctime)s - %(message)s",
                                      "%H:%M:%S")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)



if __name__ == '__main__':
    options = cli.parse_args()
    list_of_tests = []
    tests = ContentTests.ContentTests()

    logger.info("Getting files from 'git diff'")
    git_wrapper.git_init(options.repository_path, local=options.local)
    changed_files = git_wrapper.git_diff_files(options.base_branch,
                                               new_branch=options.branch,
                                               pr_number=options.pr_number)

    # Analyze each file separately and make set of tests for each one
    for file_record in changed_files:
        try:
            diff_structure = diff_analysis.analyse_file(file_record)
            diff_structure.fill_tests(tests)
        except diff_analysis.UnknownAnalysisFileType:
            logger.warning("Unknown type of file %s. Analysis has not been "
                           "performed for it." % file_record["filepath"])
            continue

    list_of_tests = connect_to_labels.get_labels(tests)

    logger.info(list_of_tests)
    logger.info("Finished")