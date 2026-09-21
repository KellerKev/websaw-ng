"""A ``threading.local`` replacement backed by ``contextvars``.

Per-request context/fixture state must be isolated **per task** under an async
(ASGI) server and **per thread** under a sync (WSGI) server. ``contextvars``
gives both (each thread has its own context; each asyncio task copies the
context), so ``ContextLocal`` is a drop-in for ``threading.local`` that is safe
for concurrent async requests on a single event loop while staying
behaviour-equivalent for threaded WSGI serving.
"""
from __future__ import annotations

import contextvars


class ContextLocal:
    """Attribute storage that is private to the current thread (WSGI) or task (ASGI).

    Writes are copy-on-write: setting an attribute copies the current dict and stores
    the copy in the ContextVar, so it lands in the writing task's own context only.
    Mutating the stored dict in place would not be safe: a dict created before the
    tasks exist (a module-level ``ctxd = Context()`` sets defaults at import time) is
    inherited *by reference* by every task, and concurrent requests would then share,
    and overwrite, each other's state. Reads see whatever the task inherited, so
    import-time defaults stay visible.

    Values stored here that are themselves mutable (a dict, a SimpleNamespace) are
    only per-request if each request assigns a fresh one, as ``BaseContext.initialize``
    does for ``state``, ``env`` and the fixtures' ``fixtures_data``.
    """

    __slots__ = ("_cv",)

    def __init__(self):
        object.__setattr__(self, "_cv", contextvars.ContextVar("websaw.ctxlocal"))

    def _store(self):
        """The current values, read-only: never mutate the returned dict."""
        return self._cv.get(None) or {}

    def __getattr__(self, name):
        try:
            return self._store()[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        d = dict(self._store())
        d[name] = value
        self._cv.set(d)

    def __delattr__(self, name):
        d = dict(self._store())
        try:
            del d[name]
        except KeyError:
            raise AttributeError(name)
        self._cv.set(d)
