# content-test-filtering
Purpose of this project is automatic tests filtering for project [ComplianceAsCode](https://github.com/ComplianceAsCode/content/).

This project filters tests based on static analysis of changed files. Changed files are taken from `git`, analysed based on a type of each file, and analysis result is used for test selection.

## Requirements
-  Python 3.4 or newer
-  Git 1.7 or newer
-  GitPython (Python package)
-  PyYAML (Python package)
-  DeepDiff (Python package)
-  Jinja2 (Python package)
-  xmldiff (Python package)

## Installation
Fedora/RHEL:
```
yum install python3 git
pip install gitpython PyYAML deepdiff Jinja2 xmldiff
git clone https://github.com/mildas/content-test-filtering
```

## Usage
Project has two modes how to get changes from `git`:
-  **Pull request number** - get changes from specific [Pull request created for ComplianceAsCode project](https://github.com/ComplianceAsCode/content/pulls)
-  **Branch name** - name of a branch
```
$ python3 content_test_filtering.py --help
usage: content_test_filtering.py [-h] {pr,branch} ...

positional arguments:
  {pr,branch}  Subcommands: pr, branch
    pr              Compare base against selected pull request
    branch     Compare base against selected branch

optional arguments:
  -h, --help        show this help message and exit
```

Both modes have common optional arguments:
-  **--base BASE_BRANCH** - Base branch which is used for comparison with new changes. If not provided, `master` branch is used as base branch.
-  **--repository REPOSITORY_PATH** - Path to ComplianceAsCode repository. If not provided, the repository will be clonned into temporary folder under `/tmp` path. *WARNING:* Newly clonned repository is **NOT deleted** after finishing.
-  **--remote_repo REMOTE_REPO** - Remote repository for pulling, updating and finding branches (Pull requests). Default is `https://github.com/ComplianceAsCode/content`.

### Examples
**Pull request mode**
As an example of is used [PR#4957](https://github.com/ComplianceAsCode/content/pull/4957)
```
$ python3 content_test_filtering.py pr --repository /tmp/content 4957
INFO 16:46:52 - Getting files from 'git diff'
INFO 16:46:54 - Fetched to pr-4957 branch
INFO 16:46:55 - Comparing commit 6bac23a68cf80c63ffc1d79ad2f3f549c430ebba with HEAD of pr-4957
INFO 16:46:55 - Analyzing profile file rhel7/profiles/ospp.profile
INFO 16:46:56 - Added rules to profile: 
INFO 16:46:56 - Removed rules from profile: directory_access_var_log_audit
INFO 16:46:56 - ['build_product rhel7', 'test_suite.py profile --libvirt qemu:///system test-suite-vm --datastream build/ssg-rhel7-ds.xml ospp', 'test_suite.py profile --libvirt qemu:///system test-suite-vm --datastream build/ssg-rhel7-ds.xml ncp', 'test_suite.py profile --libvirt qemu:///system test-suite-vm --datastream build/ssg-rhel7-ds.xml cui']
INFO 16:46:56 - Finished
```

**Branch mode**
Branch mode is similar as Pull request mode. The difference is in arguments used.
[ComplainceAsCode](https://github.com/ComplianceAsCode/content) project usually doesn't have any branches, so for testing purposes was created [ctf_test_branch](https://github.com/ComplianceAsCode/content/compare/master...mildas:ctf_test_branch) at [forked repository](https://github.com/mildas/scap-security-guide).

*WARNING*: You need to specify [remote repository](https://github.com/mildas/scap-security-guide). And add it to git tracked repositories (`git remote` command) or let `content-test-filtering` to clone it's own repository.
```
$ python3 content_test_filtering.py branch --remote_repo https://github.com/mildas/scap-security-guide --repository /tmp/content ctf_test_branch
INFO 22:05:50 - Getting files from 'git diff'
INFO 22:05:52 - Fetched to ctf_test_branch branch
INFO 22:05:52 - Comparing commit 9bcd1c9f004d539cde8eddfed918b60633d8aaef with HEAD of ctf_test_branch
INFO 22:05:53 - Analyzing ansible file linux_os/guide/services/ssh/ssh_server/sshd_use_approved_macs/ansible/shared.yml
INFO 22:05:53 - Analyzing bash file linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/bash/shared.sh
INFO 22:05:53 - Analyzing profile file rhel8/profiles/ospp.profile
INFO 22:05:53 - Added rules to profile: 
INFO 22:05:53 - Removed rules from profile: 
INFO 22:05:53 - Analyzing python file ssg/utils.py
INFO 22:05:53 - ['(cd build && ctest -j4)', 'build_product wrlinux1019', 'test_suite.py rule --libvirt qemu:///system test-suite-vm --remediate ansible --datastream build/ssg-wrlinux1019-ds.xml sshd_use_approved_macs', 'test_suite.py rule --libvirt qemu:///system test-suite-vm --remediate bash --datastream build/ssg-wrlinux1019-ds.xml rpm_verify_permissions']
INFO 22:05:53 - Finished
```

### Local testing
For testing purposes on local changes is created `--local` argument.
When the argument is passed, no branches will be pulled from remote repository, passed branch must be at local repository.

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
INFO 17:10:42 - Getting files from 'git diff'
INFO 17:10:42 - Fetched to test_branch branch
INFO 17:10:42 - Comparing commit 0f7a0015b15af9dad9950c622b19ecb292b5c83f with HEAD of test_branch
INFO 17:10:42 - ['build_product wrlinux1019', 'test_suite.py rule --libvirt qemu:///system test-suite-vm --remediate ansible --datastream build/ssg-wrlinux1019-ds.xml sshd_disable_compression']
INFO 17:10:42 - Finished
```
