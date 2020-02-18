#!/bin/bash
load test_utils

prepare_repository


@test "Change documentation_complete" {
    file="rhel8/profiles/ospp.profile"
    sed -i 's/documentation_complete: true/documentation_complete: false/' "$file"
    regex_check="INFO .*\s-\s\[]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content-test-filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change title" {
    file="rhel8/profiles/ospp.profile"
    sed -i "s/title: .*/title: 'Some title'/" "$file"
    regex_check="INFO .*\s-\s\[]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content-test-filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Add new category" {
    file="rhel8/profiles/ospp.profile"
    echo >> "$file"
    sed -i "\$asome_category: 'with_string'" "$file"
    regex_check="INFO .*\s-\s\[.*build_product\srhel8.*]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    echo $tmp_file
    python3 $BATS_TEST_DIRNAME/../content-test-filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change rule (= adding new rule and removing old one)" {
    file="rhel8/profiles/ospp.profile"
    sed -i 's/disable_host_auth/enable_host_auth/' "$file"
    regex_check="INFO .*\s-\s\[.*build_product rhel8.*test_suite\.py profile.*ospp.*]$"

    git add "$file" && git commit -m "test commit" &>/dev/null

    echo $tmp_file
    python3 $BATS_TEST_DIRNAME/../content-test-filtering.py base_branch --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}
