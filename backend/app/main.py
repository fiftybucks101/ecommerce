from fastapi import fastapi

app = FastAPI(
    title="E-Commerce API",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }