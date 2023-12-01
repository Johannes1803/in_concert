import uvicorn
from sqlalchemy import Engine, create_engine

from in_concert.app import create_app
from in_concert.settings import AppSettingsDev

if __name__ == "__main__":
    app_settings_dev = AppSettingsDev()
    engine: Engine = create_engine(app_settings_dev.db_connection_string.get_secret_value())
    app = create_app(app_settings_dev, engine=engine)
    uvicorn.run(
        app,
        host="localhost",
        port=8001,
        log_level="debug",
    )
