import uvicorn

from in_concert.app import create_app, get_db_session_factory
from in_concert.settings import Auth0SettingsDev

if __name__ == "__main__":
    auth_settings = Auth0SettingsDev()
    session_factory = get_db_session_factory(auth_settings)
    app = create_app(auth_settings, session_factory=session_factory)
    uvicorn.run(
        app,
        host="localhost",
        port=8001,
        log_level="debug",
    )
