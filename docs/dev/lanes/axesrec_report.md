# axesrec — reconciling O-47's three unreconciled facts (2026-09-23)

Docs-only, no `src`/`tests`/`docs/spec` change. Fetched I-89 block (A)'s
real transcript (`scp` from ubuntubudu `/tmp/optloop2/axes_full.log`) and
read it against `linux_ask_i89.md`'s own EXPECT text, `tests/axes/
run_axes.sh`'s classification rule, and the pin-vs-main script diff.

**Verdict: all three "facts" O-47 reported as unreconciled are ONE
mechanism — a constant +2-row mislabeling in O-47's own prose paragraph,
not a pcrec finding.** Read against the CORRECT row (confirmed against
the raw log), bits 28-30 read `24,343/0/0/0` each, identical to darwin's
restricted run and to I-89's own EXPECT; `-fprefilter` reads its real,
already-documented 15,426-row refused-documented population (floor
12,000); `-fno-possessify` reads clean, and the 230-row exception belongs
to `-fno-counter`, already one of I-89's four documented exceptions.
`run_axes.sh` between the O-47 pin (`8d716693`) and `main` differs only
in the `[b2fix]` `PCREC_BIT(N)` respelling — zero classification-logic
change, ruling out a script-version explanation.

Deliverables:
- `docs/dev/optloop/runs/2026-09-23-i89A-8d716693/` — the archived
  transcript + README (provenance, pin, wall time).
- `docs/dev/optloop/axes_reconciliation_2026-09-23.md` — the full
  reconciliation: the corrected per-axis table, each of the three facts
  traced to its real row with the transcript line number, the ruled-out
  script-version diff, and a named (evidence-backed, not asserted
  certain) mechanical cause for the +2 offset.
- `docs/dev/optloop/linux_ask_i89.md` — annotated in place with a dated
  correction note after the "four documented exceptions" paragraph
  (history preserved; it is a sent ask).
- `docs/dev/optloop/CLAUDE.md` — entry for both new files above.

Head commit: (see branch `lane/axesrec`, committed after this report).
