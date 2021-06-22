#!/usr/bin/python3
import argparse
import requests
import json
import sys

REPO_URL = "https://api.github.com/repos/ComplianceAsCode/content/issues/"
USER = "openscap-ci"
COMMENT_STRING_1 = "Changes identified:"
COMMENT_STRING_2 = "Recommended tests to execute:"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", dest="gh_auth", required=True,
                        help=("Authorization token for comments at Github."))
    parser.add_argument("--pr", dest="pr", required=True,
                        help=("Pull Request number where to send the comment."))
    parser.add_argument("--comment", dest="comment_file", required=True,
                        help=("File with content that will be send as comment to " +
                              "the Pull Request."))
    return parser.parse_args()


if __name__ == '__main__':
    options = parse_args()
    # Prepare method's specifications
    headers = {"Authorization": "token %s" % options.gh_auth}
    data = {}
    comment_id = ""
    with open(options.comment_file) as comment:
        data["body"] = comment.read()
    if not data["body"]:  # If the comment is empty -> don't delete/send anything
        sys.exit()
    data = json.dumps(data)
    add_comment_url = REPO_URL + options.pr + "/comments"
    # Get all comments from the Pull Request
    response = requests.get(add_comment_url)
    parsed_comments = json.loads(response.content)
    # Delete comments with specific comment string
    for comment in parsed_comments:
        if comment["user"]["login"] == USER and \
            (COMMENT_STRING_1 in comment["body"] or \
                COMMENT_STRING_2 in comment["body"]):
            comment_id = str(comment["id"])

    if comment_id: # Comment already exists - update it
        comment_url = REPO_URL + "comments/" + comment_id
        response = requests.patch(comment_url, data=data, headers=headers)
    else: # Comment does not exist - create a new one
        response = requests.post(add_comment_url, data=data, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
