from mangum import Mangum
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from news.router import router as news_router

load_dotenv()


app = FastAPI(
    title="Gmore backend service", summary="Backend service for Gmore News Summary App"
)
handler = Mangum(app)


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/ping", include_in_schema=False)
async def ping() -> dict[str, str]:
    return {"message": "pong"}


app.include_router(news_router, prefix="", tags=["News"])
