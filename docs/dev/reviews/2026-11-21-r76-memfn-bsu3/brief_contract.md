# CRITIC CONTRACT (opus): r76 memfn-bsu3

Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/COMMON.md first (including its "R75 ITEMS" section).
Your lens dir: .../crit-memfn-bsu3/contract/
Findings file (pre-created, APPEND only): .../crit-memfn-bsu3/contract.md. Deliver file: .../contract_deliver.txt.

## Your ONE question
Does the built compiler do exactly what the subject's spec hunks say, for every admitted input
class, and do the names describe behaviour (D80, D174)?
The hunks: `docs/spec/limits.md` §8.3¶3 (the stamp's parts and the span-vector bound),
`docs/spec/registry.md` §6¶8a `span-vector`, `docs/spec/tuning.md` §2.43 (¶3a, ¶3d),
`docs/spec/match_api.md` (abi 112), `docs/dev/history/abi_changelog.md` (the 111 -> 112 entry), and
`--help` / `options.def` text for `span-vector`. Probe each sentence with the built compiler:
`-fmemfn-simd` = off / `generic` / `x86-64` / `x86-64-v3` / a LIST / an arm64 target; the deny
`--memfn=no-span-vector` at each (restores BASE's bytes? at which layers, and what is the spec's
promise exactly); `MEMFN_FORMS` token(s) on an artifact with two V sites or a V site plus a vrun
site (`(?i)` sites); `<PREFIX>_SIMD_GUARDED_BYTES` against the bracketed bytes; `-e utf8`;
`--engine=vm` and `auto`; the default and 4095 widths; a `-p` prefix other than `rx`.
- sub-part (a) D94: grep the WHOLE review tree for the old abi number's readers (`111` in an abi
  sense: the `.abi` stamp, test expectations, spec sentences, the gate pins) and list any reader that
  did not move to 112 (excluding the denied files, and excluding main's 110 re-pin question, which is
  not a finding).
- sub-part (b) the owner-quote check: verify, word for word, every owner quote the subject's changed
  text (spec hunks, code comments, test comments, block_span.md's U3-relevant sections) cites,
  against `git show fb258a000:docs/dev/decisions.md`. You are the ONE lens that checks quotes.
Compile cap: 200 compiles. State your matrix product before running it. Do not plant anything.
