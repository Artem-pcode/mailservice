from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import accounts, admin, fetch, web

app = FastAPI(title="Mail Service API", description="Приватный API для управления почтовыми ящиками без веб-интерфейса", docs_url=None, redoc_url=None, openapi_url=None)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'"
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["postorel.ru", "www.postorel.ru", "localhost", "127.0.0.1"])

app.include_router(accounts.router)
app.include_router(admin.router)
app.include_router(fetch.router)
app.include_router(web.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
