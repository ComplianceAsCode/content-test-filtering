import os
from ctf.diff import git_wrapper


def get_repository_files(subfolder=""):
    for root, dirs, files in os.walk(git_wrapper.repo_path + subfolder):
        dirs[:] = list(filter(lambda x: not x in
                                ["build", "build_new", "build_old",
                                "docs", "utils", ".git"],
                                dirs))
        #dirs[:] = [d for d in dirs if d not in ["build", "build_new", "build_old", "docs", "utils", ".git"]]
        for f in files:
            if f.endswith(".pyc") or f.endswith(".cache"):
                continue
            filepath = root + "/" + f
            yield filepath