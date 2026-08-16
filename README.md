unix_stuff
==========

Unix stuff I carry from one place to the next


Agent guardrails
----------------

`.agent.checks.sh` wraps `git` and `pip` to stop coding agents from doing
things that are hard to undo (`git add .`, `--no-verify`, pushing, branching
from a stale or remote-tracking ref). Source it from `.bashrc` and `.zshrc`:

```
source ~/.agent.checks.sh
```

It has to keep working under both shells, so run the tests after editing it:

```
$ ./.agent.checks.test.sh
```


For django command-line completion:

```
$ wget -O ~/.django_bash_completion.sh https://raw.github.com/django/django/master/extras/django_bash_completion
```

See

- https://codingpub.dev/ubuntu-django-bash-auto-completion/
- https://docs.djangoproject.com/en/dev/ref/django-admin/#bash-completion
