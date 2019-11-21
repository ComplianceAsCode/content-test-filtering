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

    if not os.path.isdir(repo_path):
        logger.warning("%s is not a directory! Creating a new directory" %
                repo_path)

    if repo_path is None:
        repo_path = mkdtemp()
        logger.info("Clonning repository to %s directory" % repo_path)
        Repo.clone_from(URL, repo_path)

    repo = Repo(repo_path)

    for r in repo.remotes:
        if re.search(URL, r.url):
            remote = r

    fetch_branch = "pr-" + pr_number
    logger.info("Fetching branch is %s" % fetch_branch)
    # Checkout to master, so we can fetch, even if the branch exist - it is not
    # possible to fetch, when we are on the same branch
    repo.git.checkout(base_branch)
    remote.fetch("pull/" + pr_number + "/head:" + fetch_branch, force=True)
    repo.git.checkout(fetch_branch)
    # git log --name-status --oneline master..HEAD
    git_log = repo.git.log("--name-status", "--format=\"%H\"", "master..HEAD")
    file_list = []

    rev_list_before = repo.git.rev_list('master')
    rev_list_after = repo.git.rev_list('--first-parent HEAD')
    logger.info(rev_list_before)
    # M,A,D,Rxxx
    # for git_line in git_log.splitlines():
    #     line = git_line.split("\t")
    #     flags_regexp = re.compile(r'^[M|A|D|R\d{3}|C\d{3}]')
    #     if flags_regexp.search(line[0]):
    #         if line[0] != 'A':
    #             file_before = repo.git.show("master:./" + line[1])
    #         if line[0] != 'D':
    #             file_after = repo.git.show("HEAD:./" + line[1])
    #         line.append(file_before)
    #         line.append(file_after)
    #         file_list.append(line)

    # return file_list
    #print(repo.git.log("master..HEAD", name-status=True))
    #commits = list(repo.iter_commits("master..HEAD"))
    #for c in commits:
    #    print(c.stats)
    #    print(inspect.getmembers(c.stats))
