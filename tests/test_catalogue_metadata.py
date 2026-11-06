import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue_properties


class CatalogueMetadataTests(unittest.TestCase):
    def test_missing_or_ambiguous_embeddedness_fails_validation(self):
        original = copy.deepcopy(next(iter(catalogue_properties.registry().values())))
        for value in (None, {'key': 'immersed', 'text': 'Immersed'}, {'key': 'embedded', 'text': ''}):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temporary:
                record = copy.deepcopy(original)
                if value is None:
                    del record['cases'][0]['embeddedness']
                else:
                    record['cases'][0]['embeddedness'] = value
                path = Path(temporary)
                (path / 'catalogue-properties.json').write_text(json.dumps({'examples': [record]}))
                catalogue_properties.registry.cache_clear()
                try:
                    with patch.object(catalogue_properties, 'ROOT', path):
                        with self.assertRaisesRegex(ValueError, 'embeddedness status and explanation'):
                            catalogue_properties.registry()
                finally:
                    catalogue_properties.registry.cache_clear()


if __name__ == '__main__':
    unittest.main()
