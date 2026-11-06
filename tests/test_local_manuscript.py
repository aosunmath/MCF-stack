"""Local content provenance must be exact without fetching or inventing Git commits."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build
from source_snapshot import manuscript_snapshot, revision_id, revision_markup


class LocalManuscriptTests(unittest.TestCase):
    def manuscript(self, root):
        folder = root / 'content' / 'sample'
        folder.mkdir(parents=True)
        (folder / 'book.tex').write_text('Original definition.')
        (folder / 'references.bib').write_text('')
        return folder

    def test_local_source_does_not_fetch_and_keeps_hash_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = self.manuscript(root)
            record = {'repository': 'https://github.com/owner/project', 'local_path': 'content/sample'}
            with patch.object(build, 'ROOT', root), patch.object(build.subprocess, 'run') as run, patch.object(build.subprocess, 'check_output') as output:
                result = build.fetch_source(record, {})
            run.assert_not_called()
            output.assert_not_called()
            self.assertEqual(result['path'], folder.resolve())
            self.assertNotIn('commit', result)
            self.assertTrue(revision_id(result).startswith('sha256:'))
            self.assertNotIn('/commit/', revision_markup(result, record['repository']))

    def test_snapshot_changes_when_a_proof_or_reference_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.manuscript(Path(tmp))
            before = manuscript_snapshot(folder)
            self.assertEqual(before, manuscript_snapshot(folder))
            (folder / 'proof.tex').write_text('A proof.')
            after = manuscript_snapshot(folder)
            self.assertNotEqual(before['source_sha256'], after['source_sha256'])
            (folder / 'references.bib').write_text('A corrected edition.')
            self.assertNotEqual(after['source_sha256'], manuscript_snapshot(folder)['source_sha256'])

    def test_symlink_escape_and_incomplete_manuscript_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                manuscript_snapshot(root)
            folder = self.manuscript(root)
            (folder / 'external.tex').symlink_to(root / 'outside.tex')
            with self.assertRaises(ValueError):
                manuscript_snapshot(folder)
            (root / 'content' / 'outside').symlink_to('/tmp')
            with patch.object(build, 'ROOT', root), self.assertRaises(ValueError):
                build.fetch_source({'repository': 'https://github.com/owner/project', 'local_path': 'content/outside'}, {})

    def test_reference_copies_and_proof_coverage_are_explicit(self):
        folder = ROOT / 'content' / 'gmt-foundations'
        inventory = json.loads((folder / 'source-inventory.json').read_text())
        audit = json.loads((ROOT / 'documentation' / 'catalogue-source-audit.json').read_text())
        recorded = {f['filename']: f['sha256'] for f in inventory['files']}
        for supplied in audit['files']:
            self.assertEqual(recorded[supplied['filename']], supplied['sha256'])
        self.assertEqual(len(audit['files']) - len({f['sha256'] for f in audit['files']}), 1)
        self.assertTrue(all(f['redistributed'] is False for f in inventory['files']))
        review = json.loads((folder / 'entry-review.json').read_text())
        known = {e['label'] for e in review['entries']}
        for entry in review['entries']:
            self.assertEqual(entry['formal_verification'], 'none')
            self.assertFalse(set(entry['dependencies']) - known)
            if entry['kind'] == 'theorem':
                self.assertIn(entry['status'], ('cited-theorem', 'proof-included'))
                self.assertTrue(entry['citations'])
        self.assertEqual(json.loads((ROOT / 'formalizations.json').read_text())['entries'], [])


if __name__ == '__main__':
    unittest.main()
