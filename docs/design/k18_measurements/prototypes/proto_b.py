#!/usr/bin/env python3
"""Prototype B — the CHEAP, NARROW alternative: transparent epsilon states.

MEASUREMENT ARTIFACT, NOT A PROPOSED PATCH.

Keep the memo global and keyed on state alone, exactly as today, and change
only what an already-seen state does: an already-seen N_EPS no longer kills
the walk, it is walked THROUGH. K18's repro dies on precisely such a state
(the outer star's loop-back N_EPS), so this reaches it for two lines of diff
and no new data structure.

Termination (the same shape of argument the K17 fix carries): a walk that did
not terminate would have to take infinitely many already-seen hops, since a
state is EXPANDED at most once per closure. The already-seen hops are (a) the
loop-entry redirect, which K17's entry argues points strictly outward past the
loop and is therefore acyclic, and (b) this new N_EPS pass-through, which
follows a single out-edge. A cycle built from those would be a cycle in the
epsilon graph avoiding every expansion — and every cycle in the epsilon graph
runs through a loop-entry SPLIT, because `frag_star` (src/ir/nfa.c) is the only
construction that creates a back edge and its target is always a `loop=1`
split. At such a split the walk takes the redirect, which is outward. So the
hops strictly descend the loop-nesting order and the walk terminates.

What it does NOT reach is the same conflation happening at a SPLIT rather than
at an N_EPS -- see the design note's section on B's exactness.
"""
import sys

path = sys.argv[1]
src = open(path).read()

old = """            const NState *ls = &cl->nfa->st[s];
            if (ls->loop) {
                s = ls->exit_is_t2 ? ls->t2 : ls->t1;
                continue;
            }
            return;"""

new = """            const NState *ls = &cl->nfa->st[s];
            if (ls->loop) {
                s = ls->exit_is_t2 ? ls->t2 : ls->t1;
                continue;
            }
            /* PROTOTYPE B (K18): an already-seen ORDINARY epsilon state is
             * transparent rather than fatal. It has exactly one out-edge and
             * no priority of its own, so passing through it cannot reorder
             * anything; what it can do is let the walk reach the loop entry
             * one hop further on, whose redirect is the answer K18 loses. */
            if (ls->k == N_EPS) { s = ls->t1; continue; }
            return;"""

assert old in src, "anchor drift in clo_visit"
src = src.replace(old, new)
open(path, "w").write(src)
print("proto B applied to", path)
