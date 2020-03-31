import os
import re
import subprocess
import logging
import shutil
from git import Repo, GitCommandError
from tempfile import mkdtemp

logger = logging.getLogger("content-test-filtering.diff")
URL = "https://github.com/ComplianceAsCode/content"


class RemoteNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GitDiffWrapper(metaclass=Singleton):
    def __init__(self):
        self.repo_url = None
        self.repository = None
        self.repo_path = None
        self.only_local = False
        self.remote = None
        self.old_branch = None
        self.new_branch = None
        self.diverge_commit = None
        self.current_branch = None

    def git_init(self, remote_repo, local_repo_path=None, local=False):
        self.repo_url = remote_repo
        self.repo_path = local_repo_path
        self.prepare_repo_dir()
        self.repo_path = os.path.abspath(self.repo_path)
        self.repository = Repo(self.repo_path)
        self.only_local = local

    def checkout_branch(self, branch):
        self.repository.git.checkout(branch)
        self.current_branch = branch

    def build_project(self, old_build_path, new_build_path,
                      products=["rhel7", "rhel8"]):

        old_build = self.repo_path + old_build_path
        new_build = self.repo_path + new_build_path

        shutil.rmtree(old_build)
        shutil.rmtree(new_build)
        try:
            os.mkdir(old_build)
        except FileExistsError:
            pass
        try:
            os.mkdir(new_build)
        except FileExistsError:
            pass

        self.checkout_branch(self.diverge_commit)
        subprocess.run("cmake ../", shell=True, cwd=old_build)
        self.checkout_branch(self.new_branch)
        subprocess.run("cmake ../", shell=True, cwd=new_build)

        for product in products:
            self.checkout_branch(self.diverge_commit)
            subprocess.run("make generate-internal-templated-content-"+product,
                           shell=True, cwd=old_build)
            self.checkout_branch(self.new_branch)
            subprocess.run("make generate-internal-templated-content-"+product,
                           shell=True, cwd=new_build)

    def is_dir(self, directory):
        is_directory = True

        if not os.path.isdir(directory):
            logger.warning("%s is not a directory.", directory)
            is_directory = False

        return is_directory

    def prepare_repo_dir(self):
        if self.repo_path is not None and self.is_dir(self.repo_path):
            return
        self.repo_path = mkdtemp()
        self.init_repository(self.repo_url, self.repo_path)

    def init_repository(self, url, path):
        logger.info("Cloning repository to %s directory", path)
        Repo.clone_from(url, path)

    def update_branch(self, branch):
        self.checkout_branch(branch)
        if not self.only_local:
            self.remote.pull(branch)

    def find_remote(self, remote_url):
        remote = None
        for r in self.repository.remotes:
            if re.search(remote_url, r.url):
                remote = r
                break
        if not remote:
            raise RemoteNotFound("Remote repository '%s' was not found "
                                 "in local tracked repositories." % remote_url)
        return remote

    def get_compare_commit(self, old_branch, new_branch):
        self.checkout_branch(new_branch)

        git_log_old = self.repository.git.log("--format=%H", old_branch)
        git_log_old = git_log_old.split()
        git_log_new = self.repository.git.log("--format=%H")
        git_log_new = git_log_new.split()

        common_commit = None
        for commit_sha in git_log_new:
            if commit_sha in git_log_old:
                common_commit = commit_sha
                break

        # If common branch is HEAD of target branch, then the branch
        # has been already merged and we need to find commit to compare
        if git_log_new[0] == common_commit:
            git_log = self.repository.git.log(old_branch, "^" + new_branch,
                                              "--ancestry-path", "--format=%P",
                                              "--reverse")
            merge_commits = git_log.partition("\n")[0]
            merge_commits = merge_commits.split(" ")
            compare_commit = self.repository.git.merge_base("--all", merge_commits)
        else:  # The branch was not merged - common commit
            compare_commit = common_commit

        logger.info("Comparing commit " + compare_commit + " with "
                    "HEAD of " + new_branch)
        return compare_commit

    def create_file_record(self, flag, filepath, file_before, file_after):
        file_record = {}
        file_record["flag"] = flag
        file_record["filepath"] = filepath
        file_record["file_before"] = file_before
        file_record["file_after"] = file_after
        return file_record

    def file_added(self, new_file):
        file_before = ""
        file_after = self.repository.git.show("HEAD:./" + new_file)
        return file_before, file_after

    def file_deleted(self, old_file):
        file_before = self.repository.git.show(self.diverge_commit + ":./" + old_file)
        file_after = ""
        return file_before, file_after

    def file_modified(self, old_file, new_file):
        file_before = self.repository.git.show(self.diverge_commit + ":./" + old_file)
        file_after = self.repository.git.show("HEAD:./" + new_file)
        return file_before, file_after

    def create_file_records_from_diff(self, compare_commit):
        file_records = []

        git_diff = self.repository.git.diff("--name-status",
                                            compare_commit + "..HEAD")

        for line in git_diff.splitlines():
            git_diff_output = line.split("\t")
            if git_diff_output[0].startswith("R"):
                flag, old_filepath, filepath = git_diff_output
            else:
                flag, filepath = git_diff_output
                old_filepath = filepath

            if flag == "A":
                file_before, file_after = self.file_added(filepath)
            elif flag == "D":
                file_before, file_after = self.file_deleted(filepath)
            else:
                file_before, file_after = self.file_modified(old_filepath, filepath)

            file_record = self.create_file_record(flag, filepath,
                                                  file_before, file_after)
            file_records.append(file_record)

        return file_records

    def git_diff_files(self, old_branch, new_branch=None, pr_number=None):
        assert new_branch or pr_number

        self.remote = self.find_remote(self.repo_url)
        self.update_branch(old_branch)

        if new_branch:
            target_branch = new_branch
            fetch_refs = new_branch + ":" + new_branch
        else:
            target_branch = "pr-" + pr_number
            fetch_refs = "pull/" + pr_number + "/head:" + target_branch

        if not self.only_local:
            self.remote.fetch(fetch_refs, force=True)
        logger.info("Fetched to %s branch", target_branch)

        self.new_branch = target_branch
        self.diverge_commit = self.get_compare_commit(old_branch, target_branch)
        file_records = self.create_file_records_from_diff(self.diverge_commit)
        return file_records


git_wrapper = GitDiffWrapper()
