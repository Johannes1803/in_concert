from fastapi import FastAPI


def create_app():
    app = FastAPI()

    @app.get("/")
    async def read_main():
        return {"message": "Hello World"}

    return app
