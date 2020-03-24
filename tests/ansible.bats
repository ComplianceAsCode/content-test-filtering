#!/bin/bash
load test_utils

prepare_repository


@test "Add comment line" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/ansible/shared.yml"
    sed -i "\$a# comment" "$file"
    regex_check="INFO .*\s-\s\[]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change metadata" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/ansible/shared.yml"
    sed -i 's/# reboot = false/# reboot = true/' "$file"
    regex_check="INFO .*\s-\s\['build_product rhv4']$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change name" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/ansible/shared.yml"
    sed -i 's/- name: disable.*/- name: some name/' "$file"
    regex_check="INFO .*\s-\s\[]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change remediation part" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/ansible/shared.yml"
    sed -i 's;path: .*;path: /some/path/;' "$file"
    regex_check="INFO .*\s-\s\[.*build_product rhv4.*test_suite\.py rule.*disable_prelink.*]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change templated remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_approved_macs/ansible/shared.yml"
    sed -i 's/ansible_sshd_set/ansible_some_template/' "$file"
    regex_check="INFO .*\s-\s\[.*build_product wrlinux1019.*test_suite\.py rule.*sshd_use_approved_macs.*]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Remove ansible remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_approved_macs/ansible/shared.yml"
    rm -f "$file"
    regex_check="INFO .*\s-\s\[]"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Add new ansible remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/ansible/shared.yml"
    mkdir -p "./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/ansible/"
    echo "echo \"IgnoreRhosts yes\" > /tmp/ssh_tmp_file" > "$file"
    regex_check="INFO .*\s-\s\[.*build_product.*,.*test_suite\.py rule.*ansible.*sshd_disable_rhosts.*]"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}
