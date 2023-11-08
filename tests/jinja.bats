#!/bin/bash
load test_utils

prepare_repository


@test "Change sshd macro" {
    file="./shared/macros/10-bash.jinja"
    sed -i "/macro bash_sshd_config_set/a echo 1" "$file"
    regex_check_1="build_product"
    regex_check_2="test_suite.py rule.*sshd_set_"
    regex_check_3="test_suite.py rule.*sshd_use_"

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
    if ! grep -q "$regex_check_3" "$tmp_file"; then
        echo "$regex_check_3 not found in:" && cat "$tmp_file"
        return 1
    fi
    if ! grep -q "$regex_check_4" "$tmp_file"; then
        echo "$regex_check_4 not found in:" && cat "$tmp_file"
        return 1
    fi
}

