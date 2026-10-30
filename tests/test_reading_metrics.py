import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.build import _reviewed_metrics_paths


class MetricsReviewTest(unittest.TestCase):
    def test_changed_or_unpublished_article_cannot_be_measured(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'content/cs').mkdir(parents=True)
            (root / 'infra/reading-metrics').mkdir(parents=True)
            article = root / 'content/cs/example.md'
            article.write_bytes(b'approved\r\n')
            path = '/cs/tech/example/'
            review = [{'source':'content/cs/example.md', 'path':path,
                       'sha256':hashlib.sha256(b'approved\n').hexdigest()}]
            (root / 'infra/reading-metrics/reviewed-paths.json').write_text(json.dumps(review))
            self.assertEqual(_reviewed_metrics_paths(root, {path}), [path])
            self.assertEqual(_reviewed_metrics_paths(root, set()), [])
            article.write_text('changed', encoding='utf-8')
            self.assertEqual(_reviewed_metrics_paths(root, {path}), [])
