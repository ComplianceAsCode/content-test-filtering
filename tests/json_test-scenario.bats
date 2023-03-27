#!/bin/bash
load test_utils

prepare_repository

@test "Add comment line" {
    file="./linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/tests/bad_permissions.fail.sh"
    sed -i "\$a#comment" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Update test scenario" {
    file="./linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/tests/bad_permissions.fail.sh"
    sed -i "\$a echo \$x" "$file"
    regex_check='{.*"rules": \["rpm_verify_permissions"\].*"bash": "True".*"ansible": "True"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found int:" && cat "$tmp_file"
        return 1
    fi
}

@test "Update test metadata" {
    file="./linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/tests/bad_permissions.fail.sh"
    sed -i "1i # platform = fedora" "$file"
    regex_check='{.*"rules": \["rpm_verify_permissions"\].*"bash": "True".*"ansible": "True"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found int:" && cat "$tmp_file"
        return 1
    fi
}

@test "New test scenario" {
    file="./linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/tests/new_test.pass.sh"
    touch "$file"
    regex_check='{.*"rules": \["rpm_verify_permissions"\].*"bash": "True".*"ansible": "True"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found int:" && cat "$tmp_file"
        return 1
    fi
}

@test "Test removed" {
    file="./linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/tests/bad_permissions.fail.sh"
    rm "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

