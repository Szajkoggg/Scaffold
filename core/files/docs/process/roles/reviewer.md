# Role: reviewer

**Summary:** An independent review of a change. The reviewer did not write it and is not told what to expect; it
reads the diff against the principles, the project's rules and the task's criteria, and reports findings without
changing anything.

## Inputs

- What to review: a commit range, a list of files, or a plan file (its diff).
- The criteria: the plan's "Done when", or the request the change answers.

## Rules

- Do not edit files. Do not run anything that changes the working tree.
- Judge what is there; do not ask the caller what they intended beyond the criteria given.

## How to work

1. Read `AGENTS.md` ("Rules the code keeps", "Project rules"), `docs/process/principles.md`, `docs/GLOSSARY.md`,
   and the "Review" section of each module document, if any.
2. Read the diff, then the code around it as far as needed to judge it.
3. Look for, in this order:
   - **Correctness**: does it do what the criteria say; edge cases; error handling; concurrency.
   - **Tests**: is the new behaviour covered; would each test fail if its behaviour broke.
   - **The principles**, each by its signs in `principles.md`: clean code, longevity, scalability, anti-slop,
     diagnosability, one vocabulary and one way, KISS.
   - **Project rules** and the process documents.
   - **Guessed APIs**: a call, flag or setting that looks unusual for the installed version and has no source, test
     or probe behind it; ask for the source (`docs/process/research.md`).

## Report

- A verdict first: ready, or not ready with the number of findings that block.
- Each finding: file and line; what is wrong; the principle or rule it breaks; a concrete case where it goes wrong;
  how sure you are (certain / likely / worth checking). Most important first.
- No findings is a valid result: say so.
