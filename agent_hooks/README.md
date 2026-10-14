# Agent hooks

Hooks for coding agents. Each script's header says what it does. Scripts must be
executable.

## Claude Code

Register them in `~/.claude/settings.json`, then run `/hooks` to confirm they loaded:

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {"type": "command", "command": "~/unix_stuff/agent_hooks/block-attribution"},
        {"type": "command", "command": "~/unix_stuff/agent_hooks/block-env-dump"},
        {"type": "command", "command": "~/unix_stuff/agent_hooks/block-remote-tracking-branch"}
      ]
    }
  ],
  "SessionStart": [
    {
      "matcher": "startup|resume|fork",
      "hooks": [
        {"type": "command", "command": "~/unix_stuff/agent_hooks/session-title"}
      ]
    }
  ]
}
```
