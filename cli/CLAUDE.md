# cli — command-line compiler tool

Entry point: pcrec command-line tool. Parses flags, calls pcrec_compile(), writes output to disk or stdout.

## Files

- **main.c** — CLI: option parsing ([-p PREFIX] [-e ascii|utf8] [-i] [--emit-main] -o OUT.c 'PATTERN'; -i is ASCII case-insensitive, folded into the automaton at parse time — see OS-1/D23); output file writing

## Conventions

The tool normalizes output paths (e.g., -o out.c generates out.h automatically; -o - prints self-contained C to stdout). It passes all work to lib/pcrec.h and writes the generated .c/.h files to the filesystem.

Maintenance: update this file when files are added/removed or their roles change.
