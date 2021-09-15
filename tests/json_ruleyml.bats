#!/bin/bash
load test_utils

prepare_repository

@test "Change rule title" {
    file="linux_os/guide/services/avahi/disable_avahi_group/service_avahi-daemon_disabled/rule.yml"
    sed -i "s/title:.*/title: 'New title'/" "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Change variable in template" {
    file="linux_os/guide/services/avahi/disable_avahi_group/service_avahi-daemon_disabled/rule.yml"
    sed -i "s/servicename:.*/servicename: new_service/" "$file"
    regex_check='{.*"rules": \["service_avahi-daemon_disabled"\].*"bash": "True".*"ansible": "True".*}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in: " && cat "$tmp_file"
        return 1
    fi
}

@test "New rule added" {
    file="linux_os/guide/services/avahi/disable_avahi_group/some_avahi_service/rule.yml"
    mkdir -p "linux_os/guide/services/avahi/disable_avahi_group/some_avahi_service"
    touch "$file"
    cat > "$file" << EOF
title: 'New service rule'
description: |-
    Description of new rule.
template:
    name: service_disabled
    vars:
        servicename: some-daemon
EOF
    regex_check='{.*"rules": \["some_avahi_service"\].*"bash": "True".*"ansible": "True".*}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in: " && cat "$tmp_file"
        return 1
    fi
}

@test "Rule removed" {
    file="linux_os/guide/services/avahi/disable_avahi_group/service_avahi-daemon_disabled/rule.yml"
    rm "$file"

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}

@test "Add template section" {
    file="linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/rule.yml"
    cat > "$file" << EOF

template:
    name: template_name
EOF
    regex_check='{.*"rules": \["rpm_verify_permissions"\].*"bash": "True".*"ansible": "True".*}'

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if ! grep -q "$regex_check" "$tmp_file"; then
        echo "$regex_check not found in: " && cat "$tmp_file"
        return 1
    fi
}

@test "Add unknown section" {
    file="linux_os/guide/system/software/integrity/software-integrity/rpm_verification/rpm_verify_permissions/rule.yml"
    cat > "$file" << EOF

unknown_section: unknown section
EOF

    git add "$file" && git commit -m "test commit" &>/dev/null

    python3 $BATS_TEST_DIRNAME/../content_test_filtering.py branch --output json --local --repository "$repo_dir" test_branch &> "$tmp_file"

    [ "$?" -eq 0 ]

    if [ -s "$tmp_file" ]; then
        echo "Output is not empty" && cat "$tmp_file"
        return 1
    fi
}
