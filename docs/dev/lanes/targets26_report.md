# targets26 report: next optimization targets, fact table

Deliverable: `docs/dev/optloop/targets_2026-10-26.md` (13 target rows, regressions, subst losses, 7 bench-only
questions). Facts only; no build, no timing, no make. Ratios are pcrec/peer, > 1 = pcrec slower.

## Headline: top 5 by loss x population

1. **T1/T2 literal/alternation scan below jit** (litrun `alt-foo-tails` x8.2, `lit-l40` x2.5; ~15 syntax cells x1.8-3.0;
   ~14 syntax cells at one shared x1.25 floor). About 35-50 large-subject cells. Zen 1, vs jit, pin 6b2dbd3e.
   SIMD-attributable by cause (the roster is `simdna`); overlaps [MEMFN]. Also the cause of subst `2-rare` (x2.66 vs jit).
2. **T3 lookaround on the VM route** (`lka-pos`/`lkb-pos` x2.8-3.0, 6 syntax cells; bounded `ctx-*` x1.6; subst
   `7-url-tld-fix` x3.9 vs jit). Overlaps [DD-11.5], [MEMFN]. Rows [CTX-PREFILTER], [OPT-HYB-RESEED-XCALL] not started.
3. **T5 START-SET / hit-restart** (`stack-frame` x2.75, `aws-access-key-id` x2.6, `quoted-delim-match` x3.8,
   `json-constant` x9.0 vs rust; subst `5b-mask-email` x3.16 vs rust). 14 cells. [START-DENSE]/[OPT-VMSEED]/[REQ-HANDOFF-L1].
4. **T11 utf8 literal pick vs rust/re2** (`lit-cyr-run` x18, `lit-sharp-s` x14; 21 of 138 utf8 cells >= x1.3; pcrec
   leads jit on all 138). [U8-PICK] started. Pin 751b9c6d, stale.
5. **T4 bounded `ctx-*`/`line-80`/`cls-atleast-4096`** (x1.5-2.35 jit; x7 rust on `ctx-*`), 10 cells, no overlap named.

Also notable: T8 (capture cost, pcrec caps vs nocaps, 21 of 141 capability rows >= x1.3) is a pcrec-vs-pcrec cost with no
peer pressure shown (pcrec caps still beats rust/re2/jit on short subjects in sentinel).

## Regressions

Exactly one slower mover outside its null band across 871 judged cells: capability `tail-space-eol` large, x6.09
(auto-caps) / x6.12 (auto-nocaps), 11,976 to 72,939 ns, band 33%, program identical; lane trimreg owns it. Its short
cell went x1.48 FASTER and the other tail/anchor cells got faster (x1.2-1.4), consistent with the rev-end mark
(abi 77/78). Inside-band slowers worth one bounded look: `qnt-poss-quest` x1.23-1.24 and `lit-anchored-run`
x1.19-1.21 (both consistent at large and short); the rest is listed in section 2.

## Subst losses

All three (`2-rare` x2.66, `5b-mask-email` x1.59 vs jit / x3.16 vs rust, `7-url-tld-fix` x3.89) are search-bound,
not replacement-bound, and NO [SUBST-*] row owns them: [SUBST-SPEED] covers `\U` (case 6, a pcrec win) and replace-all
per-match overhead (case 3, a pcrec win). They belong to T1/T2, T5 and T3 respectively.

## Limits you should know

The 10-13 handoff reports contain ONLY libpcre2 (jit, interp) as a peer; no re2/rust/hyperscan. The re2/rust ratios
come from the 09-27 fullroster (Zen 1, pin 751b9c6d) and the 10-11 gap report, both stale. Only sentinel (short
subjects) and subst carry peers at the current pin; the sentinel's one loss is concat-sqli short x1.26 vs rust.
So which of T3-T12 still exist at 9ae59f5d4 is unknown until Q1 is answered.

## Bench-only questions (full text in the table file, section 4)

Q1 re-run peers at the current pin for large subjects; Q2 capability per-subject split for `moment-iso8601`/`email-owasp`;
Q3 patterns and templates of subst `2-rare`/`5b`/`7`; Q4 sentinel's 16 superseded records and the re2 after-sample
failure; Q5 vectorscan x80-x26,000 utf8 ratios (real or a different question?); Q6 trial-level data for the
`tail-space-eol` x6 mover; Q7 a Zen 4 jit/rust/re2 run of syntax+litrun before any SIMD decision.

## STATE AT HANDOFF

Branch lane/targets26, committed; no code, no make, nothing run on the box beyond python reading reports (scratch
scripts under the worktree's gitignored `build/`). Rulings file `docs/dev/lanes/targets26_rulings.md` re-read at
the final commit: "(none yet)", so no ruling applied. Validation: none owed. Not read: the 10-26 `.md`
renderings and subject-grain files, interpretation sidecars beyond sentinel's head, any bench ledger or code.
