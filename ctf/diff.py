from git import Repo
from tempfile import mkdtemp
import re
import logging
import os
import inspect
import re

logger = logging.getLogger("content-test-filtering.diff")

URL = "https://github.com/ComplianceAsCode/content"

def get_git_diff_files(options):
    pr_number = options.target
    base_branch = options.base_branch
    repo_path = options.repository_path

    if repo_path is not None and not os.path.isdir(repo_path):
        logger.warning("%s is not a directory! Creating a new directory" %
                repo_path)

    if repo_path is None:
        repo_path = mkdtemp()
        logger.info("Clonning repository to %s directory" % repo_path)
        Repo.clone_from(URL, repo_path)

    repo = Repo(repo_path)
    repo.git.checkout(base_branch)
    repo.remotes.origin.pull()

    for r in repo.remotes:
        if re.search(URL, r.url):
            remote = r

    fetch_branch = "pr-" + pr_number
    logger.info("Fetching branch is %s" % fetch_branch)
    # Checkout to master, so we can fetch, even if the branch exist - it is not
    # possible to fetch, when we are on the same branch
    remote.fetch("pull/" + pr_number + "/head:" + fetch_branch, force=True)
    repo.git.checkout(fetch_branch)
    git_log_old = repo.git.log("--format=%H", "master")
    git_log_old = git_log_old.split()
    git_log_new = repo.git.log("--format=%H")
    git_log_new = git_log_new.split()
    for i in git_log_new:
        if i in git_log_old:
            print(i)
            break
    # repo.git.checkout(fetch_branch)
    # repo.git.checkout(base_branch)
    #git_log = repo.git.log("master", "^" + fetch_branch, "--ancestry-path",
    #                       "--format=\"%P\"", "--reverse")
    # if git_log:
    #     print(git_log)
    #     merge_base = git_log.partition("\n")[0]
    #     merge_base = merge_base.replace("\"","")
    #     merge_base = merge_base.split(" ")
    #     print(merge_base)
    #     # git log --name-status --oneline master..HEAD
    #     # git_base_commit = repo.git.log("--name-status", "--format=\"%H\"", base_branch + "..HEAD")
    #     git_base_commit = repo.git.merge_base("--all", merge_base)
    # else:
    #     git_base_commit = base_branch + "."
    # repo.git.checkout(fetch_branch)
    # git_diff = repo.git.diff("--name-status", git_base_commit + "..HEAD")
    # print(git_diff)
    # file_list = []

    # rev_list_before = repo.git.rev_list('master')
    # rev_list_after = repo.git.rev_list('--first-parent HEAD')
    # logger.info(rev_list_before)
    # M,A,D,Rxxx
    #logger.info(git_log)
    for git_line in git_diff.splitlines():
        line = git_line.split("\t")
        flags_regexp = re.compile(r'^[M|A|D|R\d{3}|C\d{3}]')
        if flags_regexp.search(line[0]):
            if line[0] != 'A':
                file_before = repo.git.show(git_base_commit + ":./" + line[1])
            if line[0] != 'D':
                file_after = repo.git.show("HEAD:./" + line[1])
            print(file_before)
            print("----------------------------------------------")
            print(file_after)
            line.append(file_before)
            line.append(file_after)
            line[1] = repo_path + "/" + line[1]
            file_list.append(line)

    return file_list
    #print(repo.git.log("master..HEAD", name-status=True))
    #commits = list(repo.iter_commits("master..HEAD"))
    #for c in commits:
    #    print(c.stats)
    #    print(inspect.getmembers(c.stats))
