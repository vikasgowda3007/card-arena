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

## The loop
Keep a running transcript string `ANSWERS_SO_FAR` (starts empty).

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
2. Write its `requirements_md` to OUT verbatim (it already has `## Player profile`,
   `## Weighted criteria` summing to 100, and `## Judging notes`).
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
