from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy
from app.core.config import settings # To get the SECRET_KEY

# SECRET needs to be defined for get_jwt_strategy
# It's typically loaded from settings, which should already have SECRET_KEY
SECRET = settings.SECRET_KEY

cookie_transport = CookieTransport(cookie_name="animemateauth", cookie_max_age=3600) # Cookie expires in 1 hour

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600) # JWT token also expires in 1 hour

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
