---
name: game-dev-work-orders
description: Run a game project like a studio with an AI agent - audit the game with measurements, turn findings into numbered work orders with acceptance tests, fix them in batches, verify in the editor with numbers, keep a worklog and an owner-decisions list, and build once per batch. Use whenever the user says "find all the bugs", "what is wrong with my game", "make it production quality", "plan the next steps", "the game feels off / laggy / unfair", wants a QA pass or playtest plan, or a long project needs structure so work does not get lost between sessions.
---

# Work orders: audit, measure, fix, verify

Long game projects fail from lost context and unverified fixes, not from hard code. This is
the loop that kept a large project on track across many sessions.

## The documents (in `Docs/Handoff/`)

| File | Purpose |
|---|---|
| `00_READ_FIRST.md` | What the game is, how to run it, where things are, the rules. Every new session reads it first. |
| `NN_<AREA>.md` | One file per audit round or area (AI, UI, audio, performance, story). Findings + work orders. |
| `WORKLOG.md` | One dated line per finished work order: what changed, the evidence, the commit. |
| `OWNER_DECISIONS.md` | Questions only the owner can answer (scope, taste, money). The agent never decides these silently. |
| `V1_CHECKLIST.md` | What must be true to call version 1 done. |

Templates: `references/templates.md`.

## The loop

1. **Audit with numbers.** Play-test through the editor bridge and *measure*: frame times,
   distances, how often a door hits the player, how long a robot is stuck, how many objectives
   complete in a full run. "Feels laggy" becomes "median frame 24 ms, spikes to 90 ms when
   room X loads".
2. **Research when the answer is not obvious.** Look at how 5-10 shipped games solve the same
   problem and write the pattern down with sources.
3. **Write work orders.** One per problem: id (`WO-A3`), the finding with its number, the fix,
   the files, and an **acceptance test** that is a measurement ("0 of 120 robot door opens hit
   the player", "objective 7 completes in 10 of 10 runs").
4. **Fix in a batch.** Several work orders, editor only. After each, run its acceptance test.
5. **Regression pass.** Re-run the full playthrough or soak test; compare with the last numbers.
6. **Build once** at the end of the batch. Builds are slow; one per batch.
7. **Log it.** WORKLOG line + commit message with what and why.

## Rules

- A fix is not done until its acceptance number says so.
- Keep findings and fixes separate: write all findings first, then fix. You will find the
  real root cause behind several symptoms.
- Prefer root causes: one renderer feature missing its resources was the whole cause of a
  black screen; one off-main-thread callback was why a whole subsystem silently failed.
- Protect working code: list files a work order must NOT touch.
- When the user reports bugs, collect the whole list, then fix them in one batch.

## Bug report intake (from players or the owner)

For each report capture: what they did, what they expected, what happened, where (scene,
objective, position), how often. Reproduce it in the editor before fixing; if you cannot
reproduce it, add logging around it and say so.

> **Example (HOLD STILL):** 28 handoff files and a worklog carried the game from a prototype to
> a finished 4-act game across many sessions. Measured fixes included doors that swung into the
> player (60 of 120 robot opens, fixed to 0 of 120), an objective that never completed because
> two rooms' bounds overlapped, and a frame governor that locked fast devices to 30 fps because
> it measured during loading hitches (rewritten to use the median after a settle period).
