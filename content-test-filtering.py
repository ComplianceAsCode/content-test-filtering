#!/usr/bin/python3
import logging
import sys
from ctf import cli, diff, diff_analysis, connect_to_labels, ContentTests

logger = logging.getLogger("content-test-filtering")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s %(asctime)s - %(message)s',
                                      "%H:%M:%S")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


if __name__ == '__main__':
    options = cli.parse_args()
    list_of_tests = []
    tests = ContentTests.ContentTests()

    logger.info("Getting files from 'git diff'")
    changed_files = diff.get_git_diff_files(options)

    # Analyze each file separately and make set of tests for each one
    for file_record in changed_files:
        diff_structure = diff_analysis.analyse_file(file_record)
        diff_structure.fill_tests(tests)

    list_of_tests = connect_to_labels.get_labels(tests)
    
    logger.info(list_of_tests)
    logger.info("Finished")