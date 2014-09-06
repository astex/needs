needs
=====

Context booleans, a pythonic way of expressing what your code needs.


Installation
------------

```
$ pip install needs
```


Introduction
------------

A need is basic requirement to run a piece of python code.  It can take
arbitrary arguments, but should ulitmately return a boolean.  For example, in
a web context, you may have code that needs a logged-in user to run.  Using
needs, you would simply run the code `with` a `login_need`.


Usage
-----

The root of all needs is a subclass of `Need`:

```python
from needs import Need

class HasSerializeNeed(Need):
    """A need to check if an object has a serialize method."""
    error = AttributeError

    def __init__(self, obj):
        self.obj = obj

    def is_met(self):
        """Checks that `self.obj` has a serialize callable."""
        return \
          hasattr(self.obj, 'serialize') and
          hasattr(self.obj.serialize, '__call__')
```

This can be instantiated whenever:

```python
some_obj = Serializer() # < I think that's a made up class...
serializer_need = HasSerializerNeed(some_obj)
```

This can then be used in a variety of ways:

```python
if serializer_need():
    # Do some code if the need is met.

with serializer_need:
    # Raise an attribute error if the need is not met.
    # Otherwise, execute this code.
```


Singletons
----------

One of the simplest usage of a need is as a singleton that applies to your
whole project.  For example, in a web framework, you may have a function that
checks if a user is logged in.  You could then do:

```python
class LoginNeed(Need):
    error = Unauthorized

    def is_met(self):
        return is_user_logged_in()

login_need = LoginNeed()
```

In this way, a `Need` can be a handy wrapper for any function that returns a
boolean.


Decorator
---------

Any `Need` can be used as a decorator by feeding it as an argument to `@needs()`:

```python
@needs(login_need)
def get_current_user():
    # This will raise an Unauthorized error if login_need is not met.
    # Otherwise, the code will be executed.
```


Operators
---------

`Need`s can operate logically with eachother in just about the way you expect.
Say that you have an `admin_need` that is met if the logged in user is an
admin:

```python
# A need that is met if no user is logged in.
no_login_need = ~login_need
```

```python
# A need that is met if no user is logged in or the user is admin.
user_create_need = admin_need | no_login_need
```

```python
# A need that is only met if the user is logged in and not admin.
normal_user_need = login_need & ~admin_need
```


No Need
-------

There is a special need object included which is always met.  This is useful
as a default when some need must be used.  For example:

```python
from needs import no_need

need = no_need

if this_should_require_a_login:
    need = login_need
elif this_should_require_admin:
    need = admin_need

with need:
    # Do some code.
```
