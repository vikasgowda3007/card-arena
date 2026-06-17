---
description: Interview the player across multiple angles and write a personalised judging rubric to personal/requirements.md.
argument-hint: "[output path]  (optional, defaults to personal/requirements.md)"
allowed-tools: Task, AskUserQuestion, Read, Write
---

# /build-profile — build the player's rubric by interview

You run a short adaptive interview, then write a weighted rubric the judge can
use. A separate **`profile-interviewer`** subagent listens to every answer and
decides what to ask next — you only relay its questions to the human and feed it
back what they said. You never decide the questions yourself.

## Resolve inputs
- OUT = `${1:-personal/requirements.md}`  (gitignored by default — personal, never published)

## Seed from any existing profile (update, don't restart)
Before the loop, check whether `OUT` already exists. If it does, **read it** and
seed `ANSWERS_SO_FAR` with its contents under a header like
`EXISTING PROFILE (verify and update, do not re-ask what's already concrete):`,
followed by the file body verbatim. This makes the interviewer treat the saved
profile as already-gathered answers — it will only probe angles that are missing,
vague, or stale instead of re-interviewing from scratch, and it preserves the
existing weights unless the human changes something. If `OUT` does not exist,
`ANSWERS_SO_FAR` starts empty (a fresh interview).

## The loop
Keep a running transcript string `ANSWERS_SO_FAR` (seeded above; empty if no
existing profile).

Repeat, starting at ROUND=1 (hard stop after ROUND=5 to avoid loops):

1. **Ask the interviewer what to ask.** Spawn the listener:
   - Task → subagent `profile-interviewer`:
     `ROUND=<n>. ANSWERS_SO_FAR="""<transcript so far>"""`
2. **Read its STRICT JSON reply.**
   - If `status == "complete"` → break out of the loop, keep its `requirements_md`.
   - If `status == "need_more"` → take its `questions` array and put it straight
     into a SINGLE `AskUserQuestion` call (one entry per question, copy `header`,
     `question`, and `options`; the human may always pick "Other").
3. **Append** each question and the human's chosen/typed answer to
   `ANSWERS_SO_FAR`, then loop with ROUND+1.

The point: the interviewer is the brain deciding coverage; the command is just
the mouth. That is the "separate agent that keeps listening and asks when needed."

## Write the result
When the interviewer returns `status == "complete"`:
1. Make sure the parent dir of OUT exists.
2. Write the rubric to OUT. `requirements_md` holds the body only — it starts at
   `## Player profile` and has `## Weighted criteria` summing to 100 and
   `## Judging notes`. If OUT already existed, **preserve its preamble** —
   everything above the first `## Player profile` line, e.g. a `# The Prize` title
   and the `> PERSONAL FILE` gitignore note — and replace only the body below it
   with `requirements_md`. If OUT is new, write `requirements_md` as-is.
3. Print the `profile_summary` bullets back to the human and tell them how to use it:

```
✅ Profile saved → <OUT>
Run the arena against it:
  /judge-cards            (tournament; auto-uses personal/requirements.md when present)
  /scout-cards 5          (discover more cards that fit this profile)
  python -m arena --requirements <OUT>
```

## Notes
- Default output is gitignored (`personal/`), so the profile stays private. Pass a
  different path if you actually want to commit a shareable example.
- Not financial advice — this only encodes what the player tells you.
