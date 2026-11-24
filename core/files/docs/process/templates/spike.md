# Spike: <question>

**Summary:** <The question to answer, and the decision it feeds.>

Status: draft
Mode: attended
Template: spike
Created: YYYY-MM-DD
Time box: <e.g. one session>

## Goal

An answer to <question>, with evidence, and a recommendation. Not production code.

## Context

<What is known; the options on the table; what decision waits on this.>

## Steps

- [ ] 1. Investigate
  - Do: <prototypes, measurements, reading>. Throwaway code goes on a `spike/<slug>` branch or in `tmp/`, never on
    the main branch.
  - Done when: each option has evidence for and against, or the time box is used up.
- [ ] 2. Report
  - Do: findings and a recommendation in Notes; the conclusion in `docs/ideas/` or `docs/design/` (as a proposal
    until the user decides).
  - Done when: the user can decide from the report without rerunning anything.

## Stop conditions

- The time box is used up: report what is known.
- The question turns out to be the wrong one: report that, with the better question.

## Notes

## Outcome
