import os
from ctf.diff import git_wrapper


def get_repository_files(subfolder=""):
    for root, dirs, files in os.walk(git_wrapper.repo_path + subfolder):
        dirs[:] = list(filter(lambda x: x not in
                              ["build", "build_new", "build_old",
                               "docs", "utils", ".git"], dirs))
        for f in files:
            if f.endswith(".pyc") or f.endswith(".cache"):
                continue
            filepath = root + "/" + f
            yield filepath


def get_suffix(filetype):
    if filetype == "ANACONDA":
        suffix = ".anaconda"
    elif filetype == "ANSIBLE":
        suffix = ".yml"
    elif filetype == "BASH":
        suffix = ".sh"
    elif filetype == "OVAL":
        suffix = ".xml"
    elif filetype == "PUPPET":
        suffix = ".pp"
    else:
        raise TypeError
    return suffix
