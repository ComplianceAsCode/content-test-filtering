#!/bin/bash

function prepare_repository() {
        if [[ -z "$repo_dir" ]]; then
            repo_dir="$(mktemp -d)"
            git clone https://github.com/ComplianceAsCode/content/ "$repo_dir"
        fi

        cd "$repo_dir"
        git checkout master &>/dev/null
        git checkout -B test_branch &>/dev/null

        export repo_dir
}

function clean_up() {
        cd "$repo_dir"
        git reset --hard master
}

function setup() {
        tmp_file="$(mktemp)"
        no_test_regex="Recommended tests to execute"
}

function teardown() {
        clean_up
}
