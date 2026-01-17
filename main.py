from src.api import create_app

app = create_app()


@app.get("/")
async def root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
