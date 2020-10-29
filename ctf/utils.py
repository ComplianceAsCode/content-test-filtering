import os
import re
from ctf.diff import git_wrapper


def get_repository_files(subfolder=""):
    for root, dirs, files in os.walk(git_wrapper.repo_path + subfolder):
        dirs[:] = list(filter(lambda x: x not in
                              ["build", "build_new", "build_old",
                               "docs", "utils", ".git"], dirs))
        for f in files:
            if f.endswith(".pyc") or f.endswith(".cache") or f.endswith(".swp"):
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


def file_path_to_log(filepath):
    log = ""
    if re.search(r"/build.*/bash/.*\.sh", filepath):
        m = re.match(r".*/([^/]+)\.sh", filepath)
        log = "In Bash remediation for %s." % m.group(1)
    elif re.search(r"/build.*/ansible/.*\.yml", filepath):
        m = re.match(r".*/([^/]+)\.yml", filepath)
        log = "In Ansible remediation for %s." % m.group(1)
    elif re.search(r"/build.*/oval/.*\.yml", filepath):
        m = re.match(r".*/([^/]+)\.xml", filepath)
        log = "In OVAL check for %s." % m.group(1)
    elif re.search(r"/bash/.*\.sh$", filepath):
        m = re.match(r".*/([^/]+)/bash/.*", filepath)
        log = "In Bash remediation for %s." % m.group(1)
    elif re.search(r"/ansible/.*\.yml$", filepath):
        m = re.match(r".*/([^/]+)/ansible/.*", filepath)
        log = "In Ansible remediation for %s." % m.group(1)
    elif re.search(r"/oval/.*\.xml$", filepath):
        m = re.match(r".*/([^/]+)/oval/.*", filepath)
        log = "In OVAL check for %s." % m.group(1)
    elif re.search(r"/rule.yml$", filepath):
        m = re.match(r".*/([^/]+)/rule.yml$", filepath)
        log = "In rule description for %s." % m.group(1)
    return log
