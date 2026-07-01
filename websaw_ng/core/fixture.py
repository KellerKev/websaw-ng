from types import SimpleNamespace
from typing import Optional, Any

from .ctxlocal import ContextLocal


class Fixture:

    # Central context-local storage to hold local data of all fixtures
    # (per-thread under WSGI, per-task under ASGI). See ctxlocal.ContextLocal.
    _local = ContextLocal()

    # Should the fixture be treated as a set of hooks - take_on/take_off.
    # If it is set to True, then 'take_off' method is called
    # regardless of whether 'take_on' method was called
    is_hook = False

    # The name of the fixture in the Context.
    # It is intended to be used in generic fixtures (e.g. Tempalte)
    # and supposed to be set in __init__
    context_key: Optional[str]

    @classmethod
    def initialize_safe_storage(cls):
        """Initialize the central thread local storage of all fixtures.

        We do it with one shot!
        """
        cls._local.fixtures_data = {}

    @classmethod
    def prepare_for_use(cls, fixture: 'Fixture'):
        """Initialize the thread local storage for concrete 'fixture'."""
        cls._local.fixtures_data[fixture] = SimpleNamespace()

    @property
    def data(self) -> SimpleNamespace:
        """Return the thread local fixture storage."""
        return self._local.fixtures_data[self]

    def app_mounted(self, ctx):
        """Is called when app is mounted."""
        ...

    def take_on(self, ctx) -> Optional[Any]:
        """Is called when the fixture is accessed as the context attribute.

        This hook is intended for the fixture initialization when it is accessed
        the first time during request processing.
        The return value is what the consumer will get when accessing the fixture
        as the context attribute. So it should return something useful
        e.g. opened file-descriptor or db-connection, if it returns None
        then the fixture itself will be used.
        The return value is cached in the context until take_off-hook is called.

        Note: This hook is only called if it's the request processing:

        @app.route('index')
        @app.use(ctxd.foo)  # won't be called as it's app loading stage
        def some(ctx):
            ctx.foo         # will be called as it's request processing

        """
        ...

    def take_off(self, ctx):
        """Is called at the end of request processing.

        if self.is_hook is set to False then it is only called if take_on-hook was called

        This hook is for cleanup/tear down action (e.g. to close a file or db-connection)
        """
        ...

    # --- async lifecycle (ASGI) ---------------------------------------------
    # Async controllers run through make_async_handler, which awaits these.
    # The defaults delegate to the sync hooks, so plain sync fixtures work
    # unchanged in an async request; async fixtures (e.g. an async DAL) override
    # atake_off to `await` their teardown (commit/close).
    async def atake_on(self, ctx) -> Optional[Any]:
        return self.take_on(ctx)

    async def atake_off(self, ctx):
        return self.take_off(ctx)


class SPAFixture(Fixture):
    def make_component_reference(self, ctx, prefix) -> str:
        raise NotImplementedError()

