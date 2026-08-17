# docs/design/mrl_impl/probes/ — the [M4.6d] MRL build lane's probes

Two files, both described in the parent directory's CLAUDE.md:

- `mrl.py` — steps, a three-way differential against python, and emitted size.
- `throughput.sh` — the forward-path cost, three arms (pruned / placebo /
  denied), pinned when taskset permits and saying which when it does not.

Both drive the SHIPPED compiler (`build/pcrec`) rather than patching emitted
C, which is the difference between this lane and the design lane it inherits
from — with one deliberate exception: `throughput.sh` DOES edit the emitted C,
to build its placebo, and that edit neutralises the bound rather than adding
one.

Not built or run by pcrec's `make`. The checks that must keep passing are in
`../../../../tests/mrl/`.

Maintenance: update this file when probes are added or removed.
