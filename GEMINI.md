# Gemini Instructions

When working in this repository, please follow these instructions:

- This project uses `hatch` to manage dependencies and run tasks.
- Before any change, please validate that the following checks are not broken.
- To run tests, use the command: `hatch run test:check`.
- To run type checks, use the command: `hatch run types:check`.
- To run formatting checks, use the command: `hatch run fmt:check`.
- To automatically fix formatting issues, use the command: `hatch run fmt:fmt`.
- Always run the autoformatter (`hatch run fmt:fmt`) before committing your changes.

# Git Best Practices

- Avoid amending commits that have already been pushed to a remote branch, as this rewrites history and can cause issues for collaborators. If you must amend a pushed commit, use `git push --force-with-lease` with caution.
- Always pull after switching to the `master` branch.
- Always open a pull request instead of pushing to `master` directly.
