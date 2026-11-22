import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import indexnow  # noqa: E402


class IndexNowTest(unittest.TestCase):
    def test_only_new_and_changed_pages_are_submitted(self):
        previous = {"/": "a", "/jhn/3/": "b", "/gone/": "c"}
        current = {"/": "a", "/jhn/3/": "B", "/word/g26-agape/": "d"}
        self.assertEqual(indexnow.changed(previous, current), ["/jhn/3/", "/word/g26-agape/"])
        self.assertEqual(indexnow.changed({}, current), sorted(current))

    def test_submissions_are_batched_and_name_the_key(self):
        sent = []

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        def urlopen(request, timeout):
            import json
            sent.append(json.loads(request.data))
            return Response()
        urls = [f"https://openwordbible.org/p{i}/" for i in range(indexnow.BATCH + 5)]
        with mock.patch("urllib.request.urlopen", urlopen):
            self.assertEqual(indexnow.submit(urls), [200, 200])
        self.assertEqual([len(b["urlList"]) for b in sent], [indexnow.BATCH, 5])
        self.assertEqual(sent[0]["host"], "openwordbible.org")
        self.assertEqual(sent[0]["keyLocation"], f"https://openwordbible.org/{indexnow.KEY}.txt")


if __name__ == "__main__":
    unittest.main()
