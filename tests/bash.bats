#!/bin/bash
load test_utils

prepare_repository


@test "Add comment line" {
    file="./linux_os/guide/services/sssd/sssd_run_as_sssd_user/bash/shared.sh"
    sed -i "\$a# comment" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if grep -q "$no_test_regex" "$tmp_file"; then
        echo "$no_test_regex not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change indetation" {
    file="./linux_os/guide/services/sssd/sssd_run_as_sssd_user/bash/shared.sh"
    sed -i "s/\s*touch \$SSSD_CONF/touch \$SSSD_CONF/" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if grep -q "$no_test_regex" "$tmp_file"; then
        echo "$no_test_regex not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change remediation" {
    file="./linux_os/guide/services/sssd/sssd_run_as_sssd_user/bash/shared.sh"
    sed -i "s/chmod 600/chmod 744/" "$file"
    regex_check_1="build_product.*"
    regex_check_2="test_suite\.py rule.*sssd_run_as_sssd_user"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check_1" "$tmp_file"; then
        echo "$regex_check_1 not found in:" && cat "$tmp_file"
        return 1
    fi
    if ! grep -q "$regex_check_2" "$tmp_file"; then
        echo "$regex_check_2 not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change templated remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_strong_ciphers/bash/shared.sh"
    sed -i "s/bash_sshd_config_set/bash_some_template/" "$file"
    regex_check_1="build_product.*"
    regex_check_2="test_suite\.py rule.*sshd_use_strong_ciphers"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check_1" "$tmp_file"; then
        echo "$regex_check_1 not found in:" && cat "$tmp_file"
        return 1
    fi
    if ! grep -q "$regex_check_2" "$tmp_file"; then
        echo "$regex_check_2 not found in:" && cat "$tmp_file"
        return 1
    fi
}


@test "Remove bash remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_approved_macs/bash/shared.sh"
    rm -f "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if grep -q "$no_test_regex" "$tmp_file"; then
        echo "$no_test_regex not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Add new bash remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/bash/shared.sh"
    mkdir -p "./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/bash/"
    echo "echo \"IgnoreRhosts yes\" > /tmp/ssh_tmp_file" > "$file"
    regex_check_1="build_product"
    regex_check_2="test_suite\.py rule.*bash.*sshd_disable_rhosts"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check_1" "$tmp_file"; then
        echo "$regex_check_1 not found in:" && cat "$tmp_file"
        return 1
    fi
    if ! grep -q "$regex_check_2" "$tmp_file"; then
        echo "$regex_check_2 not found in:" && cat "$tmp_file"
        return 1
    fi
}

