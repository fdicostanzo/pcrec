# predarg: load lane predfold1127's model (the in-force walker, WALK1127) up to its checks, as its probes do,
# plus its sweep definitions (sw11: every printed three-mode line). Imported by the other predarg scripts.
# Design evidence only; asserts nothing.
import builtins
import contextlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.normpath(os.path.join(HERE, "..", "predfold1127_evidence", "predfold1127_model.py"))
for v in list(os.environ):
    if v.startswith(("PREDFOLD1127_", "PREDFIX111_", "PREDFOLD1125_", "PREDFIX90_", "PREDSPOT_")) or v.endswith("_SABOTAGE"):
        os.environ.pop(v)
src = builtins.open(M, encoding="utf-8").read()
cut = src.index("\n# ==== CHECKS (a probe loads the model up to this line)")
NS = {"__name__": "predarg_probe", "__file__": M}
LOADLOG = io.StringIO()
with contextlib.redirect_stdout(LOADLOG):
    exec(compile(src[:cut], M, "exec"), NS)                  # noqa: S102
    s11 = NS["_src11"]
    s111 = NS["_src111"]
    exec(compile(s11[s11.index("def sw11(docs):"):s11.index("def key11(k):")], NS["P1125"], "exec"), NS)   # noqa: S102
    exec(compile(s111[s111.index("_sweep_one11, _modes_of11, _fmt11 = "):s111.index("OLD111 = {")], NS["P111"],
                 "exec"), NS)                                # noqa: S102
