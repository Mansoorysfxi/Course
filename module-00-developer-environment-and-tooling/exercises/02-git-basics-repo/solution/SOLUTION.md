# Reference Solution — Git Basics Repo

Don't read this until you've made a genuine attempt.

```bash
mkdir ~/recipe-box
cd ~/recipe-box
git init
git branch                     # confirm "* main"

echo "# Recipe Box" > README.md
echo "" >> README.md
echo "A small collection of my favorite (fake) recipes." >> README.md
git add README.md
git commit -m "Add project README"

cat > pancakes.md << 'EOF'
# Pancakes

## Ingredients
- 1 cup flour
- 1 egg
- 1 cup milk
- 1 tbsp sugar

## Steps
1. Mix everything together.
2. Cook on a hot pan until golden on both sides.
EOF
git add pancakes.md
git commit -m "Add pancakes recipe"

echo "reminder: buy more flour" > notes-to-self.log

cat > .gitignore << 'EOF'
*.log
EOF
git status                     # notes-to-self.log should NOT appear
git add .gitignore
git commit -m "Add .gitignore for scratch log files"

cat >> pancakes.md << 'EOF'

## Tip
Let the batter rest for 5 minutes before cooking for fluffier pancakes.
EOF
git diff                       # read this before staging
git add pancakes.md
git commit -m "Add resting-time tip to pancakes recipe"

git log --oneline
```

**Expected `git log --oneline` shape** (your hashes will differ):
```
d4e5f6a Add resting-time tip to pancakes recipe
c3d4e5f Add .gitignore for scratch log files
b2c3d4e Add pancakes recipe
a1b2c3d Add project README
```

## Notes on grading this yourself before asking for review

- The critical check is that `notes-to-self.log` was **never staged**. If
  you ran `git add .` at any point *before* creating `.gitignore`, the log
  file would have been staged already, and `.gitignore` alone wouldn't
  un-stage it — you'd need `git restore --staged notes-to-self.log` too.
  Order of operations matters here, which is the actual point of the
  exercise.
- Four commits, each doing one coherent thing, is the other main check.
  If you bundled `.gitignore` into the pancakes commit, that's a real
  (if minor) issue: it makes the history harder to read and makes it
  unclear later *why* the `.gitignore` change happened, disconnected from
  the recipe content.
