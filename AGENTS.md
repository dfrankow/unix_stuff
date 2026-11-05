# Agent notes for unix_stuff

This repo is public. Write "the user" rather than anyone's name, and keep
private details (paths with a username, hosts, other projects) out of it.

## Committing

This repo commits directly to `main`. The pre-commit hook `no-commit-to-branch`
blocks that, so skip it explicitly:

```
SKIP=no-commit-to-branch git commit ...
```
