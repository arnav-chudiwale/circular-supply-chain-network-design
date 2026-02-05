# Safe daily git workflow (run in repo root - PowerShell / Git Bash / WSL)

# 1) See what changed
git status

# 2) Stage changes
# - interactive (recommended):
git add -p
# - or stage everything:
git add .

# 3) Commit with a clear message
# Short summary (50 chars max), blank line, optional body.
# Examples:
git commit -m "feat(module): add route-visualization"
# OR multi-line:
git commit -m "fix(vrp): handle empty routes" -m "Avoid KeyError when no vehicles are used."

# 4) Integrate remote updates (safe rebase)
git fetch origin
git rebase origin/main
# If conflicts occur:
#  - edit files to resolve
git add <fixed-files>
git rebase --continue

# Alternative (merge) if you prefer:
# git pull origin main
# resolve conflicts, commit

# 5) Push your commits
git push origin main

# 6) Quick verification
git status
git log --oneline -5

# Helpers / edge cases
# If you're mid-work and not ready to commit:
git stash push -m "WIP: short note"
# After pull/rebase:
git stash pop

# Inspect remote/local divergence if needed:
git fetch origin
git log --oneline HEAD..origin/main   # commits on remote not local
git log --oneline origin/main..HEAD   # local commits not on remote
```// filepath: c:\Users\Arnav\Desktop\last_mile_delivery\Git Commit Reference Card.sh
# Safe daily git workflow (run in repo root - PowerShell / Git Bash / WSL)

# 1) See what changed
git status

# 2) Stage changes
# - interactive (recommended):
git add -p
# - or stage everything:
git add .

# 3) Commit with a clear message
# Short summary (50 chars max), blank line, optional body.
# Examples:
git commit -m "feat(module): add route-visualization"
# OR multi-line:
git commit -m "fix(vrp): handle empty routes" -m "Avoid KeyError when no vehicles are used."

# 4) Integrate remote updates (safe rebase)
git fetch origin
git rebase origin/main
# If conflicts occur:
#  - edit files to resolve
git add <fixed-files>
git rebase --continue

# Alternative (merge) if you prefer:
# git pull origin main
# resolve conflicts, commit

# 5) Push your commits
git push origin main

# 6) Quick verification
git status
git log --oneline -5

# Helpers / edge cases
# If you're mid-work and not ready to commit:
git stash push -m "WIP: short note"
# After pull/rebase:
git stash pop

# Inspect remote/local divergence if needed:
git fetch origin
git log --oneline HEAD..origin/main   # commits on remote not local
git log --oneline origin/main..HEAD   # local commits not on remote