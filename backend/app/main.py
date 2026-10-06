from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.products.routers import router as product_router

app = FastAPI(
    title="E-Commerce API",
    version="0.1.0"
)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

app.include_router(product_router)
