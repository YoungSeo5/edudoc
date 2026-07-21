# Gongmun template assets

This directory currently contains `gyeonggi_style_profile.toml`, a reference/loadable style-profile description for Gongmun-oriented DOCX work.

The runtime does not select this asset from an input or output extension. Gongmun attachment wording, `끝.`, and the Gongmun DOCX style apply only through the dedicated Gongmun generator or explicit compose `profile_family="gongmun"`. General reports, plans, proposals, and press releases use neutral policy by default.

This directory does not contain an approved HWPX template package. Approved reusable templates are registered under `templates/institutions/<institution>/<document_type>/` and require `template.json` with `status: approved`.
