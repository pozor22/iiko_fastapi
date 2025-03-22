from fastapi import FastAPI

from core.router import router as core_router

app = FastAPI(
    title='Iiko_fastapi',
    description='API for iiko_fastapi',
    version='1.0.0',
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect"
)


app.include_router(core_router)
