# samples/

This folder contains small local input samples for manual pipeline testing.

It is not a user workspace. `README.md`, `AGENTS.md`, and similar files are
repository/control files, not business source documents.

Generated outputs must not be stored here. Runtime outputs belong in `exports/`
or the configured output directory.

Automated tests should prefer stable fixtures under `tests/fixtures/`.

In the product direction, real user materials should become filtered
source/reference bundles for document understanding and generation, not files
that are blindly converted to another extension.
