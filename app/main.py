from fastapi import FastAPI

from app.routers import accounts, admin, fetch

app = FastAPI(title="Mail Service API", description="API для управления почтовыми ящиками")

app.include_router(accounts.router)
app.include_router(admin.router)
app.include_router(fetch.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
