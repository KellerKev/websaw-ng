from websaw_ng import wsgi

websaw_app = wsgi()

def test_app():
    assert websaw_app


