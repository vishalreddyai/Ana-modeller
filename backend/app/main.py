"""Compatibility shim: on some Python versions (notably 3.13) the
`typing.ForwardRef._evaluate` signature changed to require a
keyword-only `recursive_guard` argument.  Some third-party libraries
(e.g. older Pydantic 1.x) call `_evaluate` with a different calling
convention which causes a TypeError during import.  To avoid that we
wrap `ForwardRef._evaluate` with a thin adapter that accepts both
signatures.

This keeps the change local to the application and avoids forcing a
dependency change or Python downgrade.
"""

import typing

_FR = getattr(typing, "ForwardRef", None)
if _FR is not None and hasattr(_FR, "_evaluate"):
    _orig_eval = _FR._evaluate

    def _evaluate_compat(self, globalns, localns=None, *args, **kwargs):
        """Compatibility wrapper for typing.ForwardRef._evaluate.

        Accepts either positional or keyword-only `recursive_guard` and
        forwards the call to the original implementation.
        """
        try:
            # Prefer a direct call first (works when signatures align)
            return _orig_eval(self, globalns, localns, *args, **kwargs)
        except TypeError:
            # Try to normalize arguments: if a positional recursive_guard
            # was provided in args, use it; otherwise try kwargs; default
            # to an empty set.
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
                # Last resort: call with only globalns/localns if the
                # original expects that form.
                return _orig_eval(self, globalns, localns)

    _FR._evaluate = _evaluate_compat

"""Main FastAPI application module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth

app = FastAPI(title="Ana Modeller API", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])



