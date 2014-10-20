"""A library for dealing with authentication."""


from functools import wraps


__all__ = ['Need', 'needs', 'no_need']


class Need(object):
    """An authentication requirement.

        This can be used in a few different ways.  Calling the need returns a
        boolean which indicates whether or not the need is met.  This allows
        you to do things like this:

            ```
            if login_need:
                # Do stuff that requires a login.
            else:
                # Do other stuff that doesn't require a login.
            ```

        You can also use a need as a context, which will raise an Unauthorized
        exception if the need is not met:

            ```
            with login_need:
                # Do stuff that requires a login.
            ```

        Implementing a need is simple, just overwrite the is_met() method.

        While these will tend to be singletons (e.g login_need, admin_need,
        ...), they don't have to be.  One use case would be for owner
        permissions, which will likely require an argument when initializing
        the need.  For example:

            ```
            class ObjectOwnerNeed(Need):
                def is_met(self):
                    return bool(obj.owner == self.session.user)

            # later...
            owner_need = ObjectOwnerNeed(some_obj)
            with owner_need:
                # Do something only the owner of that object should do.
            ```

        Needs can be inverted using the `~` unary operator:

            ```
            with ~login_need:
                # Do stuff that a logged-in user cannot do.
            ```

        Needs can also be and-ed or or-ed together:

            ```
            with admin_need | -login_need:
                # Do stuff that can't be done while logged in as a normal user.

            with admin_need & owner_need(some_obj):
                # Do stuff that can only be done as an admin owner of some_obj.
            ```

        Needs can also be used as a decorator:

            ```
            @login_need
            def do_something():
                # Do stuff that can't be done while not logged in.
            ```
    """
    error = Exception

    def __call__(self, f):
        @wraps(f)
        def decorated(*args, **kargs):
            with self:
                return f(*args, **kargs)
        return decorated

    def __enter__(self):
        if not self:
            raise self.error

    def __exit__(self, type_, value, traceback):
        pass

    def __invert__(self):
        return self.Negator(self)

    def __and__(self, other):
        return self.Combinator(self, other, lambda a, b: a and b)

    def __or__(self, other):
        return self.Combinator(self, other, lambda a, b: a or b)

    def __xor__(self, other):
        return self.Combinator(self, other, lambda a, b: a != b)

    def is_met(self):
        """This should be overwritten for each need class.

            Returns:
                (bool) - True if the need is met, False otherwise.
        """
        return True

    # Aliases for is_met().
    def __bool__(self):
        return self.is_met()
    __nonzero__ = __bool__

class NegativeNeed(Need):
    """A need that returns the opposite of its parent need."""
    @property
    def error(self):
        return self.parent_need.error

    def __init__(self, parent_need):
        self.parent_need = parent_need

    def is_met(self):
        return not bool(self.parent_need)
Need.Negator = NegativeNeed

class CombinationNeed(Need):
    """A base need for combining two needs."""
    @property
    def error(self):
        return self.first_need.error

    def __init__(self, first_need, second_need, comparator):
        self.first_need = first_need
        self.second_need = second_need
        self.comparator = comparator

    def is_met(self):
        return self.comparator(bool(self.first_need), bool(self.second_need))
Need.Combinator = CombinationNeed

def needs(need):
    """A decorator to handle different needs.

        needs(login_need)(f) == login_need(f)
    """
    def adapt(f):
        return need(f)
    return adapt

no_need = Need()
