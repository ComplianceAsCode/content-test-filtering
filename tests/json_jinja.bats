#!/bin/bash
load test_utils

prepare_repository


@test "Change sshd macro" {
    file="./shared/macros-bash.jinja"
    sed -i "/macro bash_sshd_config_set/a echo 1" "$file"
    regex_check_1='{.*"rules": \[.*"sshd_use_strong_ciphers".*\].*"bash": "True".*"ansible": "False".*}'
    regex_check_2='{.*"rules": \[.*"sshd_use_strong_macs".*\].*"bash": "True".*"ansible": "False".*}'
    regex_check_3='{.*"rules": \[.*"sshd_set_keepalive".*\].*"bash": "True".*"ansible": "False".*}'
    regex_check_4='{.*"rules": \[.*"sshd_set_idle_timeout".*\].*"bash": "True".*"ansible": "False".*}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

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

