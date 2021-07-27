#!/bin/bash
load test_utils

prepare_repository


@test "Add comment line" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/oval/shared.xml"
    sed -i "/<def-group>/a <!--comment-->" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Change filepath in OVAL" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/oval/shared.xml"
    sed -i 's/PRELINKING=no/PRELINKING=yes/' "$file"
    regex_check='{.*"rules": \[.*"disable_prelink".*\].*"bash": "True".*"ansible": "True"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Change node in OVAL" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/oval/shared.xml"
    sed -i '/PRELINKING=/d' "$file"
    regex_check='{.*"rules": \[.*"disable_prelink".*\].*"bash": "True".*"ansible": "True"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}

@test "Remove OVAL check" {
    file="./linux_os/guide/system/software/integrity/disable_prelink/oval/shared.xml"
    rm -f "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Add new OVAL check" {
    file="./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/oval/shared.xml"
    mkdir -p "./linux_os/guide/services/ssh/ssh_server/sshd_disable_rhosts/oval/"
    cat "./linux_os/guide/system/software/integrity/disable_prelink/oval/shared.xml" > "$file"
    regex_check='{.*"rules": \[.*"sshd_disable_rhosts".*\].*"bash": "True".*"ansible": "True"}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in:" && cat "$tmp_file"
        return 1
    fi
}
