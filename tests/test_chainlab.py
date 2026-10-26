import copy
import unittest
from chainlab import build_chain, verify_chain, ChainError


class ChainIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.records = [{"event": "asset-created", "id": "A-1"}, {"event": "reviewed", "id": "A-1"}]

    def test_valid_chain(self):
        chain = build_chain(self.records)
        self.assertTrue(verify_chain(chain))
        self.assertEqual(len(chain), 2)
        self.assertEqual(chain[0]["previous_hash"], "0" * 64)

    def test_tampered_record_detected(self):
        chain = build_chain(self.records)
        chain[0]["record"]["id"] = "A-2"
        self.assertFalse(verify_chain(chain))

    def test_tampered_link_detected(self):
        chain = build_chain(self.records)
        chain[1]["previous_hash"] = "a" * 64
        self.assertFalse(verify_chain(chain))

    def test_order_mutation_detected(self):
        chain = build_chain(self.records)
        chain.reverse()
        self.assertFalse(verify_chain(chain))

    def test_empty_and_nonobject_records_rejected(self):
        for value in ([], "not records", [5], [None]):
            with self.subTest(value=value):
                with self.assertRaises(ChainError):
                    build_chain(value)


if __name__ == "__main__":
    unittest.main()
