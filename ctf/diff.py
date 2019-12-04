from git import Repo
from tempfile import mkdtemp
import re
import logging
import os
import inspect
import re

logger = logging.getLogger("content-test-filtering.diff")
URL = "https://github.com/ComplianceAsCode/content"


def fetch_pr(remote, pr_number):
    target_branch = "pr-" + pr_number
    remote.fetch("pull/" + pr_number + "/head:" + target_branch, force=True)
    return target_branch


def fetch_branch(remote, branch_name):
    remote.fetch(branch_name + ":" + branch_name, force=True)
    return branch_name


def get_git_diff_files(options):
    base_branch = options.base_branch
    repo_path = options.repository_path
    changed_files = []

    # Create a new temporary dictory if it does not exist
    if repo_path is not None and not os.path.isdir(repo_path):
        logger.warning("%s is not a directory! Creating a new one" % repo_path)
        repo_path = mkdtemp()
        logger.info("Clonning repository to %s directory" % repo_path)
        Repo.clone_from(URL, repo_path)

    repo = Repo(repo_path)
    repo.git.checkout(base_branch)
    repo.remotes.origin.pull()

    # Set upstream as remote
    # TODO: Add custom remote option
    for r in repo.remotes:
        if re.search(URL, r.url):
            remote = r

    logger.info("Fetching branch...")
    if options.subcommand == "pr":
        target_branch = fetch_pr(remote, options.pr_number)
    elif options.subcommand == "base_branch":
        target_branch = fetch_branch(remote, options.branch)
    else:
        raise "Unknown target"
    logger.info("Fetched to " + target_branch)

    repo.git.checkout(target_branch)

    # Get SHA-1 for both branches (base and target)
    git_log_base = repo.git.log("--format=%H", base_branch)
    git_log_target = repo.git.log("--format=%H")
    git_log_base = git_log_base.split()
    git_log_target = git_log_target.split()

    # Find first common commit from branches
    for commit_sha in git_log_target:
        if commit_sha in git_log_base:
            common_commit = commit_sha
            break

    # If common branch is HEAD of target branch, then the branch
    # has been already merged and we need to find commit to compare
    if git_log_target[0] == common_commit:
        git_log = repo.git.log(base_branch, "^" + target_branch,
                               "--ancestry-path", "--format=%P", "--reverse")
        merge_commits = git_log.partition("\n")[0]
        merge_commits = merge_commits.split(" ")
        compare_commit = repo.git.merge_base("--all", merge_commits)
    else:  # If it was not merged, then common commit can be used to diff
        compare_commit = common_commit

    git_diff = repo.git.diff("--name-status", compare_commit + "..HEAD")

    # M,A,D,Rxxx
    for git_line in git_diff.splitlines():
        file_record = dict()
        file_before = None
        file_after = None

        flag, filepath = git_line.split("\t")  # Parse flag and filepath
        if flag != 'A':  # If file wasn't added, we have previous version
            file_before = repo.git.show(compare_commit + ":./" + filepath)
        if flag != 'D':  # If file wasn't deleted, we have new version
            file_after = repo.git.show("HEAD:./" + filepath)

        file_record["flag"] = flag
        file_record["filepath"] = filepath
        file_record["file_before"] = file_before
        file_record["file_after"] = file_after
        changed_files.append(file_record)

    return changed_files
