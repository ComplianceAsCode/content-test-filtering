#!/bin/bash
load test_utils

prepare_repository


@test "Change documentation_complete" {
    file="products/rhel8/profiles/ospp.profile"
    sed -i 's/documentation_complete: true/documentation_complete: false/' "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Change title" {
    file="products/rhel8/profiles/ospp.profile"
    sed -i "s/title: .*/title: 'Some title'/" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Add new category" {
    file="products/rhel8/profiles/ospp.profile"
    echo >> "$file"
    sed -i "\$asome_category: 'with_string'" "$file"
    regex_check='{.*"profiles": \[.*"ospp".*\], "product": "rhel8".*}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change rule (= adding new rule and removing old one)" {
    file="products/rhel8/profiles/ospp.profile"
    sed -i 's/disable_host_auth/enable_host_auth/' "$file"
    regex_check='{.*"profiles": \[.*"ospp".*\], "product": "rhel8".*}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Remove profile" {
    file="products/rhel8/profiles/ospp.profile"
    rm -f "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Add new profile" {
    file="products/rhel8/profiles/some_profile.profile"
    cat "products/rhel8/profiles/ospp.profile" > "$file"
    regex_check='{.*"profiles": \[.*"some_profile".*\], "product": "rhel8".*}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}
