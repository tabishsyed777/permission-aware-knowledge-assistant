import unittest
import core

class DomainTests(unittest.TestCase):
    def test_staff_and_public_isolation(self):
        import domain
        rows=core.read(core.DEFAULT)
        self.assertIsNone(domain.lookup(rows,"staff parking",{"public"}))
        self.assertEqual(domain.lookup(rows,"staff parking",{"public","staff"})[0],"Use lot F.")

    def test_unsupported_scope(self):
        rows=core.read(core.DEFAULT)
        rows[0]["scope"]="everyone"
        with self.assertRaises(ValueError): core.validate(rows)

    def test_challenge_queries(self):
        rows=core.validate(core.read(core.DEFAULT))
        for query,expected in core.read(core.DEFAULT.parent.parent/"qa/challenge.json"):
            with self.subTest(query=query):
                self.assertEqual(core.answer(rows,query)["answer"],expected)
