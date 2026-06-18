# Kingdom-Loop Project

This project exists to execute **kingdom-loop.md** — a self-paced compound-engineering
loop that builds a text-based fantasy-kingdom management game.

## How to run
The user will paste/run the contents of `kingdom-loop.md`. Treat that file as the task.
It is the authoritative source for the goal, the artifact set, the loop rules, and the
exit conditions — follow it; do not re-derive or override it.

## Operating mode for this project
- **Autonomous loop.** Run cycle after cycle without waiting for the user between cycles.
  Only stop on the exit conditions in kingdom-loop.md, or the "same failing test 3 cycles"
  stuck-clause, or an explicit user interruption.
- **Self-contained, always.** No network calls, no APIs, no external datasets — ever.
  All game content is procedurally generated. This is a hard constraint, not a preference.
- **Stack:** pick ONE simple, zero-dependency stack and stick with it (Python stdlib is a
  fine default on this Windows machine). The self-play harness must run with one command.
- **The artifacts ARE the memory:** spec.md / architecture.md / tasks.md / test_plan.md /
  ux_review.md / lessons_learned.md. Keep them current every cycle — a fresh session must be
  able to resume from them alone.

## Environment
- Working dir: the repository root.
- Developed on Windows 11 (PowerShell primary; Bash available for POSIX scripts),
  but the game is pure Python 3 stdlib and runs anywhere.
