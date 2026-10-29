
- 2026-10-26 CANDIDATE (lane ic1badvice, [INLINE-C] 1b): `pcrec_error.msg` is a fixed 256 bytes. The `once` advice (culprit + fix + verdict + witness subject) had to be compacted, and it drops the witness clause when it would not fit. A longer or caller-sized diagnostic belongs to the push.
