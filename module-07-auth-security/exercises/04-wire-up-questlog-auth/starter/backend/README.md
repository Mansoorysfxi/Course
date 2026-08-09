# Exercise 04 starter — QuestLog backend, WITHOUT real auth

This is Module 06's finished QuestLog backend, copied here unchanged
(same routes, same `DEFAULT_USER_EMAIL`-owned quests, same lack of any
password or JWT anywhere) so you can independently build the exact same
auth system the real `project/questlog/backend/` already has, **before**
looking at how the course built it.

See [`../INSTRUCTIONS.md`](../../INSTRUCTIONS.md) for the full task,
acceptance criteria, and hints. Do not read
`module-07-auth-security/project/questlog/backend/` until you've made a
real attempt — that folder **is** the reference solution for this
exercise, wired into the real running project.

Quick reminder of what's already true about this code, unchanged from
Module 06: three tables (`users`, `quest_lines`, `quests`), every quest
has a `nullable=False` `owner_id` foreign key already, but every quest
created via `POST /api/quests` is silently assigned to one seeded
`player@questlog.local` user (`app/repository.py`'s
`_get_default_owner_id`) — there is no password, no login, and no route
in this file tree checks who's asking at all.
