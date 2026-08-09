# lib — public library API

The only header file installed for embedding pcrec as a library. Declares the three public functions and the options/output/error structs.

## Files

- **pcrec.h** — public API: pcrec_compile(), pcrec_output_free(), pcrec_default_options(); encoding enum and option/output/error types

## Conventions

This is the sole public interface; everything under src/ is internal. The library works in two modes: -o out.c writes a self-contained .c file (no header), or -o out.c with options.header_name='out.h' writes paired .c/.h files. Generated code has no dependency on pcrec at runtime.

Maintenance: update this file when files are added/removed or their roles change.
