# Templates

## 00_READ_FIRST.md

```markdown
# <GAME> - read first

**What it is:** <one paragraph: genre, core verb, place, length>
**Engine / version:** <Unity 6000.x, URP>   **Run:** open <scene>, press Play
**Where things are:** Scripts/<...>, Art/<...>, Audio/<...>, Docs/Handoff/<...>
**Rules:** measure before fixing; batch fixes, build once; every asset in Docs/ASSET_LICENSES.md;
do not edit <protected files> without an owner decision.
**Current state:** <what works, what is next, link to the latest audit file>
```

## A work order

```markdown
### WO-D2  Doors swing into the player when a robot opens them

**Finding (measured):** 60 of 120 scripted robot door opens swung toward a player standing
within 2 m (test: DoorSwingProbe, 120 random positions).
**Cause:** robot opens use the default swing side; only player opens use "away from opener".
**Fix:** when the player is within 4 m, swing away from the player regardless of the opener.
**Files:** Scripts/World/Door.cs (ResolveSwing). Do NOT touch: AI/RobotDoorOpener.cs.
**Acceptance:** DoorSwingProbe: 0 of 120 opens toward the player; player opens still 130/130 away.
**Status:** open / fixed (commit abc123) / verified
```

## WORKLOG.md line

```markdown
2026-11-19  WO-D2 fixed: robot opens swing away from a nearby player. Probe 0/120 (was 60/120). abc123
```

## OWNER_DECISIONS.md entry

```markdown
- [ ] D-7  Low crates: should the player be able to step onto 0.4 m crates? (step height is 0.42 m;
  yes = easier escapes, no = crates are real obstacles). Recommendation: no. Needs: owner.
```

## Bug list from a playtest

| # | What I did | Expected | Happened | Where | How often |
|---|---|---|---|---|---|
| 1 | tapped HINT | map opens with the hint | nothing | act 2, lab | always |
