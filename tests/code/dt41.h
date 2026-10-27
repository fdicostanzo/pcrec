/* tests/code/dt41.h — DT-4.1 inline (docs/design/inline_c_requirements.md):
 * the counter a counting segment bumps. A static in the header, so the
 * driver that #includes the artifact reads the same object. */
static int dt41_n;
