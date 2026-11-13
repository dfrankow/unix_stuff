# unix_stuff

Unix stuff I carry from one place to the next

## Agent guardrails

`.agent.checks.sh` wraps `git` and `pip` to stop coding agents from doing things
that are hard to undo (`git add .`, `--no-verify`, pushing, branching from a
stale or remote-tracking ref). Source it from `.bashrc` and `.zshrc`:

```
source ~/.agent.checks.sh
```

It has to keep working under both shells, so run the tests after editing it:

```
$ ./.agent.checks.test.sh
```

## Agent advice

`docs/agent_advice.md` holds instructions for every coding agent session; import
it from `~/.claude/CLAUDE.md` with `@~/unix_stuff/docs/agent_advice.md`.
`docs/agent_advice_python.md` is a Claude Code path-scoped rule, so that its
Python and Django advice loads only when an agent touches those files. Link it
into the user rules directory:

```
mkdir -p ~/.claude/rules && ln -s ~/unix_stuff/docs/agent_advice_python.md ~/.claude/rules/python.md
```

For django command-line completion:

```
$ wget -O ~/.django_bash_completion.sh https://raw.github.com/django/django/master/extras/django_bash_completion
```

See

- https://codingpub.dev/ubuntu-django-bash-auto-completion/
- https://docs.djangoproject.com/en/dev/ref/django-admin/#bash-completion
