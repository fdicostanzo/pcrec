# altrev2_evidence — probes for alt_normal_form.md rev 2 (lane altrev2, 2026-11-05)

Evidence only; nothing builds or reads it. pcrec at main 82d95943c (worktree build), libpcre2-8 10.46.

- `probe.py` — pattern pairs through libpcre2 (ctypes) and pcrec (`-p rx` + a counting driver): span, every capture, callout count, mark. Scratch binaries go under `$PCREC_TMPDIR/scratch/altrev2/bin`.
- `snd1.tsv` / `snd1.out` — SND-1: which side effects in an intervening branch move an answer when a later branch is merged past it (P0-P10).
- `altnf_proc.py` / `.out` — the rev 2 §3.3 merge procedure re-implemented from the text on literal lists, checked against a brute-force leftmost-first oracle.
- `p7_altcls.out` — P7 row 1's one DIFF explained: altcls's merge of `a|a` (fire count, allowed by match_api.md §11.6¶1).
