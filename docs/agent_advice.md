# General AI Coding Agent Advice (Project-Agnostic)

This file consolidates reusable guidance for AI coding agents (Claude, Codex, and others) across projects. Copy relevant sections into project-specific instruction files (e.g. `CLAUDE.md`, `AGENTS.md`) as needed.

## Writing (Comments, Docstrings, Docs)

### Comments
- **Don't leak implementation details** - a comment should not describe HOW something works internally, nor how a value happened to be produced. That belongs in the documentation comment, not scattered through the codebase. Same for a doc in `docs/`: say what to run and what judgment the reader brings, not a script's flags, prompts, or output - `--help` covers those
- **I prefer top-comments to side-comments**
- **Make comments timeless** - should still be relevant in six months, not likely to go stale. If a detail really is time-sensitive, date it explicitly ("June 2026: we reduced workers to 1 because...") so a future reader knows it may no longer apply.
- **Don't add comments with magic numbers that are likely to go out of date**
- **Default to writing no comments** - write one only when the WHY is non-obvious
- **Don't write task-specific comments** - write for tomorrow, not today
- **Don't refer to files unavailable from the repo you're in** - scratch notes outside git, `tmp/` files, or docs in another checkout. A path the reader can't open is dead weight; spell out the rule instead of pointing at it. This applies equally to a write-up meant as a public report, such as one attached to an issue tracker card; attach the underlying data files if reviewers need them. The rule is directional: an uncommitted doc may point at a committed one, never the reverse
- **Verify a "because" before writing it** - a reason that names other code is a claim about that code, so go read it first. Asserting that some downstream step needs a field, when nothing there reads it, is a reason invented to fill the slot. An unverified reason is worse than none, since a comment is exactly where a reader stops checking. Give the reason you can confirm, or none.
- **If one rewrite does not land, stop rewording** - a reader who still does not understand is missing a fact or has caught a false one, and the third phrasing of a wrong claim is still wrong. Ask what they think the sentence says, or go verify the claim.
- **Describe this code, not the rest of the system** - a comment explains what it sits near. Describing behavior that lives elsewhere means that code can change and nothing points back here to say the comment is now wrong. Narrative that ties parts together is sometimes worth writing, but it should be rare and belong somewhere central - a module docstring, a README - not scattered where it will silently rot.

### Documentation Comments (docstrings / Javadoc)
- **Don't reveal most internal implementation details** - the implementation might change
- **Write documentation that will still be relevant in a week** - leave out today's information if it's not relevant long-term
- **Say it once** - a constraint belongs in one canonical place, with everything else pointing there. The same hazard explained in a docstring, its mirror in another language, and the README is three copies to keep true.
- **When trimming, cut restatement, not facts** - the chatty pattern is fact → why it matters → dramatized consequence. Keep the fact, usually keep the why, always cut the third. Shortening by deleting the fact and keeping the framing makes the doc worse, not shorter.

### Phrasing
- **Explain why in the shape "X does Y so that Z"** - X is on the screen, Z is a good outcome. Not "a backbone that did not name itself would collide", which asks the reader to picture a system that does not exist. A sentence that will not fit the shape is one the writer does not understand yet. The usual failure is starting at Z: the fact about the world arrives first and the reader has to work back to which line it describes.
- **When a filter picks one value, say why not the adjacent one** - a reader who sees one enum value named asks why the neighbour was not, and rewording the first half never reaches that question.
- **Favor positive phrasing over negative** - it reads faster. "Skips annotations that label a whole video", not "does not include annotations that lack frame bounds".

## Communication Style

### Word Choice
- **Never say "breakthrough"** - none of your results are breakthroughs
- **Prefer full terms over abbreviations** - "leave-one-session-out" over "LOSO"

### Output
- **Responses should be short and concise**
- **Don't overpromise** - narrowing is not solving

## General Code Style (Language-Independent)

### Variable Naming
- **Avoid one-letter variable names** - prefer "err" instead of "e", "idx" instead of "i", "jdx" instead of j

### Function Design
- **No default parameters** - Defaults belong at the outer layer (argparse, config files) where they're visible and easily changed. Inner functions receive explicit values. If one is genuinely wanted (dependency injection for tests, say), raise it rather than adding it quietly.
- **Type-hint arguments and return values**
- **Use as few return statements as possible** - Ideally 0 or 1
- **Avoid private members unless absolutely necessary** - propose plans to make public interfaces or new functions instead

### Interfaces
- **For computer-to-computer interfaces (APIs, functions), be intolerant** - it finds bugs more quickly

### Exception Handling
- **Avoid broad exceptions** - catching "except Exception" (or Java's `catch (Exception e)`) is almost always wrong. Just let exceptions raise so we can detect errors.
- **If we don't expect the code to fail, just let exceptions raise**
- **If there is an expected exception case, do an if check if possible**
- **If not, use a narrower exception class**

### Assertions
- **If you always expect something to be true due to code structure, assert it** rather than if-check it

### Data Sources
- **No fallback to a less reliable source unless we agree it's worthwhile** - prefer no data over bad data. A silent fallback looks like a normal answer, so stale or guessed values pass unnoticed. Fail, or name the source in the output.

### Constants and Symbols
- **Use the symbol, not the constant** - If there is an enum or constant, don't copy its value, use the symbol. That helps tie code together.

## Code Organization Philosophy

**Less code is better:**
- Prefer an existing package, or an existing reusable function or class, to writing new code

**Splitting an over-long file:**
- Don't carve off a small chunk to squeak under a limit — find a seam that halves the file and split there
- Do it as its own PR with no functionality changes, so it reviews as a pure move

**Favor leaner code:**
- Less task-specific comments and prints
- Write for tomorrow, not just today's task
- You have a tendency to write too much code that's too specific to the current moment
- Keep functions and modules focused on their core responsibility
- **Favor simplicity over backward compatibility** when you control the entire codebase and there are no external clients depending on it

## Python-Specific Style

### Function Calls
- **Calling with named parameters is okay** - we can still catch missing parameters

### Imports
- **All imports at the top of the file** - never use inline imports inside functions or methods, even in tests
- **Don't manually remove unused imports** - ruff handles this automatically

### Other
- **Never modify sys.path** - assume PYTHONPATH is set correctly
- **Don't use `from __future__ import annotations`** unless the project is on Python < 3.12 and you actually need it

## Django-Specific

### Development
- **Minimal JavaScript**: Absolute bare minimum. Prefer server-side solutions.
- **When JS needed**: Use htmx first, custom JavaScript only as last resort.
- **Architecture**: Server-side rendering, standard HTML forms, progressive enhancement.

## Java-Specific Style

*(no conventions recorded yet - add here as they come up)*

## Linting and Code Quality

### General Principle
- **Never disable a linter check** (ruff, pylint, checkstyle, eslint, etc.) **without discussion** - prefer fixing the underlying issue
- **Don't add suppression comments** (`# noqa`, `pylint: disable`, `@SuppressWarnings`, etc.) **without asking first**
- **If we decide to disable, add a BRIEF comment explaining why**
- **Don't silently suppress warnings** - they usually point to real issues

When a linter flags a problem, discuss whether to:
- Refactor (too many arguments → config object, variable shadowing → rename)
- Fix directly (missing `strict=` in zip → add it)
- Suppress with justification (rare cases where the rule doesn't apply)

### Python (Ruff/Pylint)
- **Don't waste time eliminating extra imports** - ruff will take care of them
- **Run ruff**: `pre-commit run ruff-check --all-files`
- **Run all pre-commit hooks**: `pre-commit run --all-files`
- **Don't run `pre-commit` by hand** - committing runs it
- **Run the tests once, straight after committing** - amend if they fail, which is the uncommon case

## Testing

### TDD Approach
**Red/Green TDD for bug fixes and features:**
1. **RED**: Write failing tests first that capture the expected behavior
2. **GREEN**: Write minimal code to make tests pass
3. **REFACTOR**: Clean up code while keeping tests green

This prevents regressions and ensures fixes actually work.

### Python/Django Test File Naming
**Unit tests mirror source directory structure:**
- Source file: `bar/foo.py`
- Test file: `tests/bar/test_foo.py`

Examples:
- `evaluation/metrics.py` → `tests/evaluation/test_metrics.py`
- `app/foo.py` → `app/tests/test_foo.py` (Django convention)
- `classifiers.py` → `tests/test_classifiers.py`

## Git

- I almost always squash-merge to main in my projects, with only occasional exceptions if I want to preserve history of a long branch.

### Commit Messages
- **No "Co-Authored-By" or "Generated with" or Claude icon** - it's like an ad

### Repository State
- **Ask git before saying what is pushed, merged, committed or still uncommitted** - `git ls-remote`, `git status`, `git log`. A summary or an earlier turn says what was true then, and someone else may have committed since

### Committing
- **Never git commit files without asking me first**
- **Never use `git --no-verify`** - don't skip hooks without explicit request
- **Never skip hooks or bypass signing** unless explicitly asked
- **Try to create new commits rather than amending** unless explicitly requested
- **Before destructive operations, consider safer alternatives**

### File Operations
- **Never `git add .` or `git add -A`** - it sweeps up junk. Name the files you want.
- **`git add` new files as soon as you create them** - don't wait until commit time
- **If you change the name of a file, use `git mv`**
- **Don't remove the executable bit from scripts**
- **Never use `git rm` on `.idea/`, `.vscode/`, or similar IDE dirs**
- **Large datasets belong in Git LFS**, under a dedicated directory (e.g. `data/`)

## Shell and Environment

- **Change files with the Edit/Write tools, never through the shell** (`sed`, heredocs, inline `python`), whatever the current mode says - a scripted edit shows only its own source, not the resulting diff, so a replacement that matches too much or too little lands unreviewed
- **No "timeout" command on macOS** - it doesn't exist
- **Put temporary files in `tmp/DATE`** where DATE is MMDD or YYYYMMDD
- **If a debugging tool will be generally useful, put it in `bin/`**
- **You can use `jq` to parse JSON or NDJSON**

**If giving a command to run that is more than one line, put it in a file** - copying and pasting from the CLI has weird spacing issues (indented at least 2 spaces, sometimes picks up spaces after lines).
