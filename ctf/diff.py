import os
import re
import subprocess
import logging
from git import Repo, remote
from tempfile import mkdtemp

logger = logging.getLogger("content-test-filtering.diff")
URL = "https://github.com/ComplianceAsCode/content"



def fetch_pr(remote_repository, pr_number):
    target_branch = "pr-" + pr_number
    # Fetch every time, even we have the branch localy
    remote_repository.fetch("pull/" + pr_number + "/head:" + target_branch,
                            force=True)
    return target_branch


def fetch_branch(remote, branch_name, local_branch=False):
    # If we don't specify explicitly that we want local branch, then fetch
    if not local_branch:
        remote.fetch(branch_name + ":" + branch_name, force=True)
    return branch_name


def get_git_diff_files(options):
    base_branch = options.base_branch
    repo_path = os.path.abspath(options.repository_path)
    changed_files = []

    # Create a new temporary dictory if it input directory is not a directory
    if repo_path is not None and not os.path.isdir(repo_path):
        logger.warning("%s is not a directory!"
                       " Creating a new folder " % repo_path)
        repo_path = None

    # Create a new directory if no valid directory was provided
    if repo_path is None:
        repo_path = mkdtemp()
        logger.info("Clonning repository to %s directory" % repo_path)
        Repo.clone_from(URL, repo_path)

    repo = Repo(repo_path)
    repo.git.checkout(base_branch)

    # For testing local branch (testing purposes) do not pull
    if not options.local_branch:
        repo.remotes.origin.pull()

    # Set upstream as remote
    # TODO: Add custom remote option
    for remote in repo.remotes:
        if re.search(URL, remote.url):
            remote_repository = remote
            break

    logger.info("Fetching branch...")
    if options.subcommand == "pr":
        target_branch = fetch_pr(remote_repository, options.pr_number)
    elif options.subcommand == "base_branch":
        target_branch = fetch_branch(remote_repository, options.branch,
                                     options.local_branch)
    else:
        raise "Unknown target"
    logger.info("Fetched to " + target_branch + " branch")

    # Create folders for building templated content
    try:
        os.mkdir(repo_path + "/build_old")
    except FileExistsError:
        pass

    try:
        os.mkdir(repo_path + "/build_new")
    except FileExistsError:
        pass

    # Build templated content with old code
    subprocess.run("cmake ../ && make generate-internal-templated-content-rhel8"
                   " generate-internal-templated-content-rhel7", shell=True,
                   cwd=repo_path+"/build_old")
    repo.git.checkout(target_branch)
    # Build templated content with new code
    subprocess.run("cmake ../ && make generate-internal-templated-content-rhel8"
                   " generate-internal-templated-content-rhel7", shell=True,
                   cwd=repo_path+"/build_new")

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
        # Show comints on the ancestry chain
        git_log = repo.git.log(base_branch, "^" + target_branch,
                               "--ancestry-path", "--format=%P", "--reverse")
        merge_commits = git_log.partition("\n")[0]
        merge_commits = merge_commits.split(" ")
        # Get commit against we need to compare
        compare_commit = repo.git.merge_base("--all", merge_commits)
    else:  # If the branch was not merged, then common commit can be used to diff
        compare_commit = common_commit

    git_diff = repo.git.diff("--name-status", compare_commit + "..HEAD")

    # Parse line by line from changed files
    for git_line in git_diff.splitlines():
        file_record = dict()
        file_before = None
        file_after = None

        # Flags: M (modified), A (added), D (deleted), Rxxx (renamed)
        flag, file_path = git_line.split("\t")  # Parse flag and filepath
        if flag != 'A':  # If file wasn't added, we have previous version
            file_before = repo.git.show(compare_commit + ":./" + file_path)
        if flag != 'D':  # If file wasn't deleted, we have new version
            file_after = repo.git.show("HEAD:./" + file_path)
        # diff = repo.git.diff(compare_commit + ":./" + file_path, "HEAD:./" + file_path)

        file_record["flag"] = flag
        file_record["file_path"] = file_path
        file_record["repository_path"] = repo_path
        file_record["file_before"] = file_before
        file_record["file_after"] = file_after

        changed_files.append(file_record)

    return changed_files
