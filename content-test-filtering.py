#!/usr/bin/python3

import logging
import sys
from ctf import cli, diff, diff_analysis

logger = logging.getLogger("content-test-filtering")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s %(asctime)s - %(message)s', "%H:%M:%S")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


if __name__ == '__main__':
    options = cli.parse_args()
    logger.info("Getting files from 'git diff'")
    list_of_files = diff.get_git_diff_files(options)
    for file_record in list_of_files:
        diff_structure = diff_analysis.analyse_file(file_record)
        print(diff_structure.diff_type)
    logger.info("Finished")
