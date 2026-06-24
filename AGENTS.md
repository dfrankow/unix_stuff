# Agent notes for unix_stuff

## Committing

This repo commits directly to `main`. The pre-commit hook `no-commit-to-branch`
blocks that, so skip it explicitly:

```
SKIP=no-commit-to-branch git commit ...
```
