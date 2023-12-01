import uvicorn
from sqlalchemy import Engine, create_engine

from in_concert.app import AppFactory
from in_concert.settings import AppSettingsDev

if __name__ == "__main__":
    app_settings_dev = AppSettingsDev()
    app_factory = AppFactory()
    app_factory.configure(app_settings_dev)

    engine: Engine = create_engine(app_settings_dev.db_connection_string.get_secret_value())
    app = app_factory.create_app(app_settings_dev, engine=engine)
    uvicorn.run(
        app,
        host="localhost",
        port=8001,
        log_level="debug",
    )
