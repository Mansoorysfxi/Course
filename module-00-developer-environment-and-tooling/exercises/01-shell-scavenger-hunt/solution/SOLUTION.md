# Reference Solution — Shell Scavenger Hunt

Don't read this until you've made a genuine attempt and either finished or
are stuck after checking the hints in `INSTRUCTIONS.md`. There is more than
one valid set of commands for several steps — this is *a* correct solution,
not *the only* correct one.

```bash
# 1. Confirm current location
pwd

# 2. Three subfolders in one command
mkdir alpha beta gamma

# 3. Empty file
touch alpha/treasure.txt

# 4. Write first line (overwrite/create)
echo "X marks the spot" > alpha/treasure.txt

# 5. Append second line
echo "Found by: Mansoor" >> alpha/treasure.txt

# 6. Print contents
cat alpha/treasure.txt

# 7. Copy into beta, same name
cp alpha/treasure.txt beta/treasure.txt

# 8. Rename the copy inside beta
mv beta/treasure.txt beta/clue.txt

# 9. Four empty files in gamma
touch gamma/a.log gamma/b.log gamma/c.txt gamma/d.txt

# 10. List only .log files in gamma
ls gamma/*.log

# 11. Delete both .log files with one wildcard command
rm gamma/*.log

# 12. Print HOME
echo $HOME

# 13. Count top-level entries
ls -la | wc -l

# 14. Create then delete a folder in one command each
mkdir temporary-junk
touch temporary-junk/scratch.txt
rm -r temporary-junk
```

## Notes on grading this yourself before asking for review

- Step 11 must be **one** `rm` command using `*.log`, not `rm gamma/a.log`
  followed by `rm gamma/b.log`. If you did two separate commands, that's a
  correctness gap against the acceptance criteria (it works, but it doesn't
  demonstrate the wildcard concept the exercise is checking).
- Step 13's exact count depends on whether `alpha`, `beta`, `gamma` still
  have trailing folders etc. — the number itself isn't graded, the fact
  that you correctly piped `ls -la` into `wc -l` is.
- If `cat alpha/treasure.txt` in Step 6 shows only one line, the most common
  cause is using `>` instead of `>>` in Step 5, which overwrote line one
  instead of adding a second line — this is exactly the mistake called out
  in Lesson 01's "Try it yourself" for `>` vs `>>`.
