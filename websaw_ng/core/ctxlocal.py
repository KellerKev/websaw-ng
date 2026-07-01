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
    __slots__ = ("_cv",)

    def __init__(self):
        object.__setattr__(self, "_cv", contextvars.ContextVar("websaw.ctxlocal"))

    def _store(self):
        d = self._cv.get(None)
        if d is None:
            d = {}
            self._cv.set(d)
        return d

    def __getattr__(self, name):
        try:
            return self._store()[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self._store()[name] = value

    def __delattr__(self, name):
        try:
            del self._store()[name]
        except KeyError:
            raise AttributeError(name)
