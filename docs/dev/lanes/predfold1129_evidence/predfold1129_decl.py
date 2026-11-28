# predfold1129 SWEEP129 declarations: a printed program at START129 whose line this lane moved or dropped -> why.
# Read by predfold1129_model.py (exec'd); each key must be USED by the sweep, or it is a STALE DECLARATION.
LNG = "label-names-gate: the label over a binding's use is a gate, never skipped; "
GONE129.update({
    '[ab = ([b = B] | [a = A])] & (ab.l: <20)': LNG + "the alternation line re-spelled with each branch's text in place under its label, answers equal",
    'atomic([ab = ([b = B] | [a = A])]) & (ab.l: <20)': LNG + "the atomic line re-spelled the same way, answers equal",
    '[ab = [b = B] | [a = A]] & (ab.l: <20)': LNG + "the precedence line re-spelled the same way, answers equal",
    'X & (X.n.d: <5)': LNG + "core/labels/paths' public-part line now reads `X.n.m.d`, answers equal",
    '[n = [m = P] SEQ "!"] & (n.d: <5)': LNG + "core/labels/paths' in-place reading moved to the text in place; the binding form is now a printed compile error",
    '[n = ([a = P] SEQ [b = Q])] & some(@n.d, <5)': LNG + "one-path's array line: the array form is exempt from one-path, not from a gate; re-spelled in place, the binding form a printed compile error",
    'X & (X.h: <5)': LNG + "stacked-chain: `X.h` skips the gate n; now a printed compile error beside `X.n.h` and `X.m.h`",
    'X & (X.a.h: <5)': LNG + "stacked-chain's two-levels line re-spelled with the gates named",
    '[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)': LNG + "skip-past-wall: `m` over text in place; the binding form a printed compile error",
    '[n = ([m = P] & [_x = Q])] & (n.d: <5)': LNG + "skip-past-wall's `&` line re-spelled in place, answers equal",
    '[n = ([m = P] | [_x = Q])] & (n.d: <5)': LNG + "skip-past-wall's `|` line re-spelled in place, answers equal",
    'pub & (pub.h: <5)': LNG + "export's public lines re-spelled with the gate named (`pubhin`, `pubh`)",
    'B(A)': "nested-scope (part-of-argument, last-placement): Example 3's line (`A := [d = rx.digits]`, a bare `dd` read) re-written under the ruled statement as the lines ex3d and ex3rx",
})
