#!/bin/bash
load test_utils

prepare_repository


@test "Add comment" {
    file="tests/automatus.py"
    sed -i "1 i # some comment" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if grep -q "$no_test_regex" "$tmp_file"; then
        echo "$no_test_regex not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Delete comments" {
    file="tests/automatus.py"
    sed -i "/^\s*#.*/d" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if grep -q "$no_test_regex" "$tmp_file"; then
        echo "$no_test_regex not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change code" {
    file="tests/automatus.py"
    sed -i "/^\s*subparsers\.required.*/d" "$file"
    regex_check="ctest"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}
