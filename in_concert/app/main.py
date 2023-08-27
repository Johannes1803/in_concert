import uvicorn

from in_concert.app import create_app
from in_concert.settings import Auth0SettingsDev

if __name__ == "__main__":
    auth_settings = Auth0SettingsDev()
    app = create_app(auth_settings)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="debug",
    )
