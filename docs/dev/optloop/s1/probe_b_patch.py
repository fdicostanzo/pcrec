#!/usr/bin/env python3
"""Option-B census PROBE (lane s1b, 2026-09-25; docs/design/litscan_s1.md §6.1).

A superset of probe_patch.py's probe: the SAME `S1\t...` stderr line with the
SAME keys (so census.py's classify() reads it unchanged), plus the facts the
option-B placement reads, evaluated off the SAME derivations the emitter uses
(unanch_start, dfa_pf_of, dfa_needs_seed, pcrec_dfa_scan_state_written):

  kind    UnanchStart.kind (0 none, 1 memchr, 2 byte-class)
  cbyte   UnanchStart.cand.byte when kind == memchr, else -1
  views   UnanchStart.views (the D11 bound: which twin a row takes)
  seeded  dfa_needs_seed(&job->dfa)
  se      pcrec_dfa_scan_state_written(cx, &job->dfa) TODAY (the reseeds bit
          scanedge.c's precondition (8) reads)
  implm   the MODEL's selection verifies the pinned run (every offset
          pin..pin+L-1 selected as a singleton) -- read off `sel`, not off
          the selected row's name (probe_patch.py's `implies` reads the name;
          under default flags the two agree, and this column says so)
  rowb    litscan_s1.md §1.1's run row predicate as option B writes it,
          clauses 1-4, evaluated on EVERY artifact regardless of REQ_WHY

SCRATCH ONLY: applied to a `git archive` of the base, never to a tracked tree.
Usage: git archive BASE | tar -x -C $SCR/probe && probe_b_patch.py $SCR/probe
       && make -C $SCR/probe CC=gcc-16 build/pcrec"""
import sys
p = sys.argv[1] + "/src/gen/emit_dfa.c"
s = open(p).read()
anchor = '    ReqAdmit admit = req_admit(cx);\n    if (admit == REQ_ADMIT_EMITTED) need_string_h = true;\n'
assert s.count(anchor) == 1, "anchor moved: re-derive the probe site"
BLOCK = r'''
    if (getenv("S1PROBE")) {
        const ReqRun *rr = &cx->job->req_run;
        char runhex[64] = "-"; int L = rr->len;
        if (L >= 2) { for (int i = 0; i < L; i++) sprintf(runhex + 2*i, "%02x", rr->bytes[i]); }
        const char *pfn = "-"; int nsel = 0, nwalk = 0, pin = -1, implies = 0, scank = -1, pfbyte = -1;
        int kind = -1, cbyte = -1, views = -1, seeded = -1, se = -1, implm = 0, rowb = 0;
        char walk[128] = ""; char sel[64] = "";
        bool dscan = pcrec_artifact_has_dfa_scan(cx);
        if (dscan && cx->job->engine == PCREC_ENG_UNANCH) {
            UnanchStart us; unanch_start(cx, &us);
            if (!us.empty) {
                const DfaPf *pf = dfa_pf_of(cx, &us); pfn = pf->c.name;
                pfbyte = us.cand.use_memchr ? us.cand.byte : -1;
                kind = (int)us.kind; cbyte = us.kind == DFA_PF_MEMCHR ? us.cand.byte : -1;
                views = us.views; seeded = dfa_needs_seed(&cx->job->dfa);
                se = pcrec_dfa_scan_state_written(cx, &cx->job->dfa);
                nwalk = us.ofsk.nwalk; nsel = us.ofsk.nsel;
                for (int j = 0; j < nwalk && j < 20; j++) {
                    char t[8]; if (us.ofsk.k[j].count == 1) sprintf(t, "%02x.", us.ofsk.k[j].byte); else sprintf(t, "*%d.", us.ofsk.k[j].count);
                    strcat(walk, t);
                }
                for (int i = 0; i < nsel; i++) { char t[8]; sprintf(t, "%d%s,", us.ofsk.k[us.ofsk.sel[i]].k, i == us.ofsk.scan ? "*" : ""); strcat(sel, t); }
                if (nsel) scank = us.ofsk.k[us.ofsk.sel[us.ofsk.scan]].k;
                if (L >= 2) {
                    for (int o = 0; o + L <= nwalk && pin < 0; o++) {
                        int ok = 1;
                        for (int i = 0; i < L && ok; i++) ok = us.ofsk.k[o+i].count == 1 && us.ofsk.k[o+i].byte == rr->bytes[i];
                        if (ok) pin = o;
                    }
                    if (pin >= 0 && nsel > 0 && strcmp(pfn, "offset-set") == 0 ? 1 : (pin >= 0 && nsel > 0 && strcmp(pfn, "offset-set-bounded") == 0)) {
                        int all = 1;
                        for (int i = 0; i < L && all; i++) {
                            int f = 0;
                            for (int t = 0; t < nsel; t++) if (us.ofsk.k[us.ofsk.sel[t]].k == pin + i && us.ofsk.k[us.ofsk.sel[t]].count == 1) f = 1;
                            all = f;
                        }
                        implies = all;
                    }
                    if (pin >= 0 && nsel > 0) {
                        int all = 1;
                        for (int i = 0; i < L && all; i++) {
                            int f = 0;
                            for (int t = 0; t < nsel; t++) if (us.ofsk.k[us.ofsk.sel[t]].k == pin + i && us.ofsk.k[us.ofsk.sel[t]].count == 1) f = 1;
                            all = f;
                        }
                        implm = all;
                    }
                    if (pin >= 0 && us.kind != DFA_PF_NONE) {
                        int sk = pin + rr->idx;
                        int c3 = (nsel > 0 && scank == sk) ||
                                 (nsel == 0 && sk == 0 && us.kind == DFA_PF_MEMCHR && us.cand.byte == rr->bytes[rr->idx]);
                        rowb = c3 && !implm;
                    }
                }
            }
        }
        fprintf(stderr, "S1\t%s\tvm=%d\teng=%d\tdscan=%d\twhy=%s\trb=%d\trun=%s\tidx=%d\tpf=%s\tpfbyte=%d\tnwalk=%d\twalk=%s\tsel=%s\tscank=%d\tpin=%d\timplies=%d\tkind=%d\tcbyte=%d\tviews=%d\tseeded=%d\tse=%d\timplm=%d\trowb=%d\n",
                getenv("S1PROBE"), cx->job->fit.chosen == ENGM_VM, (int)cx->job->engine, dscan, req_why_name(admit), cx->job->req_byte, runhex, rr->idx,
                pfn, pfbyte, nwalk, walk, sel, scank, pin, implies, kind, cbyte, views, seeded, se, implm, rowb);
    }
'''
open(p, "w").write(s.replace(anchor, anchor + BLOCK, 1))
