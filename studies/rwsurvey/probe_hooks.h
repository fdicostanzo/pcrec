/* probe_hooks.h -- rwsurvey probe: hooks injected into a COPY of src/core/compile.c.
 * Throwaway survey instrument; never merged into src/. See CLAUDE.md here. */
#ifndef RWSURVEY_PROBE_HOOKS_H
#define RWSURVEY_PROBE_HOOKS_H
#include "core/internal.h"
void probe_begin(const Ctx *cx);                 /* once per pipeline attempt */
void probe_ast(const Ctx *cx, const char *stage, const Ast *root);
void probe_dfa(const Ctx *cx, const Dfa *d, const char *name, int line);
#endif
