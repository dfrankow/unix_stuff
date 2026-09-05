# Guardrails for coding agents (Claude Code, Codex, ...). Source from .bashrc
# and .zshrc.
#
# THIS FILE MUST WORK UNDER BOTH BASH AND ZSH, and is worth keeping that way:
# one file means a guard added on the zsh laptops also protects the bash one.
# Two divergences to write around, both of which have already caused silent
# breakage here:
#
#   - [[ "$x" =~ "pat" ]] means different things. zsh reads a quoted right-hand
#     side as a regex, bash as a literal string, so a quoted pattern silently
#     never matches under bash - no error, just no protection. Put the pattern
#     in a variable and leave that variable unquoted: [[ "$x" =~ $pat ]].
#   - Prefer `case` with globs over `=~` whenever a glob will do.
#
# Both shells here are old (bash 3.2 ships with macOS), so stick to what 3.2
# has: no associative arrays, no ${var^^}.
#
# .agent.checks.test.sh tests this file under both shells. Run it after edits.

# Forbidden words in git commit messages - meaningless marketing babble
FORBIDDEN_COMMIT_WORDS=(
    "comprehensive"
    "robust"
    "seamless"
    "leverage"
    "synergy"
    "paradigm"
    "holistic"
    "cutting-edge"
    "state-of-the-art"
    "enterprise-grade"
    "noreply@anthropic.com"
)

# TODO: Fix commit message checking - currently broken with complex quoting
# check_commit_message() {
#     local commit_msg="$1"
#     local forbidden_found=()
#
#     for word in "${FORBIDDEN_COMMIT_WORDS[@]}"; do
#         if echo "$commit_msg" | grep -iq "$word"; then
#             forbidden_found+=("$word")
#         fi
#     done
#
#     if [ ${#forbidden_found[@]} -gt 0 ]; then
#         echo "🚫 BLOCKED: Commit message contains forbidden marketing babble:"
#         printf "   - %s\n" "${forbidden_found[@]}"
#         echo ""
#         echo "Please use clear, specific language instead."
#         return 1
#     fi
#
#     return 0
# }

# Helper names here avoid a leading underscore so that coding agents get the
# guards too: Claude Code replays a snapshot of these functions in each of its
# shells, and it drops names starting with '_' as zsh completion functions. A
# helper it drops still parses at the call site below, so the guard fails open -
# it prints "command not found" and skips the check.
#
# Succeed when a git command creates a branch, printing the start point it would
# branch from (empty means from HEAD). Fails when the command creates nothing.
# 'git branch <name> <start>' creates one without any flag, so the positional
# count decides that case.
agent_branch_start_point() {
    local subcommand="$1"
    shift
    local making_branch=false
    local positional=0
    local start_point=""

    for arg in "$@"; do
        case "$arg" in
            -b|-B|-c|-C) making_branch=true ;;
            -*) ;;
            *)
                positional=$((positional + 1))
                [ "$positional" -ge 2 ] && start_point="$arg"
                ;;
        esac
    done

    [ "$subcommand" = "branch" ] && [ "$positional" -ge 2 ] && making_branch=true
    [ "$making_branch" = "true" ] || return 1

    echo "$start_point"
}

# Branching from a remote-tracking ref sets the new branch's upstream to it, so a
# later bare 'git push' targets that remote branch. Git's own suggested fix for
# the resulting name mismatch pushes straight to main.
agent_reject_remote_start_point() {
    local start_point="$1"
    # Unquoted below on purpose; see the bash/zsh note at the top of the file.
    local remote_main_re='^[A-Za-z0-9._-]+/(main|master)$'

    if [[ "$start_point" =~ $remote_main_re ]]; then
        echo "🚫 BLOCKED: never branch from '$start_point'"
        echo "   Pull ${start_point#*/} from ${start_point%%/*} and branch locally:"
        echo "     git switch ${start_point#*/} && git pull && git switch -c <name>"
        echo ""
        echo "   Branching from $start_point sets the new branch's upstream to it,"
        echo "   so a later bare 'git push' targets ${start_point#*/}."
        return 1
    fi

    return 0
}

# The reason to reach for origin/main is that local main goes stale, so a stale
# base has to be caught too, or forbidding the remote ref just trades one bug for
# another. An empty start point means branching from HEAD, which is checked too.
agent_reject_stale_start_point() {
    local base="${1:-HEAD}"

    if [ "$base" = "HEAD" ]; then
        base=$(command git symbolic-ref --quiet --short HEAD 2>/dev/null) || return 0
    fi

    local upstream behind
    upstream=$(command git rev-parse --abbrev-ref "$base@{upstream}" 2>/dev/null) || return 0
    [ -z "$upstream" ] && return 0

    behind=$(command git rev-list --count "$base..$upstream" 2>/dev/null)
    if [ -n "$behind" ] && [ "$behind" != "0" ]; then
        echo "🚫 BLOCKED: local $base is $behind commit(s) behind $upstream"
        echo "   Update it first, then branch:"
        echo "     git switch $base && git pull && git switch -c <name>"
        echo ""
        echo "   (Counted against the last fetch; run 'git fetch' if that is old.)"
        return 1
    fi

    return 0
}

git() {
    # Check for --no-verify flag anywhere in arguments
    for arg in "$@"; do
        if [ "$arg" = "--no-verify" ]; then
            echo "🚫 BLOCKED: --no-verify flag not allowed"
            echo "   From CLAUDE.md: Never use git --no-verify"
            return 1
        fi
    done

    # Block uncontrolled git add - THIS IS CRITICAL. Every argument is checked,
    # not just the first, so 'git add foo .' is caught too.
    # Allows: git add -u (tracked files only) and specific paths.
    if [ "$1" = "add" ]; then
        for arg in "$@"; do
            case "$arg" in
                .|-A|--all)
                    echo "🚫 BLOCKED: Use specific file paths with 'git add', not '$arg'"
                    echo "   Example: git add file1.py file2.py"
                    echo "   From CLAUDE.md: NEVER git add directories (or 'git add .' or 'git add -A')"
                    echo "   Note: 'git add -u' is allowed (updates tracked files only)"
                    return 1
                    ;;
            esac
        done
    fi

    # Branch creation has to start from an up-to-date local branch, never from a
    # remote-tracking ref.
    if [ "$1" = "checkout" ] || [ "$1" = "switch" ] || [ "$1" = "branch" ]; then
        local start_point
        if start_point=$(agent_branch_start_point "$@"); then
            agent_reject_remote_start_point "$start_point" || return 1
            agent_reject_stale_start_point "$start_point" || return 1
        fi
    fi

    # Block git rm on IDE directories unless using --cached
    if [ "$1" = "rm" ]; then
        local has_cached=false
        for arg in "$@"; do
            if [ "$arg" = "--cached" ]; then
                has_cached=true
                break
            fi
        done

        if [ "$has_cached" = "false" ]; then
            for arg in "$@"; do
                case "$arg" in
                    *.idea*|*.vscode*|*.vs/*)
                        echo "🚫 BLOCKED: Use 'git rm --cached' for IDE directories like '$arg'"
                        echo "   From CLAUDE.md: Never git rm on .idea/, .vscode/, or similar IDE dirs"
                        return 1
                        ;;
                esac
            done
        fi
    fi

    # Block git push for agents, allow silently for interactive users
    if [ "$1" = "push" ]; then
        if [ ! -t 0 ] || [ ! -t 1 ]; then
            # No interactive terminal (likely an agent or a script)
            echo "🚫 BLOCKED: git push not allowed in non-interactive context (likely an agent)"
            echo "   If you're a human user, run this command directly in your terminal"
            return 1
        fi
        # Interactive terminal - allow silently
    fi

    # TODO: Re-enable commit message checking once quote parsing is fixed
    # if [ "$1" = "commit" ]; then
    #     # Complex parsing here was causing shell substitution errors
    # fi

    command git "$@"
}

# Prevent pip install without -r (installing random packages)
pip() {
    if [ "$1" = "install" ]; then
        local has_requirements=false
        for arg in "$@"; do
            if [ "$arg" = "-r" ]; then
                has_requirements=true
                break
            fi
        done

        if [ "$has_requirements" = "false" ]; then
            echo "🚫 BLOCKED: Use 'pip install -r requirements.txt' instead of installing individual packages"
            echo "   This prevents installing random packages and ensures consistent environments"
            echo "   If you need a new package, add it to requirements.in and run pip-compile"
            return 1
        fi
    fi

    command pip "$@"
}

# Redirect ruff commands to pre-commit if ruff isn't installed
if ! command -v ruff >/dev/null 2>&1; then
    ruff() {
        echo "🔄 REDIRECTING: ruff -> pre-commit run ruff-check --all-files"
        echo "   From CLAUDE.md: it's installed as pre-commit ruff-check"

        # Handle common ruff commands
        case "$1" in
            "check")
                shift
                pre-commit run ruff-check --all-files "$@"
                ;;
            "format")
                shift
                pre-commit run ruff-format --all-files "$@"
                ;;
            "--fix"|"--check"|"--select"|"--ignore")
                # Common ruff check flags - redirect to ruff-check with --all-files
                pre-commit run ruff-check --all-files "$@"
                ;;
            "")
                # No arguments - default to check all files
                pre-commit run ruff-check --all-files
                ;;
            *)
                # Any other arguments - try ruff-check on all files
                pre-commit run ruff-check --all-files "$@"
                ;;
        esac
    }
fi
