from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:3000",
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "Hello": "World"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
