"""
RAGHack API
"""
import config
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from routes import rag_hack

app = FastAPI()


@app.get("/ping")
def health_check():
    """Health Check API
    Returns:
        dict: Status object with success message
    """
    return {
        "success": True,
        "message": f"Successfully reached RAGHACK API",
        "data": {}
    }


origins = ["*"]  # specify orgins to handle CORS issue
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1 = FastAPI()

api_v1.include_router(rag_hack.router)

app.mount(f"/raghack/api/v1", api_v1)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(config.PORT),
        log_level="debug",
        workers=1,
        reload=True)
