# content-test-filtering
Purpose of this project is automatic tests filtering for project [ComplianceAsCode](https://github.com/ComplianceAsCode/content/).

This project filters tests based on static analysis of changed files. Changed files are taken from `git`, analysed based on a type of each file, and the analysis result is used for the test selection.

## Requirements
-  Python 3.4 or newer
-  Git 1.7 or newer
-  GitPython (Python package)
-  PyYAML (Python package)
-  DeepDiff (Python package)
-  Jinja2 (Python package)
-  xmldiff (Python package)
-  requests (Python package, required for experiments and Github comments)

## Installation
Fedora/RHEL:
```
yum install python3 git
pip install gitpython PyYAML deepdiff Jinja2 xmldiff requests
git clone https://github.com/mildas/content-test-filtering
```

**WARNING:** For analysis of Jinja files, ComplianceAsCode dependencies are required. See [ComplianceAsCode Developer Guide](https://github.com/ComplianceAsCode/content/blob/master/docs/manual/developer_guide.adoc)

## Usage
Project has two modes how to get changes from `git`:
-  **Pull request number** - get changes from a specific [Pull request created for ComplianceAsCode project](https://github.com/ComplianceAsCode/content/pulls)
-  **Branch name** - name of a branch
```
$ python3 content_test_filtering.py --help
usage: content_test_filtering.py [-h] {pr,branch} ...

positional arguments:
  {pr,branch}  Subcommands: pr, branch
    pr         Compare base against selected pull request
    branch     Compare base against selected branch

optional arguments:
  -h, --help   show this help message and exit
```

Both modes have common optional arguments:
-  **-h, --help** - Help message.
-  **--base BASE_BRANCH** - Base branch which is used for comparison with new changes. If not provided, `master` branch is used as base branch.
-  **--repository REPOSITORY_PATH** - Path to ComplianceAsCode repository. If not provided, the repository will be clonned into temporary folder under `/tmp` path. *WARNING:* Newly clonned repository is **NOT deleted** after finishing.
-  **--remote_repo REMOTE_REPO** - Remote repository for pulling, updating and finding remote branches (Pull Requests). Default is `https://github.com/ComplianceAsCode/content`.
-  **--local** - Force the project to use local branch and to not pull changes from remote repository. For testing purposes.
-  **--verbose** - Increase verbose level of logging to DEBUG level.
-  **--output-tests** - Outputs only list of tests. Completely turns off all other outputs.
-  **--output-format {raw,markdown}** - Output format selection. Default is **raw**.

### Examples
**Pull request mode**
As an example of is used [PR#4957](https://github.com/ComplianceAsCode/content/pull/4957)
```
$ python3 content_test_filtering.py pr 4957
Changes identified:
  Profile ospp on rhel7:
    Rule directory_access_var_log_audit removed from ospp profile.
  Profile ncp on rhel7:
    NCP profile extends changed OSPP profile.
  Profile cui on rhel7:
    CUI profile extends changed OSPP profile.

Recommended tests to execute:
    build_product rhel7
    tests/test_suite.py profile --libvirt qemu:///system test-suite-vm --datastream build/ssg-rhel7-ds.xml cui
    tests/test_suite.py profile --libvirt qemu:///system test-suite-vm --datastream build/ssg-rhel7-ds.xml ospp
    tests/test_suite.py profile --libvirt qemu:///system test-suite-vm --datastream build/ssg-rhel7-ds.xml ncp
```

**Branch mode**
Branch mode is similar as Pull request mode. The difference is in arguments used.
[ComplainceAsCode](https://github.com/ComplianceAsCode/content) project usually doesn't have any branches, so for testing purposes was created [ctf_test_branch](https://github.com/ComplianceAsCode/content/compare/master...mildas:ctf_test_branch) at [forked repository](https://github.com/mildas/scap-security-guide).

**WARNING**: You need to specify [remote repository](https://github.com/mildas/scap-security-guide). And add it to git tracked repositories (`git remote` command) or let `content-test-filtering` to clone it's own repository.
```
$ python3 content_test_filtering.py branch --remote_repo https://github.com/mildas/scap-security-guide ctf_test_branch
Changes identified:
  Rule sshd_use_approved_macs:
    Ansible remediation changed.
  Rule rpm_verify_permissions:
    Found change in bash remediation.
  Others:
    Python abstract syntax tree change found in ssg/utils.py.

Recommended tests to execute:
    build_product wrlinux1019
    tests/test_suite.py rule --libvirt qemu:///system test-suite-vm --remediate-using ansible --datastream build/ssg-wrlinux1019-ds.xml sshd_use_approved_macs
    tests/test_suite.py rule --libvirt qemu:///system test-suite-vm --remediate-using bash --datastream build/ssg-wrlinux1019-ds.xml rpm_verify_permissions
    (cd build && cmake ../ && ctest -j4)
```

### Local testing
For testing purposes on local changes is created the `--local` argument.
When the argument is passed, no branches will be pulled from a remote repository, the provided branch name must be at the local repository.

Local testing example:
```bash
$ cd /tmp/content
$ git checkout -b "test_branch"
Switched to a new branch 'test_branch'
$ vim ./linux_os/guide/services/ssh/ssh_server/sshd_disable_compression/ansible/shared.yml # Change the file
$ git diff
...
-{{{ ansible_sshd_set(parameter="Compression", value="delayed") }}}
+{{{ ansible_sshd_set(parameter="Compression", value="0") }}}
...
$ git add ./linux_os/guide/services/ssh/ssh_server/sshd_disable_compression/ansible/shared.yml
$ git commit -m "Update remediation"
$ cd ~/content-test-filtering
$ python3 content_test_filtering.py branch --local --repository /tmp/content test_branch                                                                                             
Changes identified:
  Rule sshd_disable_compression:
    Template usage changed in ansible remediation.

Recommended tests to execute:
    build_product wrlinux1019
    tests/test_suite.py rule --libvirt qemu:///system test-suite-vm --remediate-using ansible --datastream build/ssg-wrlinux1019-ds.xml sshd_disable_compression
```
