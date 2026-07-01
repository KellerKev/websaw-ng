from websaw_ng import DefaultApp, DefaultContext
import ombott_ng

ombott_ng.default_app().setup(dict(debug=True))


class Context(DefaultContext):
    ...


ctxd = Context()
app = DefaultApp(ctxd, name=__package__)


@app.route('index')
def index(ctx: Context):
    
    msg = 'Hello from skeleton app index'
    return dict(msg = msg)
