"""The end picture must retain the audited input topology, not invent a cap."""
import hashlib
import json
from pathlib import Path
import unittest

ASSETS = Path(__file__).resolve().parents[1]/'site/assets/solitons'


class SunWangEndPictureTests(unittest.TestCase):
    def test_horizontal_slices_retain_the_audited_shrinker_mesh(self):
        data = json.loads((ASSETS/'sun-wang-doubled-sphere-end.json').read_text())
        source = ASSETS/data['source_mesh']['asset']
        shrinker = json.loads(source.read_text())
        self.assertEqual(data['source_mesh']['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
        for key in ['vertices', 'faces', 'normals', 'sites', 'vertexGroups', 'faceGroups', 'genus']:
            self.assertEqual(data[key], shrinker[key])
        self.assertEqual((data['ambient_dimension'], data['dimension'], data['slice_dimension']), (4,3,2))
        self.assertEqual(data['status'], 'schematic')
        self.assertEqual(data['end_model']['compact_core'], 'not drawn')


if __name__ == '__main__':
    unittest.main()
