"""Lightweight HWPX package metadata inspection."""
from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile, is_zipfile


def inspect_hwpx_package(path: Path) -> dict:
    """Return safe native metadata from an HWPX ZIP/XML package.

    This does not parse paragraphs, tables, layout, or styles. It only records
    package-level facts so DocumentModel can distinguish native HWPX metadata
    from Markdown-derived fallback structure.
    """
    path = Path(path)
    if not is_zipfile(path):
        return {
            "hwpx_package_detected": False,
            "native_metadata_available": False,
            "native_metadata_reason": "not_a_zip_package",
            "extracted_native_fields": [
                "hwpx_package_detected",
                "native_metadata_available",
                "native_metadata_reason",
            ],
        }

    try:
        with ZipFile(path) as package:
            entries = sorted(info.filename for info in package.infolist())
            xml_meta = _inspect_xml_metadata(package, entries)
    except BadZipFile:
        return {
            "hwpx_package_detected": False,
            "native_metadata_available": False,
            "native_metadata_reason": "bad_zip_package",
            "extracted_native_fields": [
                "hwpx_package_detected",
                "native_metadata_available",
                "native_metadata_reason",
            ],
        }

    xml_entries = [name for name in entries if name.lower().endswith(".xml")]
    section_entries = [
        name for name in xml_entries
        if name.lower().startswith("contents/section")
    ]
    binary_entries = [
        name for name in entries
        if name.lower().startswith("bindata/")
    ]
    media_entries = [
        name for name in binary_entries
        if name.lower().endswith((
            ".bmp", ".gif", ".jpg", ".jpeg", ".png", ".tif", ".tiff",
        ))
    ]

    meta = {
        "hwpx_package_detected": True,
        "native_metadata_available": True,
        "native_metadata_source": "zip_package",
        "xml_file_count": len(xml_entries),
        "section_file_count": len(section_entries),
        "binary_file_count": len(binary_entries),
        "media_file_count": len(media_entries),
        "package_entries": entries,
        "extracted_native_fields": [
            "hwpx_package_detected",
            "native_metadata_available",
            "native_metadata_source",
            "xml_file_count",
            "section_file_count",
            "binary_file_count",
            "media_file_count",
            "package_entries",
        ],
    }
    meta.update(xml_meta)
    return meta


def _inspect_xml_metadata(package: ZipFile, entries: list[str]) -> dict:
    content_hpf_present = "Contents/content.hpf" in entries
    manifest_present = "META-INF/manifest.xml" in entries
    header_xml_present = "Contents/header.xml" in entries
    section_files = [
        name for name in entries
        if name.lower().startswith("contents/section")
        and name.lower().endswith(".xml")
    ]

    meta = {
        "content_hpf_present": content_hpf_present,
        "manifest_present": manifest_present,
        "header_xml_present": header_xml_present,
        "section_files": section_files,
        "extracted_xml_fields": [
            "content_hpf_present",
            "manifest_present",
            "header_xml_present",
            "section_files",
        ],
    }

    xml_available = False

    if content_hpf_present:
        content_root = _read_xml(package, "Contents/content.hpf")
        if content_root is not None:
            title = _first_text(content_root, "title")
            creator = _meta_value(content_root, "creator")
            manifest_count = _count_nodes(content_root, "item")
            if title:
                meta["document_title_candidate"] = title
                meta["extracted_xml_fields"].append("document_title_candidate")
            if creator:
                meta["creator_candidate"] = creator
                meta["extracted_xml_fields"].append("creator_candidate")
            meta["manifest_item_count"] = manifest_count
            meta["extracted_xml_fields"].append("manifest_item_count")
            xml_available = True

    if header_xml_present:
        header_root = _read_xml(package, "Contents/header.xml")
        if header_root is not None:
            section_count = header_root.attrib.get("secCnt")
            if section_count is not None:
                meta["header_section_count"] = _int_or_text(section_count)
                meta["extracted_xml_fields"].append("header_section_count")
            xml_available = True

    if manifest_present:
        manifest_root = _read_xml(package, "META-INF/manifest.xml")
        if manifest_root is not None:
            file_entry_count = _count_nodes(manifest_root, "file-entry")
            meta["odf_manifest_file_entry_count"] = file_entry_count
            meta["extracted_xml_fields"].append("odf_manifest_file_entry_count")
            xml_available = True

    meta["xml_metadata_available"] = xml_available
    if not xml_available:
        meta["xml_metadata_reason"] = "known_xml_files_missing_or_unreadable"
    return meta


def _read_xml(package: ZipFile, name: str):
    try:
        with package.open(name) as stream:
            return ElementTree.parse(stream).getroot()
    except (ElementTree.ParseError, KeyError, OSError):
        return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _first_text(root, local_name: str) -> str | None:  # noqa: ANN001
    for elem in root.iter():
        if _local_name(elem.tag) == local_name and elem.text:
            text = elem.text.strip()
            if text:
                return text
    return None


def _meta_value(root, name: str) -> str | None:  # noqa: ANN001
    for elem in root.iter():
        if _local_name(elem.tag) != "meta":
            continue
        if elem.attrib.get("name") != name:
            continue
        text = (elem.text or "").strip()
        if text:
            return text
        content = (elem.attrib.get("content") or "").strip()
        if content:
            return content
    return None


def _count_nodes(root, local_name: str) -> int:  # noqa: ANN001
    return sum(1 for elem in root.iter() if _local_name(elem.tag) == local_name)


def _int_or_text(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value
