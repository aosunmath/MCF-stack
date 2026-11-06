"""Render the special-solution catalogue from the registered local manuscript."""
from pathlib import Path
import sys
import json
from common import configure, export
from project import CONTRIBUTORS, REPOSITORY
from source_snapshot import manuscript_snapshot

configure('gmt-foundations', 'Special solutions of mean curvature flow',
          REPOSITORY, author=CONTRIBUTORS)
def check_entry_status(source, records):
    review = json.loads((source / 'entry-review.json').read_text())
    registered = {item['label']: item for item in review['entries']}
    actual = {record['label']: record for record in records if not record['section']}
    if registered.keys() != actual.keys() or len(registered) != len(review['entries']):
        raise ValueError('Update the entry-status register for changed manuscript entries')
    for label, item in registered.items():
        record = actual[label]
        if item['kind'] != record['kind'] or item['formal_verification'] != 'none':
            raise ValueError(f'Incorrect draft status: {label}')
        if (item['status'] == 'proof-included') != bool(record['proof_html']):
            raise ValueError(f'Proof coverage changed: {label}')
        if set(item['dependencies']) - actual.keys():
            raise ValueError(f'Unresolved proof dependency: {label}')
    return records


export(Path(sys.argv[1]), Path(sys.argv[2]), local=True, transform=check_entry_status)

# These inventories contain citations and hashes, never the supplied scans or OCR.
for name in ('source-inventory.json', 'entry-review.json'):
    (Path(sys.argv[2]) / name).write_bytes((Path(sys.argv[1]) / name).read_bytes())

edition = json.loads((Path(sys.argv[2]) / 'edition.json').read_text())
if manuscript_snapshot(Path(sys.argv[1]))['source_sha256'] != edition['source_sha256']:
    raise ValueError('Local manuscript changed while copying source records')
