# r4a2lx — R4a' Linux verdict (kit branch lane/memfn-r4a2)

Verdict: RED. `test-encoding-checks` failed (2 checks). Census NOT run (brief: stop on any failing section).

## Commands as run
- Mac: `git push ubuntubudu lane/memfn-r4a2:refs/heads/lane/memfn-r4a2` (new branch)
- box pre-check: `/ 98G used 80G free 14G (86%)`, load average 0.00, 57db5152 present
- `git worktree add --detach /home/duxevents/pcrec/worktrees/r4a2-linux lane/memfn-r4a2`
- HEAD = eef95511178a5b0348abede3005b88d168e4f9cf (equals pushed tip)
- `gnutimeout 1800 make -j8`: 5 s, clean
- `nohup gnutimeout 10800 make test > r4a2_make_test.log` (in the worktree), duration 5404 s

## Trailer
RUN-STAMP: tree=eef95511178a5b0348abede3005b88d168e4f9cf (clean) sections=53/53 duration=5404s

## Verdict grep
`grep -n '\*\*\* \[test-' r4a2_make_test.log` printed NOTHING, but the brief's pattern misses the failure:
make prints it as `[Makefile:646: test-encoding-checks]`:

    6197:make[1]: *** [Makefile:646: test-encoding-checks] Error 1
    6348:make: *** [Makefile:376: test] Error 1

## Failing section excerpt (test-encoding-checks, checks passed: 10, failed: 2)
    FAIL: DD12a(i) [K50] the undeclared-form exception list does NOT match: of the manifest's 11 pattern(s), 4 were reached this run and this run diverged on 5. ...
    FAIL: DD12a(i) 7 of 245 strict-identity pairs differ OUTSIDE the named encoding-owned regions — an encoding conditional reached the hot path (see dd12ai.out FINDING lines)
    FINDING pat=[fra(n|m)k|frost] ... first non-data differing line: #define RX_MEMFN_LIBC "memchr,memcmp"
    FINDING pat=[\Z] (x2) ... first non-data differing line: static inline int rx_forward_accepts_class(...)
    FINDING pat=[\b] (x2), [\B] ... first non-data differing line: static inline unsigned rx_forward_row(rx_forward_state s) { return s / N; }
    FINDING pat=[$] ... rx_forward_accepts_class

Note the first FINDING's differing line is a memfn LIBC stamp (the R4a' line), suggesting the byte/utf8 identity pair
disagrees on RX_MEMFN_LIBC. Not diagnosed further. Log: /home/duxevents/pcrec/worktrees/r4a2-linux/r4a2_make_test.log (lines ~6170-6197).

## Census
Not run.

## Delivery
SendMessage to pcrecdev3: not sent (kit session paused per manager).
Box worktree left in place.
