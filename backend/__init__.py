"""Package initialization for the backend.

We apply a small compatibility shim here that adapts
typing.ForwardRef._evaluate to accept the newer keyword-only
`recursive_guard` argument used in Python 3.13. This prevents
third-party packages (Pydantic v1.x) from crashing at import time on
Python 3.13+.
"""

import typing

_FR = getattr(typing, "ForwardRef", None)
if _FR is not None and hasattr(_FR, "_evaluate"):
    _orig_eval = _FR._evaluate

    def _evaluate_compat(self, globalns, localns=None, *args, **kwargs):
        try:
            return _orig_eval(self, globalns, localns, *args, **kwargs)
        except TypeError:
            recursive_guard = None
            if args:
                recursive_guard = args[0]
            elif "recursive_guard" in kwargs:
                recursive_guard = kwargs["recursive_guard"]
            else:
                recursive_guard = set()

            try:
                return _orig_eval(self, globalns, localns, recursive_guard=recursive_guard)
            except TypeError:
                return _orig_eval(self, globalns, localns)

    _FR._evaluate = _evaluate_compat
