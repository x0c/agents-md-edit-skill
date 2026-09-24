#!/usr/bin/env python3
"""Read-only structural audit for an instruction Markdown file."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CODE_RE = re.compile(r"`([^`]+)`")
AGENTSYNC_MARKER_RE = re.compile(r"<!--\s*agentsync:(begin|end)\s+([^\s]+)\s*-->")
MANAGED_MARKER_RE = re.compile(r"<!--\s*managed:([^:>]+):(start|end)\s*-->")
INDEX_TITLES = {
    "index",
    "document index",
    "documentation index",
    "rule index",
    "rules index",
    "document navigation",
    "documentation navigation",
    "文档索引",
    "规则索引",
    "文档导航",
}
PATH_SUFFIXES = (".md", ".markdown", ".rst", ".txt", ".yaml", ".yml")


def cells(line: str) -> list[str]:
    """Split a simple Markdown table row into cells."""
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    return [part.strip() for part in value.split("|")]


def is_index_heading(title: str) -> bool:
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", title.casefold()).strip()
    return normalized in INDEX_TITLES


def local_target(raw: str, base: Path) -> tuple[str, bool] | None:
    """Return (display path, exists) for a local Markdown destination."""
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1:value.index(">")]
    else:
        value = re.split(r"\s+[\"']", value, maxsplit=1)[0]
    value = value.strip()
    if not value or value.startswith("#"):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = base / path
    try:
        resolved = path.resolve(strict=False)
        exists = resolved.exists()
    except OSError:
        exists = False
        resolved = path
    return path_text, exists


def explicit_backtick_path(value: str) -> bool:
    candidate = value.strip().rstrip(".,;:")
    return "/" in candidate or "\\" in candidate or candidate.casefold().endswith(PATH_SUFFIXES)


def audit(path: Path) -> dict[str, object]:
    target = path.expanduser().resolve(strict=True)
    text = target.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings: list[tuple[int, str, int]] = []
    indexes: list[tuple[int, str]] = []
    code_fence: str | None = None
    fenced_lines: set[int] = set()
    for number, line in enumerate(lines, start=1):
        fence = re.match(r"^\s*(```+|~~~+)", line)
        if fence:
            fenced_lines.add(number)
            marker = fence.group(1)[0]
            if code_fence is None:
                code_fence = marker
            elif marker == code_fence:
                code_fence = None
            continue
        if code_fence:
            fenced_lines.add(number)
            continue
        match = HEADING_RE.match(line)
        if match:
            title = match.group(2).strip()
            headings.append((number, title, len(match.group(1))))
            if is_index_heading(title):
                indexes.append((number, title))

    entries: list[dict[str, object]] = []
    duplicate_entries: list[dict[str, object]] = []
    missing: list[dict[str, object]] = []
    by_index: dict[int, Counter[str]] = {}
    all_index_paths: dict[str, list[dict[str, object]]] = {}
    index_starts = [line for line, _ in indexes]
    for index_number, _title in indexes:
        by_index[index_number] = Counter()
        next_heading = next((line for line, _, _ in headings if line > index_number), len(lines) + 1)
        for line_number in range(index_number + 1, next_heading):
            if line_number in fenced_lines:
                continue
            line = lines[line_number - 1]
            destinations = [match.group(1) for match in LINK_RE.finditer(line)]
            if line.lstrip().startswith("|"):
                row = cells(line)
                if not row or all(re.fullmatch(r":?-{3,}:?", item.replace(" ", "")) for item in row):
                    continue
                first_cell_without_links = LINK_RE.sub("", row[0])
                for code in CODE_RE.findall(first_cell_without_links):
                    if explicit_backtick_path(code):
                        destinations.append(code)
            for raw in destinations:
                result = local_target(raw, target.parent)
                if result is None:
                    continue
                display, exists = result
                candidate = Path(display).expanduser()
                if not candidate.is_absolute():
                    candidate = target.parent / candidate
                normalized = str(candidate.resolve(strict=False))
                by_index[index_number][normalized] += 1
                entry = {"line": line_number, "path": display, "exists": exists}
                entries.append(entry)
                all_index_paths.setdefault(normalized, []).append({"line": line_number, "index_line": index_number, "path": display})
                if not exists:
                    missing.append(entry)
        for normalized, count in by_index[index_number].items():
            if count > 1:
                duplicate_entries.append({"index_line": index_number, "path": normalized, "count": count})

    normalized_index_titles = Counter(title.casefold() for _, title in indexes)
    duplicate_indexes = [
        {"title": title, "count": count}
        for title, count in normalized_index_titles.items()
        if count > 1
    ]

    managed_stack: list[tuple[str, int]] = []
    managed_errors: list[dict[str, object]] = []
    managed_regions: list[dict[str, object]] = []
    marker_stack: list[tuple[str, str, int]] = []
    for number, line in enumerate(lines, start=1):
        if number in fenced_lines:
            continue
        markers: list[tuple[str, str, str]] = []
        markers.extend(("agentsync", match.group(1), match.group(2)) for match in AGENTSYNC_MARKER_RE.finditer(line))
        markers.extend(("managed", match.group(2), match.group(1)) for match in MANAGED_MARKER_RE.finditer(line))
        for family, kind, name in markers:
            if kind == "begin":
                marker_stack.append((family, name, number))
            elif kind == "start":
                marker_stack.append((family, name, number))
            elif not marker_stack:
                managed_errors.append({"line": number, "message": f"end marker for {name!r} has no matching begin"})
            elif marker_stack[-1][:2] != (family, name):
                managed_errors.append({"line": number, "message": f"end marker for {family}:{name} does not match {marker_stack[-1][0]}:{marker_stack[-1][1]}"})
            else:
                _, _, start = marker_stack.pop()
                managed_regions.append({"name": f"{family}:{name}", "start_line": start, "end_line": number})
    for family, name, number in marker_stack:
        managed_errors.append({"line": number, "message": f"begin marker for {family}:{name} is not closed"})

    findings: list[dict[str, object]] = []
    findings.extend({"kind": "missing_link", **item} for item in missing)
    findings.extend({"kind": "duplicate_index_entry", **item} for item in duplicate_entries)
    findings.extend({"kind": "duplicate_index_heading", **item} for item in duplicate_indexes)
    findings.extend({"kind": "managed_marker", **item} for item in managed_errors)
    findings.extend(
        {"kind": "repeated_path_across_indexes", "severity": "advisory", "path": path, "references": references}
        for path, references in all_index_paths.items()
        if len({item["index_line"] for item in references}) > 1
    )
    return {
        "file": str(target),
        "measurements": {"lines": len(lines), "characters": len(text), "headings": len(headings), "index_sections": len(index_starts)},
        "index_entries": entries,
        "managed_regions": managed_regions,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only structural audit for an instruction Markdown file.")
    parser.add_argument("path", type=Path, help="Markdown file to inspect")
    parser.add_argument("--json", action="store_true", help="write the report as JSON")
    args = parser.parse_args()
    try:
        report = audit(args.path)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"audit: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"File: {report['file']}")
        print("Measurements: " + ", ".join(f"{key}={value}" for key, value in report["measurements"].items()))
        print(f"Index references: {len(report['index_entries'])}; managed regions: {len(report['managed_regions'])}")
        findings = report["findings"]
        if not findings:
            print("Findings: none")
        else:
            print(f"Findings: {len(findings)}")
            for item in findings:
                print("- " + json.dumps(item, ensure_ascii=False, sort_keys=True))
        print("Structural observations only; review semantics and intentional repetition manually.")
    return 1 if any(item.get("severity") != "advisory" for item in report["findings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
