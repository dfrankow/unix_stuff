#!/usr/bin/env bash
# Tests .agent.checks.sh under bash AND zsh, because the file has to keep
# working in both and the ways it can stop are silent ones. The quoted-regex
# divergence between the shells broke two guards with no error message at all;
# these tests exist so that stays caught.
#
# Usage:  ./.agent.checks.test.sh        run the suite under every shell
#         zsh .agent.checks.test.sh      run it under one shell only

set -u

checks_dir=$(cd "$(dirname "$0")" && pwd)
checks_file="$checks_dir/.agent.checks.sh"

# --- driver: re-run this script under each shell ------------------------------

if [ -z "${AGENT_CHECKS_INNER:-}" ]; then
    driver_status=0
    for shell_name in bash zsh; do
        if ! command -v "$shell_name" >/dev/null 2>&1; then
            echo "SKIP $shell_name (not installed)"
            continue
        fi
        echo "=== $shell_name ($("$shell_name" -c 'echo $BASH_VERSION$ZSH_VERSION') ) ==="
        AGENT_CHECKS_INNER=1 "$shell_name" "$0" || driver_status=1
    done
    exit "$driver_status"
fi

# --- assertions ---------------------------------------------------------------

passed=0
failed=0

ok() {
    passed=$((passed + 1))
    printf '  ok    %s\n' "$1"
}

bad() {
    failed=$((failed + 1))
    printf '  FAIL  %s\n' "$1"
    [ -n "${2:-}" ] && printf '        got: %s\n' "$2"
}

# The guard fired: nonzero exit AND our own message. Both matter - plain git
# failures are nonzero too, and a guard that prints without blocking is a bug.
expect_block() {
    local desc="$1"
    shift
    # Not named 'status': zsh reserves that as a read-only alias for $?.
    local out exit_code
    out=$("$@" 2>&1)
    exit_code=$?

    if [ "$exit_code" -eq 0 ]; then
        bad "$desc" "exit 0, expected a block"
    elif ! printf '%s' "$out" | grep -q 'BLOCKED'; then
        bad "$desc" "exit $exit_code but no BLOCKED message: $(printf '%s' "$out" | head -1)"
    else
        ok "$desc"
    fi
}

# The guard stayed out of the way. Deliberately does not require exit 0: git
# itself may reject the command for unrelated reasons, and that is not our
# concern here. What must not appear is our block.
refute_block() {
    local desc="$1"
    shift
    local out
    out=$("$@" 2>&1)

    if printf '%s' "$out" | grep -q 'BLOCKED'; then
        bad "$desc" "blocked, expected to pass through: $(printf '%s' "$out" | head -1)"
    else
        ok "$desc"
    fi
}

# --- fixtures -----------------------------------------------------------------

# A throwaway repo with a real 'origin', so the branch checks have an upstream
# to reason about. Prints the clone's path.
make_repo() {
    local root remote clone
    root=$(mktemp -d)
    remote="$root/remote.git"
    clone="$root/clone"

    command git init --quiet --bare -b main "$remote"
    command git clone --quiet "$remote" "$clone" 2>/dev/null

    command git -C "$clone" symbolic-ref HEAD refs/heads/main
    echo one > "$clone/file.txt"
    command git -C "$clone" add file.txt
    command git -C "$clone" commit --quiet -m "first"
    command git -C "$clone" push --quiet -u origin main 2>/dev/null

    echo "$clone"
}

# Push a commit to origin from a second clone, then fetch, leaving the first
# clone's local main behind its upstream.
age_repo() {
    local clone="$1"
    local remote second
    remote=$(command git -C "$clone" config remote.origin.url)
    second="$(dirname "$clone")/second"

    command git clone --quiet "$remote" "$second" 2>/dev/null
    echo two > "$second/file.txt"
    command git -C "$second" add file.txt
    command git -C "$second" commit --quiet -m "second"
    command git -C "$second" push --quiet origin main 2>/dev/null

    command git -C "$clone" fetch --quiet origin
}

export GIT_AUTHOR_NAME="Checks Test"
export GIT_AUTHOR_EMAIL="test@example.invalid"
export GIT_COMMITTER_NAME="Checks Test"
export GIT_COMMITTER_EMAIL="test@example.invalid"

# --- the suite ----------------------------------------------------------------

# shellcheck source=.agent.checks.sh
. "$checks_file"

repo=$(make_repo)
cd "$repo" || exit 1
echo untracked > extra.txt
mkdir -p .idea && echo junk > .idea/workspace.xml

echo "git add"
expect_block "git add ."            git add .
expect_block "git add -A"           git add -A
expect_block "git add --all"        git add --all
expect_block "git add extra.txt ."  git add extra.txt .
refute_block "git add -u"           git add -u
refute_block "git add extra.txt"    git add extra.txt
command git reset --quiet

echo "--no-verify"
expect_block "git commit --no-verify"  git commit --no-verify -m x
expect_block "git push --no-verify"    git push --no-verify

echo "git rm on IDE dirs"
expect_block "git rm .idea/workspace.xml"           git rm .idea/workspace.xml
refute_block "git rm --cached .idea/workspace.xml"  git rm --cached .idea/workspace.xml
refute_block "git rm file.txt"                      git rm --dry-run file.txt

echo "branch start point"
# The two that the quoted regex silently let through under bash.
expect_block "git switch -c x origin/main"    git switch -c x origin/main
expect_block "git checkout -b x origin/main"  git checkout -b x origin/main
expect_block "git branch x origin/main"       git branch x origin/main
refute_block "git switch -c x (from HEAD)"    git switch -c x
command git switch --quiet main
refute_block "git switch main (no branch made)"  git switch main

echo "stale start point"
age_repo "$repo"
expect_block "git switch -c y, main behind origin"  git switch -c y
refute_block "git status, main behind origin"       git status --short

echo "git push"
# The suite always runs without a tty, which is the case the guard is aimed at.
expect_block "git push (non-interactive)"  git push

echo "pip"
expect_block "pip install requests"           pip install requests
refute_block "pip install -r requirements"    pip install -r /dev/null

cd / || exit 1
rm -rf "$(dirname "$repo")"

printf '  %s passed, %s failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
