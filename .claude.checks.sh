# Claude Code helper functions and redirects
# Only redirect commands if the actual tools aren't available

# Redirect ruff commands to pre-commit if ruff isn't installed
if ! command -v ruff &> /dev/null; then
    ruff() {
        echo "🔄 REDIRECTING: ruff -> pre-commit run ruff-check --all-files"
        echo "   From CLAUDE.md: 'it's installed as \"pre-commit ruff-check\"'"

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
