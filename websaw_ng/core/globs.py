import ombott_ng
from ombott_ng.router import Route  # NOQA
from types import SimpleNamespace

from websaw_ng.core.utils import make_storage

ombott_ng.DefaultConfig.max_memfile_size = 16 * 1024 * 1024

app = ombott_ng.default_app()
app.setup()

# Context-local proxies (not app.request/app.response): they resolve to whichever
# ombott app is serving the current request, so redirect()/ctx.response/Set-Cookie
# always target the right response -- even with several apps in one process.
request = ombott_ng.request
response = ombott_ng.response
static_file = ombott_ng.static_file

request_hooks = SimpleNamespace(before=set())


def _before_request(*args, **kw):
    [h(*args, **kw) for h in request_hooks.before]


app.add_hook("before_request", _before_request)


@make_storage
class Config:
    apps_folder = 'apps'
    service_folder = ".service"
    service_db_uri = "sqlite://service.storage"
    password_file = 'password.txt'
    session_secret = None

    host = '127.0.0.1'
    port = 8000
    server = 'default'
    ssl_cert = None
    number_workers = 0

    dashboard_mode = 'full'
    watch = 'lazy'


# patched by install.py
current_config = Config()
