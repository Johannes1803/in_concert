import uvicorn
from sqlalchemy import Engine, create_engine

from in_concert.app import create_app
from in_concert.settings import Auth0SettingsDev

if __name__ == "__main__":
    auth_settings = Auth0SettingsDev()
    engine: Engine = create_engine(auth_settings.db_connection_string.get_secret_value())
    app = create_app(auth_settings, engine=engine)
    uvicorn.run(
        app,
        host="localhost",
        port=8001,
        log_level="debug",
    )
