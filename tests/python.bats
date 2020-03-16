#!/bin/bash
load test_utils

prepare_repository


@test "Add comment" {
    file="tests/test_suite.py"
    sed -i "1 i # some comment" "$file"
    regex_check="INFO .*\s-\s\[]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Delete comments" {
    file="tests/test_suite.py"
    sed -i "/^\s*#.*/d" "$file"
    regex_check="INFO .*\s-\s\[]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change code" {
    file="tests/test_suite.py"
    sed -i "/^\s*subparsers\.required.*/d" "$file"
    regex_check="INFO .*\s-\s\[.*ctest.*]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}


