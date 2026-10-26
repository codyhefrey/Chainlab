import unittest
from chainlab import build_chain, chain_tip, verify_chain, verify_against_checkpoint


class TrustedCheckpointTests(unittest.TestCase):
    def test_checkpoint_catches_rewritten_history(self):
        original = build_chain([{"amount": 1}, {"amount": 2}])
        trusted = chain_tip(original)
        altered = build_chain([{"amount": 999}, {"amount": 2}])
        self.assertTrue(verify_chain(altered))  # Entire altered chain is internally consistent.
        self.assertFalse(verify_against_checkpoint(altered, trusted))
        self.assertTrue(verify_against_checkpoint(original, trusted))

    def test_invalid_checkpoint_does_not_match(self):
        chain = build_chain([{"name": "sample"}])
        for invalid in ("", "x"*64, "0"*63, None, 50):
            with self.subTest(value=invalid):
                self.assertFalse(verify_against_checkpoint(chain, invalid))


if __name__ == "__main__":
    unittest.main()
