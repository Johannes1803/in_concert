from fastapi import FastAPI

from in_concert.app.app_factory import create_app


class TestApp:
    def test_get_app_should_return_fast_api_app(self):
        app = create_app()
        assert app
        assert isinstance(app, FastAPI)
