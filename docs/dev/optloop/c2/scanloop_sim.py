#!/usr/bin/env python3
"""[OPTLOOP.2 c2prep] A COUNTING simulator of pcrec's emitted unanchored DFA
scan loop, used to answer ONE question the I-85 profile left open:

    `cycle1_analysis.md` M3's hand-twin narrowed `rx_can_begin_match` from
    63 bytes to 3 on `json-constant` and the artifact got SLOWER (x1.10,
    `cycle1_profile.md` M3.c).  A candidate-density argument predicts a
    large win.  WHY DIDN'T IT HAPPEN?

The emitted scan loop only consults the candidate table when the forward
machine is in state 0:

    for (;;) {
        if (forward_state == 0 && last_accept_position == (size_t)-1)
            while (... && !rx_can_begin_match[subject[scan_position]]) scan_position++;
        ...one transition step...
    }

so the candidate set is NOT the skip loop's reach -- the state-0 residency
is.  This script replays that exact loop over a subject, counting (never
timing): state-0 residency, skip-loop entries, and BYTES ACTUALLY SKIPPED,
under the artifact's own table and under any substitute candidate set.

It reads the tables straight out of an emitted `.c` (so the machine is
pcrec's, not a reimplementation of it) and requires
`RX_DFA_TABLE "premultiplied"`, which is today's default.

Usage:  python3 scanloop_sim.py ART.c SUBJECT.bin [SUBSTITUTE_BYTES ...]
        e.g. ... json.c t-1m.bin tfn
"""
import re, sys

def arr(src, name):
    m = re.search(r'\b' + re.escape(name) + r'\[(\d+)\]\s*=\s*\{(.*?)\};', src, re.S)
    if not m:
        return None
    n = int(m.group(1))
    vals = [int(x, 0) for x in re.findall(r'-?\d+', m.group(2))]
    assert len(vals) == n, (name, len(vals), n)
    return vals

def main():
    art, subj = sys.argv[1], sys.argv[2]
    subst = sys.argv[3] if len(sys.argv) > 3 else None
    src = open(art).read()
    if 'RX_DFA_TABLE "premultiplied"' not in src:
        sys.exit("this simulator models the premultiplied table only")
    bcls = arr(src, "rx_forward_byte_class")
    nxt  = arr(src, "rx_forward_next_state")
    beg  = arr(src, "rx_can_begin_match")
    accC = arr(src, "rx_forward_is_accepting_by_class")
    if beg is None:
        sys.exit("artifact has no rx_can_begin_match (no byte-class prefilter)")
    ncls = len(nxt) // (len(accC) // len(nxt) * 0 + 1)      # placeholder
    # nclasses = len(next_state) / nstates ; nstates = len(is_accepting)
    acc = arr(src, "rx_forward_is_accepting")
    nstates = len(acc)
    ncls = len(nxt) // nstates
    if subst is not None:
        beg = [0] * 256
        for ch in subst.encode("latin-1"):
            beg[ch] = 1
    b = open(subj, "rb").read()
    n = len(b)

    # The emitted loop, verbatim in structure.  DEAD = 65535.
    scan = 0
    last_accept = -1
    st = 0
    at_state0 = 0          # outer-loop iterations with the gate OPEN
    skip_entries = 0       # times the while loop was reached
    skipped = 0            # bytes the while loop actually advanced past
    steps = 0              # transition-loop steps
    while True:
        if st == 0 and last_accept == -1:
            at_state0 += 1
            skip_entries += 1
            while scan + 1 < n and not beg[b[scan]]:
                scan += 1
                skipped += 1
        if scan >= n:
            break
        cl = bcls[b[scan]]
        if accC[st + cl]:
            last_accept = scan
        st = nxt[st + cl]
        scan += 1
        steps += 1
        if st == 65535:
            break
    print("artifact          %s" % art)
    print("subject           %s  n=%d" % (subj, n))
    print("candidate set     %d bytes%s"
          % (sum(beg), "  (SUBSTITUTED: %r)" % subst if subst else "  (as emitted)"))
    print("transition steps  %d   (%.4f%% of subject)" % (steps, 100.0*steps/n))
    print("skip-loop entries %d" % skip_entries)
    print("BYTES SKIPPED     %d   (%.4f%% of subject)" % (skipped, 100.0*skipped/n))
    print("bytes per entry   %.4f" % (skipped/skip_entries if skip_entries else 0.0))

if __name__ == "__main__":
    main()
