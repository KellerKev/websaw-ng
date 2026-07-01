"""Per-app (instance-scoped) routing.

By default apps share the single ``globs.app`` ombott instance (one server serves
every mounted app). With ``isolated=True`` an app gets its OWN ombott router — so
two apps can live side by side in one process (e.g. importing two service modules
in one pytest run) with no route collision.
"""
import ombott_ng

from websaw_ng import DefaultApp, DefaultContext
from websaw_ng.core import globs


def test_shared_router_by_default():
    app = DefaultApp(DefaultContext(), name=__name__)
    assert app.ombott is globs.app                     # backward-compatible default


def test_isolated_app_has_its_own_router():
    app = DefaultApp(DefaultContext(), name=__name__, isolated=True)
    assert app.ombott is not globs.app
    assert isinstance(app.ombott, ombott_ng.Ombott)
    assert app.asgi == app.ombott.asgi                 # serve one app per process


def test_two_isolated_apps_dont_collide():
    a = DefaultApp(DefaultContext(), name=__name__, isolated=True)
    b = DefaultApp(DefaultContext(), name=__name__, isolated=True)
    assert a.ombott is not b.ombott

    assert a.ombott.router is not b.ombott.router

    # the SAME path on both isolated apps — impossible on one shared router,
    # fine here because routing is instance-scoped
    ra = a.add_route("/ping", "GET", lambda: "a")
    rb = b.add_route("/ping", "GET", lambda: "b")
    assert ra is not rb                                # distinct routes on distinct routers
