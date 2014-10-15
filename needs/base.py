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
    """
    error = Exception

    def __call__(self):
        return bool(self)

    def __enter__(self):
        if not self:
            raise self.error

    def __exit__(self, type_, value, traceback):
        pass

    def __invert__(self):
        return NegativeNeed(self)

    def __and__(self, other):
        return AndNeed(self, other)

    def __or__(self, other):
        return OrNeed(self, other)

    def __xor__(self, other):
        return XorNeed(self, other)

    def __bool__(self):
        return self.is_met()
    __nonzero__ = __bool__

    def is_met(self):
        """This should be overwritten for each need class.

            Returns:
                (bool) - True if the need is met, False otherwise.
        """
        return True

class NegativeNeed(Need):
    """A need that returns the opposite of its parent need."""
    def __init__(self, parent_need):
        self.parent_need = parent_need
        self.error = parent_need.error

    def is_met(self):
        return not bool(self.parent_need)

class CombinationNeed(Need):
    """A base need for combining two needs."""
    def __init__(self, first_need, second_need):
        self.first_need = first_need
        self.second_need = second_need

        # Take the error of the first need without checking the second.
        self.error = first_need.error

class AndNeed(CombinationNeed):
    """A need that returns the combination of two needs using and."""
    def is_met(self):
        return bool(self.first_need) and bool(self.second_need)

class OrNeed(CombinationNeed):
    """A need that returns the combination of two needs using or."""
    def is_met(self):
        return bool(self.first_need) or bool(self.second_need)

class XorNeed(CombinationNeed):
    """A need that returns the combination of two needs using xor."""
    def is_met(self):
        return bool(self.first_need) != bool(self.second_need)

def needs(need):
    """A decorator to handle different needs.

        This wraps a function in a Need context so that an error is raised if
        the need is not met:

            ```
            @needs(login_need)
            def a_route(*args, **kargs):
                # Do some stuff that requires a login.
            ```
    """
    def adapt(f):
        @wraps(f)
        def decorated(*args, **kargs):
            with need:
                return f(*args, **kargs)
        return decorated
    return adapt

no_need = Need()
