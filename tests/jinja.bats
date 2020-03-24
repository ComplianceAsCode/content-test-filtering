#!/bin/bash
load test_utils

prepare_repository


@test "Change sshd macro" {
    file="./shared/macros-bash.jinja"
    sed -i "/macro bash_sshd_config_set/a echo 1" "$file"
    regex_check1="INFO .*\s-\s\[.*build_product.*test_suite.py rule.*sshd_use_strong_macs.*]$"
    regex_check2="INFO .*\s-\s\[.*build_product.*test_suite.py rule.*sshd_set_loglevel_info.*]$"
    regex_check3="INFO .*\s-\s\[.*build_product.*test_suite.py rule.*sshd_disable_rhosts.*]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}
