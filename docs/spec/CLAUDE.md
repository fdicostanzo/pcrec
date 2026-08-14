# docs/spec/ — spec documents

Spec documents detail how the tool and its surfaces actually work and how to
use them. They are deliverables like code: actively maintained (not
append-only), carry no build history, and may reference docs/design/
documents for the reasoning behind a design without repeating it.

Build history is NOT part of the spec (Frank, 2026-08-14): how a surface
came to be — panel outcomes, refuted predictions, rulings, the design
process — stays in docs/design/ and docs/dev/. A spec may refer to design
documents but only INFORMATIONALLY: such references are background for the
curious reader, never normative. The spec alone states the contract; if a
spec and a design doc disagree, the spec is what the tool promises.

Empty today — no spec documents exist yet. First candidates will be split
out of existing design/process documents, or authored fresh, when Frank
asks for them. FIRST SCHEDULED (Frank, 2026-08-14, D40 addendum): the
as-built M4 match-API contract, authored at [M4.7]'s close from the
shipped surface (docs/dev/plan.md [M4.7]).

Maintenance: update this file when files are added/removed or their roles
change.
