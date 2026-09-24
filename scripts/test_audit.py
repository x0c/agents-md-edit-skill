from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import audit


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "GUIDE.md").write_text("# Guide\n", encoding="utf-8")
        self.target = self.root / "AGENTS.md"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_target(self, body: str) -> None:
        self.target.write_text(body, encoding="utf-8")

    def test_cli_resolves_target_when_run_from_another_directory(self) -> None:
        self.write_target("# Agent\n\n## Index\n| [Guide](docs/GUIDE.md) | Summary |\n")
        result = subprocess.run(
            [sys.executable, str(Path(audit.__file__).resolve()), str(self.target), "--json"],
            cwd=str(self.root / "docs"),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["index_entries"][0]["exists"])

    def test_prose_basename_is_not_counted_as_an_index_link(self) -> None:
        self.write_target(
            "# Agent\n\n## Index\n| [Guide](docs/GUIDE.md) | Mentions `GITHUB_STAR_GROWTH_GUIDE.md` as prose. |\n"
        )
        report = audit.audit(self.target)
        self.assertEqual([entry["path"] for entry in report["index_entries"]], ["docs/GUIDE.md"])
        self.assertEqual(report["findings"], [])

    def test_table_summary_accepts_first_column_link_and_bare_filename(self) -> None:
        (self.root / "GUIDE.md").write_text("# Guide\n", encoding="utf-8")
        self.write_target(
            "# Agent\n\n## Documentation Index\n"
            "| `GUIDE.md` | Guide contents |\n| [Guide](docs/GUIDE.md) | Another summary |\n"
        )
        report = audit.audit(self.target)
        self.assertEqual(len(report["index_entries"]), 2)
        self.assertTrue(all(entry["exists"] for entry in report["index_entries"]))

    def test_duplicate_entries_and_duplicate_index_headings_are_reported(self) -> None:
        self.write_target(
            "# Agent\n\n## Index\n| `docs/GUIDE.md` | Summary |\n| `docs/GUIDE.md` | Duplicate |\n"
            "\n## Index\n| [Missing](docs/MISSING.md) | Summary |\n"
        )
        report = audit.audit(self.target)
        kinds = [finding["kind"] for finding in report["findings"]]
        self.assertIn("duplicate_index_entry", kinds)
        self.assertIn("duplicate_index_heading", kinds)
        self.assertIn("missing_link", kinds)

    def test_bullet_links_and_space_paths_are_checked_but_fenced_examples_are_ignored(self) -> None:
        (self.root / "docs" / "My Guide.md").write_text("# Guide\n", encoding="utf-8")
        self.write_target(
            "# Agent\n\n## Rules Index\n"
            "- [Guide](<docs/My Guide.md>)\n\n"
            "```markdown\n- [Example](docs/DOES_NOT_EXIST.md)\n```\n"
        )
        report = audit.audit(self.target)
        self.assertEqual([entry["path"] for entry in report["index_entries"]], ["docs/My Guide.md"])
        self.assertEqual(report["findings"], [])

    def test_url_encoded_local_link_path_resolves(self) -> None:
        (self.root / "docs" / "My Guide.md").write_text("# Guide\n", encoding="utf-8")
        self.write_target("# Agent\n\n## Index\n- [Guide](docs/My%20Guide.md)\n")
        report = audit.audit(self.target)
        self.assertTrue(report["index_entries"][0]["exists"])
        self.assertEqual(report["findings"], [])

    def test_managed_markers_inside_fenced_examples_are_ignored(self) -> None:
        self.write_target(
            "# Agent\n\n## Index\n"
            "```markdown\n<!-- agentsync:begin example -->\n"
            "<!-- managed:inherited-agents:start -->\n```\n"
        )
        report = audit.audit(self.target)
        self.assertEqual(report["managed_regions"], [])
        self.assertEqual(report["findings"], [])

    def test_same_document_under_distinct_index_headings_is_advisory(self) -> None:
        self.write_target(
            "# Agent\n\n## 规则索引\n- [Guide](docs/GUIDE.md)\n"
            "\n## 文档导航\n- [Guide](docs/GUIDE.md)\n"
        )
        report = audit.audit(self.target)
        repeated = [finding for finding in report["findings"] if finding["kind"] == "repeated_path_across_indexes"]
        self.assertEqual(len(repeated), 1)
        self.assertEqual(repeated[0]["severity"], "advisory")

    def test_policy_heading_about_navigation_is_not_an_index_section(self) -> None:
        self.write_target(
            "# Agent\n\n## Document Index\n| [Guide](docs/GUIDE.md) | Summary |\n"
            "\n### 4. Navigation and indexes\nPolicy prose mentioning links and navigation.\n"
        )
        report = audit.audit(self.target)
        self.assertEqual(report["measurements"]["index_sections"], 1)
        self.assertEqual(len(report["index_entries"]), 1)

    def test_symlink_and_managed_region_are_read_only_and_resolved(self) -> None:
        link = self.root / "docs" / "LINK.md"
        try:
            link.symlink_to(self.root / "docs" / "GUIDE.md")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable")
        body = (
            "# Agent\n\n## Index\n| [Guide](docs/LINK.md) | Summary |\n\n"
            "<!-- agentsync:begin custom -->\nkeep me\n<!-- agentsync:end custom -->\n"
            "<!-- managed:inherited-agents:start -->\nkeep this too\n<!-- managed:inherited-agents:end -->\n"
        )
        self.write_target(body)
        before = self.target.read_bytes()
        report = audit.audit(self.target)
        self.assertTrue(report["index_entries"][0]["exists"])
        self.assertEqual(len(report["managed_regions"]), 2)
        self.assertEqual(self.target.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
