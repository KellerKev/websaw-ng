"""Per-app (instance-scoped) routing, and that it plays nice with redirect/cookies.

Default: apps share the single ``globs.app`` ombott instance. ``isolated=True``
gives an app its OWN router *and* its own request/response. ombott resolves the
module-level ``request``/``response`` (and ``redirect()``/``ctx.response``)
context-locally -- per request-handling task -- so those always target the app
actually serving, even when several isolated apps run in one process, concurrently.
"""
import asyncio
import io

import ombott_ng

from websaw_ng import DefaultApp, DefaultContext
from websaw_ng.core import globs


def test_shared_router_by_default():
    app = DefaultApp(DefaultContext(), name=__name__)
    assert app.ombott is globs.app


def test_isolated_router_is_separate():
    app = DefaultApp(DefaultContext(), name=__name__, isolated=True)
    assert app.ombott is not globs.app
    assert isinstance(app.ombott, ombott_ng.Ombott)
    assert app.asgi == app.ombott.asgi
    # its own request/response objects (context-local resolution keeps them correct)
    assert app.ombott.request is not globs.app.request
    assert app.ombott.response is not globs.app.response


def test_two_isolated_apps_same_route_dont_collide():
    a = DefaultApp(DefaultContext(), name=__name__, isolated=True)
    b = DefaultApp(DefaultContext(), name=__name__, isolated=True)
    assert a.ombott.router is not b.ombott.router
    ra = a.add_route("/ping", "GET", lambda: "a")
    rb = b.add_route("/ping", "GET", lambda: "b")
    assert ra is not rb


def _wsgi(app, path):
    env = {"REQUEST_METHOD": "GET", "PATH_INFO": path, "SERVER_NAME": "t", "SERVER_PORT": "80",
           "wsgi.input": io.BytesIO(b""), "wsgi.errors": io.StringIO(), "wsgi.url_scheme": "http",
           "SERVER_PROTOCOL": "HTTP/1.1"}
    box = {}

    def start(status, headers, exc_info=None):
        box["status"], box["headers"] = status, headers
    b"".join(app.wsgi(env, start))
    return box["status"], box["headers"]


def test_isolated_login_redirect_keeps_cookie_and_location():
    """The regression that shelved isolation: a login (Set-Cookie) + redirect on an
    isolated app must keep BOTH the cookie and the Location header."""
    app = DefaultApp(DefaultContext(), name=__name__, isolated=True)

    @app.ombott.route("/login", "GET")
    def login():
        ombott_ng.response.set_cookie("session", "abc123")   # == ctx.response (context-local)
        ombott_ng.redirect("/home")

    status, headers = _wsgi(app.ombott, "/login")
    low = [(k.lower(), v) for k, v in headers]
    assert status.startswith("30")                                        # redirect survived
    assert any(k == "location" and v.endswith("/home") for k, v in low)   # Location survived
    assert any(k == "set-cookie" and "session=abc123" in v for k, v in low)  # cookie survived


async def _asgi_get(app, path):
    scope = {"type": "http", "method": "GET", "path": path, "raw_path": path.encode(),
             "query_string": b"", "headers": [], "server": ("t", 80), "scheme": "http"}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    events = []

    async def send(ev):
        events.append(ev)
    await app.asgi(scope, receive, send)
    start = next(e for e in events if e["type"] == "http.response.start")
    hdrs = {}
    for k, v in start["headers"]:
        hdrs.setdefault(k.decode().lower(), []).append(v.decode())
    return start["status"], hdrs


def test_concurrent_isolated_apps_keep_separate_responses():
    """Two isolated apps serving simultaneously must not clobber each other's
    response -- the whole point of context-local request/response."""
    a = DefaultApp(DefaultContext(), name=__name__, isolated=True)
    b = DefaultApp(DefaultContext(), name=__name__, isolated=True)

    def make(tag):
        async def handler():
            ombott_ng.response.set_cookie("who", tag)
            await asyncio.sleep(0)                       # force interleave with the other request
            ombott_ng.response.headers["X-Who"] = tag
            return tag
        return handler

    a.ombott.route("/who", "GET")(make("A"))
    b.ombott.route("/who", "GET")(make("B"))

    async def run():
        return await asyncio.gather(_asgi_get(a.ombott, "/who"),
                                    _asgi_get(b.ombott, "/who"))

    (sa, ha), (sb, hb) = asyncio.run(run())
    assert ha["x-who"] == ["A"] and any("who=A" in c for c in ha["set-cookie"])
    assert hb["x-who"] == ["B"] and any("who=B" in c for c in hb["set-cookie"])
