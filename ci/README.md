# CI templates

`github-workflows/` holds the GitHub Actions for the public mirror (schema validation +
Pages deploy on merge; weekly linkcheck that auto-opens issues). They live here instead of
`.github/workflows/` only because the current mirror token lacks the `workflow` scope —
after `gh auth refresh -h github.com -s workflow`, move them:

    git mv ci/github-workflows/*.yaml .github/workflows/ && git push

Until then: validation runs at the Gitea origin, and Pages deploys from the `gh-pages`
branch (built by `build/build.py`).
