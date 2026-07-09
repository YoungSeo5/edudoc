"""edudoc template profiles and deterministic extraction (edudoc-owned).

Phase 1 scope: extract a document's real style (fonts, size, margins, spacing)
from an HWPX reference, with evidence. Nothing is defaulted here — see
``core.exporters.style_profile`` for render-time fallback values, which are kept
strictly separate from extracted truth.
"""
