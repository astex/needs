"""A module to test the behavior of the Need class."""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from needs import Need, no_need, needs


__all__ = ['TestNeed']


class TestNeed(unittest.TestCase):
    """Tests Need."""
    def setUp(self):
        self.need = Need()

    def test_need(self):
        assert self.need
        assert no_need

    def test_invert_need(self):
        assert not ~self.need

    def test_cast_need(self):
        """Tests instantiating a need with a boolean."""
        assert not Need(False)

    def test_or_need(self):
        assert self.need | self.need
        assert ~self.need | self.need
        assert self.need | ~self.need
        assert not ~self.need | ~self.need

    def test_and_need(self):
        assert self.need & self.need
        assert not ~self.need & self.need
        assert not self.need & ~self.need
        assert not ~self.need & ~self.need

    def test_xor_need(self):
        assert not self.need ^ self.need
        assert ~self.need ^ self.need
        assert self.need ^ ~self.need
        assert not ~self.need & ~self.need

    def test_decorator(self):
        """Tests the need as a decorator."""
        unmet_need = ~no_need
        @unmet_need
        def should_not_execute():
            raise ValueError()

        try:
            should_not_execute()
        except Exception as e:
            assert not isinstance(e, ValueError)

    def test_needs(self):
        """Tests the @needs decorator."""
        @needs(~no_need)
        def should_not_execute():
            raise ValueError()

        try:
            should_not_execute()
        except Exception as e:
            assert not isinstance(e, ValueError)


class TestNeedErrors(unittest.TestCase):
    """Tests the error inheritence of Need."""
    def setUp(self):
        class Err(Exception):
            pass
        self.Err = Err

        class UnMetNeed(Need):
            error = Err()
        self.unmet_need = UnMetNeed(False)

    def test_and_errors(self):
        try:
            with no_need & self.unmet_need:
                raise AssertionError
        except self.Err as e:
            assert e == self.unmet_need.error

        try:
            with self.unmet_need & no_need:
                raise AssertionError
        except self.Err as e:
            assert e == self.unmet_need.error

        try:
            with self.unmet_need & ~no_need:
                raise AssertionError
        except self.Err as e:
            assert e == self.unmet_need.error

    def test_or_errors(self):
        try:
            with ~no_need | self.unmet_need:
                raise AssertionError
        except self.Err as e:
            assert e == self.unmet_need.error

    def test_xor_errors(self):
        try:
            with ~self.unmet_need ^ no_need:
                raise AssertionError
        except self.Err as e:
            assert e == self.unmet_need.error

        try:
            with ~no_need ^ self.unmet_need:
                raise AssertionError
        except self.Err as e:
            assert e == self.unmet_need.error

    def test_combination_errors(self):
        try:
            with (self.unmet_need & no_need) & no_need:
                raise AssertionError
        except self.Err as e:
            assert e == self.unmet_need.error
