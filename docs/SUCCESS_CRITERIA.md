# Success criteria

Current success criteria are route-specific and source/test-backed.

- Generic `main.py run/watch` succeeds when supported input normalizes and requested exporters report their actual result. It does not prove or apply Gongmun writing rules.
- Dedicated Gongmun generation succeeds only after `gongmun_rules` validates its generated draft. `?.` and `[??]` are limited to that explicit route or compose `profile_family="gongmun"`.
- HWPX output succeeds only when its package validator passes; HWPX is a format, not a Gongmun profile.
- DOCX/PPTX are partially stabilized within their tested content/structure scope. PDF remains an optional fallback and HWPX Pipeline output remains experimental.

Historical pre-routing success criteria are preserved in [archive/success-criteria-historical.md](archive/success-criteria-historical.md).
