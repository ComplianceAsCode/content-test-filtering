# content-test-filtering
Automatic tests filtering for [ComplianceAsCode/content project](https://github.com/ComplianceAsCode/content/).

The project analyses changed files, then based on changes decides what has been affected, and at the end selects what should be tested.

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
pip3 install gitpython PyYAML deepdiff Jinja2 xmldiff
git clone https://github.com/mildas/content-test-filtering
```

**WARNING:** For analysis of Jinja files, ComplianceAsCode dependencies are required. See [ComplianceAsCode Developer Guide](https://github.com/ComplianceAsCode/content/blob/master/docs/manual/developer_guide.adoc)

## Usage
How to obtain changes:
-  **Pull request number** - get changes from a [ComplianceAsCode/content PR](https://github.com/ComplianceAsCode/content/pulls)
-  **Branch name** - name of a branch
```
positional arguments:
  {pr,branch}  Subcommands: pr, branch
    pr         Compare base against selected pull request
    branch     Compare base against selected branch
```

Both options have common optional arguments:
```
  -h, --help            show this help message and exit
  --base BASE_BRANCH    Base branch against which we want to compare, default is "master" branch
  --repository REPOSITORY_PATH
                        Path to ComplianceAsCode repository. If not provided, the repository will be cloned into
                        /tmp folder.
  --remote_repo REMOTE_REPO
                        Remote repository for pulling, updating and finding branches (Pull requests). Default is
                        https://github.com/ComplianceAsCode/content.
  --local               Do not pull from remote, use local branches. Mainly for testing purposes.
  --verbose             Increase verbose level of logging to DEBUG level. Default level is INFO
  --output-tests        Output only list of tests. Completely turns off all other outputs.
  --output-format {raw,markdown}
                        Output format.
  --output {commands,json}
                        Output from the tool.
  --profile             Print only profile tests.
  --rule                Print only rule tests.
```

### Remote vs local analysis
By default, changes are obtained from remote repository. When no optional arguments are passed, [ComplianceAsCode/content repository](https://github.com/ComplianceAsCode/content/) is clonned, branch with changes fetched, and then localy analysed.

To disable clonning of the repository and fetch only changes, `--repository` is needed.
To perform local changes analysis, `branch` (Pull Request numbering is unknown in local repository), `--local` (disable branch fetching), and `--repository` (path to local repository) arguments must be used.

### Output format
By default, the project prints human-readable output with identified rule and profile changes and with recommended tests to execute. Github comments support Markdown format, and so to make the output nice for comments, using `--output-format markdown` argument outputs it in the format.

For machine-readble output, use `--output json` argument. It outputs separate output for profile changes and for rule related changes:
- profile changes - `profile` and `product` keys
- rule changes - `rule`, `product`, `bash`, and `ansible` keys

## Tests
Tests are located in `tests/` directory and are using [BATS](https://github.com/bats-core/bats-core).

For each script with tests, testing repository is prepared.
For each test scenario, setup and clean up phase are done. The setup phase creates temporary file for changes, and clean up puts the repository to previous state.
