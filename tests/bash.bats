#!/bin/bash
load test_utils

prepare_repository


@test "Add comment line" {
    file="./linux_os/guide/services/sssd/sssd_run_as_sssd_user/bash/shared.sh"
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

@test "Change indetation" {
    file="./linux_os/guide/services/sssd/sssd_run_as_sssd_user/bash/shared.sh"
    sed -i "s/\s*touch \$SSSD_CONF/touch \$SSSD_CONF/" "$file"
    regex_check="INFO .*\s-\s\[]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change remediation" {
    file="./linux_os/guide/services/sssd/sssd_run_as_sssd_user/bash/shared.sh"
    sed -i "s/chmod 600/chmod 744/" "$file"
    regex_check="INFO .*\s-\s\[.*build_product .*test_suite\.py rule.*sssd_run_as_sssd_user.*]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change templated remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_strong_ciphers/bash/shared.sh"
    sed -i "s/bash_sshd_config_set/bash_some_template/" "$file"
    regex_check="INFO .*\s-\s\[.*build_product .*test_suite\.py rule.*sshd_use_strong_ciphers.*]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

