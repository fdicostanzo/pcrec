# docs/dev/pcre2_notes — prose notes from the PCRE2 clean-room wall (D181)

Frank 2026-10-29: a pinned copy of the PCRE2 source is allowed, but nothing is
copied: a Chinese wall between reading and writing.

## The wall

- The copy: tag pcre2-10.46 at `$PCREC_TMPDIR/ref/pcre2-10.46` (default
  `/var/tmp/pcrec-<user>/ref/`), read-only, never built or run, never in the repo.
- READ side: only a `pcre2-reader` subagent (`.claude/agents/pcre2-reader.md`).
  `scripts/hooks/pcre2_ref_guard.sh` blocks every other caller, the main session
  included, on any tool call naming the copy, and blocks every writer to it.
  Briefs to a reader must NOT name the path (the hook scans the prompt).
- WRITE side: the manager and every lane. They read notes, never the copy.
  A writer needing a fact asks for a note: ONE named question per reader run.

## How a note crosses

1. The reader writes `$PCREC_TMPDIR/scratch/pcre2notes/<slug>.md`.
2. `scripts/check_pcre2_note.sh NOTE.md` passes (rejects fenced code, statements,
   brace blocks, preprocessor lines, C operator runs, internal identifier shapes).
   It is the least that catches an accidental paste; the manager also reads the note.
3. The manager commits it here as `<slug>.md`. Writers cite the note
   (`docs/dev/pcre2_notes/<slug>.md`), never the copy or its file:line.

## Citing a note from code (Frank 2026-10-29)

When pcrec code is designed substantially from a note (the algorithm or structure
came from the source, not merely behaviour we match), the site carries

and the note's last section, "Cited by", lists the pcrec sites (the manager adds
it when the code lands). Slugs are stable once committed, so citations do not
dangle. Matching PCRE2's behaviour is D26 and needs no citation. The key
`[PCRE2src]` is in root REFERENCES.md.

## Not allowed here

Code, quotes, internal identifiers, copied tables. A note that fails the checker is
reworded, not allowlisted. Notes are behaviour facts; D26 still decides what pcrec does.
