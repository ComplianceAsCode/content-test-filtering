#!/bin/bash
load test_utils

prepare_repository


@test "Add comment line" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/ansible/shared.yml"
    sed -i "\$a# comment" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Change metadata" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/ansible/shared.yml"
    sed -i 's/# reboot = false/# reboot = true/' "$file"
    regex_check="build_product "

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Change name" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/ansible/shared.yml"
    sed -i 's/- name: disable.*/- name: some name/' "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Change remediation part" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/ansible/shared.yml"
    sed -i 's;path: .*;path: /some/path/;' "$file"
    regex_check="{.*'rules': \['disable_prelink'\].*'bash': 'False'.*'ansible': 'True'}"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change templated remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_approved_macs/ansible/shared.yml"
    sed -i 's/ansible_sshd_set/ansible_some_template/' "$file"
    regex_check="{.*'rules': \['sshd_use_approved_macs'\].*'bash': 'False'.*'ansible': 'True'}"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Remove ansible remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_approved_macs/ansible/shared.yml"
    rm -f "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Add new ansible remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/ansible/shared.yml"
    mkdir -p "./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/ansible/"
    echo "echo \"IgnoreRhosts yes\" > /tmp/ssh_tmp_file" > "$file"
    regex_check="{.*'rules': \['sshd_disable_rhosts'\].*'bash': 'False'.*'ansible': 'True'}"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}
