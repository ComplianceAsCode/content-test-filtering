#!/bin/bash
load test_utils

prepare_repository


@test "Add comment line" {
    file="./linux_os/guide/services/sssd/sssd_run_as_sssd_user/bash/shared.sh"
    sed -i "\$a# comment" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not emtpy" && cat "$tmp_file"
        return 1
    fi
}

@test "Change indetation" {
    file="./linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/bash/shared.sh"
    # Add 2 extra space at beginning of each line
    sed -i "s/\(.*\)/  \1/" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not emtpy" && cat "$tmp_file"
        return 1
    fi
}

@test "Change remediation" {
    file="./linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/bash/shared.sh"
    sed -i "s/rpm//" "$file"
    regex_check='{.*"rules": \["rpm_verify_permissions"\].*"bash": "True".*"ansible": "False"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change templated remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_strong_ciphers/bash/shared.sh"
    sed -i "s/bash_sshd_config_set/bash_some_template/" "$file"
    regex_check='{.*"rules": \["sshd_use_strong_ciphers"\].*"bash": "True".*"ansible": "False"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}


@test "Remove bash remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_use_approved_macs/bash/shared.sh"
    rm -f "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not emtpy" && cat "$tmp_file"
        return 1
    fi
}

@test "Add new bash remediation" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/bash/shared.sh"
    mkdir -p "./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/bash/"
    echo "echo \"IgnoreRhosts yes\" > /tmp/ssh_tmp_file" > "$file"
    regex_check='{.*"rules": \["sshd_disable_rhosts"\].*"bash": "True".*"ansible": "False"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}
