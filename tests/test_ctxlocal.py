"""Per-request state must stay per request when requests run concurrently (ASGI).

ContextLocal keeps its values in a ContextVar. A module-level ``ctxd = Context()``
writes defaults at import time, before any request task exists, and every task then
inherits that state. Writes must therefore land in the writing task's own context
(copy-on-write); mutating the inherited dict in place would let concurrent requests
overwrite each other's fixture values.
"""
import asyncio

from websaw_ng import DefaultApp, DefaultContext
from websaw_ng.core.ctxlocal import ContextLocal
from websaw_ng.core.fixture import Fixture
from websaw_ng.fixtures.url import URLBuilder


# ─── ContextLocal itself ─────────────────────────────────────────────────────

def test_import_time_default_is_visible_in_tasks():
    loc = ContextLocal()
    loc.flag = "default"

    async def read():
        return loc.flag

    async def run():
        return await asyncio.gather(read(), read())

    assert asyncio.run(run()) == ["default", "default"]


def test_concurrent_tasks_keep_their_own_values():
    loc = ContextLocal()
    loc.value = "default"                 # created before the tasks, like ctxd at import

    async def worker(tag):
        loc.value = tag
        for _ in range(5):
            await asyncio.sleep(0)        # let the other tasks write in between
        return loc.value

    async def run():
        return await asyncio.gather(*(worker(f"t{i}") for i in range(20)))

    assert asyncio.run(run()) == [f"t{i}" for i in range(20)]
    assert loc.value == "default"         # nothing leaked back into the root context


def test_delattr_is_task_local():
    loc = ContextLocal()
    loc.value = "default"

    async def drop():
        del loc.value
        await asyncio.sleep(0)
        return hasattr(loc, "value")

    async def keep():
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        return loc.value

    async def run():
        return await asyncio.gather(drop(), keep())

    assert asyncio.run(run()) == [False, "default"]
    assert loc.value == "default"


def test_fixture_data_is_per_task():
    class F(Fixture):
        pass

    f = F()
    Fixture.initialize_safe_storage()      # the import-time/root state

    async def request(tag):
        Fixture.initialize_safe_storage()  # what BaseContext.initialize does per request
        Fixture.prepare_for_use(f)
        f.data.tag = tag
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        return f.data.tag

    async def run():
        return await asyncio.gather(*(request(i) for i in range(10)))

    assert asyncio.run(run()) == list(range(10))


def test_url_context_is_per_task():
    async def request(tag):
        URLBuilder.setup(tag)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        return URLBuilder._local.url_ctx

    async def run():
        return await asyncio.gather(*(request(f"u{i}") for i in range(10)))

    assert asyncio.run(run()) == [f"u{i}" for i in range(10)]


# ─── end to end: concurrent requests through an app ──────────────────────────

class WhoFixture(Fixture):
    """Per-request value taken from the request, like a current-user fixture."""

    async def atake_on(self, ctx):
        await asyncio.sleep(0)
        return ctx.request.headers.get("X-Who")


class WhoContext(DefaultContext):
    who = WhoFixture()


async def _asgi_get(app, path, headers):
    scope = {"type": "http", "method": "GET", "path": path, "raw_path": path.encode(),
             "query_string": b"", "server": ("t", 80), "scheme": "http",
             "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()]}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    events = []

    async def send(ev):
        events.append(ev)
    await app.asgi(scope, receive, send)
    status = next(e for e in events if e["type"] == "http.response.start")["status"]
    body = b"".join(e.get("body", b"") for e in events if e["type"] == "http.response.body")
    return status, body.decode()


def test_concurrent_requests_see_their_own_fixture_values():
    """The regression: with several requests in flight, ``ctx.who`` came back as the
    Fixture object (another request's teardown had reset the shared state) instead
    of this request's value."""
    ctxd = WhoContext()
    app = DefaultApp(ctxd, name=__name__, isolated=True)

    @app.route("/who", method="GET")
    @app.use(ctxd.who)
    async def who(ctx):
        seen = []
        for _ in range(3):
            seen.append(ctx.who)
            await asyncio.sleep(0)
        return "|".join(s if isinstance(s, str) else type(s).__name__ for s in seen)

    app.mount()

    async def run():
        return await asyncio.gather(*(
            _asgi_get(app.ombott, "/who", {"X-Who": f"user{i}"})
            for i in range(12)))

    results = asyncio.run(run())
    for i, (status, body) in enumerate(results):
        assert status == 200, (i, status, body)
        assert body == "|".join([f"user{i}"] * 3), (i, body)
