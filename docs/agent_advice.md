# General AI Coding Agent Advice (Project-Agnostic)

This file is shared across machines as general advice for all agents. Python and
Django advice lives in `agent_advice_python.md`, which loads only for those
files.

## Writing (Comments, Docstrings, Docs)

### Comments

- **Don't leak implementation details** - a comment or docstring says what the
  code does and why, not how it works internally or how a value happened to be
  produced, so that it stays true when the implementation changes. Same for a
  doc in `docs/`: say what to run and what judgment the reader brings, not a
  script's flags, prompts, or output - `--help` covers those
- **I prefer top-comments to side-comments**
- **A TODO starts with what to do** - `TODO: Skip X when Y.` first, then any
  background. A reader scanning TODOs wants the task, not a description of
  today's behavior they have to turn into one
- **Make comments and docs timeless** - a comment should still be relevant in
  six months. If a detail really is time-sensitive, date it explicitly ("June
  2026: we reduced workers to 1 because...")
- **Don't add comments with magic numbers that are likely to go out of date**
- **Default to writing no comments** - write one only when the WHY is
  non-obvious
- **Don't refer to files unavailable from the repo you're in** - scratch notes
  outside git, `tmp/` files, or docs in another checkout. Spell out the rule
  instead of pointing at it. This applies equally to a public write-up, such as
  one attached to an issue tracker card; attach the underlying data files if
  reviewers need them. The rule is directional: an uncommitted doc may point at
  a committed one, never the reverse
- **Verify a "because" before writing it** - a reason that names other code is a
  claim about that code, so go read it first. Asserting that some downstream
  step needs a field, when nothing there reads it, is a reason invented to fill
  the slot. A comment is exactly where a reader stops checking, so give the
  reason you can confirm, or none
- **If one rewrite does not land, stop rewording** - a reader who still does not
  understand is missing a fact or has caught a false one. Ask what they think
  the sentence says, or go verify the claim
- **Describe this code, not the rest of the system** - a comment explains what
  it sits near, so that when other code changes no comment here silently goes
  wrong. Narrative that ties parts together belongs somewhere central - a module
  docstring, a README - and should be rare

### Documentation Comments (docstrings / Javadoc)

- **Say it once** - a constraint belongs in one canonical place, with everything
  else pointing there. The same hazard explained in a docstring, its mirror in
  another language, and the README is three copies to keep true.
- **When trimming, cut restatement, not facts** - the chatty pattern is fact →
  why it matters → dramatized consequence. Keep the fact, usually keep the why,
  always cut the third. Shortening by deleting the fact and keeping the framing
  makes the doc worse, not shorter.
- **Lean away from history in docs, and keep them short** - you tend to add "was
  X until 11-13" and "we found that" where how things are now would do. Some
  past belongs, by judgment, such as a write-up's list of what was tried and
  isn't worth trying again; the rest goes in the commit or PR text. Prefer a
  one-line pointer to a new section, and when adding, look for something to cut

### Phrasing

- **Explain why in the shape "X does Y so that Z"** - X is on the screen, Z is a
  good outcome. Not "a backbone that did not name itself would collide", which
  asks the reader to picture a system that does not exist. A sentence that will
  not fit the shape is one the writer does not understand yet. The usual failure
  is starting at Z: the fact about the world arrives first and the reader has to
  work back to which line it describes.
- **When a filter picks one value, say why not the adjacent one** - a reader who
  sees one enum value named asks why the neighbour was not, and rewording the
  first half never reaches that question.
- **Favor positive phrasing over negative** - it reads faster. "Skips
  annotations that label a whole video", not "does not include annotations that
  lack frame bounds".

## Communication Style

- **Never say "breakthrough"** - none of your results are breakthroughs
- **Prefer full terms over abbreviations** - "leave-one-session-out" over "LOSO"
- **Responses should be short and concise**
- **Don't overpromise** - narrowing is not solving
- **Look before asserting the state of anything outside the conversation** -
  whether a command was run, a file exists, a result is current. Handing someone
  a command is not knowing they ran it, and an earlier turn says what was true
  then. For git state, see Repository State below
- **Never use Markdown blockquotes (`> `)** - the leading `> ` is selected along
  with the text and has to be stripped by hand. Anything meant to be copied - a
  prompt for another tool, a command, a config snippet, a message to send
  someone - goes in a fenced code block. Anything not meant to be copied is just
  prose.

## General Code Style (Language-Independent)

- **Avoid one-letter variable names** - "err" not "e", "idx" not "i", "jdx" not
  "j"
- **No default parameters** - Defaults belong at the outer layer (argparse,
  config files) where they're visible and easily changed. Inner functions
  receive explicit values. If one is genuinely wanted (dependency injection for
  tests, say), raise it rather than adding it quietly.
- **Type-hint arguments and return values**
- **Use as few return statements as possible** - Ideally 0 or 1
- **Avoid private members unless absolutely necessary** - propose plans to make
  public interfaces or new functions instead
- **For computer-to-computer interfaces (APIs, functions), be intolerant** - it
  finds bugs more quickly
- **Avoid broad exceptions** - catching "except Exception" (or Java's
  `catch (Exception e)`) is almost always wrong. If we don't expect the code to
  fail, let it raise so we can detect errors. For an expected failure, do an if
  check if possible, and otherwise catch a narrower exception class
- **If you always expect something to be true due to code structure, assert it**
  rather than if-check it
- **No fallback to a less reliable source unless we agree it's worthwhile** -
  prefer no data over bad data. A silent fallback looks like a normal answer, so
  stale or guessed values pass unnoticed. Fail, or name the source in the
  output.
- **Use the symbol, not the constant** - If there is an enum or constant, use
  the symbol rather than copying its value, so that the code stays tied together

## Code Organization

- **Less code is better** - you tend to write too much code that's too specific
  to the current moment. Prefer an existing package, function or class to new
  code, and keep functions and modules focused on their core responsibility
- **Favor simplicity over backward compatibility** when you control the entire
  codebase and there are no external clients depending on it
- **Split an over-long file at a seam that halves it** - not by carving off a
  small chunk to squeak under a limit. Do it as its own PR with no functionality
  changes, so it reviews as a pure move

## Linting and Code Quality

- **Never disable a linter check** (ruff, pylint, checkstyle, eslint, etc.) **or
  add a suppression comment** (`# noqa`, `pylint: disable`, `@SuppressWarnings`,
  etc.) **without discussion** - warnings usually point to real issues. If we
  decide to disable, add a BRIEF comment explaining why
- **Don't run `pre-commit` by hand** - committing runs it

When a linter flags a problem, discuss whether to:

- Refactor (too many arguments → config object, variable shadowing → rename)
- Fix directly (missing `strict=` in zip → add it)
- Suppress with justification (rare cases where the rule doesn't apply)

## Testing

### Run the suite once per finished change

Not after every edit. During TDD, run only the test you are writing; save the
full suite for the end. A run that started before your latest edit reports on
code that no longer exists, so its result is noise, and reacting to it pulls you
off the work in hand. Fix a failure in a follow-up commit; the pre-commit hooks
are the gate, so don't hold a commit for a test run.

### Never run tests in the foreground

**Run every test suite in the background, targeted runs included.** A foreground
run blocks the session for its whole duration with nothing to read, which wastes
my time.

- Assume the tests will pass. Keep working, or answer whatever question is open,
  while they run
- Report the result only if something failed
- Don't pause to announce that you're about to run them, and don't wait on them
  before continuing to the next thing
- Don't poll a backgrounded run (an `until grep ... done` loop over its output,
  say). Read the output when the task notification arrives

The same goes for any long-running command: builds, imports, data jobs, deploys.

**A run longer than a minute shows progress**, through tqdm or a log line per
step, so that I can tell how far along it is. Its output goes to a file I can
watch, never through `grep`, `tail`, `head` or another pipe that holds it back
until the end or replaces the command's exit code with the pipe's.

### TDD Approach

**Red/Green TDD for bug fixes and features:**

1. **RED**: Write failing tests first that capture the expected behavior
2. **GREEN**: Write minimal code to make tests pass
3. **REFACTOR**: Clean up code while keeping tests green

## Git

I almost always squash-merge to main in my projects, with only occasional
exceptions if I want to preserve history of a long branch.

### Commit Messages

- **No "Co-Authored-By" or "Generated with" or Claude icon** - it's like an ad

### Pull Requests

- **Start the description with the squash-merge message** - a title-sized
  summary and a few short bullets covering the whole PR, so that it can be
  pasted as the squash commit body. The description is the only copy: no
  separate squash-message file. When later commits change what the PR does,
  update that top section. Anything else (approaches tried and dropped,
  follow-ups) goes below a `---` line and stays short, so it stays out of git
  log
- **When the bottom of a PR stack merges, let GitHub retarget the next one** -
  it moves the next PR's base on its own, so don't edit the base by hand. It
  rebases the branch only sometimes: after `git fetch`, if
  `git log origin/<base>..origin/<branch>` still lists the merged PR's commits,
  merge the base into the branch so that the PR's diff shows only its own
  changes

### Repository State

- **Ask git before saying what is pushed, merged, committed or still
  uncommitted** - `git ls-remote`, `git status`, `git log`. A summary or an
  earlier turn says what was true then, and someone else may have committed
  since

### Committing

- **Never git commit files without asking me first**, unless the project's
  AGENTS.md allows it for some kinds of change (doc-only, say)
- **Never skip hooks (`git --no-verify`) or bypass signing** unless explicitly
  asked
- **Try to create new commits rather than amending** unless explicitly requested
- **Before destructive operations, consider safer alternatives**

### Pushing

- **Push after every commit, when you can** - don't stop to ask; the branch rule
  below still applies
- **Push your own branches; never main, master or dev** - a guard in
  `.agent.checks.sh` refuses an agent's push to any of those, so that they
  change only through a pull request or a person at a terminal. A session
  started before a change to the guard keeps the old one until it restarts

### File Operations

- **`git add` new files as soon as you create them** - don't wait until commit
  time
- **If you change the name of a file, use `git mv`**
- **Don't remove the executable bit from scripts**
- **Large datasets belong in Git LFS**, under a dedicated directory (e.g.
  `data/`)

## Shell and Environment

- **Change files with the Edit/Write tools, never through the shell** (`sed`,
  heredocs, inline `python`), whatever the current mode says - a scripted edit
  shows only its own source, not the resulting diff, so a replacement that
  matches too much or too little lands unreviewed
- **No "timeout" command on macOS** - it doesn't exist
- **Put temporary files in `tmp/DATE`** where DATE is MMDD or YYYYMMDD
- **If a debugging tool will be generally useful, put it in `bin/`**
- **You can use `jq` to parse JSON or NDJSON**
- **Put a command to run that is more than one line in a file** - pasting from
  the CLI picks up stray indentation and trailing spaces
