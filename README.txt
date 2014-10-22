needs
=====

Context booleans.  A pythonic way of expressing what your code needs.


Installation
------------

    $ pip install needs


Introduction
------------

A need is basic requirement to run a piece of python code.  It can take
arbitrary arguments, but should ulitmately return a boolean.  For example, in
a web context, you may have code that needs a logged-in user to run.  Using
needs, you would simply run the code `with` a `login_need`.


Subclassing
-----------

The root of all needs is a subclass of `Need`:

    from needs import Need

    class ObjectOwner(Need):
        """A need to check if the current user owns an object."""
        error = Unauthorized

        def __init__(self, obj):
            self.obj = obj

        def is_met(self):
            """Checks that the current user owns `self.obj`."""
            return self.obj.owner == get_current_user()


Singletons
----------

One of the simplest ways to use `Need`s is as a singleton that applies to your
whole project.  For example, in a web framework, you may have a function that
checks if a user is logged in.  You could then do:

    class LoginNeed(Need):
        error = Unauthorized

        def is_met(self):
            return is_user_logged_in()

    login_need = LoginNeed()

In this way, a `Need` can be a handy wrapper for any function that returns a
boolean.


Instantiation
-------------

The singleton need above does not take arguments, but if the `Need`'s
initializer does, then you can instantiate it however you like:

    some_obj = SomeObjectClass()
    owner_need = ObjectOwnerNeed(some_obj)

By default, the Need initializer can take a boolean as an argument, for example:

    logged_in_need = Need(is_logged_in())


Boolean
-------

Needs may be used as a boolean as desired:

    if login_need:
        # Do something that requires a login.


Context
-------

Any `Need` may also be used as a context, erroring out if the need is not met:

    with login_need:
        # Raise an Unauthorized error if the need is not met.
        # Otherwise, execute this code.


Decorator
---------

Any `Need` can be used as a decorator either by feeding it as an argument to
`@needs()` or using it directly:

    @needs(login_need)
    def get_current_user():
        # This will raise an Unauthorized error if login_need is not met.
        # Otherwise, the code will be executed.

    @login_need
    def get_current_user():
        # ...


Operators
---------

`Need`s can operate logically with eachother in just about the way you expect.
Say that you have an `admin_need` that is met if the logged in user is an
admin:

    # A need that is met if no user is logged in.
    no_login_need = ~login_need

    # A need that is met if no user is logged in or the user is admin.
    user_create_need = admin_need | no_login_need

    # A need that is only met if the user is logged in and not admin.
    normal_user_need = login_need & ~admin_need

    # A need that is met if the user is not logged in xor owns a given object.
    weird_need = ~login_need ^ ObjectOwnerNeed(some_obj)


No Need
-------

There is a special `Need` which is always met.  This is useful as a default
when some need must be used.  For example:

    from needs import no_need

    need = no_need

    if this_should_require_a_login:
        need = login_need
    elif this_should_require_admin:
        need = admin_need

    with need:
        # Do some code.
