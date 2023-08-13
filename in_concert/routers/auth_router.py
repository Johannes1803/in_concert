from fastapi.routing import APIRouter

from in_concert.settings import Auth0Settings


def create_router(auth_settings: Auth0Settings):
    router = APIRouter()

    @router.get("/login")
    async def login():
        pass

    return router
