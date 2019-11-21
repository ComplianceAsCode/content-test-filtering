import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    common_parser = argparse.ArgumentParser(add_help=False)

    common_parser.add_argument("--base", dest="base_branch", default="master",
                               help=("Base branch against which we want to "
                                     "compare, default is \"master\" branch"))
    common_parser.add_argument("--repository", dest="repository_path",
                               help=("Path to ComplianceAsCode repository. "
                                      "If not provided, the repository will be"
                                      "cloned into /tmp folder."))

    subparsers = parser.add_subparsers(dest="subcommand",
                                       help="Subcommands: pr, branch")
    subparsers.required = True

    parser_pr = subparsers.add_parser("pr", parents=[common_parser],
                                      help=("Compare base against selected "
                                            "pull request"))
    parser_pr.add_argument("target", metavar="PR_NUMBER",
                           help=("Pull request number, which we want compare "
                                 "against base"))
    #parser_pr.set_defaults(func...)
    parser_branch = subparsers.add_parser("branch", parents=[common_parser],
                                          help=("Compare base against "
                                                "selected branch"))
    parser_branch.add_argument("target", metavar="BRANCH_NAME",
                           help=("Branch, which we want compare "
                                 "against base"))

    options = parser.parse_args()

    return options
