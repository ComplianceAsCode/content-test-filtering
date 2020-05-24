#!/usr/bin/python3
import argparse
import requests
import json
import os
import inspect
import subprocess

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENT_DIR = os.path.dirname(current_dir)

BUILD_TIME = 94
RULE_TIME = 315
PROFILE_TIME = 678
CTEST_TIME = 1881
ALL_TESTS_COMPLETE_TIME = CTEST_TIME + 132 * PROFILE_TIME + 248 * RULE_TIME
ALL_TESTS_SELECTION_TIME = CTEST_TIME + 25 * PROFILE_TIME + 94 * RULE_TIME


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", dest="repo", required=True,
                        help=("Path to CaC repository."))
    return parser.parse_args()


def running_filtering_case(repo_path, pr_number):
    result = subprocess.run("python3 content_test_filtering.py pr --verbose " +
                            "--repository " + repo_path + " " + pr_number, shell=True,
                            cwd=PARENT_DIR, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("Pull Request %s filtering failed." % pr_number)
        print(result.stdout)
        print(result.stderr)
        return 0
    output = result.stdout.decode("utf-8")
    # print(output)
    analysed_count = output.count("Analyzing ")
    rule_test_count = output.count("test_suite.py rule")
    profile_test_count = output.count("test_suite.py profile")
    ctest_test_count = output.count("ctest -j4")
    build_count = output.count("build_product")

    build_time = BUILD_TIME * build_count
    # print("build: %s" % build_time)
    rule_test_time = RULE_TIME * rule_test_count
    # print("rules: %s" % rule_test_time)
    profile_test_time = PROFILE_TIME * profile_test_count
    # print("profile: %s" % profile_test_time)
    ctest_test_time = CTEST_TIME * ctest_test_count
    # print("ctest: %s" % ctest_test_time)
    total_time = build_time + rule_test_time + profile_test_time + ctest_test_time
    # When it couldn't analyse any file from the PR
    if total_time == 0 and analysed_count == 0:
        return -1
    return total_time


if __name__ == '__main__':
    options = parse_args()
    list_of_pr = []
    for i in range(1, 6):
        params = {"state": "closed", "per_page": "100", "page": i}
        response = requests.get(
            "https://api.github.com/repos/ComplianceAsCode/content/pulls",
            params=params
        )
        parsed_response = json.loads(response.content)
        for pr in parsed_response:
            if pr["number"] in list_of_pr:
                continue
            list_of_pr.append(str(pr["number"]))

    time_filtering_complete = 0
    time_all_complete = 0
    time_specific_complete = 0
    for i, pr in enumerate(list_of_pr):
        print("%s - PR %s" % (i, pr))
        time_filtering = running_filtering_case(options.repo, pr)
        print(time_filtering)
        if time_filtering == -1:
            time_filtering = ALL_TESTS_SELECTION_TIME
        time_all = ALL_TESTS_COMPLETE_TIME
        time_specific = ALL_TESTS_SELECTION_TIME

        time_filtering_complete = time_filtering_complete + time_filtering
        time_all_complete = time_all_complete + time_all
        time_specific_complete = time_specific_complete + time_specific

    print("Filtering   complete: %ss" % time_filtering_complete)
    filtering_average = int(time_filtering_complete) / 500
    print("Filtering    average: %ss" % filtering_average)
    print("All         complete: %ss" % time_all_complete)
    all_average = int(time_all_complete) / 500
    print("All          average: %ss" % all_average)
    print("Selection   complete: %ss" % time_specific_complete)
    selection_average = int(time_specific_complete) / 500
    print("Selection    average: %ss" % selection_average)
