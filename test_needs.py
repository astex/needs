"""A module to test the behavior of the Need class."""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from needs import Need, no_need


__all__ = ['TestNeed']


class TestNeed(unittest.TestCase):
    """Tests peanuts.lib.auth.Need."""
    def setUp(self):
        self.need = Need()

    def test_need(self):
        assert self.need()
        assert no_need()

    def test_invert_need(self):
        assert not (~self.need)()

    def test_or_need(self):
        assert (self.need | self.need)()
        assert (~self.need | self.need)()
        assert (self.need | ~self.need)()
        assert not (~self.need | ~self.need)()

    def test_and_need(self):
        assert (self.need & self.need)()
        assert not (~self.need & self.need)()
        assert not (self.need & ~self.need)()
        assert not (~self.need & ~self.need)()

    def test_xor_need(self):
        assert not (self.need ^ self.need)()
        assert (~self.need ^ self.need)()
        assert (self.need ^ ~self.need)()
        assert not (~self.need & ~self.need)()
