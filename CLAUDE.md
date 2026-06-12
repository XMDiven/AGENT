# CLAUDE.md

Project-specific behavior rules for Claude Code. These OVERRIDE Claude's default behavior.

## Git commits & PRs — no AI attribution

- Do NOT add a `Co-Authored-By: Claude ...` trailer (or any Claude / AI co-author or
  co-contributor line) to commit messages. This is what makes Claude show up as a
  co-contributor on GitHub — never add it.
- Do NOT add "🤖 Generated with Claude Code", "Co-Authored-By: Claude", or any similar
  AI-attribution line to PR titles or PR bodies.
- Write commit messages and PR descriptions as the user's own work, with no AI authorship
  attribution of any kind.
- Everything else about commit messages (clear summary, conventional-commit style, etc.)
  stays as normal.
