# docs/dev/lanes/predspec261_evidence/ — rev 26.1 of predicates_draft.md (review r47's fixes; the conditional), its evidence

Lane predspec261 (2026-11-18), DESIGN EVIDENCE: review r47's verified witnesses re-run, its evidence defects (C1-C4)
fixed, and the owner's 2026-11-18 afternoon rulings on the CONDITIONAL run in every mode. Rules nothing. Historical
after merge; never edited after. `../predspec26_evidence/` stays as committed (this engine is a copy, not an import).

## Files

- `predspec261_model.py` — STANDALONE. predspec26's parts N..OQ with r47's fixes IN PLACE (N3 replaced by NZ; the
  first/last-atom `outward` replaced by a reach classifier `rx_reach` over a small regex parser, checked by HF2
  against libpcre2 own-text vs in-subject runs; CS3's `&` arm an independent path-enumerating FILTER model, one level
  and inside a loop; `hole_ok` with the count kind split and a backreference error, P6 rows), plus PART R47 (A1-A6,
  B1-B6, B13) and PART COND (four forms against a semantic model and PCRE2's `(?(?=A)B|C)`; the shown when-test table;
  rev 26's `when` as the special case; the call forms; the else-only form by NOT; not-test). Controls: libpcre2-8
  10.46 through `../rxmodel_evidence/pcre2h.py` (run, never read: D181), Python `re`.
- `predspec261_model.out` — forward run: CHECKS 156 of 156 OK.
- `predspec261_sabotage.out` — all 29 sabotages at once: 100 of 156. `predspec261_sabotage_each.out` — each alone;
  every one fails at least one check.

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec261 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec261_evidence/predspec261_model.py > fwd.out)

Seconds. `PREDSPEC261_SABOTAGE=1` or `s1,..`; the list (s1-s13 predspec26's, s14-s29 new) is the script's header.

## RULE-AS-CODE (consistency checks, never independent controls)

| predicate | draft sentence (rev 26.1) |
|---|---|
| `rx_reach`: an edge counts if nothing can stand before/after it; any anchor; a lookahead wider than what follows, a lookbehind wider than what precedes | R.1.0 KIND column; R.1.4 operand-context |
| `hole_ok`: count = a non-negative int (-1 a kind error; > 65535 a removed copy); backreference = error; class/option = OPEN | R.1.0 HOLE POSITIONS |
| `quant_ok` + the group-of-conditions row | R.1.14 quantified-condition; B4's draft reading |
| `when_call`: the signature `when(cond, then, else = null)`, by position or name | R.1.10 (8) |

LIMITS: `rx_parse` covers the witnesses' syntax (atoms, classes, groups, lookarounds, quantifiers, `|`, `${..}` as one
opaque character), not all of PCRE; the conditional's warning and the comma check are not runnable (no parser).
Minimum witness lengths: A1 0-4 characters, A3 3, A4 7 and 6, A5 4, B1 3, B5 3, B6 2, COND 0-3, NZ 3.
