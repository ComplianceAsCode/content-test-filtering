# content-test-filtering
Purpose of this project is automatic tests filtering for project [ComplianceAsCode](https://github.com/ComplianceAsCode/content/).

This project filters tests based on static analysis of changed files. Changed files are taken from `git`, analysed based on a type of each file, and analysis result is used for test selection.


## Requirements
- Python 3.4 or newer
- Git 1.7 or newer
- GitPython (Python package)
- PyYAML (Python package)
- DeepDiff (Python package)
- Jinja2 (Python package)
- ruamel.yaml (Python package)
- xmldiff (Python package)


## Installation
Fedora/RHEL:
```
yum install python3 git
pip install gitpython PyYAML deepdiff Jinja2 ruamel.yaml xmldiff
git clone https://github.com/mildas/content-test-filtering
```

## Usage
Project has two modes how to get changes from `git`:
- **Pull request number** - get changes from specific [Pull request created for ComplianceAsCode project](https://github.com/ComplianceAsCode/content/pulls)
- **Branch name** - name of a branch
```
$ python3 content_test_filtering.py --help
usage: content_test_filtering.py [-h] {pr,base_branch} ...

positional arguments:
  {pr,base_branch}  Subcommands: pr, branch
    pr              Compare base against selected pull request
    base_branch     Compare base against selected branch

optional arguments:
  -h, --help        show this help message and exit
```

Both modes have common optional arguments:
- **--base BASE_BRANCH**- Base branch which is used for comparison with new changes. If not provided, `master` branch is used as base branch.
- **--repository REPOSITORY_PATH**- Path to ComplianceAsCode repository. If not provided, the repository will be clonned into temporary folder under `/tmp` path. *WARNING:* Newly clonned repository is **NOT deleted** after finishing.


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

**Base branch mode**
Branch mode is similar as Pull request mode. The difference is in arguments used.
```
$ python3 content_test_filtering.py base_branch --repository /tmp/content stabilization-v0.1.49
INFO 16:52:54 - Getting files from 'git diff'
INFO 16:52:56 - Fetched to stabilization-v0.1.49 branch
INFO 16:52:57 - Comparing commit b3d8dc340d71659167be6304a0bbd3f2e4ee9fac with HEAD of stabilization-v0.1.49
WARNING 16:52:57 - Unknown type of file Contributors.md. Analysis has not been performed for it.
WARNING 16:52:57 - Unknown type of file Contributors.xml. Analysis has not been performed for it.
INFO 16:52:57 - []
```

### Local testing
For testing purposes on local changes is created `--local` argument.
When the argument is passed, no branches will be pulled from remote repository, passed branch must be at local repository.

Local testing example:
```
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
$ python3 content_test_filtering.py base_branch --local --repository /tmp/content test_branch
INFO 17:10:42 - Getting files from 'git diff'
INFO 17:10:42 - Fetched to test_branch branch
INFO 17:10:42 - Comparing commit 0f7a0015b15af9dad9950c622b19ecb292b5c83f with HEAD of test_branch
INFO 17:10:42 - ['build_product wrlinux1019', 'test_suite.py rule --libvirt qemu:///system test-suite-vm --remediate ansible --datastream build/ssg-wrlinux1019-ds.xml sshd_disable_compression']
INFO 17:10:42 - Finished
```
