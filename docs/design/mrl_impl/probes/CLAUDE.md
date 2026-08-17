# docs/design/mrl_impl/probes/ — the [M4.6d] MRL build lane's probe

One file, `mrl.py`, described in the parent directory's CLAUDE.md. It drives
the SHIPPED compiler (`build/pcrec`) rather than patching emitted C, which is
the difference between this lane and the design lane it inherits from.

Not built or run by pcrec's `make`. The checks that must keep passing are in
`../../../../tests/mrl/`.

Maintenance: update this file when probes are added or removed.
